
from fastapi import APIRouter, HTTPException, Query,Depends
# from es.es_model import *
from utils.file_operations import *
# from es import analytics_es_config as config
import json
import os

current_file_path = os.path.abspath(__file__)
subsystem_name = current_file_path.split(os.path.sep)[-3]
import_model = f"from {subsystem_name}.es_model import *"
import_config = f"from {subsystem_name} import analytics_es_config as config"
exec(import_model)
exec(import_config)


# router = APIRouter(tags=['ES Time Series Forecasting'])
# @router.get('/Forecasting', summary='Forecasts the AQI values',description='Time series forecasting of Aqi values weekly',response_description='Dictionary of actual,predicted and validation results')
def forecasting(test_size: int = Query(config.DEFAULT_VALUES['DEFAULT_TEST_SIZE'], description='Please provide the size of the test data'),
                validation_size: int = Query(config.DEFAULT_VALUES['DEFAULT_VALIDATION_SIZE'], description='Please provide the size of the validation data'),
                subsystem_name_for_pickle_file: str = Query(..., description='Please provide the name of the subsystem')):
    """
     Time series forecasting of Aqi values weekly
    - **subsystem_name_for_pickle_file** mandatory query parameter
    - **test_size** default query parameter
    - **validation_size** default query parameter
    """
    logger=setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])
    # setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])
    # logger = get_logger("es_log_file")

    # Initialize an empty dictionary to store predicted results
    predicted_results = {}

    try:
        # Load the CSV data from the pickle file
        regionwise_data = load_pickle_file(config.PICKLE_FILES_DIRECTORY['pickle_files_path']+f'csv_file_{subsystem_name_for_pickle_file}.pkl')
        
         # Get the unique list of zones from the loaded DataFrame
        if 'Zone' in regionwise_data:
            region_column = 'Zone'
        else:
            region_column = 'Location'
        full_region_list = list(regionwise_data[region_column].unique())

        for region in full_region_list:
            # Create an instance of the Time_Series_Forecasting class for the current zone
            class_for_model_fitting = ES_Time_Series_Forecasting(regionwise_data, region) 
            region_dataframe=class_for_model_fitting.es_regionwise_dataframe(region_column)

            # Opening pickle files  
            model_results=load_pickle_file(config.PICKLE_FILES_DIRECTORY['pickle_files_path']+f'{subsystem_name_for_pickle_file}_modelresults_{region}.pkl') 
            fitted_model= load_pickle_file(config.PICKLE_FILES_DIRECTORY['pickle_files_path']+f'{subsystem_name_for_pickle_file}_fitresults_{region}.pkl') 
            
            # Update the model results based on user inputs
            model_results['X_test'] = str(test_size)+'weeks'
            model_results['X_validation'] = str(validation_size)+'weeks'
            model_results['X_train'] = str(len(region_dataframe)-test_size-validation_size)+'weeks'

            if not os.path.exists(config.JSON_FILE_PATH['forecasting_file_path']):
                os.makedirs(config.JSON_FILE_PATH['forecasting_file_path'])

            with open(f"{config.JSON_FILE_PATH['forecasting_file_path']}es_model_results_{region}.json", 'w') as json_file:
                json.dump(model_results, json_file)
            
            #  Forecasting values for each zone
            regionwise_predictions = fitted_model.predict(len(regionwise_data[regionwise_data[region_column]==region]), len(regionwise_data[regionwise_data[region_column]==region])+(test_size-1), typ='levels').round(2)

            # Creating a DataFrame with actual, predicted, and validation values  
            dataframe_with_actual_predicted_and_validation = class_for_model_fitting.es_dataframe_creation('Value', regionwise_predictions, test_size, validation_size)
            dataframe_with_actual_predicted_and_validation = dataframe_with_actual_predicted_and_validation.fillna('')
            dataframe_with_actual_predicted_and_validation['Date'] = dataframe_with_actual_predicted_and_validation['Date'].astype('str')

            # dataframe_with_actual_predicted_and_validation.to_json(config.JSON_FILE_PATH['upload_file_path']+'es_forecasting.json',orient='records')
            dataframe_with_actual_predicted_and_validation.to_json(f"{config.JSON_FILE_PATH['forecasting_file_path']}es_forecasting_{region}.json", orient='records')

            # Convert DataFrame to a list of dictionaries for each record
            final_dataframe_to_dictionary = dataframe_with_actual_predicted_and_validation.to_dict('records')

            # Store the results in the predicted_results dictionary using keys specific to each zone 
            predicted_results[f'{subsystem_name_for_pickle_file}_model_result_{region}'] = model_results
            predicted_results[f'{subsystem_name_for_pickle_file}_df_{region}'] = final_dataframe_to_dictionary
        # else:
        #     full_region_list = list(regionwise_data['Location'].unique())

        #     for loc in full_region_list:
        #         # Create an instance of the Time_Series_Forecasting class for the current location
        #         class_for_model_fitting = ES_Time_Series_Forecasting(regionwise_data, 'Location', loc) 
        #         zone_dataframe=class_for_model_fitting.es_regionwise_dataframe()

        #         # Opening pickle files  
        #         model_results=load_pickle_file(config.PICKLE_FILES_DIRECTORY['pickle_files_path']+f'{subsystem_name_for_pickle_file}_modelresults_location_{loc}.pkl') 
        #         fitted_model= load_pickle_file(config.PICKLE_FILES_DIRECTORY['pickle_files_path']+f'{subsystem_name_for_pickle_file}_fitresults_location_{loc}.pkl') 
                
        #         # Update the model results based on user inputs
        #         model_results['X_test'] = str(test_size)+'weeks'
        #         model_results['X_validation'] = str(validation_size)+'weeks'
        #         model_results['X_train'] = str(len(zone_dataframe)-test_size-validation_size)+'weeks'

        #         #  Forecasting values for each zone
        #         regionwise_predictions = fitted_model.predict(len(regionwise_data[regionwise_data.Location==loc]), len(regionwise_data[regionwise_data.Location==loc])+(test_size-1), typ='levels').round(2)

        #         # Creating a DataFrame with actual, predicted, and validation values  
        #         dataframe_with_actual_predicted_and_validation = class_for_model_fitting.es_dataframe_creation('Value', regionwise_predictions, test_size, validation_size)
        #         dataframe_with_actual_predicted_and_validation = dataframe_with_actual_predicted_and_validation.fillna('')
        #         dataframe_with_actual_predicted_and_validation['Date'] = dataframe_with_actual_predicted_and_validation['Date'].astype('str')

        #         # Convert DataFrame to a list of dictionaries for each record
        #         final_dataframe_to_dictionary = dataframe_with_actual_predicted_and_validation.to_dict('records')

        #         # Store the results in the predicted_results dictionary using keys specific to each zone 
        #         predicted_results[f'{subsystem_name_for_pickle_file}_model_result_location_{loc}'] = model_results
        #         predicted_results[f'{subsystem_name_for_pickle_file}_df_location_{loc}'] = final_dataframe_to_dictionary

        logger.info("Forecasted data was saved successfully")
        # predicted_results.to_json('/opt/siap/analytics/es/logs/forecasted_values.txt')
        return predicted_results

    except FileNotFoundError as e:
        logging.exception('File not found:%s',str(e))
    # Raise HTTPException with status code 404 (Not Found) and detail message
        raise HTTPException(status_code=404, detail="Pickle file not found")

    except Exception as e:
        logging.exception('Exception occurred during forecasting')
        # If an exception occurs during forecasting, raise an HTTPException with a 500 status code
        raise HTTPException(status_code=500, detail="Exception occurred during forecasting")

