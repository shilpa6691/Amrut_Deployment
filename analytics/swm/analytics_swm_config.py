import os
current_file_path = os.path.abspath(__file__)
subsystem_name = current_file_path.split(os.path.sep)[-2]

# Default values
DEFAULT_VALUES = {
"DEFAULT_TEST_SIZE" : 8,
"DEFAULT_VALIDATION_SIZE" : 8
}


# Path to the CSV file for storing uploaded data
CSV_FILE_PATH = {"upload_file_path":"/opt/siap/data/processed_data/",
                 "location_file_path":f"/opt/siap/data/location_details/{subsystem_name}/"}#/swm"}

DATA_FILE_NAMES = {
#processed data csv file name 
# 'processed_data_csv_file_name':'zone_total.csv',
'processed_data_csv_file_name':'swm_complaints_data.csv',
'location_data_csv_file_name':'swm_lat_long.csv'
}


#Analytics log Path
LOG_FILE_PATH = {'analytics_logs_path':f'/opt/siap/analytics/{subsystem_name}/logs/',
                 'analytics_logs_name':f'{subsystem_name}_log_file'}
                # 'analytics_logs_name':datetime.now().strftime("swm_log_file-%Y-%m-%d.log")}

# Directory for storing pickle files
PICKLE_FILES_DIRECTORY = {'pickle_files_path':f'/opt/siap/analytics/{subsystem_name}/files/'}


