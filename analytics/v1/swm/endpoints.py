# from swm.router.swm_model_fitting import *
# from swm.router.swm_storing_csv_as_pickle import *
# from swm.router.swm_forecasting import *
# from swm.router.swm_visualization import *
from fastapi import APIRouter
from utils.file_operations import *
from auth.authbearer import *
from auth.authentication import *
import os

# Retriving dir path to get the subsystem name
current_file_path = os.path.abspath(__file__)
subsystem_name = current_file_path.split(os.path.sep)[-2]

# Importing the respective files using the retrieved subsystem name
import_model_fitting = f"from {subsystem_name}.router.{subsystem_name}_model_fitting import *"
import_storing_csv = f"from {subsystem_name}.router.{subsystem_name}_storing_csv_as_pickle import *"
import_forecasting = f"from {subsystem_name}.router.{subsystem_name}_forecasting import *"
import_visualization = f"from {subsystem_name}.router.{subsystem_name}_visualization import *"
# import_visualization_pagination = f"from {subsystem_name}.router.es_visualization_pagination import *"
exec(import_model_fitting)
exec(import_storing_csv)
exec(import_forecasting)
exec(import_visualization)

router = APIRouter()#prefix='/swm_time_series_forecasting')


router.post(f'/{subsystem_name.upper()}_model_fitting',tags=[f'{subsystem_name.upper()} Time Series Forecasting'],summary='Model results and fitted model to pickle files')(model_fitting)
router.post(f'/{subsystem_name.upper()}_storing_csv_pickle',tags=[f'{subsystem_name.upper()} Time Series Forecasting'],summary='csv to pickle file')(swm_storing_csv_pickle)
router.get(f'/{subsystem_name.upper()}_forecasting',tags=[f'{subsystem_name.upper()} Time Series Forecasting'], summary='Forecasts the total complaints',description='Time series forecasting of complaints values weekly')(forecasting)
router.get(f'/{subsystem_name.upper()}_bargraph',tags=[f'{subsystem_name.upper()} Data Visualization'], summary='SWM complaints across zones')(bargraph)
router.get(f'/{subsystem_name.upper()}_sunburst', tags=[f'{subsystem_name.upper()} Data Visualization'], summary='SWM sunburst graph')(sunburst)
router.get(f'/{subsystem_name.upper()}_data_for_map',tags=[f'{subsystem_name.upper()} Data Visualization'], summary='Number of open complaints for map creation')(swm_map_creation_data)
