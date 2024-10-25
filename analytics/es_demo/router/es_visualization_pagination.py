from fastapi import APIRouter, HTTPException, Query,Depends
import pandas as pd
# from es.es_visualization_model import *
#from ES.utils.file_operations import *
#import analytics_es_config as config
from utils.file_operations import *
import os
# from es import analytics_es_config as config
# from pandas.tseries.offsets import MonthEnd
# from fastapi.security import OAuth2PasswordBearer
current_file_path = os.path.abspath(__file__)
subsystem_name = current_file_path.split(os.path.sep)[-3]
import_model = f"from {subsystem_name}.es_visualization_model import *"
import_config = f"from {subsystem_name} import analytics_es_config as config"
exec(import_model)
exec(import_config)


data = pd.read_csv(config.CSV_FILE_PATH['upload_file_path']+config.DATA_FILE_NAMES['processed_data_csv_file_name'])
data['DateTime'] = pd.to_datetime(data['DateTime']).dt.strftime('%Y-%m-%d')
data = data.sort_values('DateTime')
# data['MonthYear'] = pd.to_datetime(data['DateTime'])+MonthEnd(0)
data['MonthYear'] = pd.to_datetime(data['DateTime']).dt.strftime('%Y-%m')
unique_dates = data['DateTime'].unique().tolist()
unique_months = data['MonthYear'].unique().tolist()
# Create an APIRouter for time series visualization related endpoints.
# router = APIRouter(tags=['ES Data Visualization'])

# Define a route for the AQI Heatmap endpoint.
# @router.get('/Aqi classification',summary='AQI Heatmap location and zone wise')
def aqi_location_and_zonewise_classification_page(
        page: int = Query(1, ge=1, description="Page number, starting from 1."),
        rows_per_page: int = Query(1000, ge=1, le=1000, description="Number of rows to fetch per page.")
        ):
    logger=setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])
    # setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])
    # logger = get_logger("es_log_file")
    try:
        # Initialize the data processor with the path to your data file.
        # data_processor = ES_Data_Visualization(config.CSV_FILE_PATH['upload_file_path']+config.DATA_FILE_NAMES['processed_data_csv_file_name'])
        data_processor = ES_Data_Visualization(data)
        logging.info("Processing data to classify aqi location and zonewise ...")
        ###### Pagination #######
        if 'Zone' in data.columns:
            processed_data_zone, processed_data_loc = data_processor.location_and_zonewise_aqi_classifier()

            logging.info('Aqi location and zonewise classification completed.')
            # Calculate total rows and pages for zone data
            total_rows_zone = len(processed_data_zone) #8
            total_rows_loc = len(processed_data_loc) #29

            total_pages_zone = (total_rows_zone + rows_per_page - 1) // rows_per_page #2
            total_pages_loc = (total_rows_loc + rows_per_page - 1) // rows_per_page #6

            total_pages = total_pages_zone+total_pages_loc #((total_rows_zone+total_rows_loc) + rows_per_page - 1) // rows_per_page #8

            # Calculate start and end indices for zone data pagination
            start_index_zone = (page - 1) * rows_per_page #0 #5
            end_index_zone = start_index_zone + rows_per_page #5 #10
            has_more_rows_zone = end_index_zone <= total_rows_zone #5<8 #10<8
            # end_index_loc = 0
            # Get subset of processed zone data
            processed_data_zone_subset = processed_data_zone.iloc[start_index_zone:end_index_zone].to_dict('records')
            if page <= total_pages_zone:
                if has_more_rows_zone:
                    result = {'aqi_zonewise_classification': processed_data_zone_subset}
                    result['current_page'] = f'page {page} of {total_pages} pages'
                else:
                    result = {'aqi_zonewise_classification': processed_data_zone_subset}
                    result['Message'] = 'End of zone data. Loc data will start from the next page.'
                    result['current_page'] = f'page {page} of {total_pages} pages'
            else:
                start_index_loc = (page - (total_pages_zone+1)) * rows_per_page #0 #5 3-(2+1) 4-(2+1) 5-(2+1)
                end_index_loc = start_index_loc + rows_per_page #5 #10
                processed_data_loc_subset = processed_data_loc.iloc[start_index_loc:end_index_loc].to_dict('records')
                result = {'aqi_locwise_classification': processed_data_loc_subset}
                result['current_page'] = f'page {page} of {total_pages} pages'
            return result
        else:
            processed_data_loc = data_processor.location_and_zonewise_aqi_classifier()
            logging.info('Aqi location and zonewise classification completed.')
            total_rows = len(processed_data_loc)
            total_pages = (total_rows + rows_per_page - 1) // rows_per_page
            start_index = (page - 1) * rows_per_page
            end_index = start_index + rows_per_page
            # has_more_rows = end_index < total_rows
            processed_data_loc_subset = processed_data_loc.iloc[start_index:end_index].to_dict('records')
            
            result = {'aqi_locwise_classification':processed_data_loc_subset}
            result['current_page'] = f'page {page} of {total_pages} pages'

            return result

    except Exception as e:
        logging.error(f"Exception occurred:%s",str(e))
         # If an exception occurs, return a 500 Internal Server Error with a detailed error message.
        raise HTTPException(status_code=500, detail=f"Exception occurred: {e}")

# @router.get('/Average values of pollutants and aqi',summary='Average value of 6 pollutants and AQI')
def monthly_average_value_of_6_pollutants_and_aqi_page(
        start_date: str = Query(..., description="Start date",enum=unique_months),
        end_date: str = Query(..., description="End date",enum=unique_months),
        page: int = Query(1, ge=1, description="Page number, starting from 1."),
        rows_per_page: int = Query(1000, ge=1, le=1000, description="Number of rows to fetch per page.")
        ):
    logger=setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])
    # setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])
    # logger = get_logger("es_log_file")
    try:
        # Initialize the data processor with the path to your data file.
        # data_processor = ES_Data_Visualization(config.CSV_FILE_PATH['upload_file_path']+config.DATA_FILE_NAMES['processed_data_csv_file_name'])#['processed_data_csv_file_name'])
        # print('start_date',start_date)
        # print('end_date',end_date)
        # print(data.head(25)) 
        filtered_data = data[(data['MonthYear'] >= start_date) & (data['MonthYear'] <= end_date)]
        print(filtered_data)
        data_processor = ES_Data_Visualization(filtered_data)

        logging.info("Processing data to generate Average value of pollutants and AQI...")
         # Process data to generate the Bargraph information.
        aqi_data,pollutants_data = data_processor.average_value_of_variables()
        logging.info("Average values of pollutants and aqi data processing completed.")
        
        ###### Pagination #######
        total_rows_aqi = len(aqi_data) #8
        total_rows_pollutants = len(pollutants_data) #29

        total_pages_aqi = (total_rows_aqi + rows_per_page - 1) // rows_per_page #2
        total_pages_pollutants = (total_rows_pollutants + rows_per_page - 1) // rows_per_page #6
        total_pages = total_pages_aqi + total_pages_pollutants
        # total_pages = ((total_rows_aqi+total_rows_pollutants) + rows_per_page - 1) // rows_per_page #8

        # Calculate start and end indices for zone data pagination
        start_index_aqi = (page - 1) * rows_per_page #0 #5
        end_index_aqi = start_index_aqi + rows_per_page #5 #10
        has_more_rows_aqi = end_index_aqi <= total_rows_aqi #5<8 #10<8
        # end_index_loc = 0
        # Get subset of processed zone data
        aqi_data_subset = aqi_data.iloc[start_index_aqi:end_index_aqi].to_dict('records')
        if page <= total_pages_aqi:
            if has_more_rows_aqi:
                result = {'aqi_vs_id': aqi_data_subset}
                result['current_page'] = f'page {page} of {total_pages} pages'
            else:
                result =  {'aqi_vs_id': aqi_data_subset}
                result['Message'] = 'End of AQI data. Pollutants data will start from the next page.'
                result['current_page'] = f'page {page} of {total_pages} pages'
        else:
            start_index_pollutants = (page - (total_pages_aqi+1)) * rows_per_page #0 #5 3-(2+1) 4-(2+1) 5-(2+1)
            end_index_pollutants = start_index_pollutants + rows_per_page #5 #10
            pollutants_data_subset = pollutants_data.iloc[start_index_pollutants:end_index_pollutants].to_dict('records')
            result = {'pollutants_concentration_vs_id': pollutants_data_subset}
            result['current_page'] = f'page {page} of {total_pages} pages'
        return result
    

    except Exception as e:
        logging.error(f"Exception occurred: {e}")
        # If an exception occurs, return a 500 Internal Server Error with a detailed error message.
        raise HTTPException(status_code=500, detail=f"Exception occurred: {e}")

# @router.get('/Es_outlier', summary='idwise outlier detection')
def ids_vs_outlier_page(
        start_date: str = Query(..., description="Start date",enum=unique_dates),
        end_date: str = Query(..., description="End date",enum=unique_dates),
        page: int = Query(1, ge=1, description="Page number, starting from 1."),
        rows_per_page: int = Query(1000, ge=1, le=1000, description="Number of rows to fetch per page.")
        ):
    logger=setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])
    # setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])
    # logger = get_logger("es_log_file")
    try:
        # Initialize the data processor with the path to your data file.
        # data_processor = ES_Data_Visualization(config.CSV_FILE_PATH['upload_file_path']+config.DATA_FILE_NAMES['processed_data_csv_file_name'])#['processed_data_csv_file_name'])
        filtered_data = data[(data['DateTime'] >= start_date) & (data['DateTime'] <= end_date)]
        data_processor = ES_Data_Visualization(filtered_data)
        #data_path=config.CSV_FILE_PATH['upload_file_path']+config.DATA_FILE_NAMES['visualization_data_csv_file_name2']
        df_assetloc = pd.read_csv(config.CSV_FILE_PATH['location_file_path']+config.DATA_FILE_NAMES['location_data_csv_file_name'])
        df_assetloc = df_assetloc.rename(columns={'id':'Loc id'})
        # print(df_assetloc)
        logging.info("Processing data to generate outlier...")
        
        processed_data = data_processor.outlier_detection(df_assetloc)
        # print(processed_data)

        logging.info("Outlier detection completed.")

        # Pagination
        total_rows = len(processed_data)
        total_pages = (total_rows + rows_per_page - 1) // rows_per_page
        start_index = (page - 1) * rows_per_page
        end_index = start_index + rows_per_page
        # has_more_rows = end_index < total_rows
        processed_data_subset = processed_data.iloc[start_index:end_index].to_dict('records')

        # if has_more_rows:
        result = {'total outliers based on id': processed_data_subset}
        result['current_page'] = f'page {page} of {total_pages} pages'
        return result
        
        # Return the processed data.
        # return processed_data

    except Exception as e:
        logging.exception(f"Exception occurred:%s.",str(e))
         # If an exception occurs, return a 500 Internal Server Error with a detailed error message.
        raise HTTPException(status_code=500, detail=f"Exception occurred: {e}")




# @router.get('/Pollutants_value_count', summary='Value counts classification of 6 pollutants')
def daywise_valuecounts_for_pollutants_page(
        start_date: str = Query(..., description="Start date",enum=unique_dates),
        end_date: str = Query(..., description="End date",enum=unique_dates),
        page: int = Query(1, ge=1, description="Page number, starting from 1."),
        rows_per_page: int = Query(1000, ge=1, le=1000, description="Number of rows to fetch per page.")
        ):
    logger=setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])

    try:
        # Initialize the data processor with the path to your data file.
        filtered_data = data[(data['DateTime'] >= start_date) & (data['DateTime'] <= end_date)]
        data_processor = ES_Data_Visualization(filtered_data)
        logging.info("Processing value counts data...")
        # Process data to generate pie chart information.
        pollutants = ['PM10', 'PM25', 'SO2', 'CO', 'O3', 'NO2']
        processed_data_dict = {}
        for pollutant in pollutants:
            processed_data_dict[f'processed_data_{pollutant}'] = data_processor.pollutants_valuecount_classifier(pollutant)
            logging.info(f'Value counts data processing {pollutant} completed.')
       
        dataframes = []
        for key, df in processed_data_dict.items():
            # key=df
            df['pollutant'] = key.split('_')[2]  
            dataframes.append(df)
        merged_dataframe = pd.concat(dataframes, ignore_index=True)
        
        # ######## Pagination ##########
        total_rows = len(merged_dataframe)
        total_pages = (total_rows + rows_per_page - 1) // rows_per_page
        start_index = (page - 1) * rows_per_page
        end_index = start_index + rows_per_page
        # # has_more_rows = end_index < total_rows
        processed_data_subset = merged_dataframe[start_index:end_index].to_dict('records')
        result = {'valuecount_for_pollutant_data':processed_data_subset}
        result['current_page'] = f'page {page} of {total_pages} pages'
        return result

    except Exception as e:
        logging.exception(f"Exception occurred:%s.",str(e))
        # If an exception occurs, return a 500 Internal Server Error with a detailed error message.
        raise HTTPException(status_code=500, detail=f"Exception occurred: {e}")


def aqi_map_creation_data_page(page: int = Query(1, ge=1, description="Page number, starting from 1."),
        rows_per_page: int = Query(1000, ge=1, le=1000, description="Number of rows to fetch per page.")):
    logger=setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])
    try:
        logging.info('Loading csv file')
        data_processor = ES_Data_Visualization(data)
        logging.info("Processing es map creation data...")
        processed_data = data_processor.map_creation_AQI()
        logging.info("Processing of es map creation data completed")
        #### Pagination
        total_rows = len(processed_data)
        total_pages = (total_rows + rows_per_page - 1) // rows_per_page
        start_index = (page - 1) * rows_per_page
        end_index = start_index + rows_per_page
        # # has_more_rows = end_index < total_rows
        processed_data_subset = processed_data[start_index:end_index].to_dict('records')
        result = {'latest_value_of_AQI':processed_data_subset}
        result['current_page'] = f'page {page} of {total_pages} pages'
        return result

    except Exception as e:
        logging.exception(f"Exception occurred: {e}")
        raise HTTPException(status_code=500, detail=f"Exception occurred: {e}")