# from es.router.es_model_fitting import *
# from es.router.es_storing_csv_as_pickle import *
# from es.router.es_forecasting import *
# from es.router.es_visualization import *
# from es.router.es_visualization_pagination import *
from fastapi import APIRouter
from utils.file_operations import *
import os

# Retriving dir path to get the subsystem name
current_file_path = os.path.abspath(__file__)
subsystem_name = current_file_path.split(os.path.sep)[-2]

# Importing the respective files using the retrieved subsystem name
import_model_fitting = f"from {subsystem_name}.router.es_model_fitting import *"
import_storing_csv = f"from {subsystem_name}.router.es_storing_csv_as_pickle import *"
import_forecasting = f"from {subsystem_name}.router.es_forecasting import *"
import_visualization = f"from {subsystem_name}.router.es_visualization import *"
# import_visualization_pagination = f"from {subsystem_name}.router.es_visualization_pagination import *"
exec(import_model_fitting)
exec(import_storing_csv)
exec(import_forecasting)
exec(import_visualization)
# exec(import_visualization_pagination)

router = APIRouter()

router.post(f'/{subsystem_name.upper()}_model_fitting',tags=[f'{subsystem_name.upper()} Time Series Forecasting'],summary='Model results and fitted model to pickle files')(model_fitting)
router.post(f'/{subsystem_name.upper()}_storing_csv_pickle',tags=[f'{subsystem_name.upper()} Time Series Forecasting'],summary='csv to pickle file')(es_storing_csv_pickle)
router.get(f'/{subsystem_name.upper()}_forecasting',tags=[f'{subsystem_name.upper()} Time Series Forecasting'], summary='Forecasts the AQI values',description='Time series forecasting of Aqi values weekly',response_description='Dictionary of actual,predicted and validation results')(forecasting)
router.get(f'/{subsystem_name.upper()}_aqi_classification',tags=[f'{subsystem_name.upper()} Data Visualization'],summary='AQI Heatmap location and zone wise (last week)')(aqi_location_and_zonewise_classification)
router.get(f'/{subsystem_name.upper()}_monthly_average_values_of_pollutants_and_aqi',tags=[f'{subsystem_name.upper()} Data Visualization'],summary='Monthly average value of 6 pollutants and AQI')(monthly_average_value_of_6_pollutants_and_aqi)
router.get(f'/{subsystem_name.upper()}_outlier',tags=[f'{subsystem_name.upper()} Data Visualization'], summary='location-wise outlier detection')(ids_vs_outlier)
router.get(f'/{subsystem_name.upper()}_pollutants_value_count',tags=[f'{subsystem_name.upper()} Data Visualization'], summary='Value counts classification of 6 pollutants')(daywise_valuecounts_for_pollutants)
router.get(f'/{subsystem_name.upper()}_data_for_map',tags=[f'{subsystem_name.upper()} Data Visualization'], summary='Latest value of AQIs for map creation')(aqi_map_creation_data)
# router.get(f'/{subsystem_name.upper()}_aqi_classification_with_pagination',tags=[f'{subsystem_name.upper()} Data Visualization Pagination'],summary='AQI Heatmap location and zone wise (last week)')(aqi_location_and_zonewise_classification_page)
# router.get(f'/{subsystem_name.upper()}_monthly_average_values_of_pollutants_and_aqi_with_pagination',tags=[f'{subsystem_name.upper()} Data Visualization Pagination'],summary='Monthly average value of 6 pollutants and AQI')(monthly_average_value_of_6_pollutants_and_aqi_page)
# router.get(f'/{subsystem_name.upper()}_outlier_with_pagination',tags=[f'{subsystem_name.upper()} Data Visualization Pagination'], summary='location-wise outlier detection')(ids_vs_outlier_page)
# router.get(f'/{subsystem_name.upper()}_pollutants_value_count_with_pagination',tags=[f'{subsystem_name.upper()} Data Visualization Pagination'], summary='Value counts classification of 6 pollutants')(daywise_valuecounts_for_pollutants_page)
# router.get(f'/{subsystem_name.upper()}_data_for_map_with_pagination',tags=[f'{subsystem_name.upper()} Data Visualization Pagination'], summary='Latest value of AQIs for map creation')(aqi_map_creation_data_page)
