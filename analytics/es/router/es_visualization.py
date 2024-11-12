from fastapi import APIRouter, HTTPException, Query,Depends
import pandas as pd
import os
# from es.es_visualization_model import *
#from ES.utils.file_operations import *
#import analytics_es_config as config
from utils.file_operations import *
# from es import analytics_es_config as config
# from pandas.tseries.offsets import MonthEnd
# from fastapi.security import OAuth2PasswordBearer
current_file_path = os.path.abspath(__file__)
subsystem_name = current_file_path.split(os.path.sep)[-3]
import_model = f"from {subsystem_name}.es_visualization_model import *"
import_config = f"from {subsystem_name} import analytics_es_config as config"
exec(import_model)
exec(import_config)

#with open('/opt/siap/data/raw_data/filekey.key', 'rb') as filekey:
    #key = filekey.read()

#data_csv = file_decrypt(config.CSV_FILE_PATH['upload_file_path']+config.DATA_FILE_NAMES['processed_data_csv_file_name'],key)
#data = pd.read_csv(data_csv)
data = pd.read_csv(config.CSV_FILE_PATH['upload_file_path']+config.DATA_FILE_NAMES['processed_data_csv_file_name'])
# data['DateTime'] = pd.to_datetime(data['DateTime']).dt.strftime('%Y-%m-%d')
# # data['MonthYear'] = pd.to_datetime(data['DateTime'])+MonthEnd(0)
# data['MonthYear'] = pd.to_datetime(data['DateTime']).dt.strftime('%Y-%m')
# unique_dates = data['DateTime'].unique().tolist()
# unique_months = data['MonthYear'].unique().tolist()
# # Create an APIRouter for time series visualization related endpoints.
# router = APIRouter(tags=['ES Data Visualization'])

# Define a route for the AQI Heatmap endpoint.
# @router.get('/Aqi classification',summary='AQI Heatmap location and zone wise')
def aqi_location_and_zonewise_classification():
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
            if not os.path.exists(config.JSON_FILE_PATH['upload_file_path']):
                os.makedirs(config.JSON_FILE_PATH['upload_file_path'])
            processed_data_zone.to_json(config.JSON_FILE_PATH['upload_file_path']+'aqi_zonewise_classification.json',orient='records')
            processed_data_loc.to_json(config.JSON_FILE_PATH['upload_file_path']+'aqi_locwise_classification.json',orient='records')
            processed_data_zone= processed_data_zone.to_dict('records')
            processed_data_loc= processed_data_loc.to_dict('records')
            logging.info('Aqi location and zonewise classification completed.')
            result = {
                'aqi_zonewise_classification':processed_data_zone,
                'aqi_locwise_classification':processed_data_loc
                }
            # Calculate total rows and pages for zone data
        else:
            processed_data_loc = data_processor.location_and_zonewise_aqi_classifier()
            logging.info('Aqi location and zonewise classification completed.')
            if not os.path.exists(config.JSON_FILE_PATH['upload_file_path']):
                os.makedirs(config.JSON_FILE_PATH['upload_file_path'])
            processed_data_loc.to_json(config.JSON_FILE_PATH['upload_file_path']+'aqi_locwise_classification.json',orient='records')
            processed_data_loc= processed_data_loc.to_dict('records')
            
            result = {'aqi_locwise_classification':processed_data_loc}

        return result

    except Exception as e:
        logging.exception(f"Exception occurred:%s",str(e))
         # If an exception occurs, return a 500 Internal Server Error with a detailed error message.
        raise HTTPException(status_code=500, detail=f"Exception occurred: {e}")

# @router.get('/Average values of pollutants and aqi',summary='Average value of 6 pollutants and AQI')
def monthly_average_value_of_6_pollutants_and_aqi(
        # start_date: str = Query(..., description="Start date",enum=unique_months),
        # end_date: str = Query(..., description="End date",enum=unique_months)
        ):
    logger=setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])
    try:
        # Initialize the data processor with the path to your data file.
        # data_processor = ES_Data_Visualization(config.CSV_FILE_PATH['upload_file_path']+config.DATA_FILE_NAMES['processed_data_csv_file_name'])#['processed_data_csv_file_name'])
        data_processor = ES_Data_Visualization(data)
        # print('start_date',start_date)
        # print('end_date',end_date)
        # print(data.head(25)) 
        # filtered_data = data[(data['MonthYear'] >= start_date) & (data['MonthYear'] <= end_date)]
        # data_processor = ES_Data_Visualization(filtered_data)

        logging.info("Processing data to generate Average value of pollutants and AQI...")
         # Process data to generate the Bargraph information.
        aqi_data,pollutants_data = data_processor.average_value_of_variables()
        logging.info("Average values of pollutants and aqi data processing completed.")
        if not os.path.exists(config.JSON_FILE_PATH['upload_file_path']):
            os.makedirs(config.JSON_FILE_PATH['upload_file_path'])
        aqi_data.to_json(config.JSON_FILE_PATH['upload_file_path']+'monthly_average_aqi.json',orient='records')
        pollutants_data.to_json(config.JSON_FILE_PATH['upload_file_path']+'monthly_average_pollutant.json',orient='records')
        aqi_data = aqi_data.to_dict('records')
        pollutants_data = pollutants_data.to_dict('records')
        result = {'aqi_vs_id': aqi_data,
                  'pollutants_concentration_vs_id': pollutants_data}
        return result
    

    except Exception as e:
        logging.exception(f"Exception occurred: {e}")
        # If an exception occurs, return a 500 Internal Server Error with a detailed error message.
        raise HTTPException(status_code=500, detail=f"Exception occurred: {e}")

# @router.get('/Es_outlier', summary='idwise outlier detection')
def ids_vs_outlier(
        # start_date: str = Query(..., description="Start date",enum=unique_dates),
        # end_date: str = Query(..., description="End date",enum=unique_dates)
        ):
    logger=setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])
    # setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])
    # logger = get_logger("es_log_file")
    try:
        # Initialize the data processor with the path to your data file.
        # data_processor = ES_Data_Visualization(config.CSV_FILE_PATH['upload_file_path']+config.DATA_FILE_NAMES['processed_data_csv_file_name'])#['processed_data_csv_file_name'])
        data_processor = ES_Data_Visualization(data)
        # filtered_data = data[(data['DateTime'] >= start_date) & (data['DateTime'] <= end_date)]
        # data_processor = ES_Data_Visualization(filtered_data)
        df_assetloc_csv = file_decrypt(config.CSV_FILE_PATH['location_file_path']+config.DATA_FILE_NAMES['location_data_csv_file_name'],key)
        df_assetloc = pd.read_csv(df_assetloc_csv)
        #data_path=config.CSV_FILE_PATH['upload_file_path']+config.DATA_FILE_NAMES['visualization_data_csv_file_name2']
        # df_assetloc = pd.read_csv(config.CSV_FILE_PATH['location_file_path']+config.DATA_FILE_NAMES['location_data_csv_file_name'])
        df_assetloc = df_assetloc.rename(columns={'id':'Loc id'})
        # print(df_assetloc)
        logging.info("Processing data to generate outlier...")
        
        processed_data = data_processor.outlier_detection(df_assetloc)
        # print(processed_data)

        logging.info("Outlier detection completed.")
        if not os.path.exists(config.JSON_FILE_PATH['upload_file_path']):
            os.makedirs(config.JSON_FILE_PATH['upload_file_path'])
        processed_data.to_json(config.JSON_FILE_PATH['upload_file_path']+'total_outliers_based_on_id.json',orient='records')
        processed_data = processed_data.to_dict('records')
        result = {'total outliers based on id': processed_data}
        return result
        
        # Return the processed data.
        # return processed_data

    except Exception as e:
        logging.exception(f"Exception occurred:%s.",str(e))
         # If an exception occurs, return a 500 Internal Server Error with a detailed error message.
        raise HTTPException(status_code=500, detail=f"Exception occurred: {e}")




# @router.get('/Pollutants_value_count', summary='Value counts classification of 6 pollutants')
def daywise_valuecounts_for_pollutants(
        # start_date: str = Query(..., description="Start date",enum=unique_dates),
        # end_date: str = Query(..., description="End date",enum=unique_dates)
        ):
    logger=setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])

    try:
        # Initialize the data processor with the path to your data file.
        # filtered_data = data[(data['DateTime'] >= start_date) & (data['DateTime'] <= end_date)]
        # data_processor = ES_Data_Visualization(config.CSV_FILE_PATH['upload_file_path']+config.DATA_FILE_NAMES['processed_data_csv_file_name'])#['processed_data_csv_file_name'])
        data_processor = ES_Data_Visualization(data)
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
        if not os.path.exists(config.JSON_FILE_PATH['upload_file_path']):
            os.makedirs(config.JSON_FILE_PATH['upload_file_path'])
        merged_dataframe.to_json(config.JSON_FILE_PATH['upload_file_path']+'valuecount_for_pollutant_data.json',orient='records')
        processed_data = merged_dataframe.to_dict('records')
        result = {'valuecount_for_pollutant_data':processed_data}
        return result

    except Exception as e:
        logging.exception(f"Exception occurred:%s.",str(e))
        # If an exception occurs, return a 500 Internal Server Error with a detailed error message.
        raise HTTPException(status_code=500, detail=f"Exception occurred: {e}")


def aqi_map_creation_data():
    logger=setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])
    try:
        logging.info('Loading csv file')
        # data_processor = ES_Data_Visualization(config.CSV_FILE_PATH['upload_file_path']+config.DATA_FILE_NAMES['processed_data_csv_file_name'])#['processed_data_csv_file_name'])
        data_processor = ES_Data_Visualization(data)
        logging.info("Processing es map creation data...")
        processed_data = data_processor.map_creation_AQI()
        logging.info("Processing of es map creation data completed")
        if not os.path.exists(config.JSON_FILE_PATH['upload_file_path']):
            os.makedirs(config.JSON_FILE_PATH['upload_file_path'])
        processed_data.to_json(config.JSON_FILE_PATH['upload_file_path']+'latest_value_of_aqi.json',orient='records')
        processed_data = processed_data.to_dict('records')
        return {'latest_value_of_AQI':processed_data}

    except Exception as e:
        logging.exception(f"Exception occurred: {e}")
        raise HTTPException(status_code=500, detail=f"Exception occurred: {e}")