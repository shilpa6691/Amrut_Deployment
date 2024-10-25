from fastapi import APIRouter, HTTPException,Query
from crime import crime_config as config
from utils.file_operations import *
from crime.crime_model import *
import pandas as pd


# Load your data
cleaned_data = pd.read_csv(config.CLEANED_DATA_PATH['cleaned_file_path'] + config.FILE_NAME['processed_data_csv_file_name3'])

cleaned_data['Month-Year'] = pd.to_datetime(cleaned_data['Month-Year'], format='%B-%Y')
# # Extract unique values of Month-Year column in the desired format
unique_dates = cleaned_data['Month-Year'].dt.strftime('%m-%Y').unique().tolist()


# @router.get('/monthly_count_of_crimes_locationwise_and_yearly_total_counts')
def singapore_monthly_total_crimes(
    start_date: str = Query(..., description="Start date",enum=unique_dates),
    end_date: str = Query(..., description="End date",enum=unique_dates),
    page: int = Query(1, ge=1, description="Page number, starting from 1."),
    rows_per_page: int = Query(1000, ge=1, le=1000, description="Number of rows to fetch per page.")
):

    logger=setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])

    try:
        logger.info("Loading cleaned data files.")
        # Use the loaded data
        cleaned_data = pd.read_csv(config.CLEANED_DATA_PATH['cleaned_file_path'] + config.FILE_NAME['processed_data_csv_file_name3'])
        cleaned_data['Month-Year'] = pd.to_datetime(cleaned_data['Month-Year'], format='%B-%Y')

        # Filter data based on date range
        filtered_data = cleaned_data[(cleaned_data['Month-Year'] >= start_date) & (cleaned_data['Month-Year'] <= end_date)]
        
        logger.info("Counting number of monthly crimes....")
        data_processor_class = data_processing()
        total_monthly_data = data_processor_class.get_crime_count_locationwise(filtered_data,['Month-Year','WARD_LAT','WARD_LONG','WARD','Type_Description'],'Disposition',{"Disposition":"Crime_counts"})
        total_monthly_data = total_monthly_data.groupby(['Month-Year','WARD_LAT','WARD_LONG','WARD']).apply(lambda x: x.nlargest(10, 'Crime_counts')).reset_index(drop=True)
        print (total_monthly_data)

        logger.info("Counting completed!")


        # Pagination
        total_rows = len(total_monthly_data)
        total_pages = (total_rows + rows_per_page - 1) // rows_per_page
        start_index = (page - 1) * rows_per_page
        end_index = start_index + rows_per_page
        has_more_rows = end_index < len(total_monthly_data)
        total_monthly_data_subset = total_monthly_data.iloc[start_index:end_index].to_dict('records')

        for entry in total_monthly_data_subset:
            entry['Month-Year'] = entry['Month-Year'].strftime('%B-%Y')

        result = {'Monthly count of crimes': total_monthly_data_subset}
        result['current_page'] = f'page {page} of {total_pages} pages'
        
        return result

    except Exception as e:
        logging.exception("Exception occurred during monthly_total_crimes: %s", str(e))
        raise HTTPException(status_code=500, detail="Exception occurred during monthly_total_crimes")


# @router.get('/hotspot_detection_of_crimes')
def singapore_spatial_distribution_of_crimes(page: int = Query(1, ge=1, description="Page number, starting from 1."),
    rows_per_page: int = Query(1000, ge=1, le=1000, description="Number of rows to fetch per page.")):

    logger=setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])

    try:
        logger.info("Loading cleaned data files.")
        cleaned_data = pd.read_csv(config.CLEANED_DATA_PATH['cleaned_file_path']+config.FILE_NAME['processed_data_csv_file_name3'])
        
        data_processor_class = data_processing()
        logger.info("Counting number of crimes...")
        total_locationwise_data = data_processor_class.latitude_longitudewise_crimes(cleaned_data,['WARD','WARD_LAT','WARD_LONG'],'CrimeCount') 
        logger.info("Counting completed!")


        start_index = (page - 1) * rows_per_page
        end_index = start_index + rows_per_page       
        total_locationwise_data_subset =  total_locationwise_data.iloc[start_index:end_index].to_dict('records')
        has_more_rows = end_index < len(total_locationwise_data)
        total_rows = len(total_locationwise_data)
        total_pages = (total_rows + rows_per_page - 1) // rows_per_page
 

        result = {
        'Total number of crimes': total_locationwise_data_subset}
        result['current_page'] = f'page {page} of {total_pages} pages'

        return result


    except Exception as e:
        logging.exception('Exception occurred during spatial_distribution_of_crimes:%s',str(e))
        # If an exception occurs during the model fitting process, raise an HTTPException with a 500 status code.
        raise HTTPException(status_code=500, detail="Exception occurred during spatial_distribution_of_crimes")

