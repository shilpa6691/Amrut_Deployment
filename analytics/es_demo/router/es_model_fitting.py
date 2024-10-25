from fastapi import APIRouter, File, UploadFile,Query, HTTPException,Depends
# from es.es_model import *
from utils.file_operations import *
import pandas as pd
import os
# from es import analytics_es_config as config
current_file_path = os.path.abspath(__file__)
subsystem_name = current_file_path.split(os.path.sep)[-3]
# subsystem_name = sys.argv[4]
import_model = f"from {subsystem_name}.es_model import *"
import_config = f"from {subsystem_name} import analytics_es_config as config"
exec(import_model)
exec(import_config)



# router = APIRouter(tags=['ES Time Series Forecasting'])
# Define an API endpoint to train the model and save the results as pickle files
# @router.post('/Model_fitting',summary='Model results and fitted model to pickle files')
def model_fitting(subsystem_name_for_pickle_file: str= Query(..., description="Please provide the subsystem name for the pickle file"),
                  #Upload_file: UploadFile = File("..."),
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
    # logger = get_logger("es_log_file")


    # Logging the venv path for verification
    logger.info("Venv Path(Model Fitting): "+ os.popen("which python3").read())

    try:
        # Read the CSV file uploaded by the user into a pandas DataFrame.
        es_data = pd.read_csv(config.CSV_FILE_PATH['upload_file_path']+config.DATA_FILE_NAMES['processed_data_csv_file_name'], index_col='DateTime', parse_dates=True)
        # logger.info('shape of dataframe',es_data.shape)
        # Create an instance of the TS_Data_Transformation class
        class_for_data_preparation = ES_TS_Data_Transformation(es_data)
        cleaned_data = class_for_data_preparation.data_tranformation()
        logger.info('shape of cleaned data',cleaned_data.shape)
        logger.info("TS data cleaning completed.")
        # logger.info(cleaned_data.head())

        # Get the unique list of zones from the DataFrame.
        if 'Zone' in cleaned_data:
            region_column = 'Zone'
        else:
            region_column = 'Location'
        full_region_list = list(cleaned_data[region_column].unique())
        for region in full_region_list:
            # Create an instance of the Time_Series_Forecasting class for the current zone.
            class_for_model_fitting =ES_Time_Series_Forecasting(cleaned_data, region)
            # Get the DataFrame for the current zone.  
            class_for_model_fitting.es_regionwise_dataframe(region_column)
            # Determine the optimal ARIMA order for the 'Value' column in the DataFrame.
            class_for_model_fitting.determine_ARIMA_order('Value')
            
            # Get only the model results for the 'Value' column.
            model_results=class_for_model_fitting.get_es_model_and_validation_results('Value',test_size,validation_size)[0]
            # Fit the ARIMA model for the 'Value' column.
            fitted_model=class_for_model_fitting.fit_model('Value')

            logger.info(f'The model is fitted for region {region}.')
            # Save the model results as a pickle file.
            save_pickle_file(model_results, config.PICKLE_FILES_DIRECTORY['pickle_files_path'],f'{subsystem_name_for_pickle_file}_modelresults_{region}.pkl')
            logger.info("pickle file for modelresults zone %s created successfully",region)
            
            # Save the fitted model as a pickle file.
            save_pickle_file(fitted_model,config.PICKLE_FILES_DIRECTORY['pickle_files_path'],f'{subsystem_name_for_pickle_file}_fitresults_{region}.pkl')
            logger.info("pickle file for fitresults zone %s created successfully",region)
        # else:
        #     full_region_list = list(cleaned_data['Location'].unique())

        #     for loc in full_region_list:
        #         # Create an instance of the Time_Series_Forecasting class for the current zone.
        #         class_for_model_fitting =ES_Time_Series_Forecasting(cleaned_data, 'Location', loc)
        #         # Get the DataFrame for the current zone.  
        #         class_for_model_fitting.es_regionwise_dataframe()
        #         logger.info(class_for_model_fitting.es_regionwise_dataframe())
        #         # Determine the optimal ARIMA order for the 'Value' column in the DataFrame.
        #         class_for_model_fitting.determine_ARIMA_order('Value')
        #         logger.info(class_for_model_fitting.determine_ARIMA_order('Value'))
                
        #         # Get only the model results for the 'Value' column.
        #         model_results=class_for_model_fitting.get_es_model_and_validation_results('Value',test_size,validation_size)[0]
        #         logger.info('model results', model_results)
        #         # Fit the ARIMA model for the 'Value' column.
        #         fitted_model=class_for_model_fitting.fit_model('Value')

        #         logger.info(f'The model is fitted for location {loc}.')

        #         # Save the model results as a pickle file.
        #         save_pickle_file(model_results, config.PICKLE_FILES_DIRECTORY['pickle_files_path'],f'{subsystem_name_for_pickle_file}_modelresults_location_{loc}.pkl')
        #         logger.info("pickle file for modelresults zone %s created successfully",loc)
                
        #         # Save the fitted model as a pickle file.
        #         save_pickle_file(fitted_model,config.PICKLE_FILES_DIRECTORY['pickle_files_path'],f'{subsystem_name_for_pickle_file}_fitresults_location_{loc}.pkl')
        #         logger.info("pickle file for fitresults zone %s created successfully",loc)
            
        logger.info("Model fitting of all zones completed successfully")
        # Return a success message to the user.
        return {'message': 'ES Model fitting completed successfully'}

    except Exception as e:
        logging.exception('Exception occurred during model fitting')
        # If an exception occurs during the model fitting process, raise an HTTPException with a 500 status code.
        raise HTTPException(status_code=500, detail="Exception occurred during model fitting")





