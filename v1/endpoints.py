from fastapi import APIRouter
from utils.file_operations import *
import os
from routers.usecases import *
from auth.authentication import *
from auth.authbearer import *


router = APIRouter()
router.get('/recovery_percentage_and_capacity_utilization',tags=['Data Visualization'], summary='Recovery_percentage:Indicates how much of the raw water input is successfully converted into treated water output.    Capacity_utilization:This metric is the ratio of the total treated water production in MLD to the design capacity of the WTP.',description='A higher recovery percentage suggests that the plant is optimizing the utilization of raw water resources and minimizing water losses during the treatment process. This metric is important for evaluating the plants operational efficiency and water conservation efforts. Capacity utilization indicates the extent to which the WTP is utilizing its designed capacity. This provides an insight into the operational efficiency of the plant.')(recovery_percentage_capacity_utilization)
# router.get('/capacity_utilization',tags=['Data Visualization'],summary='This metric is the ratio of the total treated water production in MLD to the design capacity of the WTP.',description='This metric indicates the extent to which the WTP is utilizing its designed capacity. This provides an insight into the operational efficiency of the plant.')(capacity_utilization)
router.get('/plant_availability',tags=['Data Visualization'], summary='The plant availability metric indicates how often the plant is available to perform its functions compared to the total time it could potentially operate.')(plant_availability)
router.get('/shift_and_zone_wise_water_production',tags=['Data Visualization'],summary='Shift_wise:An aggregate of treated water production during each shift helps the operator to understand the volume of raw water, treated water and clear water pumping flow during each shift. Zone_wise:Energy consumption across zones',description='Shift timings: Shift1 from 6 am to 2 pm, Shift 2 from 2 pm to 10 pm and Shift 3 from 10 pm to 6 pm.The 24-hour period is divided into three distinct zones, each with different energy rates. Zone 1 covers the time from 6 AM to 6 PM, Zone 2 spans from 6 PM to 10 PM, and Zone 3 from 10 PM to 6 AM')(shift_and_zone_wise_water_production)
# router.get('/water_demand_monthly_and_yearly',tags=['Data Visualization'],summary='The comparison of demand can be visualized for a desired time range (month on month, year on year)',description='The total volume of clear water pumped from treated sources reflects the water consumption by the Overhead Storage Tanks (OHSR). This water is then distributed to individual households, representing the overall demand for water.')(water_demand)
# router.get('/zone_wise_clear_water_pumping',tags=['Data Visualization'],summary='Energy consumption across zones',description='The 24-hour period is divided into three distinct zones, each with different energy rates. Zone 1 covers the time from 6 AM to 6 PM, Zone 2 spans from 6 PM to 10 PM, and Zone 3 from 10 PM to 6 AM')(zone_clear_water_pumping_flow)
router.get('/ebill_analysis',tags=['Data Visualization'],summary='Adding new columns to the kseb ebill data')(ebill_analysis)
router.get('/energy_meter_analysis',tags=['Data Visualization'])(energy_meter_analysis)
#router.post("/token",tags=['Authentication'])(login_for_access_token)

