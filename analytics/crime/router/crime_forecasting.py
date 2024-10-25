from fastapi import APIRouter, HTTPException, Query,Depends
from crime.crime_forecasting_model import *
from utils.file_operations import *
from crime import crime_config as config


# router = APIRouter(tags=['ES Time Series Forecasting'])
# @router.get('/Forecasting', summary='Forecasts the AQI values',description='Time series forecasting of Aqi values weekly',response_description='Dictionary of actual,predicted and validation results')
def forecasting_ward_wise(test_size: int = Query(config.DEFAULT_VALUES['DEFAULT_TEST_SIZE'], description='Please provide the size of the test data'),
                validation_size: int = Query(config.DEFAULT_VALUES['DEFAULT_VALIDATION_SIZE'], description='Please provide the size of the validation data'),
                name_for_pickle_file: str = Query(..., description='Please provide the name of the pickle file')):
    """
     Time series forecasting of crime_counts weekly
    - **name_for_pickle_file** mandatory query parameter
    - **test_size** default query parameter
    - **validation_size** default query parameter
    """
    logger=setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])

    # Initialize an empty dictionary to store predicted results
    predicted_results = {}

    try:
        crime_data = pd.read_csv(config.CLEANED_DATA_PATH['cleaned_file_path']+config.FILE_NAME['processed_data_csv_file_name1'], index_col='Event_Date', parse_dates=True)
        crime_data = crime_data[~crime_data["WARD"].isin(['W_0'])]
        # mapping_dict = { 1.0: 'W_1', 2.0: 'W_2',3.0:'W_3',4.0:"W_4",5.0:"W_5",6.0:"W_6"}
        # crime_data['WARD'] = crime_data['WARD'].map(mapping_dict)

        class_for_data_preparation = CRIME_TS_Data_Transformation(crime_data)
        cleaned_data = class_for_data_preparation.data_tranformation(['WARD'],'Event_Date','W',{'Disposition':'count'},{'Disposition':'Crime_Count'})
        
        ward_column='WARD'
         # Get the unique list of zones from the loaded DataFrame
        ward_list = list(cleaned_data[ward_column].unique())
        for ward in ward_list:
            # Create an instance of the Time_Series_Forecasting class for the current zone
            class_for_model_fitting = CRIME_Time_Series_Forecasting(cleaned_data,ward_column,ward) 
            crime_dataframe=class_for_model_fitting.column_type_dataframe()
            
            # Opening pickle files  
            model_results=load_pickle_file(config.PICKLE_FILES_DIRECTORY['pickle_files_path']+f'{name_for_pickle_file}_modelresults_{ward}.pkl') 
            fitted_model= load_pickle_file(config.PICKLE_FILES_DIRECTORY['pickle_files_path']+f'{name_for_pickle_file}_fitresults_{ward}.pkl') 
            
            # Update the model results based on user inputs
            model_results['X_test'] = str(test_size)+'weeks'
            model_results['X_validation'] = str(validation_size)+'weeks'
            model_results['X_train'] = str(len(crime_dataframe)-test_size-validation_size)+'weeks'

            #  Forecasting values for each zone
            crimewise_predictions = fitted_model.predict(len(cleaned_data[cleaned_data[ward_column]==ward]), len(cleaned_data[cleaned_data[ward_column]==ward])+(test_size-1), typ='levels').round(0)

            # Creating a DataFrame with actual, predicted, and validation values  
            dataframe_with_actual_predicted_and_validation = class_for_model_fitting.dataframe_creation('Crime_Count', crimewise_predictions, test_size, validation_size)
            dataframe_with_actual_predicted_and_validation = dataframe_with_actual_predicted_and_validation.fillna('')
            dataframe_with_actual_predicted_and_validation['Date'] = dataframe_with_actual_predicted_and_validation['Date'].astype('str')

            # Convert DataFrame to a list of dictionaries for each record
            final_dataframe_to_dictionary = dataframe_with_actual_predicted_and_validation.to_dict('records')

            # Store the results in the predicted_results dictionary using keys specific to each zone 
            predicted_results[f'{name_for_pickle_file}_model_result_{ward}'] = model_results
            predicted_results[f'{name_for_pickle_file}_df_{ward}'] = final_dataframe_to_dictionary
        
        logger.info("Forecasted data was saved successfully")
        return predicted_results

    except FileNotFoundError:
        logging.exception('File not found:%s',str(e))
    # Raise HTTPException with status code 404 (Not Found) and detail message
        raise HTTPException(status_code=404, detail="Pickle file not found")

    except Exception as e:
        logging.exception('Exception occurred during forecasting:%s',str(e))
        # If an exception occurs during forecasting, raise an HTTPException with a 500 status code
        raise HTTPException(status_code=500, detail="Exception occurred during forecasting")




def forecasting_crime_type_wise(test_size: int = Query(config.DEFAULT_VALUES['DEFAULT_TEST_SIZE'], description='Please provide the size of the test data'),
                validation_size: int = Query(config.DEFAULT_VALUES['DEFAULT_VALIDATION_SIZE'], description='Please provide the size of the validation data'),
                name_for_pickle_file: str = Query(..., description='Please provide the name of the pickle file')):
    """
     Time series forecasting of crime_counts weekly
    - **name_for_pickle_file** mandatory query parameter
    - **test_size** default query parameter
    - **validation_size** default query parameter
    """
    logger=setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])

    # Initialize an empty dictionary to store predicted results
    predicted_results = {}

    try:
        crime_data = pd.read_csv(config.CLEANED_DATA_PATH['cleaned_file_path']+config.FILE_NAME['processed_data_csv_file_name1'], index_col='Event_Date', parse_dates=True)
        #Replacing the crime type names because it seems to have an issue due to the forward slash ("/") which the operating system interprets as a directory separator. This can cause confusion and lead to FileNotFoundError.
        crime_data["Type_Description"] = crime_data["Type_Description"].replace({"Assault/Battery": "Assault Battery", "Fight/disturbance": "Fight disturbance"})
        #Considering only the top 10 crime categories
        crime_data = crime_data[crime_data["Type_Description"].isin(["Fight disturbance", "Burglary", "Family Disturbance","Other","Assault Battery","Accident","Malicious destruction of property","Suspicious","'Recovered Stolen Motor Vehicle","assist citizen","small LARCENY"])]
        #Removing the ward 0 because only wards 1 to 6 is present and ward 0 can mislead the data
        crime_data = crime_data[~crime_data["WARD"].isin(['W_0'])]

        class_for_data_preparation = CRIME_TS_Data_Transformation(crime_data)
        cleaned_data = class_for_data_preparation.data_tranformation(['Type_Description'],'Event_Date','W',{'Disposition':'count'},{'Disposition':'Crime_Count'})
       
         # Get the unique list of zones from the loaded DataFrame
        crime_type_column = 'Type_Description'
        crime_type_list = list(cleaned_data[crime_type_column].unique())

        for crime in crime_type_list:
            # Create an instance of the Time_Series_Forecasting class for the current zone
            class_for_model_fitting = CRIME_Time_Series_Forecasting(cleaned_data,crime_type_column,crime) 
            crime_dataframe=class_for_model_fitting.column_type_dataframe()
            
            # Opening pickle files  
            model_results=load_pickle_file(config.PICKLE_FILES_DIRECTORY['pickle_files_path']+f'{name_for_pickle_file}_modelresults_{crime}.pkl') 
            fitted_model= load_pickle_file(config.PICKLE_FILES_DIRECTORY['pickle_files_path']+f'{name_for_pickle_file}_fitresults_{crime}.pkl') 
            
            # Update the model results based on user inputs
            model_results['X_test'] = str(test_size)+'weeks'
            model_results['X_validation'] = str(validation_size)+'weeks'
            model_results['X_train'] = str(len(crime_dataframe)-test_size-validation_size)+'weeks'

            #  Forecasting values for each zone
            crimewise_predictions = fitted_model.predict(len(cleaned_data[cleaned_data[crime_type_column]==crime]), len(cleaned_data[cleaned_data[crime_type_column]==crime])+(test_size-1), typ='levels').round(0)

            # Creating a DataFrame with actual, predicted, and validation values  
            dataframe_with_actual_predicted_and_validation = class_for_model_fitting.dataframe_creation('Crime_Count', crimewise_predictions, test_size, validation_size)
            dataframe_with_actual_predicted_and_validation = dataframe_with_actual_predicted_and_validation.fillna('')
            dataframe_with_actual_predicted_and_validation['Date'] = dataframe_with_actual_predicted_and_validation['Date'].astype('str')

            # Convert DataFrame to a list of dictionaries for each record
            final_dataframe_to_dictionary = dataframe_with_actual_predicted_and_validation.to_dict('records')

            # Store the results in the predicted_results dictionary using keys specific to each zone 
            predicted_results[f'{name_for_pickle_file}_model_result_{crime}'] = model_results
            predicted_results[f'{name_for_pickle_file}_df_{crime}'] = final_dataframe_to_dictionary
        
        logger.info("Forecasted data was saved successfully")
        return predicted_results

    except FileNotFoundError:
        logging.exception('File not found:%s',str(e))
    # Raise HTTPException with status code 404 (Not Found) and detail message
        raise HTTPException(status_code=404, detail="Pickle file not found")

    except Exception as e:
        logging.exception('Exception occurred during forecasting:%s',str(e))
        # If an exception occurs during forecasting, raise an HTTPException with a 500 status code
        raise HTTPException(status_code=500, detail="Exception occurred during forecasting")




def forecasting_crime_type_and_wardwise(test_size: int = Query(config.DEFAULT_VALUES['DEFAULT_TEST_SIZE'], description='Please provide the size of the test data'),
                validation_size: int = Query(config.DEFAULT_VALUES['DEFAULT_VALIDATION_SIZE'], description='Please provide the size of the validation data'),
                name_for_pickle_file: str = Query(..., description='Please provide the name of the pickle file')):
    """
     Time series forecasting of crime_counts weekly
    - **name_for_pickle_file** mandatory query parameter
    - **test_size** default query parameter
    - **validation_size** default query parameter
    """
    logger=setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])

    # Initialize an empty dictionary to store predicted results
    predicted_results = {}

    try:
        crime_data = pd.read_csv(config.CLEANED_DATA_PATH['cleaned_file_path']+config.FILE_NAME['processed_data_csv_file_name1'], index_col='Event_Date', parse_dates=True)
        #Replacing the crime type names because it seems to have an issue due to the forward slash ("/") which the operating system interprets as a directory separator. This can cause confusion and lead to FileNotFoundError.
        crime_data["Type_Description"] = crime_data["Type_Description"].replace({"Assault/Battery": "Assault Battery", "Fight/disturbance": "Fight disturbance"})
        #Considering only the top 10 crime categories
        crime_data = crime_data[crime_data["Type_Description"].isin(["Fight disturbance", "Burglary", "Family Disturbance","Other","Assault Battery","Accident","Malicious destruction of property","Suspicious","'Recovered Stolen Motor Vehicle","assist citizen","small LARCENY"])]
        #Removing the ward 0 because only wards 1 to 6 is present and ward 0 can mislead the data
        crime_data = crime_data[~crime_data["WARD"].isin(['W_0'])]

        class_for_data_preparation = CRIME_TS_Data_Transformation(crime_data)
        cleaned_data = class_for_data_preparation.data_tranformation(['Type_Description','WARD'],'Event_Date','W',{'Disposition':'count'},{'Disposition':'Crime_Count'})
       
         # Get the unique list of zones from the loaded DataFrame
        crime_type_column = 'Type_Description'
        ward_name_column='WARD'
        crime_type_list = list(cleaned_data[crime_type_column].unique())
        ward_name_list = list(cleaned_data[ward_name_column].unique())
        for crime in crime_type_list:
            for ward in ward_name_list:
            # Create an instance of the Time_Series_Forecasting class for the current zone
                class_for_model_fitting = CRIME_Time_Series_Forecasting(cleaned_data,crime_type_column,crime) 
                crime_dataframe=class_for_model_fitting.column_type_dataframe_for_2_columns(crime_type_column,crime,ward_name_column,ward)
                
                # Opening pickle files  
                model_results=load_pickle_file(config.PICKLE_FILES_DIRECTORY['pickle_files_path']+f'{name_for_pickle_file}_modelresults_{crime}{ward}.pkl') 
                fitted_model= load_pickle_file(config.PICKLE_FILES_DIRECTORY['pickle_files_path']+f'{name_for_pickle_file}_fitresults_{crime}{ward}.pkl') 
                
                # Update the model results based on user inputs
                model_results['X_test'] = str(test_size)+'weeks'
                model_results['X_validation'] = str(validation_size)+'weeks'
                model_results['X_train'] = str(len(crime_dataframe)-test_size-validation_size)+'weeks'

                #  Forecasting values for each zone
                start = len(cleaned_data[(cleaned_data[crime_type_column] == crime) & (cleaned_data[ward_name_column] == ward)])
                end = start + (test_size - 1)
                crimewise_predictions = fitted_model.predict(start=start, end=end, typ='levels').round(0)

                # crimewise_predictions = fitted_model.predict((len(cleaned_data[cleaned_data[crime_type_column]==crime])) & (len(cleaned_data[cleaned_data[ward_name_column]==ward])), (len(cleaned_data[cleaned_data[crime_type_column]==crime])) & (len(cleaned_data[cleaned_data[ward_name_column]==ward]))+(test_size-1), typ='levels').round(0)

                # Creating a DataFrame with actual, predicted, and validation values  
                dataframe_with_actual_predicted_and_validation = class_for_model_fitting.dataframe_creation('Crime_Count', crimewise_predictions, test_size, validation_size)
                dataframe_with_actual_predicted_and_validation = dataframe_with_actual_predicted_and_validation.fillna('')
                dataframe_with_actual_predicted_and_validation['Date'] = dataframe_with_actual_predicted_and_validation['Date'].astype('str')

                # Convert DataFrame to a list of dictionaries for each record
                final_dataframe_to_dictionary = dataframe_with_actual_predicted_and_validation.to_dict('records')

                # Store the results in the predicted_results dictionary using keys specific to each zone 
                predicted_results[f'{name_for_pickle_file}_model_result_{crime}{ward}'] = model_results
                predicted_results[f'{name_for_pickle_file}_df_{crime}{ward}'] = final_dataframe_to_dictionary
            
        logger.info("Forecasted data was saved successfully")
        return predicted_results

    except FileNotFoundError as e:
        logging.exception('File not found:%s',str(e))
    # Raise HTTPException with status code 404 (Not Found) and detail message
        raise HTTPException(status_code=404, detail="Pickle file not found")

    except Exception as e:
        logging.exception('Exception occurred during forecasting:%s',str(e))
        # If an exception occurs during forecasting, raise an HTTPException with a 500 status code
        raise HTTPException(status_code=500, detail="Exception occurred during forecasting")




