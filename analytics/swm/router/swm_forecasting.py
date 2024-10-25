from fastapi import APIRouter, HTTPException, Query
# from swm.swm_model import *
from utils.file_operations import *
from enum import Enum
from swm import analytics_swm_config as config
import os

current_file_path = os.path.abspath(__file__)
subsystem_name = current_file_path.split(os.path.sep)[-3]
import_model = f"from {subsystem_name}.{subsystem_name}_model import *"
import_config = f"from {subsystem_name} import analytics_{subsystem_name}_config as config"
exec(import_model)
exec(import_config)

# router = APIRouter(prefix='/swm_time_series_forecasting',tags=['SWM Time Series Forecasting'])


# @router.get('/swm_forecasting', summary='Forecasts the total complaints',description='Time series forecasting of complaints values weekly')
def forecasting(test_size: int = Query(config.DEFAULT_VALUES['DEFAULT_TEST_SIZE'], description='Please provide the size of the test data'),
                validation_size: int = Query(config.DEFAULT_VALUES['DEFAULT_VALIDATION_SIZE'], description='Please provide the size of the validation data'),
                subsystem_name_for_pickle_file: str = Query(..., description='Please provide the name of the subsystem')):
    """
     Time series forecasting of swm complaints values weekly
    - **subsystem_name_for_pickle_file** mandatory query parameter
    - **test_size** default query parameter
    - **validation_size** default query parameter
    """
    logger = setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])
    
    # Initialize an empty dictionary to store predicted results
    predicted_results = {}

    try:
        # Load the CSV data from the pickle file
        zonewise_data = load_pickle_file(config.PICKLE_FILES_DIRECTORY['pickle_files_path']+f'csv_file_{subsystem_name_for_pickle_file}.pkl')
         # Get the unique list of zones from the loaded DataFrame
        full_zone_list = list(zonewise_data['Zone'].unique())

        
        for zone in full_zone_list:
        # Create an instance of the Time_Series_Forecasting class for the current zone
            class_for_model_fitting = SWM_Time_Series_Forecasting(zonewise_data, 'Zone', zone) 
            zone_dataframe=class_for_model_fitting.swm_zonewise_dataframe()
         # Check if all values in the 'Value' column of the zone's DataFrame are equal to 0.   
            if len(zone_dataframe[zone_dataframe['Value']!=0])==0:
                # If all values are 0, load the previously saved model results from a pickle file.
                model_results=load_pickle_file(config.PICKLE_FILES_DIRECTORY['pickle_files_path']+f'{subsystem_name_for_pickle_file}_modelresults_zone_{zone}.pkl') 
                # Create an SWM DataFrame using the 'Value' column and fill NaN values with empty strings.
                dataframe_actual = class_for_model_fitting.swm_dataframe_creation_with_zero_values('Value')
                dataframe_actual = dataframe_actual.fillna('')
                # Convert the DataFrame to a list of dictionaries.
                final_dataframe_to_dictionary = dataframe_actual.to_dict('records')
    
                # Add the loaded model results and DataFrame as entries in a dictionary.
                predicted_results[f'{subsystem_name_for_pickle_file}_model_result_zone_{zone}'] = model_results
                predicted_results[f'{subsystem_name_for_pickle_file}_df_zone_{zone}'] = final_dataframe_to_dictionary
                
            else:
               # Opening pickle files  
                model_results=load_pickle_file(config.PICKLE_FILES_DIRECTORY['pickle_files_path']+f'{subsystem_name_for_pickle_file}_modelresults_zone_{zone}.pkl') 
                fitted_model= load_pickle_file(config.PICKLE_FILES_DIRECTORY['pickle_files_path']+f'{subsystem_name_for_pickle_file}_fitresults_zone_{zone}.pkl') 
                # Update the model results based on user inputs
                model_results['X_test'] = str(test_size)+'weeks'
                model_results['X_validation'] = str(validation_size)+'weeks'
                model_results['X_train'] = str(len(zone_dataframe)-test_size-validation_size)+'weeks'

                    #  Forecasting values for each zone
                zonewise_predictions = fitted_model.predict(len(zonewise_data[zonewise_data.Zone==zone]), len(zonewise_data[zonewise_data.Zone==zone])+(test_size-1), typ='levels').round(0)

                # Creating a DataFrame with actual, predicted, and validation values  
                dataframe_with_actual_predicted_and_validation = class_for_model_fitting.swm_dataframe_creation_without_zero_values('Value', zonewise_predictions, test_size, validation_size)
                dataframe_with_actual_predicted_and_validation = dataframe_with_actual_predicted_and_validation.fillna('')

                # Convert DataFrame to a list of dictionaries for each record
                final_dataframe_to_dictionary = dataframe_with_actual_predicted_and_validation.to_dict('records')

                # Store the results in the predicted_results dictionary using keys specific to each zone 
                predicted_results[f'{subsystem_name_for_pickle_file}_model_result_zone_{zone}'] = model_results
                predicted_results[f'{subsystem_name_for_pickle_file}_df_zone_{zone}'] = final_dataframe_to_dictionary
                
        logger.info("Forecasted data was saved successfully")
        return predicted_results

    except FileNotFoundError as e:
        logging.exception('File not found:%s',str(e))
    # Raise HTTPException with status code 404 (Not Found) and detail message
        raise HTTPException(status_code=404, detail="Pickle file not found")

    except Exception as e:
        logging.exception('Exception occurred during forecasting')
        # If an exception occurs during forecasting, raise an HTTPException with a 500 status code
        raise HTTPException(status_code=500, detail="Exception occurred during forecasting")
