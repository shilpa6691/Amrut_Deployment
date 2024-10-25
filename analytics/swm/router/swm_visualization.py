import pandas as pd
from fastapi import APIRouter, HTTPException, Query,Depends
# from swm.swm_visualization_model import *#SWM_Data_Visualization
from utils.file_operations import *
# from swm import analytics_swm_config as config
import os
# from auth.authbearer import verify_token
# from auth.auth import *
current_file_path = os.path.abspath(__file__)
subsystem_name = current_file_path.split(os.path.sep)[-3]
import_model = f"from {subsystem_name}.{subsystem_name}_visualization_model import *"
import_config = f"from {subsystem_name} import analytics_{subsystem_name}_config as config"
exec(import_model)
exec(import_config)

# from pandas.tseries.offsets import MonthEnd


# logger=setup_logger(config.LOG_FILE_PATH['analytics_logs_path'])

# Create an APIRouter for time series visualization related endpoints.
# router = APIRouter(prefix='/swm_data_Visualization', tags=['SWM Data Visualization'])


data = pd.read_csv(config.CSV_FILE_PATH['upload_file_path']+config.DATA_FILE_NAMES['processed_data_csv_file_name'],low_memory=False)
lat_long_data = pd.read_csv(config.CSV_FILE_PATH['location_file_path']+config.DATA_FILE_NAMES['location_data_csv_file_name'],low_memory=False)

# data['DateTime'] = pd.to_datetime(data['DateTime']).dt.strftime('%Y-%m-%d')
# data['MonthYear'] = pd.to_datetime(data['DateTime'])+MonthEnd(0)
data['MonthYear'] = pd.to_datetime(data['DateTime']).dt.strftime('%Y-%m')
# unique_dates = data['DateTime'].unique().tolist()
unique_months = data['MonthYear'].unique().tolist()
# # Define a route for the SWM bargraph endpoint.
# @router.get('/swm_bargraph', summary='SWM complaints across zones')
def bargraph(
        start_date: str = Query(..., description="Start date",enum=unique_months),
        end_date: str = Query(..., description="End date",enum=unique_months),
        page: int = Query(1, ge=1, description="Page number, starting from 1."),
        rows_per_page: int = Query(1000, ge=1, le=1000, description="Number of rows to fetch per page.")):
        # token: str = Depends(verify_token)):
    logger=setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])
    # setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])
    # logger = get_logger("swm_log_file")
    try:
        # Load the data from a CSV file into a DataFrame
        filtered_data = data[(data['MonthYear'] >= start_date) & (data['MonthYear'] <= end_date)]
        
        # df = pd.read_csv(config.CSV_FILE_PATH['upload_file_path']+config.DATA_FILE_NAMES['processed_data_csv_file_name'],parse_dates=['DateTime'])
        # Initialize the data processor with the DataFrame and column names.
        data_processor = SWM_Data_Visualization(filtered_data, 'Zone', 'Ward', 'Variable', 'Value')
        logging.info("Processing data to generate SWM bargraph...")

        # Process data to generate the  bargraph.
        df_zones,high_low_complaints=data_processor.SWM_bargraph_process_data()
        logging.info("SWM Bargraph data processing completed.")


        # Pagination
        total_rows = len(df_zones)
        total_pages = (total_rows + rows_per_page - 1) // rows_per_page
        start_index = (page - 1) * rows_per_page
        end_index = start_index + rows_per_page
        has_more_rows = end_index < total_rows
        processed_data_subset = df_zones.iloc[start_index:end_index].to_dict('records')

        if has_more_rows:
            result = {'swm_complaints_across_zones': processed_data_subset}
            result['current_page'] = f'page {page} of {total_pages} pages'
        else:
            result = {
                'swm_complaints_across_zones': processed_data_subset,
                'high_low_complaints': high_low_complaints
            }
            result['current_page'] = f'page {page} of {total_pages} pages'

        return result

        # Return a success message or any other required response.
        # return {
        #     "swm_complaints_across_zones": df_zones,
        #     "high_low_complaints": high_low_complaints,
        # }
    except Exception as e:
        # Log the error and return a 500 Internal Server Error with a detailed error message.
        logging.error(f"Exception occurred: {e}")
        raise HTTPException(status_code=500, detail=f"Exception occurred: {e}")

# @router.get('/swm_sunburst', summary='SWM sunburst graph')
def sunburst(
        start_date: str = Query(..., description="Start date",enum=unique_months),
        end_date: str = Query(..., description="End date",enum=unique_months)
        ):
    logger=setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])
    # setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])
    # logger = get_logger("swm_log_file")
    try:
        # Load the data from a CSV file into a DataFrame
        # df = pd.read_csv(config.CSV_FILE_PATH['upload_file_path']+config.DATA_FILE_NAMES['processed_data_csv_file_name'])
        filtered_data = data[(data['MonthYear'] >= start_date) & (data['MonthYear'] <= end_date)]
        print(filtered_data)
        # Initialize the data processor with the DataFrame and column names.
        data_processor = SWM_Data_Visualization(filtered_data, 'Zone', 'Ward', 'Variable', 'Value')
        logging.info("Processing data to generate SWM sunburst...")

        # Process data to generate the sunburst graph.
        sunburst_process_data=data_processor.sunburst_process_data()
        sunburst_graph=data_processor.sunburst_graph(sunburst_process_data)
        logging.info("SWM sunburst data processing completed.")


        # Return a success message or any other required response.
        return {"sunburst_graph":sunburst_graph}

    except Exception as e:
        # Log the error and return a 500 Internal Server Error with a detailed error message.
        logging.error(f"Exception occurred: {e}")
        raise HTTPException(status_code=500, detail=f"Exception occurred: {e}")
    
def swm_map_creation_data():
    logger=setup_logger(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])
    try:
        logging.info('Loading csv file')
        data_processor = SWM_Data_Visualization(data,'Zone', 'Ward', 'Variable', 'Value')
        logging.info("Processing swm map creation data...")
        processed_data = data_processor.map_creation_SWM(lat_long_data)
        logging.info("Processing of swm map creation data completed")
        return {'Number of open complaints':processed_data}
    except Exception as e:
        logging.exception(f"Exception occurred: {e}")
        raise HTTPException(status_code=500, detail=f"Exception occurred: {e}")
