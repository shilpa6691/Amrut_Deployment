
#!/opt/siap/analytics/analytics_env/bin/python3

from fastapi import APIRouter, File, UploadFile, Query, HTTPException,Depends
import pandas as pd
import shutil
from utils.file_operations import *
# from es.es_model import *
import os
# from es import analytics_es_config as config
current_file_path = os.path.abspath(__file__)
subsystem_name = current_file_path.split(os.path.sep)[-3]
import_model = f"from {subsystem_name}.es_model import *"
import_config = f"from {subsystem_name} import analytics_es_config as config"
exec(import_model)
exec(import_config)





# router = APIRouter(tags=['ES Time Series Forecasting'])
# Define an API endpoint to store the uploaded CSV file as a pickle file
# @router.post('/Storing_csv_pickle',summary='csv to pickle file')
def es_storing_csv_pickle(#Upload_file: UploadFile = File('...'),
                       subsystem_name_for_pickle_file: str = Query(..., description='Please provide the name of the subsystem')):
        
    """
    This api stores the uploaded csv file as pickle file.
    - **subsystem_name_for_pickle_file** mandatory query parameter
    """

    # Define the path to temporarily store the uploaded CSV file
    #path=f"/opt/siap/analytics/files/{Upload_file.filename}"
    # Save the uploaded CSV file to the specified path
    #with open(path,'w+b') as buffer:
       # shutil.copyfileobj(Upload_file.file,buffer)
    logger=setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])
    # setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])
    # logger = get_logger("es_log_file")
    # Logging the venv path for verification
    logger.info("Venv Path(Storing csv as pickle file): "+os.popen("which python3").read())
    try:
        # Read the CSV file into a pandas DataFrame
        zonewise_df = pd.read_csv(config.CSV_FILE_PATH['upload_file_path']+config.DATA_FILE_NAMES['processed_data_csv_file_name'], index_col='DateTime',parse_dates=True)

        # Preparing time series analysis data
        class_for_data_preparation = ES_TS_Data_Transformation(zonewise_df) 
        cleaned_data = class_for_data_preparation.data_tranformation() 

        # Save the Dataframe to a pickle file
        save_pickle_file(cleaned_data,config.PICKLE_FILES_DIRECTORY['pickle_files_path'],f'csv_file_{subsystem_name_for_pickle_file}.pkl')


        logger.info('The csv file is saved as a pickle file')
        # Return a success message to the user
        return {'message': 'File is saved as a pickle file successfully'}

    except Exception as e:
        logging.exception('Exception occurred during storing CSV as a pickle file')
        # If an exception occurs during the process, raise an HTTPException with a 500 status code
        raise HTTPException(status_code=500, detail="Exception occurred during storing CSV as a pickle file")

