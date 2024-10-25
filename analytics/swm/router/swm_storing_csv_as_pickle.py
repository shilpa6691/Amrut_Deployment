from fastapi import APIRouter, File, UploadFile, Query, HTTPException,Depends
import pandas as pd
from utils.file_operations import *
# from swm.swm_model import *
from enum import Enum
import os
# from swm import analytics_swm_config as config
current_file_path = os.path.abspath(__file__)
subsystem_name = current_file_path.split(os.path.sep)[-3]
import_model = f"from {subsystem_name}.{subsystem_name}_model import *"
import_config = f"from {subsystem_name} import analytics_{subsystem_name}_config as config"
exec(import_model)
exec(import_config)


# router = APIRouter(prefix='/swm_time_series_forecasting',tags=['SWM Time Series Forecasting'])

# # Define an API endpoint to store the uploaded CSV file as a pickle file
# @router.post('/swm_storing_csv_pickle',summary='csv to pickle file')
def swm_storing_csv_pickle(subsystem_name_for_pickle_file: str = Query(..., description='Please provide the name of the subsystem')):
        
    """
    This api stores the uploaded csv file as pickle file.
    - **subsystem_name_for_pickle_file** mandatory query parameter
    """
    logger=setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])
    # setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])
    # logger = get_logger("swm_log_file")
    try:
        # Read the CSV file into a pandas DataFrame
        zonewise_df = pd.read_csv(config.CSV_FILE_PATH['upload_file_path']+config.DATA_FILE_NAMES['processed_data_csv_file_name'], index_col='DateTime',parse_dates=True)

        # Preparing time series analysis data
        class_for_data_preparation = SWM_TS_Data_Transformation(zonewise_df) 
        cleaned_data = class_for_data_preparation.data_tranformation() 
        # Save the Dataframe to a pickle file
        # Directory for storing pickle files
        # logger.info(cleaned_data.tail(30))
        save_pickle_file(cleaned_data,config.PICKLE_FILES_DIRECTORY['pickle_files_path'],f'csv_file_{subsystem_name_for_pickle_file}.pkl')

        logger.info('The csv file is saved as a pickle file')
        # Return a success message to the user
        return {'message': 'SWM File is saved as a pickle file successfully'}

    except Exception as e:
        logging.exception('Exception occurred during storing CSV as a pickle file')
        # If an exception occurs during the process, raise an HTTPException with a 500 status code
        raise HTTPException(status_code=500, detail="Exception occurred during storing CSV as a pickle file")
