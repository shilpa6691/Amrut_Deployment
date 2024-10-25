import os
current_file_path = os.path.abspath(__file__)
subsystem_name = current_file_path.split(os.path.sep)[-2]

# Default values
DEFAULT_VALUES = {
"DEFAULT_TEST_SIZE" : 2, #8,
"DEFAULT_VALIDATION_SIZE" : 2 #12
}


# Path to the CSV file for storing uploaded data
CSV_FILE_PATH = {
    "upload_file_path":"/opt/siap/data/processed_data/",
    "location_file_path":"/opt/siap/data/location_details/es/"}
# CSV_FILE_PATH = {"upload_file_path":"/opt/siap/data/processed_data/"}

DATA_FILE_NAMES = {
#processed data csv file name 
'processed_data_csv_file_name':f'{subsystem_name}/ES_cleaned_data.csv',
'processed_data_csv_file_name1':'ES_cleaned_loc_zone.csv',
# 'processed_data_csv_file_name':'Weekly_zone_July23_api.csv',
'visualization_data_csv_file_name1':'ES_cleaned_loc_zone.csv',
'visualization_data_csv_file_name2':'ES_cleaned.csv',
'location_data_csv_file_name':'ES_Singapore_Location.csv'

}

JSON_FILE_PATH = {
    "upload_file_path":"/opt/siap/data/results/es/",
    "forecasting_file_path":"/opt/siap/data/results/es/tsa/"}

#Analytics log Path
LOG_FILE_PATH = {'analytics_logs_path':f'/opt/siap/analytics/{subsystem_name}/logs/',
                 'analytics_logs_name':f'{subsystem_name}_log_file'}
                # 'analytics_logs_name':datetime.now().strftime("es_log_file-%Y-%m-%d.log")}

# Directory for storing pickle files
PICKLE_FILES_DIRECTORY = {'pickle_files_path':f'/opt/siap/analytics/{subsystem_name}/files/'}
