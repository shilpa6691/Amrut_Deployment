from fastapi import APIRouter,Depends
from fastapi import Query
from visualization_model import *
import logging
from utils.file_operations import *
import pandas as pd
import config as config
from auth.authbearer import verify_token
from sqlalchemy import create_engine
import json
from connect import connection
import psycopg2
from sqlalchemy import create_engine, text
import json
import config
import csv
import numpy as np


router = APIRouter()
logger=setup_logger(config.LOG_FILE_PATH['logs_path'],config.LOG_FILE_PATH['logs_name'])

# csv_file = pd.read_csv(config.CSV_FILE_PATH['upload_file_path']+config.DATA_FILE_NAMES['visualization_data_csv_file_name'],index_col='Standardized_Date',parse_dates=True)
# data_processor = Data_Visualization(csv_file)
# df=pd.read_excel(config.CSV_FILE_PATH['upload_file_path']+config.DATA_FILE_NAMES['visualization_data_csv_file_name2'],index_col='Standardized_Date',parse_dates=True)
# df1=pd.read_csv(config.CSV_FILE_PATH['upload_file_path']+config.DATA_FILE_NAMES['visualization_data_csv_file_name3'])


if not os.path.exists(config.JSON_FILE_PATH['upload_file_path']):
    os.makedirs(config.JSON_FILE_PATH['upload_file_path'])


def fetch_data_from_db(query, columns):
    try:
        # Create a cursor to interact with the database
        cursor = connection.cursor()
        
        # Execute the query and fetch the data
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        
        # Convert the rows to a DataFrame
        return pd.DataFrame(rows, columns=columns)
    
    except Exception as e:
        print("Error fetching data from database:", e)
        raise e

# Define the SQL queries and column names
queries = {
    "cleaned_data": """
        SELECT "Standardized_Date", "STANDARDIZED_TIME", "RAW WATER FLOW IN ML",
               "CLEAR WATER SUMP LEVEL IN Meter", "CLEAR WATER PUMPING FLOW ML",
               "TREATED WATER PRODUCTION IN ML", "REMARKS", "remarks category"
        FROM "process"."cleaned_data"
    """,
    "ebill_data": """
        SELECT "Standardized_Date", "Month", "Year","DateTime " , "CD (kVA)", "75% CD (kVA)",
               "130% CD (kVA)", "Connected Load (kW)", "MD Avg (kVA)",
               "Avg_Consumption (kWh)", "Units_kWh", "PF Avg", "Z1 (kWh)", "Z2 (kWh)",
               "Z3 (kWh)", "Z1 kVArh (lag)", "Z2 kVArh (lag)", "Z3 kVArh (lag)",
               "Z1 kVArh (lead)", "Z2 kVArh (lead)", "Z3 kVArh (lead)", "Z1 (kVAh)",
               "Z2 (kVAh)", "Z3 (kVAh)", "Z1 (Demand kVA)", "Z2 (Demand kVA)",
               "Z3 (Demand kVA)", "Max_demand (kVA)", "Energy Charge (Rs)",
               "PF incentive/penalty (Rs)", "Demand factor", "Utilization factor",
               "Load Factor"
        FROM "process"."ebill_data"
    """,
    "meter_data": """
        SELECT "ID", "MeterId", "Time", "Phase1_W", "Phase1_I", "Phase1_V_RY",
               "Phase1_pf", "Phase2_W", "Phase2_I", "Phase2_V_YB", "Phase2_pf",
               "Phase3_W", "Phase3_I", "Phase3_V_BR", "Phase3_pf", "W", "VA", "PF",
               "KWh_Im", "KWh_Ex", "KVAh", "Lh"
        FROM "process"."meter_data"
    """,

    "daily_aggregated_data": """
        SELECT  "Standardized_Date","RAW WATER FLOW IN ML", "CLEAR WATER SUMP LEVEL IN Meter",
                   "CLEAR WATER PUMPING FLOW ML", "TREATED WATER PRODUCTION IN ML",
                   "remarks category"
            FROM "process"."daily_aggregated_data"
    """
}

column_names = {
    "cleaned_data": ["Standardized_Date", "STANDARDIZED_TIME", "RAW WATER FLOW IN ML",
                     "CLEAR WATER SUMP LEVEL IN Meter", "CLEAR WATER PUMPING FLOW ML",
                     "TREATED WATER PRODUCTION IN ML", "REMARKS", "remarks category"],
    "ebill_data": ["Standardized_Date", "Month", "Year", "DateTime", "CD (kVA)", "75% CD (kVA)",
                   "130% CD (kVA)", "Connected Load (kW)", "MD Avg (kVA)", "Avg_Consumption (kWh)",
                   "Units_kWh", "PF Avg", "Z1 (kWh)", "Z2 (kWh)", "Z3 (kWh)", "Z1 kVArh (lag)",
                   "Z2 kVArh (lag)", "Z3 kVArh (lag)", "Z1 kVArh (lead)", "Z2 kVArh (lead)", 
                   "Z3 kVArh (lead)", "Z1 (kVAh)", "Z2 (kVAh)", "Z3 (kVAh)", "Z1 (Demand kVA)",
                   "Z2 (Demand kVA)", "Z3 (Demand kVA)", "Max_demand (kVA)", "Energy Charge (Rs)",
                   "PF incentive/penalty (Rs)", "Demand factor", "Utilization factor", "Load Factor"],
    "meter_data": ["ID", "MeterId", "Time", "Phase1_W", "Phase1_I", "Phase1_V_RY", "Phase1_pf", 
                   "Phase2_W", "Phase2_I", "Phase2_V_YB", "Phase2_pf", "Phase3_W", "Phase3_I", 
                   "Phase3_V_BR", "Phase3_pf", "W", "VA", "PF", "KWh_Im", "KWh_Ex", "KVAh", "Lh"],
    "daily_aggregated_data": ["Standardized_Date","RAW WATER FLOW IN ML", "CLEAR WATER SUMP LEVEL IN Meter",
                   "CLEAR WATER PUMPING FLOW ML", "TREATED WATER PRODUCTION IN ML",
                   "remarks category"]
}

# Fetch data from the database
df_cleaned = fetch_data_from_db(queries["cleaned_data"], column_names["cleaned_data"])
df_ebill = fetch_data_from_db(queries["ebill_data"], column_names["ebill_data"])
df_meter = fetch_data_from_db(queries["meter_data"], column_names["meter_data"])
df_daily = fetch_data_from_db(queries["daily_aggregated_data"], column_names["daily_aggregated_data"])



# Pass the DataFrame to the Data_Visualization function
data_processor = Data_Visualization(df_cleaned)


def recovery_percentage_capacity_utilization():
    try:

        processed_data = data_processor.recovery_percentage_capacity_utilization_finder(df_daily)
        processed_data = processed_data.round(2)
        processed_data.to_json(config.JSON_FILE_PATH['upload_file_path']+'recovery_percentage_capacity_utilization.json',orient='records')

        processed_data = processed_data.to_dict('records')
        logging.info("Processing recovery percentage and capacity utilization data...")

        return {'Title':'Recovery_percentage_and_capacity_utilization','Data':processed_data}

    except Exception as e:
        logging.exception(f"Exception occurred: {e}")


def plant_availability():
    try:

        processed_data = data_processor.plant_availability_finder()
        processed_data = processed_data.round(2)
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
        processed_data = processed_data.round(2)
        processed_data.to_json(config.JSON_FILE_PATH['upload_file_path']+'shift_and_zone_wise_water_production.json',orient='records')

        processed_data = processed_data.to_dict('records')
        logging.info("Processing shift wise and zone wise water production data...")

        result = {'Title':'shift_and_zone_wise_water_production','Data':processed_data}
        return result
    except Exception as e:
        logging.exception(f"Exception occurred: {e}")


def ebill_analysis():
    try:
        
        processed_data = data_processor.ebill_new_columns_adder(df_ebill)
        processed_data = processed_data.round(2)
        processed_data.to_json(config.JSON_FILE_PATH['upload_file_path']+'ebill_analysis.json',orient='records')

        processed_data = processed_data.to_dict('records')
        
        logging.info("Processing ebill data...")

        result = {'Title':'ebill_analysis','Data':processed_data}
        return result
    except Exception as e:
        logging.exception(f"Exception occurred: {e}")


def energy_meter_analysis():
    try:        
        processed_data = data_processor.energy_meter_calculator(df_meter)
        processed_data = processed_data.round(2)
        processed_data.to_json(config.JSON_FILE_PATH['upload_file_path']+'energy_meter_calculator.json',orient='records')
        processed_data = processed_data.to_dict('records')
        logging.info("Processing energy_meter data...")

        result = {'Title':'energy_meter_analysis','Data':processed_data}
        return result
    except Exception as e:
        logging.exception(f"Exception occurred: {e}")

