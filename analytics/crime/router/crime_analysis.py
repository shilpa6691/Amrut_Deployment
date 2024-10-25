from fastapi import APIRouter, HTTPException,Query,Depends
from crime import crime_config as config
from utils.file_operations import *
from crime.crime_model import *
import pandas as pd
from auth.authbearer import verify_token


# Load your data
cleaned_data = pd.read_csv(config.CLEANED_DATA_PATH['cleaned_file_path'] + config.FILE_NAME['processed_data_csv_file_name1'])
# # Convert "Month-Year" column to datetime format
cleaned_data['Month-Year'] = pd.to_datetime(cleaned_data['Month-Year'], format='%B-%Y')
# # Extract unique values of Month-Year column in the desired format
unique_dates = cleaned_data['Month-Year'].dt.strftime('%m-%Y').unique().tolist()

# @router.get('/monthly_count_of_crimes_locationwise_and_yearly_total_counts')
def monthly_total_crimes(
    start_date: str = Query(..., description="Start date",enum=unique_dates),
    end_date: str = Query(..., description="End date",enum=unique_dates),
    page: int = Query(1, ge=1, description="Page number, starting from 1."),
    rows_per_page: int = Query(1000, ge=1, le=1000, description="Number of rows to fetch per page."),token: str = Depends(verify_token)):

    logger=setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])

    try:
        logger.info("Loading cleaned data files.")
        # Use the loaded data
        cleaned_data = pd.read_csv(config.CLEANED_DATA_PATH['cleaned_file_path'] + config.FILE_NAME['processed_data_csv_file_name1'])

        # Convert start_date and end_date to datetime objects
        cleaned_data['Month-Year'] = pd.to_datetime(cleaned_data['Month-Year'], format='%B-%Y')

        # Filter data based on date range
        filtered_data = cleaned_data[(cleaned_data['Month-Year'] >= start_date) & (cleaned_data['Month-Year'] <= end_date)]
        
        logger.info("Counting number of monthly crimes....")
        data_processor_class = data_processing()
        total_monthly_data = data_processor_class.get_crime_count_locationwise(filtered_data,['Type_Description','WARD','Month-Year'],'Disposition',{"Disposition":"Crime_counts"})
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


def yearly_total_crimes(page: int = Query(1, ge=1, description="Page number, starting from 1."),
    rows_per_page: int = Query(1000, ge=1, le=1000, description="Number of rows to fetch per page.")):

    logger=setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])

    try:
        logger.info("Loading cleaned data files.")
        cleaned_data = pd.read_csv(config.CLEANED_DATA_PATH['cleaned_file_path']+config.FILE_NAME['processed_data_csv_file_name1'])
        
        
        data_processor_class = data_processing()
        logger.info("Counting number of crimes...")
        total_yearwise_data = data_processor_class.get_crime_count_yearise(cleaned_data,['Year','WARD'],'Year_count')    
        logger.info("Counting completed!")


        start_index = (page - 1) * rows_per_page
        end_index = start_index + rows_per_page       
        total_yearwise_data_subset =  total_yearwise_data.iloc[start_index:end_index].to_dict('records')
        has_more_rows = end_index < len(total_yearwise_data)
        total_rows = len(total_yearwise_data)
        total_pages = (total_rows + rows_per_page - 1) // rows_per_page
 

        
        result = {
        'Total number of crimes': total_yearwise_data_subset}
        result['current_page'] = f'page {page} of {total_pages} pages'

        return result


    except Exception as e:
        logging.exception('Exception occurred during yearly_total_crimes:%s',str(e))
        # If an exception occurs during the model fitting process, raise an HTTPException with a 500 status code.
        raise HTTPException(status_code=500, detail="Exception occurred during yearly_total_crimes")


# @router.get('/hotspot_detection_of_crimes')
def spatial_distribution_of_crimes(page: int = Query(1, ge=1, description="Page number, starting from 1."),
    rows_per_page: int = Query(1000, ge=1, le=1000, description="Number of rows to fetch per page.")):

    logger=setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])

    try:
        logger.info("Loading cleaned data files.")
        cleaned_data = pd.read_csv(config.CLEANED_DATA_PATH['cleaned_file_path']+config.FILE_NAME['processed_data_csv_file_name1'])
        
        
        data_processor_class = data_processing()
        logger.info("Counting number of crimes...")
        total_locationwise_data = data_processor_class.latitude_longitudewise_crimes(cleaned_data,['WARD','LAT','LONG'],'CrimeCount')    
        logger.info("Counting completed!")


        start_index = (page - 1) * rows_per_page
        end_index = start_index + rows_per_page       
        # total_locationwise_data.drop(total_locationwise_data.index[0:2], inplace=True)
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



# from geopy.geocoders import Nominatim
# # Create a geocoder object
# geolocator = Nominatim(user_agent="crime_analysis")

# def generate_recommendations(beat_data):

#     recommendations = []
#     for beat_info in beat_data:
#         beat_id = beat_info['Beat']
#         crime_counts = beat_info['Crime_counts']
#         latitude = beat_info['LAT']
#         longitude = beat_info['LONG']
        
#         if crime_counts > 500:
#             # Reverse geocode to get location from latitude and longitude
#             location = geolocator.reverse((latitude, longitude))
#             recommendation = f"Increase patrol in beat {beat_id} due to high crime count ({crime_counts}) near {location})"
#             recommendations.append({"beat_id": beat_id, "recommendation": recommendation})
#     return recommendations

# # @router.get('/relationship_between_no_of_beats_and_crime_rates')
# def number_of_crimes_in_beats(page: int = Query(233, ge=1, description="Page number, starting from 1."),
#     rows_per_page: int = Query(1000, ge=1, le=1000, description="Number of rows to fetch per page.")):

#     logger=setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])

#     try:
#         # Load cleaned data
#         logger.info("Loading cleaned data files.")
#         cleaned_data = pd.read_csv(config.CLEANED_DATA_PATH['cleaned_file_path'] + config.FILE_NAME['processed_data_csv_file_name1'])
        
#         data_processor_class = data_processing()
#         # Count number of beats
#         logger.info("Counting number of crimes...")
#         total_beat_data = data_processor_class.relationship_of_beat_and_crimes(cleaned_data,['General_Location','LAT','LONG','Type_Description'],{"Beat":"nunique","Disposition":"count"},'Beat',{"Disposition":"Crime_counts"})
#         logger.info("Counting completed")

#         beat_min=total_beat_data['Beat'].min()
#         beat_max=total_beat_data['Beat'].max()    
#         Beat_count1=total_beat_data[total_beat_data['Beat']==beat_min].sort_values(by='Crime_counts', ascending=False)
#         Beat_count1.drop(Beat_count1.index[0], inplace=True)
#         Beat_count2=total_beat_data[total_beat_data['Beat']==beat_max].sort_values(by='Crime_counts', ascending=False)

#         start_index = (page - 1) * rows_per_page
#         end_index = start_index + rows_per_page
#         Beat_count1_subset = Beat_count1.iloc[start_index:end_index].to_dict('records')
#         total_rows = len(Beat_count1)
#         total_pages = (total_rows + rows_per_page - 1) // rows_per_page
#         has_more_rows = end_index < len(Beat_count1)

#         if has_more_rows:
#             result = {
#                 'Total number of crimes with less beats': Beat_count1_subset,
#                 'recommendations': generate_recommendations(Beat_count1_subset),
#                 'current_page': f'page {page} of {total_pages} pages'
#             }
#         else:
#             count_max=Beat_count2['Crime_counts'].iloc[0]
#             count_min=Beat_count1['Crime_counts'].iloc[0]
#             location_min=Beat_count1['General_Location'].iloc[0]
#             location_max=Beat_count2['General_Location'].iloc[0]
#             location_min_lat=Beat_count1['LAT'].iloc[0]
#             location_min_long=Beat_count1['LONG'].iloc[0]
#             location_max_lat=Beat_count2['LAT'].iloc[0]
#             location_max_long=Beat_count2['LONG'].iloc[0]
#             type_max=Beat_count2['Type_Description'].iloc[0]
#             type_min=Beat_count1['Type_Description'].iloc[0]
#             result= {
#                 'Total number of crimes with less beats': Beat_count1_subset,
#                 'Total number of crimes with more beats': Beat_count2.to_dict('records'),
#                 'Inference': f'As the number of beats increases ({beat_max}) crime count decreases ({count_max}) and As the number of beats decreases ({beat_min}) crime count increases ({count_min}) ',
#                 'Location and type of crime which has maximum beat count': [location_max, location_max_lat, location_max_long, type_max],
#                 'Location and type of crime which has minimum beat count': [location_min, location_min_lat, location_min_long, type_min],
#                 'recommendations': generate_recommendations(Beat_count1_subset)
                
#             }
#             result['current_page'] = f'page {page} of {total_pages} pages'
        
#         return result

#     except Exception as e:
#         logging.exception('Exception occurred during number_of_crimes_in_beats:%s',str(e))
#         raise HTTPException(status_code=500, detail="Exception occurred during number_of_crimes_in_beats")


# @router.get('/classification_of_crimes_based_on_severity')
def severity_of_the_crime(page: int = Query(1, ge=1, description="Page number, starting from 1."),
    rows_per_page: int = Query(1000, ge=1, le=1000, description="Number of rows to fetch per page.")):

    logger=setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])

    try:
        logger.info("Loading cleaned data files.")
        cleaned_data = pd.read_csv(config.CLEANED_DATA_PATH['cleaned_file_path']+config.FILE_NAME['processed_data_csv_file_name1'])
        
        
        data_processor_class = data_processing()    
        logger.info("Counting number of severity...")
        total_severity_data = data_processor_class.severity_classification(cleaned_data,['WARD','Type_Description','Severity'],'Crime_counts')
        logger.info("Counting completed!")
        
        start_index = (page - 1) * rows_per_page
        end_index = start_index + rows_per_page
        severity_data_subset = total_severity_data.iloc[start_index:end_index].to_dict('records')    
        has_more_rows = end_index < len(total_severity_data)
        total_rows = len(total_severity_data)
        total_pages = (total_rows + rows_per_page - 1) // rows_per_page

        if has_more_rows:
            result = {
            'Total number of crimes':severity_data_subset}
            result['current_page'] = f'page {page} of {total_pages} pages'

        else:
            severity_max=total_severity_data.Severity.iloc[0]
            max_data=total_severity_data.iloc[0].to_dict()
            return {'Total number of crimes':severity_data_subset,
        'Inference':f'Maximum no of crimes comes under the category ({severity_max})',
        f'Location and type of the crime in {severity_max} category':max_data}

        return result

    except Exception as e:
        logging.exception('Exception occurred during severity_of_crime:%s',str(e))
        # If an exception occurs during the model fitting process, raise an HTTPException with a 500 status code.
        raise HTTPException(status_code=500, detail="Exception occurred during severity_of_crime")



cleaned_data = pd.read_csv(config.CLEANED_DATA_PATH['cleaned_file_path'] + config.FILE_NAME['processed_data_csv_file_name1'])
cleaned_data['Month-Year'] = pd.to_datetime(cleaned_data['Month-Year'], format='%B-%Y')
# Extract unique values of Month-Year column in the desired format
unique_dates = cleaned_data['Month-Year'].dt.strftime('%m-%Y').unique().tolist()

# @router.get('/time_and_location_at_which_accidents_happen_the_most')
def time_of_the_accidents(start_date: str = Query(..., description="Start date",enum=unique_dates),
    end_date: str = Query(..., description="End date",enum=unique_dates),
    page: int = Query(1, ge=1, description="Page number, starting from 1."),
    rows_per_page: int = Query(1000, ge=1, le=1000, description="Number of rows to fetch per page.")):

    logger=setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])

    try:
        logger.info("Loading cleaned data files.")
        cleaned_data = pd.read_csv(config.CLEANED_DATA_PATH['cleaned_file_path']+config.FILE_NAME['processed_data_csv_file_name1'])
        
        cleaned_data['Month-Year'] = pd.to_datetime(cleaned_data['Month-Year'], format='%B-%Y')
        # Filter data based on date range
        filtered_data = cleaned_data[(cleaned_data['Month-Year'] >= start_date) & (cleaned_data['Month-Year'] <= end_date)]
    
        logger.info("Counting number of accidents...")
        data_processor_class = data_processing()
        total_accident_data = data_processor_class.time_location_of_accidents(filtered_data,['Type_Description','WARD','time_window'],{'Type':'count'},'Type',{"Type":"Accident_counts"})
        logger.info("Counting completed!")
        
        start_index = (page - 1) * rows_per_page
        end_index = start_index + rows_per_page
        total_accident_data_subset = total_accident_data.iloc[start_index:end_index].to_dict('records')
        total_rows = len(total_accident_data)
        total_pages = (total_rows + rows_per_page - 1) // rows_per_page
        has_more_rows = end_index < len(total_accident_data)

        if has_more_rows:
            result = {
            'Total number of accidents': total_accident_data_subset}
            result['current_page'] = f'page {page} of {total_pages} pages'
        
        else:
            time=total_accident_data.time_window.iloc[0]
            count=total_accident_data.Accident_counts.iloc[0]
            location=total_accident_data.iloc[0].to_dict()
            result = {'Total number of accidents':total_accident_data_subset,
        'Inference':f'Time accidents happen the most is ({time}) and the no of accidents occured is ({count})',
        f'Location of most accidents occured in the ({time}) time_window':location}
            result['current_page'] = f'page {page} of {total_pages} pages'

        return result

    except Exception as e:
        logging.exception('Exception occurred during time_of_accidents:%s',str(e))
        # If an exception occurs during the model fitting process, raise an HTTPException with a 500 status code.
        raise HTTPException(status_code=500, detail="Exception occurred during time_of_accidents")


# @router.get('/yearwise_total_crime_rate')
def crime_rate_statistics():
    logger=setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])

    try:
        logger.info("Loading cleaned data files.")
        cleaned_data = pd.read_csv(config.CLEANED_DATA_PATH['cleaned_file_path']+config.FILE_NAME['processed_data_csv_file_name1'])
        
    
        logger.info("Counting number of crime rates...")
        data_processor_class = data_processing()
        total_crime_rate_data = data_processor_class.crime_rate_of_types_of_crimes(cleaned_data,['Year'],'Type_Description')[0]   
        crime_rate_statistics=data_processor_class.crime_rate_of_types_of_crimes(cleaned_data,['Year'],'Type_Description')[1]
        logger.info("Counting completed!")

        crime_rate_max=crime_rate_statistics.Crime_rate.iloc[0]
        year_max=crime_rate_statistics.Year.iloc[0]
        crime_rate_min=crime_rate_statistics.Crime_rate.iloc[len(total_crime_rate_data)-1]
        year_min=crime_rate_statistics.Year.iloc[len(total_crime_rate_data)-1]
        total_crime_rate_data = total_crime_rate_data.to_dict('records')

        return {'Total crime_rates':total_crime_rate_data,
        'Total_crime_rates_statistics':crime_rate_statistics.to_dict('records'),
        'Inference':f'maximum crime rates is in the year {year_max} ({crime_rate_max}) and minimum crime rates is in the year {year_min} ({crime_rate_min}) '}
    except Exception as e:
        logging.exception('Exception occurred during crime_rate_statistics:%s',str(e))
        # If an exception occurs during the model fitting process, raise an HTTPException with a 500 status code.
        raise HTTPException(status_code=500, detail="Exception occurred during crime_rate_statistics")



cleaned_data = pd.read_csv(config.CLEANED_DATA_PATH['cleaned_file_path'] + config.FILE_NAME['processed_data_csv_file_name1'])
cleaned_data['Month-Year'] = pd.to_datetime(cleaned_data['Month-Year'], format='%B-%Y')
# Extract unique values of Month-Year column in the desired format
unique_dates = cleaned_data['Month-Year'].dt.strftime('%m-%Y').unique().tolist()

# @router.get('/effect_of_cctv_and_streetlight')
def cctv_streetlight_vs_crime_count(start_date: str = Query(..., description="Start date",enum=unique_dates),
    end_date: str = Query(..., description="End date",enum=unique_dates),
    page: int = Query(1, ge=1, description="Page number, starting from 1."),
    rows_per_page: int = Query(1000, ge=1, le=1000, description="Number of rows to fetch per page.")):

    logger=setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])

    try:
        logger.info("Loading cleaned data files.")
        cleaned_data = pd.read_csv(config.CLEANED_DATA_PATH['cleaned_file_path']+config.FILE_NAME['processed_data_csv_file_name1'])
        
        cleaned_data['Month-Year'] = pd.to_datetime(cleaned_data['Month-Year'], format='%B-%Y')
        # Filter data based on date range
        filtered_data = cleaned_data[(cleaned_data['Month-Year'] >= start_date) & (cleaned_data['Month-Year'] <= end_date)]
    
        logger.info("Counting number of crime rates of cctv and streetlight...")
        data_processor_class = data_processing()
        total_crime_rate_data = data_processor_class.cctv_streetlight_effect(filtered_data,['WARD','Type_Description'],'Crime_Count')
        logger.info("Counting completed!")

        # total_crime_rate_data.drop(total_crime_rate_data.index[0], inplace=True)
        
        start_index = (page - 1) * rows_per_page
        end_index = start_index + rows_per_page
        total_crime_rate_data_subset = total_crime_rate_data.iloc[start_index:end_index].to_dict('records')
        total_rows = len(total_crime_rate_data)
        total_pages = (total_rows + rows_per_page - 1) // rows_per_page
        has_more_rows = end_index < len(total_crime_rate_data)

        if has_more_rows:
            result = {
            'Total crime_rates': total_crime_rate_data_subset}
            result['current_page'] = f'page {page} of {total_pages} pages'
        
        else:
            max_data=total_crime_rate_data.iloc[0].to_dict()
            min_data=total_crime_rate_data.iloc[len(total_crime_rate_data)-1].to_dict()
            result = {'Total crime_rates':total_crime_rate_data_subset,
        'Crime counts are less for the locations having more no of cctv and streetlights':min_data,
        'Crime counts are more for the locations having less no of cctv and streetlights':max_data}
            result['current_page'] = f'page {page} of {total_pages} pages'

        return result

    except Exception as e:
        logging.exception('Exception occurred during cctv_streetlight_vs_crime_count:%s',str(e))
        # If an exception occurs during the model fitting process, raise an HTTPException with a 500 status code.
        raise HTTPException(status_code=500, detail="Exception occurred during cctv_streetlight_vs_crime_count")


# @router.get('/comparison_of_crimes_in_2_cities')
def Las_vegas_and_San_francisco_crime_trends():
    logger=setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])

    try:
        logger.info("Loading cleaned data files.")
        cleaned_data1 = pd.read_csv(config.CLEANED_DATA_PATH['cleaned_file_path']+config.FILE_NAME['processed_data_csv_file_name1'])
        cleaned_data2 = pd.read_csv(config.CLEANED_DATA_PATH['cleaned_file_path']+config.FILE_NAME['processed_data_csv_file_name2'])
    
        logger.info("Counting number of crime rates of 2 cities...")
        data_processor_class = data_processing()
        total_crime_rate_data = data_processor_class.merging_datframes(cleaned_data1,cleaned_data2,["Year","City","Population"],'Crime_counts')
        logger.info("Counting completed!")

        count_max_city=total_crime_rate_data.City.iloc[0]
        count_max=total_crime_rate_data.Crime_Counts_per_1000_population.iloc[0]
        count_max_year=total_crime_rate_data.Year.iloc[0]
        total_crime_rate_data = total_crime_rate_data.to_dict('records')

        return {'Total crime_rates':total_crime_rate_data,
        'Inference':f'Crime counts are more for {count_max_city} ({count_max}) in the year {count_max_year}'}
    except Exception as e:
        logging.exception('Exception occurred during Las_vegas_and_San_francisco_crime_trends:%s',str(e))
        # If an exception occurs during the model fitting process, raise an HTTPException with a 500 status code.
        raise HTTPException(status_code=500, detail="Exception occurred during Las_vegas_and_San_francisco_crime_trends")


