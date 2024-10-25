from fastapi import APIRouter
from utils.file_operations import *
import os

# Retriving dir path to get the subsystem name
current_file_path = os.path.abspath(__file__)
subsystem_name = current_file_path.split(os.path.sep)[-2]

import_anomaly_detection = f"from {subsystem_name}.router.{subsystem_name}_anomaly_detection import *"
exec(import_anomaly_detection)

router = APIRouter()

router.post(f'/{subsystem_name.upper()}_RA_Temp_Anomaly_Detection',tags=[f'{subsystem_name.upper()}'])(RA_temp_anomaly_detection)
