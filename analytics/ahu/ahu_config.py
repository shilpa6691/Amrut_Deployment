import os
current_file_path = os.path.abspath(__file__)
subsystem_name = current_file_path.split(os.path.sep)[-2]

# Path to the CSV file for storing uploaded data
CSV_FILE_PATH = {
    "upload_file_path":"/opt/siap/data/processed_data/",
    # fernet key path
    "ahu_fernet_key_path" : "/opt/siap/data/keys/ahu/"}

DATA_FILE_NAMES = {
#processed data csv file name 
'processed_data_csv_file_name':f'{subsystem_name}/{subsystem_name}_cleaned_data.csv',
# fernet key name
"ahu_fernet_key_name" : "filekey.key"}

JSON_FILE_PATH = {
    "upload_file_path":f"/opt/siap/data/results/{subsystem_name}/"}

#Analytics log Path
LOG_FILE_PATH = {'analytics_logs_path':f'/opt/siap/analytics/{subsystem_name}/logs/',
                 'analytics_logs_name':f'{subsystem_name}_log_file'}