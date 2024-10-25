from cctv.router.cctv_visualization import *
from fastapi import APIRouter
from utils.file_operations import *

router = APIRouter()

router.get('/total_cameras',tags=['CCTV Visualization'],summary='The total number of cameras over a period of time')(total_number_of_cameras)
router.get('/total_cameras_Vs_faulty_cameras',tags=['CCTV Visualization'],summary='The total number of cameras and the percentage of faulty cameras over a period of time')(percentage_of_faulty_cameras_per_day)
router.get('/faulty_cameras_per_day',tags=['CCTV Visualization'],summary='The number of faulty cameras each day')(faulty_cam_per_day)
router.get('/events_captured_per_day',tags=['CCTV Visualization'],summary='The number of events captured each day')(events_per_day)
router.get('/events_captured_over_time_of_day',tags=['CCTV Visualization'],summary='The number of events captured versus time of day')(events_Vs_time_of_the_day)
