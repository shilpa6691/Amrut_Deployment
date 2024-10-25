from fastapi import APIRouter, File, UploadFile,Query, HTTPException,Depends
from crime.crime_forecasting_model import *
from utils.file_operations import *
import pandas as pd
import os
from crime import crime_config as config


# router = APIRouter(tags=['ES Time Series Forecasting'])
# Define an API endpoint to train the model and save the results as pickle files
# @router.post('/Model_fitting',summary='Model results and fitted model to pickle files')
def model_fitting_ward_wise(name_for_pickle_file: str= Query(..., description="Please provide the name for the pickle file"),
                #   Upload_file: UploadFile = File("..."),
                  test_size: int = Query(config.DEFAULT_VALUES['DEFAULT_TEST_SIZE'], description='Please provide the size of the test data'),
                  validation_size: int = Query(config.DEFAULT_VALUES['DEFAULT_VALIDATION_SIZE'], description='Please provide the size of the validation data')):

    """
     This api used to train the model once and converts the trained model results to pickle files based on different wards
    - **name_for_pickle_file** mandatory query parameter
    - **test_size** default query parameter
    - **validation_size** default query parameter
    """
    logger=setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])
    # Logging the venv path for verification
    logger.info("Venv Path(Model Fitting): "+ os.popen("which python3").read())

    try:
        # Read the CSV file uploaded by the user into a pandas DataFrame.
        crime_data = pd.read_csv(config.CLEANED_DATA_PATH['cleaned_file_path']+config.FILE_NAME['processed_data_csv_file_name1'], index_col='Event_Date', parse_dates=True)
        crime_data = crime_data[~crime_data["WARD"].isin(['W_0'])]
        # mapping_dict = { 1.0: 'W_1', 2.0: 'W_2',3.0:'W_3',4.0:"W_4",5.0:"W_5",6.0:"W_6"}
        # crime_data['WARD'] = crime_data['WARD'].map(mapping_dict)

        class_for_data_preparation = CRIME_TS_Data_Transformation(crime_data)
        cleaned_data = class_for_data_preparation.data_tranformation(['WARD'],'Event_Date','W',{'Disposition':'count'},{'Disposition':'Crime_Count'})

        logger.info('shape of cleaned data',cleaned_data.shape)
        logger.info("TS data cleaning completed.")

        ward_column='WARD'
        # Get the unique list of zones from the DataFrame.
        ward_list = list(cleaned_data[ward_column].unique())
        for ward in ward_list:
            # Create an instance of the Time_Series_Forecasting class for the current zone.
            class_for_model_fitting =CRIME_Time_Series_Forecasting(cleaned_data,ward_column,ward)
            # Get the DataFrame for the current zone.  
            class_for_model_fitting.column_type_dataframe()
            # Determine the optimal ARIMA order for the 'Value' column in the DataFrame.
            class_for_model_fitting.determine_ARIMA_order('Crime_Count')
            
            # Get only the model results for the 'Value' column.
            model_results=class_for_model_fitting.get_model_and_validation_results('Crime_Count',test_size,validation_size)[0]
            # Fit the ARIMA model for the 'Value' column.
            fitted_model=class_for_model_fitting.fit_model('Crime_Count')

            logger.info(f'The model is fitted for ward {ward}.')
            # Save the model results as a pickle file.
            save_pickle_file(model_results, config.PICKLE_FILES_DIRECTORY['pickle_files_path'],f'{name_for_pickle_file}_modelresults_{ward}.pkl')
            logger.info("pickle file for modelresults ward %s created successfully",ward)
            
            # Save the fitted model as a pickle file.
            save_pickle_file(fitted_model,config.PICKLE_FILES_DIRECTORY['pickle_files_path'],f'{name_for_pickle_file}_fitresults_{ward}.pkl')
            logger.info("pickle file for fitresults ward %s created successfully",ward)
        
        logger.info("Model fitting of all wards completed successfully")
        # Return a success message to the user.
        return {'message': 'Model fitting of all wards completed successfully'}

    
    except Exception as e:
        logging.exception('Exception occurred during model fitting:%s',str(e))
        # If an exception occurs during the model fitting process, raise an HTTPException with a 500 status code.
        raise HTTPException(status_code=500, detail="Exception occurred during model fitting")




def model_fitting_crime_type_wise(name_for_pickle_file: str= Query(..., description="Please provide the name for the pickle file"),
                #   Upload_file: UploadFile = File("..."),
                  test_size: int = Query(config.DEFAULT_VALUES['DEFAULT_TEST_SIZE'], description='Please provide the size of the test data'),
                  validation_size: int = Query(config.DEFAULT_VALUES['DEFAULT_VALIDATION_SIZE'], description='Please provide the size of the validation data')):

    """
     This api used to train the model once and converts the trained model results to pickle files based on different crime_types
    - **name_for_pickle_file** mandatory query parameter
    - **test_size** default query parameter
    - **validation_size** default query parameter
    """
    logger=setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])
    # Logging the venv path for verification
    logger.info("Venv Path(Model Fitting): "+ os.popen("which python3").read())

    try:
        # Read the CSV file uploaded by the user into a pandas DataFrame.
        crime_data = pd.read_csv(config.CLEANED_DATA_PATH['cleaned_file_path']+config.FILE_NAME['processed_data_csv_file_name1'], index_col='Event_Date', parse_dates=True)
        #Replacing the crime type names because it seems to have an issue due to the forward slash ("/") which the operating system interprets as a directory separator. This can cause confusion and lead to FileNotFoundError.
        crime_data["Type_Description"] = crime_data["Type_Description"].replace({"Assault/Battery": "Assault Battery", "Fight/disturbance": "Fight disturbance"})
        #Considering only the top 10 crime categories
        crime_data = crime_data[crime_data["Type_Description"].isin(["Fight disturbance", "Burglary", "Family Disturbance","Other","Assault Battery","Accident","Malicious destruction of property","Suspicious","'Recovered Stolen Motor Vehicle","assist citizen","small LARCENY"])]
        #Removing the ward 0 because only wards 1 to 6 is present and ward 0 can mislead the data
        crime_data = crime_data[~crime_data["WARD"].isin(['W_0'])]

        class_for_data_preparation = CRIME_TS_Data_Transformation(crime_data)
        cleaned_data = class_for_data_preparation.data_tranformation(['Type_Description'],'Event_Date','W',{'Disposition':'count'},{'Disposition':'Crime_Count'})
       
        logger.info('shape of cleaned data',cleaned_data.shape)
        logger.info("TS data cleaning completed.")

        crime_type_column = 'Type_Description'
        crime_type_list = list(cleaned_data[crime_type_column].unique())
        for crime in crime_type_list:
            # Create an instance of the Time_Series_Forecasting class for the current zone.
            class_for_model_fitting =CRIME_Time_Series_Forecasting(cleaned_data,crime_type_column,crime)
            # Get the DataFrame for the current zone.  
            class_for_model_fitting.column_type_dataframe()
            # Determine the optimal ARIMA order for the 'Value' column in the DataFrame.
            class_for_model_fitting.determine_ARIMA_order('Crime_Count')
            
            # Get only the model results for the 'Value' column.
            model_results=class_for_model_fitting.get_model_and_validation_results('Crime_Count',test_size,validation_size)[0]
            # Fit the ARIMA model for the 'Value' column.
            fitted_model=class_for_model_fitting.fit_model('Crime_Count')

            logger.info(f'The model is fitted for crime {crime}.')
            # Save the model results as a pickle file.
            save_pickle_file(model_results, config.PICKLE_FILES_DIRECTORY['pickle_files_path'],f'{name_for_pickle_file}_modelresults_{crime}.pkl')
            logger.info("pickle file for modelresults crime_type %s created successfully",crime)
            
            # Save the fitted model as a pickle file.
            save_pickle_file(fitted_model,config.PICKLE_FILES_DIRECTORY['pickle_files_path'],f'{name_for_pickle_file}_fitresults_{crime}.pkl')
            logger.info("pickle file for fitresults crime_type %s created successfully",crime)
        
        logger.info("Model fitting of all crime types completed successfully")
        # Return a success message to the user.
        return {'message': 'Model fitting of all crime types completed successfully'}

    
    except Exception as e:
        logging.exception('Exception occurred during model fitting:%s',str(e))
        # If an exception occurs during the model fitting process, raise an HTTPException with a 500 status code.
        raise HTTPException(status_code=500, detail="Exception occurred during model fitting")




def model_fitting_crime_type_and_wardwise(name_for_pickle_file: str= Query(..., description="Please provide the name for the pickle file"),
                #   Upload_file: UploadFile = File("..."),
                  test_size: int = Query(config.DEFAULT_VALUES['DEFAULT_TEST_SIZE'], description='Please provide the size of the test data'),
                  validation_size: int = Query(config.DEFAULT_VALUES['DEFAULT_VALIDATION_SIZE'], description='Please provide the size of the validation data')):

    """
     This api used to train the model once and converts the trained model results to pickle files based on different crime_types and wards
    - **name_for_pickle_file** mandatory query parameter
    - **test_size** default query parameter
    - **validation_size** default query parameter
    """
    logger=setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])
    # Logging the venv path for verification
    logger.info("Venv Path(Model Fitting): "+ os.popen("which python3").read())

    try:
        # Read the CSV file uploaded by the user into a pandas DataFrame.
        crime_data = pd.read_csv(config.CLEANED_DATA_PATH['cleaned_file_path']+config.FILE_NAME['processed_data_csv_file_name1'], index_col='Event_Date', parse_dates=True)
        #Replacing the crime type names because it seems to have an issue due to the forward slash ("/") which the operating system interprets as a directory separator. This can cause confusion and lead to FileNotFoundError.
        crime_data["Type_Description"] = crime_data["Type_Description"].replace({"Assault/Battery": "Assault Battery", "Fight/disturbance": "Fight disturbance"})
        # #Considering only the top 10 crime categories
        crime_data = crime_data[crime_data["Type_Description"].isin(["Fight disturbance", "Burglary", "Family Disturbance","Other","Assault Battery","Accident","Malicious destruction of property","Suspicious","'Recovered Stolen Motor Vehicle","assist citizen","small LARCENY"])]
        # #Removing the ward 0 because only wards 1 to 6 is present and ward 0 can mislead the data
        crime_data = crime_data[~crime_data["WARD"].isin(['W_0'])]

        class_for_data_preparation = CRIME_TS_Data_Transformation(crime_data)
        cleaned_data = class_for_data_preparation.data_tranformation(['Type_Description','WARD'],'Event_Date','W',{'Disposition':'count'},{'Disposition':'Crime_Count'})
       
        logger.info('shape of cleaned data',cleaned_data.shape)
        logger.info("TS data cleaning completed.")

        crime_type_column = 'Type_Description'
        ward_name_column='WARD'
        crime_type_list = list(cleaned_data[crime_type_column].unique())
        ward_name_list = list(cleaned_data[ward_name_column].unique())
        for crime in crime_type_list:
            for ward in ward_name_list:
            # Create an instance of the Time_Series_Forecasting class for the current zone.
                class_for_model_fitting =CRIME_Time_Series_Forecasting(cleaned_data,crime_type_column,crime)
                # Get the DataFrame for the current zone.  
                class_for_model_fitting.column_type_dataframe_for_2_columns(crime_type_column,crime,ward_name_column,ward)
                # Determine the optimal ARIMA order for the 'Value' column in the DataFrame.
                class_for_model_fitting.determine_ARIMA_order('Crime_Count')
                
                # Get only the model results for the 'Value' column.
                model_results=class_for_model_fitting.get_model_and_validation_results('Crime_Count',test_size,validation_size)[0]
                # Fit the ARIMA model for the 'Value' column.
                fitted_model=class_for_model_fitting.fit_model('Crime_Count')

                logger.info(f'The model is fitted for crime {crime}.')
                # Save the model results as a pickle file.
                save_pickle_file(model_results, config.PICKLE_FILES_DIRECTORY['pickle_files_path'],f'{name_for_pickle_file}_modelresults_{crime}{ward}.pkl')
                logger.info("pickle file for modelresults crime_type %s and ward %s created successfully",crime,ward)
                
                # Save the fitted model as a pickle file.
                save_pickle_file(fitted_model,config.PICKLE_FILES_DIRECTORY['pickle_files_path'],f'{name_for_pickle_file}_fitresults_{crime}{ward}.pkl')
                logger.info("pickle file for fitresults crime_type %s and ward %s created successfully",crime,ward)
            logger.info("Model fitting of all wards completed successfully")
        
        logger.info("Model fitting of all crime types completed successfully")
        # Return a success message to the user.
        return {'message': 'Model fitting of all crime and wards completed successfully'}

    
    except Exception as e:
        logging.exception('Exception occurred during model fitting:%s',str(e))
        # If an exception occurs during the model fitting process, raise an HTTPException with a 500 status code.
        raise HTTPException(status_code=500, detail="Exception occurred during model fitting")






