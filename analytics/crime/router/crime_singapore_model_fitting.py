from fastapi import APIRouter, File, UploadFile,Query, HTTPException,Depends
from crime.crime_forecasting_model import *
from utils.file_operations import *
import pandas as pd
import os
from crime import crime_config as config


# router = APIRouter(tags=['ES Time Series Forecasting'])
# Define an API endpoint to train the model and save the results as pickle files
# @router.post('/Model_fitting',summary='Model results and fitted model to pickle files')
def singapore_model_fitting_ward_wise(name_for_pickle_file: str= Query(..., description="Please provide the name for the pickle file"),
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
        crime_data = pd.read_csv(config.CLEANED_DATA_PATH['cleaned_file_path']+config.FILE_NAME['processed_data_csv_file_name4'], index_col='Event_Date', parse_dates=True)
        print(crime_data)
        # crime_data = crime_data[~crime_data["WARD"].isin([0.0])]
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
