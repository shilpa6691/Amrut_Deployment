from fastapi import APIRouter
from fastapi import Query
from visualization_model import *
import logging
from utils.file_operations import *
import pandas as pd
import config as config

router = APIRouter()
logger=setup_logger(config.LOG_FILE_PATH['logs_path'],config.LOG_FILE_PATH['logs_name'])

csv_file = pd.read_csv(config.CSV_FILE_PATH['upload_file_path']+config.DATA_FILE_NAMES['visualization_data_csv_file_name'],index_col='Standardized_Date',parse_dates=True)
data_processor = Data_Visualization(csv_file)
df=pd.read_excel(config.CSV_FILE_PATH['upload_file_path']+config.DATA_FILE_NAMES['visualization_data_csv_file_name2'],index_col='Standardized_Date',parse_dates=True)
df1=pd.read_csv(config.CSV_FILE_PATH['upload_file_path']+config.DATA_FILE_NAMES['visualization_data_csv_file_name3'])


if not os.path.exists(config.JSON_FILE_PATH['upload_file_path']):
    os.makedirs(config.JSON_FILE_PATH['upload_file_path'])

def recovery_percentage_capacity_utilization():
    try:

        processed_data = data_processor.recovery_percentage_capacity_utilization_finder()
        processed_data.to_json(config.JSON_FILE_PATH['upload_file_path']+'recovery_percentage_capacity_utilization.json',orient='records')

        processed_data = processed_data.to_dict('records')
        logging.info("Processing recovery percentage and capacity utilization data...")

        return {'Title':'Recovery_percentage_and_capacity_utilization','Data':processed_data}

    except Exception as e:
        logging.exception(f"Exception occurred: {e}")


def plant_availability():
    try:

        processed_data = data_processor.plant_availability_finder()
        processed_data.to_json(config.JSON_FILE_PATH['upload_file_path']+'plant_availability.json',orient='records')

        processed_data = processed_data.to_dict('records')
        logging.info("Processing plant_availability data...")
        
        return {'Title':'Plant_availability','Data':processed_data}

    except Exception as e:
        logging.exception(f"Exception occurred: {e}")


# def shift_and_zone_wise_water_production(page: int = Query(1, ge=1, description="Page number, starting from 1."),
#         rows_per_page: int = Query(1000, ge=1, le=1000, description="Number of rows to fetch per page.")):
#     try:
#         processed_data = data_processor.shift_and_zone_water_production_finder()
#         logging.info("Processing shift wise and zone wise water production data...")

#         total_rows = len(processed_data)
#         total_pages = (total_rows + rows_per_page - 1) // rows_per_page
#         start_index = (page - 1) * rows_per_page
#         end_index = start_index + rows_per_page

#         processed_data_subset = processed_data[start_index:end_index].to_dict('records')
#         result = {'shift_and_zone_wise_water_production':processed_data_subset}
#         result['current_page'] = f'page {page} of {total_pages} pages'
#         return result
#     except Exception as e:
#         logging.exception(f"Exception occurred: {e}")


def shift_and_zone_wise_water_production():
    try:

        processed_data = data_processor.shift_and_zone_water_production_finder()
        processed_data.to_json(config.JSON_FILE_PATH['upload_file_path']+'shift_and_zone_wise_water_production.json',orient='records')

        processed_data = processed_data.to_dict('records')
        logging.info("Processing shift wise and zone wise water production data...")

        result = {'Title':'shift_and_zone_wise_water_production','Data':processed_data}
        return result
    except Exception as e:
        logging.exception(f"Exception occurred: {e}")


def ebill_analysis():
    try:
        
        processed_data = data_processor.ebill_new_columns_adder(df)
        processed_data.to_json(config.JSON_FILE_PATH['upload_file_path']+'ebill_analysis.json',orient='records')

        processed_data = processed_data.to_dict('records')
        logging.info("Processing ebill data...")

        result = {'Title':'ebill_analysis','Data':processed_data}
        return result
    except Exception as e:
        logging.exception(f"Exception occurred: {e}")


def energy_meter_analysis():
    try:        
        processed_data = data_processor.energy_meter_calculator(df1)
        processed_data.to_json(config.JSON_FILE_PATH['upload_file_path']+'energy_meter_calculator.json',orient='records')
        processed_data = processed_data.to_dict('records')
        logging.info("Processing energy_meter data...")

        result = {'Title':'energy_meter_analysis','Data':processed_data}
        return result
    except Exception as e:
        logging.exception(f"Exception occurred: {e}")

