

DEFAULT_VALUES = {
"DEFAULT_TEST_SIZE" : 2, #8,
"DEFAULT_VALIDATION_SIZE" : 2 #12
}

FILE_NAME = {
    'processed_data_csv_file_name1':'las_vegas_final_cleaned_data.csv',
    'processed_data_csv_file_name2':'san_francisco_cleaned_data.csv',
    'processed_data_csv_file_name3':'singapore_data.csv'
}


CLEANED_DATA_PATH = {
    'cleaned_file_path':'/opt/siap/data/processed_data/crime/'
}


LOG_FILE_PATH = {'analytics_logs_path':'/opt/siap/analytics/crime/logs/',
                 'analytics_logs_name':'crime_log_file'}
                #  'analytics_logs_name':datetime.now().strftime("crime_log_file-%Y-%m-%d.log")}

PICKLE_FILES_DIRECTORY = {'pickle_files_path':'/opt/siap/analytics/crime/files/'}
