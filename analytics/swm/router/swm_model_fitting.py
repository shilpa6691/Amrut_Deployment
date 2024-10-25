from fastapi import APIRouter,Query, HTTPException
# from swm.swm_model import *
from utils.file_operations import *
import pandas as pd
# from swm import analytics_swm_config as config
import os

current_file_path = os.path.abspath(__file__)
subsystem_name = current_file_path.split(os.path.sep)[-3]
# subsystem_name = sys.argv[4]
import_model = f"from {subsystem_name}.{subsystem_name}_model import *"
import_config = f"from {subsystem_name} import analytics_{subsystem_name}_config as config"
exec(import_model)
exec(import_config)

# logger=setup_logger(config.LOG_FILE_PATH['analytics_logs_path'])

# router = APIRouter(prefix='/swm_time_series_forecasting',tags=['SWM Time Series Forecasting'])


# Define an API endpoint to train the model and save the results as pickle files
# @router.post('/swm_model_fitting',summary='Model results and fitted model to pickle files')
def model_fitting(subsystem_name_for_pickle_file: str= Query(..., description="Please provide the subsystem name for the pickle file"),
                  test_size: int = Query(config.DEFAULT_VALUES['DEFAULT_TEST_SIZE'], description='Please provide the size of the test data'),
                  validation_size: int = Query(config.DEFAULT_VALUES['DEFAULT_VALIDATION_SIZE'], description='Please provide the size of the validation data')):

    """
     This api used to train the model once and converts the trained model results to pickle files based on different zones
    - **subsystem_name_for_pickle_file** mandatory query parameter
    - **test_size** default query parameter
    - **validation_size** default query parameter
    """
    logger=setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])
    # setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])
    # logger = get_logger("swm_log_file")

    try:
        # Read the CSV file uploaded by the user into a pandas DataFrame.
        swm_complaints = pd.read_csv(config.CSV_FILE_PATH['upload_file_path']+config.DATA_FILE_NAMES['processed_data_csv_file_name'],index_col='DateTime', parse_dates=True)

        # Create an instance of the TS_Data_Transformation class
        class_for_data_preparation = SWM_TS_Data_Transformation(swm_complaints)
        cleaned_data = class_for_data_preparation.data_tranformation()
        logger.info("TS data cleaning completed.")

        # Get the unique list of zones from the DataFrame.
        full_zone_list = list(cleaned_data['Zone'].unique())

        for zone in full_zone_list:
            # Create an instance of the Time_Series_Forecasting class for the current zone.
            class_for_model_fitting = SWM_Time_Series_Forecasting(cleaned_data, 'Zone', zone)    
            
            # Get the DataFrame for the current zone.  
            class_for_model_fitting.swm_zonewise_dataframe()
            # Determine the optimal ARIMA order for the 'Value' column in the DataFrame.
            class_for_model_fitting.determine_ARIMA_order('Value')
            # Get only the model results for the 'Value' column.
            model_results=class_for_model_fitting.get_swm_model_and_validation_results('Value',test_size,validation_size)[0]
            # Fit the ARIMA model for the 'Value' column.
            fitted_model=class_for_model_fitting.fit_model('Value')

            logger.info(f'The model is fitted for zone{zone}')

            # Save the model results as a pickle file.
            save_pickle_file(model_results, config.PICKLE_FILES_DIRECTORY['pickle_files_path'],f'{subsystem_name_for_pickle_file}_modelresults_zone_{zone}.pkl')
            logger.info("pickle file for modelresults zone %s created successfully",zone)
            
            # Save the fitted model as a pickle file.
            save_pickle_file(fitted_model, config.PICKLE_FILES_DIRECTORY['pickle_files_path'],f'{subsystem_name_for_pickle_file}_fitresults_zone_{zone}.pkl')
            logger.info("pickle file for fitresults zone %s created successfully",zone)
            
        logger.info("Model fitting of all zones completed successfully")
        # Return a success message to the user.
        return {'message': 'SWM Model fitting completed successfully'}

    
    except Exception as e:
        logging.exception('Exception occurred during model fitting')
        # If an exception occurs during the model fitting process, raise an HTTPException with a 500 status code.
        raise HTTPException(status_code=500, detail="Exception occurred during model fitting")



