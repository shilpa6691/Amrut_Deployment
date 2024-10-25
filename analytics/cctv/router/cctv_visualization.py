from fastapi import APIRouter, HTTPException, Query
import pandas as pd
import numpy as np
from cctv.cctv_model import *
import cctv.analytics_cctv_config as config
from utils.file_operations import *

# router = APIRouter()
data1 = pd.read_csv(config.CCTV_FILE_PATH['upload_file_path']+config.FILE_NAME['processed_data_csv_file_name1'])
data2 = pd.read_csv(config.CCTV_FILE_PATH['upload_file_path']+config.FILE_NAME['processed_data_csv_file_name2'])
data3 = pd.read_csv(config.CCTV_FILE_PATH['upload_file_path']+config.FILE_NAME['processed_data_csv_file_name3'])
data1['DateTime'] = pd.to_datetime(data1['DateTime']).dt.strftime('%Y-%m-%d')
data2['DateTime'] = pd.to_datetime(data2['DateTime']).dt.strftime('%Y-%m-%d')
data3['DateTime'] = pd.to_datetime(data3['DateTime']).dt.strftime('%Y-%m-%d')
unique_dates = data1['DateTime'].unique().tolist()


# data1['Zone_Ward'] = data1['Zone']+'_'+data1['Ward']
# data2['Zone_Ward'] = data2['Zone']+'_'+data2['Ward']
# data3['Zone_Ward'] = data3['Zone']+'_'+data3['Ward']
# print(data1.head())



def total_number_of_cameras(
        start_date: str = Query(..., description="Start date",enum=unique_dates),
        end_date: str = Query(..., description="End date",enum=unique_dates),
        page: int = Query(1, ge=1, description="Page number, starting from 1."),
        rows_per_page: int = Query(1000, ge=1, le=1000, description="Number of rows to fetch per page.")
        ):
    logger=setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])
    try:
        logger.info("Loading cleaned data files.")

        # cleaned_data1 = pd.read_csv(config.CCTV_FILE_PATH['upload_file_path']+config.FILE_NAME['processed_data_csv_file_name1'])
        # cleaned_data2 = pd.read_csv(config.CCTV_FILE_PATH['upload_file_path']+config.FILE_NAME['processed_data_csv_file_name2'])
        # cleaned_data3 = pd.read_csv(config.CCTV_FILE_PATH['upload_file_path']+config.FILE_NAME['processed_data_csv_file_name3'])
        
        filtered_data1 = data1[(data1['DateTime'] >= start_date) & (data1['DateTime'] <= end_date)]
        filtered_data2 = data2[(data2['DateTime'] >= start_date) & (data2['DateTime'] <= end_date)]
        filtered_data3 = data3[(data3['DateTime'] >= start_date) & (data3['DateTime'] <= end_date)]

        data_processor_class = Data_Processing()

        logger.info("Counting number of cameras...")

        total_cam_data1 = data_processor_class.cameras_count(filtered_data1,['Zone','Ward'],['Zone','Ward'],{'LocCam':'nunique'},config.CCTV_NAME['cctv_name1'])
        total_cam_data2 = data_processor_class.cameras_count(filtered_data2,['Zone','Ward'],['Zone','Ward'],{'LocCam':'nunique'},config.CCTV_NAME['cctv_name2'])
        total_cam_data3 = data_processor_class.cameras_count(filtered_data3,['Zone','Ward'],['Zone','Ward'],{'LocCam':'nunique'},config.CCTV_NAME['cctv_name3'])
        logger.info("Counting completed!")

        logger.info("Merging total comera dataframes...")
        df_total_zone_ward = total_cam_data1.merge(total_cam_data2,on=['Zone','Ward'],how='outer')
        df_total_zone_ward = df_total_zone_ward.merge(total_cam_data3,on=['Zone','Ward'],how='outer')
        df_total_zone_ward = df_total_zone_ward.replace(np.nan,0)
        df_total_zone_ward['Zone_Ward'] = df_total_zone_ward['Zone']+'_'+df_total_zone_ward['Ward']
        logger.info("Merging completed!")

        Inferences = []
        max_value_total1 = df_total_zone_ward[config.CCTV_NAME['cctv_name1']].max()
        max_row_total1 = df_total_zone_ward[df_total_zone_ward[config.CCTV_NAME['cctv_name1']]==max_value_total1]['Zone_Ward'].unique()
        
        max_value_total2 = df_total_zone_ward[config.CCTV_NAME['cctv_name2']].max()
        max_row_total2 = df_total_zone_ward[df_total_zone_ward[config.CCTV_NAME['cctv_name2']]==max_value_total2]['Zone_Ward'].unique()
        
        max_value_total3 = df_total_zone_ward[config.CCTV_NAME['cctv_name3']].max()
        max_row_total3 = df_total_zone_ward[df_total_zone_ward[config.CCTV_NAME['cctv_name3']]==max_value_total3]['Zone_Ward'].unique()#.values
        

        Inferences.append(f"Maximum count of {config.CCTV_NAME['cctv_name1']} cameras is {max_value_total1} and is located in {' and '.join( max_row_total1)}")
        Inferences.append(f"Maximum count of {config.CCTV_NAME['cctv_name2']} cameras is {max_value_total2} and is located in {' and '.join( max_row_total2)}")
        Inferences.append(f"Maximum count of {config.CCTV_NAME['cctv_name3']} cameras is {max_value_total3} and is located in {' and '.join( max_row_total3)}")

        # Pagination
        total_rows = len(df_total_zone_ward)
        total_pages = (total_rows + rows_per_page - 1) // rows_per_page
        start_index = (page - 1) * rows_per_page
        end_index = start_index + rows_per_page
        has_more_rows = end_index < total_rows
        df_total_zone_ward = df_total_zone_ward.drop(columns='Zone_Ward')
        processed_data_subset = df_total_zone_ward.iloc[start_index:end_index].to_dict('records')

        if has_more_rows:
            result = {'Total number of cameras': processed_data_subset}
            result['current_page'] = f'page {page} of {total_pages} pages'
        else:
            result = {
                'Total number of cameras': processed_data_subset,
                'Inference from total number of cameras': Inferences
            }
            result['current_page'] = f'page {page} of {total_pages} pages'

        return result
    
    except Exception as e:
        logging.exception('Exception occurred during faulty camera dataframe preparation:%s.',str(e))
        # If an exception occurs during the model fitting process, raise an HTTPException with a 500 status code.
        raise HTTPException(status_code=500, detail="Exception occurred during faulty camera dataframe preparation")


# @router.get('/total_cameras_Vs_faulty_cameras')
def percentage_of_faulty_cameras_per_day(
        start_date: str = Query(..., description="Start date",enum=unique_dates),
        end_date: str = Query(..., description="End date",enum=unique_dates),
        page: int = Query(1, ge=1, description="Page number, starting from 1."),
        rows_per_page: int = Query(1000, ge=1, le=1000, description="Number of rows to fetch per page.")
        ):
    logger=setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])
    try:
        logger.info("Loading cleaned data files.")

        # cleaned_data1 = pd.read_csv(config.CCTV_FILE_PATH['upload_file_path']+config.FILE_NAME['processed_data_csv_file_name1'])
        # cleaned_data2 = pd.read_csv(config.CCTV_FILE_PATH['upload_file_path']+config.FILE_NAME['processed_data_csv_file_name2'])
        # cleaned_data3 = pd.read_csv(config.CCTV_FILE_PATH['upload_file_path']+config.FILE_NAME['processed_data_csv_file_name3'])
        
        filtered_data1 = data1[(data1['DateTime'] >= start_date) & (data1['DateTime'] <= end_date)]
        filtered_data2 = data2[(data2['DateTime'] >= start_date) & (data2['DateTime'] <= end_date)]
        filtered_data3 = data3[(data3['DateTime'] >= start_date) & (data3['DateTime'] <= end_date)]

        data_processor_class = Data_Processing()
        # data_processor_class2 = Data_Processing()
        # data_processor_class3 = Data_Processing()
        logger.info("Counting number of cameras...")
        # Inferences = []
        
        total_cam_data1 = data_processor_class.cameras_count(filtered_data1,['DateTime','Zone','Ward'],['DateTime','Zone','Ward'],{'LocCam':'nunique'},config.CCTV_NAME['cctv_name1'])
        # Inferences.append(f"Maximum count of {config.CCTV_NAME['cctv_name1']} cameras is {total_cam_data1[config.CCTV_NAME['cctv_name1']].max()} and is located in {total_cam_data1.loc[total_cam_data1[config.CCTV_NAME['cctv_name1']]==total_cam_data1[config.CCTV_NAME['cctv_name1']].max(),['Zone','Ward']].values}.")
        total_cam_data2 = data_processor_class.cameras_count(filtered_data2,['DateTime','Zone','Ward'],['DateTime','Zone','Ward'],{'LocCam':'nunique'},config.CCTV_NAME['cctv_name2'])
        # Inferences.append(f"Maximum count of {config.CCTV_NAME['cctv_name2']} cameras is {total_cam_data2[config.CCTV_NAME['cctv_name2']].max()} and is located in {total_cam_data2.loc[total_cam_data2[config.CCTV_NAME['cctv_name2']]==total_cam_data2[config.CCTV_NAME['cctv_name2']].max(),['Zone','Ward']].values}.")
        total_cam_data3 = data_processor_class.cameras_count(filtered_data3,['DateTime','Zone','Ward'],['DateTime','Zone','Ward'],{'LocCam':'nunique'},config.CCTV_NAME['cctv_name3'])
        # Inferences.append(f"Maximum count of {config.CCTV_NAME['cctv_name3']} cameras is {total_cam_data3[config.CCTV_NAME['cctv_name3']].max()} and is located in {total_cam_data3.loc[total_cam_data3[config.CCTV_NAME['cctv_name3']]==total_cam_data3[config.CCTV_NAME['cctv_name3']].max(),['Zone','Ward']].values}.")
        logger.info("Counting completed!")

        # Inferences = []
        # max_value_total1 = total_cam_data1[config.CCTV_NAME['cctv_name1']].max()
        # max_row_total1 = total_cam_data1[total_cam_data1[config.CCTV_NAME['cctv_name1']]==max_value_total1]['Zone_Ward'].unique()
        # max_row_date1 = total_cam_data1[total_cam_data1[config.CCTV_NAME['cctv_name1']]==max_value_total1]['DateTime'].unique()
    
        # max_value_total2 = total_cam_data2[config.CCTV_NAME['cctv_name2']].max()
        # max_row_total2 = total_cam_data2[total_cam_data2[config.CCTV_NAME['cctv_name2']]==max_value_total2]['Zone_Ward'].unique()
        # max_row_date2 = total_cam_data2[total_cam_data2[config.CCTV_NAME['cctv_name2']]==max_value_total2]['DateTime'].unique()

        # max_value_total3 = total_cam_data3[config.CCTV_NAME['cctv_name3']].max()
        # max_row_total3 = total_cam_data3[total_cam_data3[config.CCTV_NAME['cctv_name3']]==max_value_total3]['Zone_Ward'].unique()#.values
        # max_row_date3 = total_cam_data3[total_cam_data3[config.CCTV_NAME['cctv_name3']]==max_value_total3]['DateTime'].unique()

        # # Inferences.append(f"Maximum count of {config.CCTV_NAME['cctv_name1']} cameras is {max_value_total1} and is located in {' and '.join(f'({row.Zone}, {row.Ward})' for index,row in max_row_total1.iterrows())}")
        # # Inferences.append(f"Maximum count of {config.CCTV_NAME['cctv_name2']} cameras is {max_value_total2} and is located in {' and '.join(f'({row.Zone}, {row.Ward})' for index,row in max_row_total2.iterrows())}")
        # # Inferences.append(f"Maximum count of {config.CCTV_NAME['cctv_name3']} cameras is {max_value_total3} and is located in {' and '.join(f'({row.Zone}, {row.Ward})' for index,row in max_row_total3.iterrows())}")
        # Inferences.append(f"Maximum count of {config.CCTV_NAME['cctv_name1']} cameras is {max_value_total1} and is located in {' and '.join( max_row_total1)} on {' and '.join( max_row_date1)}")
        # Inferences.append(f"Maximum count of {config.CCTV_NAME['cctv_name2']} cameras is {max_value_total2} and is located in {' and '.join( max_row_total2)} on {' and '.join( max_row_date2)}")
        # Inferences.append(f"Maximum count of {config.CCTV_NAME['cctv_name3']} cameras is {max_value_total3} and is located in {' and '.join( max_row_total3)} on {' and '.join( max_row_date3)}")


        logger.info("Counting number of faulty cameras...")
        faulty_cam_data1 = data_processor_class.faulty_cam_count(filtered_data1,['DateTime','Zone','Ward','LocCam'],{'Value':'last'},['DateTime','Zone','Ward'],config.CCTV_NAME['cctv_name1'])
        faulty_cam_data2 = data_processor_class.faulty_cam_count(filtered_data2,['DateTime','Zone','Ward','LocCam'],{'Value':'last'},['DateTime','Zone','Ward'],config.CCTV_NAME['cctv_name2'])
        faulty_cam_data3 = data_processor_class.faulty_cam_count(filtered_data3,['DateTime','Zone','Ward','LocCam'],{'Value':'last'},['DateTime','Zone','Ward'],config.CCTV_NAME['cctv_name3'])
        logger.info("Preparation of number of faulty cameras dataframe completed!")

        logger.info("Merging total comera dataframes...")
        df_total_zone_ward = total_cam_data1.merge(total_cam_data2,on=['DateTime','Zone','Ward'],how='outer')
        df_total_zone_ward = df_total_zone_ward.merge(total_cam_data3,on=['DateTime','Zone','Ward'],how='outer')
        df_total_zone_ward = df_total_zone_ward.replace(np.nan,0)
        # df_total_zone_ward = df_total_zone_ward.to_dict('records')
        logger.info("Merging completed!")
        

        logger.info("Calculating faulty cam percentage")
        faulty_percent_data1 = data_processor_class.calculate_faulty_percent(total_cam_data1,faulty_cam_data1,config.CCTV_NAME['cctv_name1'])
        faulty_percent_data2 = data_processor_class.calculate_faulty_percent(total_cam_data2,faulty_cam_data2,config.CCTV_NAME['cctv_name2'])
        faulty_percent_data3 = data_processor_class.calculate_faulty_percent(total_cam_data3,faulty_cam_data3,config.CCTV_NAME['cctv_name3'])
        logger.info("Calculation of faulty camera percentage completed!")

        logger.info("Merging dataframes")
        df_faulty_zone_ward = faulty_percent_data1.merge(faulty_percent_data2,on=['DateTime','Zone','Ward'],how='outer')
        df_faulty_zone_ward = df_faulty_zone_ward.merge(faulty_percent_data3,on=['DateTime','Zone','Ward'],how='outer')
        # df_faulty_zone_ward = df_faulty_zone_ward.merge(faulty_cam_data2,on=['Zone','Ward'],how='outer')
        # df_faulty_zone_ward = df_faulty_zone_ward.merge(total_cam_data3,on=['Zone','Ward'],how='outer')
        # df_faulty_zone_ward = df_faulty_zone_ward.merge(faulty_cam_data3,on=['Zone','Ward'],how='outer')
        df_faulty_zone_ward = df_faulty_zone_ward.replace(np.nan,0)
        df_faulty_zone_ward['Zone_Ward'] = df_faulty_zone_ward['Zone']+'_'+df_faulty_zone_ward['Ward']
        logger.info("Merging of faulty camera percentage dataframe completed!")


        ######Inferences on total camera count######
        Inferences = []
        max_value_total1 = df_faulty_zone_ward[config.CCTV_NAME['cctv_name1']].max()
        max_row_total1 = df_faulty_zone_ward[df_faulty_zone_ward[config.CCTV_NAME['cctv_name1']]==max_value_total1]['Zone_Ward'].unique()
        max_row_date1 = df_faulty_zone_ward[df_faulty_zone_ward[config.CCTV_NAME['cctv_name1']]==max_value_total1]['DateTime'].unique()
    
        max_value_total2 = df_faulty_zone_ward[config.CCTV_NAME['cctv_name2']].max()
        max_row_total2 = df_faulty_zone_ward[df_faulty_zone_ward[config.CCTV_NAME['cctv_name2']]==max_value_total2]['Zone_Ward'].unique()
        max_row_date2 = df_faulty_zone_ward[df_faulty_zone_ward[config.CCTV_NAME['cctv_name2']]==max_value_total2]['DateTime'].unique()

        max_value_total3 = df_faulty_zone_ward[config.CCTV_NAME['cctv_name3']].max()
        max_row_total3 = df_faulty_zone_ward[df_faulty_zone_ward[config.CCTV_NAME['cctv_name3']]==max_value_total3]['Zone_Ward'].unique()#.values
        max_row_date3 = df_faulty_zone_ward[df_faulty_zone_ward[config.CCTV_NAME['cctv_name3']]==max_value_total3]['DateTime'].unique()

        # Inferences.append(f"Maximum count of {config.CCTV_NAME['cctv_name1']} cameras is {max_value_total1} and is located in {' and '.join(f'({row.Zone}, {row.Ward})' for index,row in max_row_total1.iterrows())}")
        # Inferences.append(f"Maximum count of {config.CCTV_NAME['cctv_name2']} cameras is {max_value_total2} and is located in {' and '.join(f'({row.Zone}, {row.Ward})' for index,row in max_row_total2.iterrows())}")
        # Inferences.append(f"Maximum count of {config.CCTV_NAME['cctv_name3']} cameras is {max_value_total3} and is located in {' and '.join(f'({row.Zone}, {row.Ward})' for index,row in max_row_total3.iterrows())}")
        # Inferences.append(f"Maximum count of {config.CCTV_NAME['cctv_name1']} cameras is {max_value_total1} and is located in {' and '.join( max_row_total1)} on {', '.join( max_row_date1)}")
        # Inferences.append(f"Maximum count of {config.CCTV_NAME['cctv_name2']} cameras is {max_value_total2} and is located in {' and '.join( max_row_total2)} on {', '.join( max_row_date2)}")
        # Inferences.append(f"Maximum count of {config.CCTV_NAME['cctv_name3']} cameras is {max_value_total3} and is located in {' and '.join( max_row_total3)} on {', '.join( max_row_date3)}")
        Inferences.append(f"The highest number of {config.CCTV_NAME['cctv_name1']} camera readings captured is {max_value_total1} at {' and '.join(max_row_total1)} on dates {' , '.join(max_row_date1)}.")
        Inferences.append(f"The highest number of {config.CCTV_NAME['cctv_name2']} camera readings captured is {max_value_total2} at {' and '.join(max_row_total2)} on dates {' , '.join(max_row_date2)}.")
        Inferences.append(f"The highest number of {config.CCTV_NAME['cctv_name3']} camera readings captured is {max_value_total3} at {' and '.join(max_row_total3)} on dates {' , '.join(max_row_date3)}.")


        ######Inferences on faulty cameras count######
        Inference1 = []
        max_value1 = df_faulty_zone_ward[config.CCTV_NAME['cctv_name1']+'_faulty_percent'].max()
        max_row1 = df_faulty_zone_ward[df_faulty_zone_ward[config.CCTV_NAME['cctv_name1']+'_faulty_percent']==max_value1]['Zone_Ward'].unique()
        max_date1 = df_faulty_zone_ward[df_faulty_zone_ward[config.CCTV_NAME['cctv_name1']+'_faulty_percent']==max_value1]['DateTime'].unique()

        max_value2 = df_faulty_zone_ward[config.CCTV_NAME['cctv_name2']+'_faulty_percent'].max()
        max_row2 = df_faulty_zone_ward[df_faulty_zone_ward[config.CCTV_NAME['cctv_name2']+'_faulty_percent']==max_value2]['Zone_Ward'].unique()
        max_date2 = df_faulty_zone_ward[df_faulty_zone_ward[config.CCTV_NAME['cctv_name2']+'_faulty_percent']==max_value2]['DateTime'].unique()

        max_value3 = df_faulty_zone_ward[config.CCTV_NAME['cctv_name3']+'_faulty_percent'].max()
        max_row3 = df_faulty_zone_ward[df_faulty_zone_ward[config.CCTV_NAME['cctv_name3']+'_faulty_percent']==max_value3]['Zone_Ward'].unique()
        max_date3 = df_faulty_zone_ward[df_faulty_zone_ward[config.CCTV_NAME['cctv_name3']+'_faulty_percent']==max_value3]['DateTime'].unique()

        Inference1.append(f"Maximum percentage of {config.CCTV_NAME['cctv_name1']} faulty cameras is {max_value1} and is located in {' and '.join(max_row1)} on dates {' , '.join(max_date1)}")
        Inference1.append(f"Maximum percentage of {config.CCTV_NAME['cctv_name2']} faulty cameras is {max_value2} and is located in {' and '.join(max_row2)} on dates {' , '.join(max_date2)}")
        Inference1.append(f"Maximum percentage of {config.CCTV_NAME['cctv_name3']} faulty cameras is {max_value3} and is located in {' and '.join(max_row3)} on dates {' , '.join(max_date3)}")
        
        # Pagination
        total_rows = len(df_faulty_zone_ward)
        total_pages = (total_rows + rows_per_page - 1) // rows_per_page
        start_index = (page - 1) * rows_per_page
        end_index = start_index + rows_per_page
        has_more_rows = end_index < total_rows
        df_faulty_zone_ward = df_faulty_zone_ward.drop(columns='Zone_Ward')
        processed_data_subset = df_faulty_zone_ward.iloc[start_index:end_index].to_dict('records')

        if has_more_rows:
            result = {'Percentage of faulty cameras': processed_data_subset}
            result['current_page'] = f'page {page} of {total_pages} pages'
        else:
            result = {
                'Percentage of faulty cameras': processed_data_subset,
                'Inference from total number of cameras': Inferences,
                'Inference from faulty camera percentage': Inference1
            }
            result['current_page'] = f'page {page} of {total_pages} pages'

        return result
        
        # df_faulty_zone_ward = df_faulty_zone_ward.to_dict('records')
        # return {'Total number of cameras':df_total_zone_ward,
        #         'Inference from total number of cameras': Inferences,
        #         'Percentage of faulty cameras': df_faulty_zone_ward,
        #         'Inference from faulty camera percentage': Inference1
        #         }
    except Exception as e:
        logging.exception('Exception occurred during faulty camera dataframe preparation:%s.',str(e))
        # If an exception occurs during the model fitting process, raise an HTTPException with a 500 status code.
        raise HTTPException(status_code=500, detail="Exception occurred during faulty camera dataframe preparation")

# @router.get('/faulty_cameras_per_day')   
def faulty_cam_per_day(
        start_date: str = Query(..., description="Start date",enum=unique_dates),
        end_date: str = Query(..., description="End date",enum=unique_dates),
        page: int = Query(1, ge=1, description="Page number, starting from 1."),
        rows_per_page: int = Query(1000, ge=1, le=1000, description="Number of rows to fetch per page.")
        ):
    logger=setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])
    try:
        logger.info("Loading cleaned data files.")

        # cleaned_data1 = pd.read_csv(config.CCTV_FILE_PATH['upload_file_path']+config.FILE_NAME['processed_data_csv_file_name1'])
        # cleaned_data2 = pd.read_csv(config.CCTV_FILE_PATH['upload_file_path']+config.FILE_NAME['processed_data_csv_file_name2'])
        # cleaned_data3 = pd.read_csv(config.CCTV_FILE_PATH['upload_file_path']+config.FILE_NAME['processed_data_csv_file_name3'])
        
        filtered_data1 = data1[(data1['DateTime'] >= start_date) & (data1['DateTime'] <= end_date)]
        filtered_data2 = data2[(data2['DateTime'] >= start_date) & (data2['DateTime'] <= end_date)]
        filtered_data3 = data3[(data3['DateTime'] >= start_date) & (data3['DateTime'] <= end_date)]
        

        data_processor_class = Data_Processing()
        # data_processor_class2 = Data_Processing()
        # data_processor_class3 = Data_Processing()
        logger.info("Counting number of faulty cameras...")
        faulty_data1 = data_processor_class.faulty_cam_count(filtered_data1,['Date','Zone','Ward','LocCam'],{'Value':'last'},['Date','Zone','Ward'],config.CCTV_NAME['cctv_name1'])
        faulty_data2 = data_processor_class.faulty_cam_count(filtered_data2,['Date','Zone','Ward','LocCam'],{'Value':'last'},['Date','Zone','Ward'],config.CCTV_NAME['cctv_name2'])
        faulty_data3 = data_processor_class.faulty_cam_count(filtered_data3,['Date','Zone','Ward','LocCam'],{'Value':'last'},['Date','Zone','Ward'],config.CCTV_NAME['cctv_name3'])
        logger.info("Preparation of number of faulty cameras dataframe completed!")
    
        ###### Pagination #######
        total_rows_data1 = len(faulty_data1) 
        total_rows_data2 = len(faulty_data2)
        total_rows_data3 = len(faulty_data3)
        logger.info({'total_rows_data1':total_rows_data1})
        logger.info({'total_rows_data2':total_rows_data2})
        logger.info({'total_rows_data3':total_rows_data3})

        total_pages_data1 = (total_rows_data1 + rows_per_page - 1) // rows_per_page 
        total_pages_data2 = (total_rows_data2 + rows_per_page - 1) // rows_per_page
        total_pages_data3 = (total_rows_data3 + rows_per_page - 1) // rows_per_page
        total_pages = total_pages_data1+total_pages_data2+total_pages_data3
        # total_2 = ((total_rows_data1+total_rows_data2+total_rows_data3) + rows_per_page - 1) // rows_per_page
        # if total_1>=total_2:
        #     total_pages = total_1
        # else:
        #     total_pages = total_2
        # total_pages = ((total_rows_data1+total_rows_data2+total_rows_data3) + rows_per_page - 1) // rows_per_page

        # Calculate start and end indices for data1 pagination
        if total_pages == 0:
            return {'Message': 'No faulty cameras'}
        else:
            start_index_data1 = (page - 1) * rows_per_page #0 #5
            end_index_data1 = start_index_data1 + rows_per_page #5 #10
            has_more_rows_data1 = end_index_data1 <= total_rows_data1 #5<8 #10<8
            
            faulty_data1_subset = faulty_data1.iloc[start_index_data1:end_index_data1].to_dict('records')
            if page <= total_pages_data1:
                if has_more_rows_data1:
                    result = {config.CCTV_NAME['cctv_name1']: faulty_data1_subset}
                    result['current_page'] = f'page {page} of {total_pages} pages'
                else:
                    result =  {config.CCTV_NAME['cctv_name1']: faulty_data1_subset}
                    result['Message'] = f'End of {config.CCTV_NAME["cctv_name1"]} data. {config.CCTV_NAME["cctv_name2"]} data will start from the next page.'
                    result['current_page'] = f'page {page} of {total_pages} pages'
            elif page-total_pages_data1 <= total_pages_data2:
                start_index_data2 = (page - (total_pages_data1+1)) * rows_per_page
                end_index_data2= start_index_data2 + rows_per_page 
                has_more_rows_data2 = end_index_data2 <= total_rows_data2
                faulty_data2_subset = faulty_data2.iloc[start_index_data2:end_index_data2].to_dict('records')
                if has_more_rows_data2:
                    result = {config.CCTV_NAME['cctv_name2']: faulty_data2_subset}
                    result['current_page'] = f'page {page} of {total_pages} pages'
                else:
                    result =  {config.CCTV_NAME['cctv_name2']: faulty_data2_subset}
                    result['Message'] = f'End of {config.CCTV_NAME["cctv_name2"]} data. {config.CCTV_NAME["cctv_name3"]} data will start from the next page.'
                    result['current_page'] = f'page {page} of {total_pages} pages'   
            else:
                start_index_data3 = (page - (total_pages_data1+total_pages_data2+1)) * rows_per_page 
                end_index_data3 = start_index_data3 + rows_per_page #5 #10
                faulty_data3_subset = faulty_data3.iloc[start_index_data3:end_index_data3].to_dict('records')
                result = {config.CCTV_NAME['cctv_name3']: faulty_data3_subset}
                result['current_page'] = f'page {page} of {total_pages} pages'
            return result

    
        # Pagination
        # total_rows = len(faulty_data1)+len(faulty_data2)+len(faulty_data3)
        # total_pages = (total_rows + rows_per_page - 1) // rows_per_page
        # start_index_1 = (page - 1) * rows_per_page
        # end_index_1 = start_index_1 + rows_per_page
        # has_more_rows = end_index_1 < total_rows
        # processed_data_subset_1 = faulty_data1.iloc[start_index_1:end_index_1].to_dict('records')

        # if has_more_rows:
        #     result = {'Percentage of faulty cameras': processed_data_subset_1}
        #     result['current_page'] = f'page {page} of {total_pages} pages'
        # else:
        #     result = {
        #         config.CCTV_NAME['cctv_name1']:faulty_data1.iloc[start_index_1:end_index_1].to_dict('records'),
        #         config.CCTV_NAME['cctv_name2']:faulty_data2.iloc[start_index_1:end_index_1].to_dict('records'),
        #         config.CCTV_NAME['cctv_name3']:faulty_data3.iloc[start_index_1:end_index_1].to_dict('records')
        #     }
        #     result['current_page'] = f'page {page} of {total_pages} pages'

        # return result
        # return {config.CCTV_NAME['cctv_name1']:faulty_data1,
        #         config.CCTV_NAME['cctv_name2']:faulty_data2,
        #         config.CCTV_NAME['cctv_name3']:faulty_data3}
    except Exception as e:
        logging.exception('Exception occurred during faulty camera dataframe preparation:%s.',str(e))
        # If an exception occurs during the model fitting process, raise an HTTPException with a 500 status code.
        raise HTTPException(status_code=500, detail="Exception occurred during faulty camera dataframe preparation")
    
# @router.get('/events_captured_per_day')
def events_per_day(
        start_date: str = Query(..., description="Start date",enum=unique_dates),
        end_date: str = Query(..., description="End date",enum=unique_dates),
        page: int = Query(1, ge=1, description="Page number, starting from 1."),
        rows_per_page: int = Query(1000, ge=1, le=1000, description="Number of rows to fetch per page.")
        ):
    logger=setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])
    try:
        logger.info("Loading cleaned data files.")

        # cleaned_data1 = pd.read_csv(config.CCTV_FILE_PATH['upload_file_path']+config.FILE_NAME['processed_data_csv_file_name1'])
        # cleaned_data2 = pd.read_csv(config.CCTV_FILE_PATH['upload_file_path']+config.FILE_NAME['processed_data_csv_file_name2'])
        # cleaned_data3 = pd.read_csv(config.CCTV_FILE_PATH['upload_file_path']+config.FILE_NAME['processed_data_csv_file_name3'])
        
        filtered_data1 = data1[(data1['DateTime'] >= start_date) & (data1['DateTime'] <= end_date)]
        filtered_data2 = data2[(data2['DateTime'] >= start_date) & (data2['DateTime'] <= end_date)]
        filtered_data3 = data3[(data3['DateTime'] >= start_date) & (data3['DateTime'] <= end_date)]
        # if len(filtered_data1) == len(filtered_data2) == len(filtered_data3) == 0:
        #     return {'Message':'No data'}

        data_processor_class = Data_Processing()
        # data_processor_class2 = Data_Processing()
        # data_processor_class3 = Data_Processing()

        logger.info("Counting number of events captured in each cameras...")
        events_data1 = data_processor_class.events_captured(filtered_data1,['Date','Zone','Ward','LocCam'],{'Value':'sum'},['Date','Zone','Ward'],config.CCTV_NAME['cctv_name1'])
        events_data2 = data_processor_class.events_captured(filtered_data2,['Date','Zone','Ward','LocCam'],{'Value':'sum'},['Date','Zone','Ward'],config.CCTV_NAME['cctv_name2'])
        events_data3 = data_processor_class.events_captured(filtered_data3,['Date','Zone','Ward','LocCam'],{'Value':'sum'},['Date','Zone','Ward'],config.CCTV_NAME['cctv_name3'])
        logger.info("Preparation of number of events captured is completed!")
        logger.info({config.CCTV_NAME['cctv_name1']:events_data1.shape})
        logger.info({config.CCTV_NAME['cctv_name2']:events_data2.shape})
        logger.info({config.CCTV_NAME['cctv_name3']:events_data3.shape})

        ###### Pagination #######
        total_rows_data1 = len(events_data1) 
        total_rows_data2 = len(events_data2)
        total_rows_data3 = len(events_data3)
        logger.info({'total_rows_data1':total_rows_data1})
        logger.info({'total_rows_data2':total_rows_data2})
        logger.info({'total_rows_data3':total_rows_data3})

        total_pages_data1 = (total_rows_data1 + rows_per_page - 1) // rows_per_page 
        total_pages_data2 = (total_rows_data2 + rows_per_page - 1) // rows_per_page
        total_pages_data3 = (total_rows_data3 + rows_per_page - 1) // rows_per_page
        total_pages = total_pages_data1+total_pages_data2+total_pages_data3
        # total_2 = ((total_rows_data1+total_rows_data2+total_rows_data3) + rows_per_page - 1) // rows_per_page
        # if total_1>=total_2:
        #     total_pages = total_1
        # else:
        #     total_pages = total_2
        # total_pages = ((total_rows_data1+total_rows_data2+total_rows_data3) + rows_per_page - 1) // rows_per_page

        # Calculate start and end indices for data1 pagination
        if total_pages == 0:
            return {'Message': 'No events captured'}
        else:
            start_index_data1 = (page - 1) * rows_per_page #0 #5
            end_index_data1 = start_index_data1 + rows_per_page #5 #10
            has_more_rows_data1 = end_index_data1 <= total_rows_data1 #5<8 #10<8
            
            events_data1_subset = events_data1.iloc[start_index_data1:end_index_data1].to_dict('records')
            if page <= total_pages_data1:
                if has_more_rows_data1:
                    result = {config.CCTV_NAME['cctv_name1']: events_data1_subset}
                    result['current_page'] = f'page {page} of {total_pages} pages'
                else:
                    result =  {config.CCTV_NAME['cctv_name1']: events_data1_subset}
                    if total_pages_data2 != 0:
                        result['Message'] = f'End of {config.CCTV_NAME["cctv_name1"]} data. {config.CCTV_NAME["cctv_name2"]} data will start from the next page.'
                        result['current_page'] = f'page {page} of {total_pages} pages'
                    else:
                        result['Message'] = f'End of {config.CCTV_NAME["cctv_name1"]} data. No data for {config.CCTV_NAME["cctv_name2"]} camera.'
                        result['current_page'] = f'page {page} of {total_pages} pages'
            elif page-total_pages_data1 <= total_pages_data2:
                start_index_data2 = (page - (total_pages_data1+1)) * rows_per_page
                end_index_data2= start_index_data2 + rows_per_page 
                has_more_rows_data2 = end_index_data2 <= total_rows_data2
                events_data2_subset = events_data2.iloc[start_index_data2:end_index_data2].to_dict('records')
                if has_more_rows_data2:
                    result = {config.CCTV_NAME['cctv_name2']: events_data2_subset}
                    result['current_page'] = f'page {page} of {total_pages} pages'
                else:
                    result =  {config.CCTV_NAME['cctv_name2']: events_data2_subset}
                    if total_pages_data3 != 0:
                        result['Message'] = f'End of {config.CCTV_NAME["cctv_name2"]} data. {config.CCTV_NAME["cctv_name3"]} data will start from the next page.'
                        result['current_page'] = f'page {page} of {total_pages} pages'
                    else:
                        result['Message'] = f'End of {config.CCTV_NAME["cctv_name2"]} data. No data for {config.CCTV_NAME["cctv_name3"]} camera.'
                        result['current_page'] = f'page {page} of {total_pages} pages' 
            else:
                start_index_data3 = (page - (total_pages_data1+total_pages_data2+1)) * rows_per_page 
                end_index_data3 = start_index_data3 + rows_per_page #5 #10
                events_data3_subset = events_data3.iloc[start_index_data3:end_index_data3].to_dict('records')
                result = {config.CCTV_NAME['cctv_name3']: events_data3_subset}
                result['current_page'] = f'page {page} of {total_pages} pages'
            return result
    
        # logger.info("Returning data")
        # return {config.CCTV_NAME['cctv_name1']:events_data1,
        #         config.CCTV_NAME['cctv_name2']:events_data2,
        #         config.CCTV_NAME['cctv_name3']:events_data3}
        
    except Exception as e:
        logging.exception('Exception occurred during the preparation of events captured per day:%s.',str(e))
        raise HTTPException(status_code=500, detail="Exception occurred during faulty camera dataframe preparation")
    

def events_Vs_time_of_the_day(
        start_date: str = Query(..., description="Start date",enum=unique_dates),
        end_date: str = Query(..., description="End date",enum=unique_dates),
        page: int = Query(1, ge=1, description="Page number, starting from 1."),
        rows_per_page: int = Query(1000, ge=1, le=1000, description="Number of rows to fetch per page.")
        ):
    logger=setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])
    try:
        logger.info("Loading cleaned data files.")

        # cleaned_data1 = pd.read_csv(config.CCTV_FILE_PATH['upload_file_path']+config.FILE_NAME['processed_data_csv_file_name1'])
        # cleaned_data2 = pd.read_csv(config.CCTV_FILE_PATH['upload_file_path']+config.FILE_NAME['processed_data_csv_file_name2'])
        # cleaned_data3 = pd.read_csv(config.CCTV_FILE_PATH['upload_file_path']+config.FILE_NAME['processed_data_csv_file_name3'])
        
        filtered_data1 = data1[(data1['DateTime'] >= start_date) & (data1['DateTime'] <= end_date)]
        filtered_data2 = data2[(data2['DateTime'] >= start_date) & (data2['DateTime'] <= end_date)]
        filtered_data3 = data3[(data3['DateTime'] >= start_date) & (data3['DateTime'] <= end_date)]

        data_processor_class = Data_Processing()
        # data_processor_class2 = Data_Processing()
        # data_processor_class3 = Data_Processing()

        logger.info("Counting number of events captured in each cameras...")
        events_data1 = data_processor_class.events_captured(filtered_data1,['time_window','Zone','Ward','LocCam'],{'Value':'sum'},['time_window','Zone','Ward'],config.CCTV_NAME['cctv_name1'])
        events_data2 = data_processor_class.events_captured(filtered_data2,['time_window','Zone','Ward','LocCam'],{'Value':'sum'},['time_window','Zone','Ward'],config.CCTV_NAME['cctv_name2'])
        events_data3 = data_processor_class.events_captured(filtered_data3,['time_window','Zone','Ward','LocCam'],{'Value':'sum'},['time_window','Zone','Ward'],config.CCTV_NAME['cctv_name3'])
        logger.info("Preparation of number of events captured is completed!")
        logger.info({config.CCTV_NAME['cctv_name1']:events_data1.shape})
        logger.info({config.CCTV_NAME['cctv_name2']:events_data2.shape})
        logger.info({config.CCTV_NAME['cctv_name3']:events_data3.shape})
        
        ###### Pagination #######
        total_rows_data1 = len(events_data1) 
        total_rows_data2 = len(events_data2)
        total_rows_data3 = len(events_data3)

        total_pages_data1 = (total_rows_data1 + rows_per_page - 1) // rows_per_page 
        total_pages_data2 = (total_rows_data2 + rows_per_page - 1) // rows_per_page
        total_pages_data3 = (total_rows_data3 + rows_per_page - 1) // rows_per_page
        total_pages = total_pages_data1+total_pages_data2+total_pages_data3
        # total_1 = total_pages_data1+total_pages_data2+total_pages_data3 ###(2+2+1 = 5)
        # total_2 = ((total_rows_data1+total_rows_data2+total_rows_data3) + rows_per_page - 1) // rows_per_page ###(1678+1016+822)+1000-1 = 4
        # if total_1>=total_2:
        #     total_pages = total_1
        # else:
        #     total_pages = total_2
        # total_pages = ((total_rows_data1+total_rows_data2+total_rows_data3) + rows_per_page - 1) // rows_per_page
        if total_pages == 0:
            return {'Message': 'No events captured'}
        else:
            # Calculate start and end indices for data1 pagination
            start_index_data1 = (page - 1) * rows_per_page #0 #5
            end_index_data1 = start_index_data1 + rows_per_page #5 #10
            has_more_rows_data1 = end_index_data1 <= total_rows_data1 #5<8 #10<8
            
            events_data1_subset = events_data1.iloc[start_index_data1:end_index_data1].to_dict('records')
            if page <= total_pages_data1:
                if has_more_rows_data1:
                    result = {config.CCTV_NAME['cctv_name1']: events_data1_subset}
                    result['current_page'] = f'page {page} of {total_pages} pages'
                else:
                    result =  {config.CCTV_NAME['cctv_name1']: events_data1_subset}
                    if total_pages_data2 != 0:
                        result['Message'] = f'End of {config.CCTV_NAME["cctv_name1"]} data. {config.CCTV_NAME["cctv_name2"]} data will start from the next page.'
                        result['current_page'] = f'page {page} of {total_pages} pages'
                    else:
                        result['Message'] = f'End of {config.CCTV_NAME["cctv_name1"]} data. No data for {config.CCTV_NAME["cctv_name2"]} camera.'
                        result['current_page'] = f'page {page} of {total_pages} pages'
            elif page-total_pages_data1 <= total_pages_data2:
                start_index_data2 = (page - (total_pages_data1+1)) * rows_per_page
                end_index_data2= start_index_data2 + rows_per_page 
                has_more_rows_data2 = end_index_data2 <= total_rows_data2
                events_data2_subset = events_data2.iloc[start_index_data2:end_index_data2].to_dict('records')
                if has_more_rows_data2:
                    result = {config.CCTV_NAME['cctv_name2']: events_data2_subset}
                    result['current_page'] = f'page {page} of {total_pages} pages'
                else:
                    result =  {config.CCTV_NAME['cctv_name2']: events_data2_subset}
                    if total_pages_data3 != 0:
                        result['Message'] = f'End of {config.CCTV_NAME["cctv_name2"]} data. {config.CCTV_NAME["cctv_name3"]} data will start from the next page.'
                        result['current_page'] = f'page {page} of {total_pages} pages'
                    else:
                        result['Message'] = f'End of {config.CCTV_NAME["cctv_name2"]} data. No data for {config.CCTV_NAME["cctv_name3"]} camera.'
                        result['current_page'] = f'page {page} of {total_pages} pages'   
            else:
                start_index_data3 = (page - (total_pages_data1+total_pages_data2+1)) * rows_per_page 
                end_index_data3 = start_index_data3 + rows_per_page #5 #10
                events_data3_subset = events_data3.iloc[start_index_data3:end_index_data3].to_dict('records')
                result = {config.CCTV_NAME['cctv_name3']: events_data3_subset}
                result['current_page'] = f'page {page} of {total_pages} pages'
            return result
    
        # logger.info("Returning data")
        # return {config.CCTV_NAME['cctv_name1']:events_data1,
        #         config.CCTV_NAME['cctv_name2']:events_data2,
        #         config.CCTV_NAME['cctv_name3']:events_data3}
        
    except Exception as e:
        logging.exception('Exception occurred during the preparation of events captured per day:%s.',str(e))
        raise HTTPException(status_code=500, detail="Exception occurred during faulty camera dataframe preparation")
    

    

