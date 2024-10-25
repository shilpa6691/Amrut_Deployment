from fastapi import APIRouter, HTTPException, Query,Depends
import pandas as pd
from utils.file_operations import *
import json
import os

current_file_path = os.path.abspath(__file__)
subsystem_name = current_file_path.split(os.path.sep)[-3]
import_model = f"from {subsystem_name}.{subsystem_name}_model import *"
import_config = f"from {subsystem_name} import {subsystem_name}_config as config"
exec(import_model)
exec(import_config)

with open(config.CSV_FILE_PATH["ahu_fernet_key_path"]+config.DATA_FILE_NAMES["ahu_fernet_key_name"], 'rb') as filekey:
    key = filekey.read()

def RA_temp_anomaly_detection():
    logger=setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])
    try:
        logger.info('Loading csv file')
        processed_data_csv = file_decrypt(config.CSV_FILE_PATH['upload_file_path']+config.DATA_FILE_NAMES['processed_data_csv_file_name'],key)
        data_csv = pd.read_csv(processed_data_csv)
        print(data_csv.head())
        anomaly_class = AnomalyDetection(data_csv,'RA TEMP')
        logging.info("Detecting anomalies")
        processed_data = anomaly_class.isolation_forest()
        logger.info(processed_data)
        print(processed_data)
        logging.info("Storing the result as json file")
        if not os.path.exists(config.JSON_FILE_PATH['upload_file_path']):
            os.makedirs(config.JSON_FILE_PATH['upload_file_path'])
        processed_data.to_json(config.JSON_FILE_PATH['upload_file_path']+'latest_value_of_aqi.json',orient='records')
        processed_data = processed_data.to_dict('records')
        # anomaly_count = processed_data.loc[-1].item()
        # return {'Anomalies':processed_data}
        # return {'Number of anomalies':anomaly_count}
        return {'Data classification based on anomalies': processed_data}

    except Exception as e:
        logging.exception(f"Exception occurred: {e}")
        raise HTTPException(status_code=500, detail=f"Exception occurred: {e}")