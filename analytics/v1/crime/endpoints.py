from crime.router.crime_analysis import *
from crime.router.crime_model_fitting import *
from crime.router.crime_forecasting import *
from crime.router.crime_singapore_model_fitting import *
from crime.router.crime_singapore_forecasting import *
from crime.router.crime_analysis_singapore import *
from fastapi import APIRouter


router = APIRouter()

router.get('/monthly_count_of_crimes_locationwise',tags=['Crime Data Visualization Las Vegas'],summary='count of crimes monthwise')(monthly_total_crimes)
router.get('/yearly_count_of_crimes_locationwise',tags=['Crime Data Visualization Las Vegas'],summary='count of crimes yearwise')(yearly_total_crimes)
router.get('/hotspot_detection_of_crimes',tags=['Crime Data Visualization Las Vegas'],summary='Crime counts based on latitude and longitude',description='Finding the latitude and longitude of most occured crimes')(spatial_distribution_of_crimes)
# router.get('/relationship_between_no_of_beats_and_crime_rates',tags=['Crime Data Visualization Las Vegas'],summary='Checking if there is any relationship between no of beats and crime_rates',description='This api finds out the relation between no of beats and crime counts. If the no of beats in a location increases crime count decreases and vice versa')(number_of_crimes_in_beats)
router.get('/classification_of_crimes_based_on_severity',tags=['Crime Data Visualization Las Vegas'],summary='classification of crimes into 5 different categories',description='This api classifies the crime types into 5 different categories based on the severity of the crime')(severity_of_the_crime)
router.get('/time_and_location_at_which_accidents_happen_the_most',tags=['Crime Data Visualization Las Vegas'],summary='Finding when and where the accidents happened most',description='This api finds when and where the accidents happen the most so that actions can taken to reduce the accidents in that area')(time_of_the_accidents)
router.get('/yearwise_total_crime_rate',tags=['Crime Data Visualization Las Vegas'],summary='Finding the crime rate based on total count of each crime types and the population of every year',description='This api gives a statistical record of the crime rates happened each year based on the total counts of each type of the crimes and population of each year')(crime_rate_statistics)
router.get('/effect_of_cctv_and_streetlight',tags=['Crime Data Visualization Las Vegas'],summary='Checking if the no of cctv and streetlights affecting the crime counts',description='This api finds if the no of cctv and streetlights in a particular area increases crime count decreases')(cctv_streetlight_vs_crime_count)
router.get('/comparison_of_crimes_in_2_cities',tags=['Crime Data Visualization Las Vegas'],summary='Comparing the crime rates of 2 cities',description='This api is comparing the crime counts of Las vegas and san francisco and analysing the most crime count city')(Las_vegas_and_San_francisco_crime_trends)
router.post('/model_fitting_ward_wise',tags=['CRIME Time Series Forecasting Las Vegas'],summary='Model results and fitted model to pickle files')(model_fitting_ward_wise)
router.get('/forecasting_ward_wise',tags=['CRIME Time Series Forecasting Las Vegas'], summary='Forecasts the crime counts based on wards',description='Time series forecasting of crime counts of different wards weekly',response_description='Dictionary of actual,predicted and validation results')(forecasting_ward_wise)
router.post('/model_fitting_crime_type_wise',tags=['CRIME Time Series Forecasting Las Vegas'],summary='Model results and fitted model to pickle files')(model_fitting_crime_type_wise)
router.get('/forecasting_crime_type_wise',tags=['CRIME Time Series Forecasting Las Vegas'], summary='Forecasts the crime counts based on crime types',description='Time series forecasting of top 10 crime types weekly',response_description='Dictionary of actual,predicted and validation results')(forecasting_crime_type_wise)
router.post('/model_fitting_crime_type_and_wardwise',tags=['CRIME Time Series Forecasting Las Vegas'],summary='Model results and fitted model to pickle files')(model_fitting_crime_type_and_wardwise)
router.get('/forecasting_crime_type_and_wardwise',tags=['CRIME Time Series Forecasting Las Vegas'], summary='Forecasts the crime counts based on crime types and wardwise',description='Time series forecasting of top 10 crime types and each wards weekly',response_description='Dictionary of actual,predicted and validation results')(forecasting_crime_type_and_wardwise)

router.get('/wardwise_monthly_count_of_crimes',tags=['Crime Data Visualization Singapore'],summary='count of crimes wardwise')(singapore_monthly_total_crimes)
router.get('/spatial_distribution_of_crimes',tags=['Crime Data Visualization Singapore'],summary='Crime counts based on latitude and longitude',description='Finding the latitude and longitude of most occured crimes')(singapore_spatial_distribution_of_crimes)
router.post('/model_fitting_singapore_wardwise',tags=['CRIME Time Series Forecasting Singapore'],summary='Model results and fitted model to pickle files')(singapore_model_fitting_ward_wise)
router.get('/forecasting_singapore_wardwise',tags=['CRIME Time Series Forecasting Singapore'], summary='Forecasts the crime counts based on wardwise',description='Time series forecasting of each wards weekly',response_description='Dictionary of actual,predicted and validation results')(singapore_forecasting_ward_wise)


