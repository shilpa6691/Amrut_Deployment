from fastapi import FastAPI
import uvicorn
# from ES.router import es_visualization,es_model_fitting,es_storing_csv_as_pickle,es_forecasting
# from SWM.router import swm_visualization,swm_model_fitting,swm_storing_csv_as_pickle,swm_forecasting
from v1.es import endpoints as es_endpoints
from v1.es_demo import endpoints as es_demo_endpoints
from v1.swm import endpoints as swm_endpoints
from v1.cctv import endpoints as cctv_endpoints
from v1.crime import endpoints as crime_endpoints
from v1.ahu import endpoints as ahu_endpoints
from v1.auth import endpoints as auth_endpoints
from logging.config import fileConfig
from utils.file_operations import *
import logging.config
from logging.handlers import RotatingFileHandler
import configparser
from datetime import datetime




# Create the FastAPI app instance
app = FastAPI()
# Include the routers in the app
# app.include_router(es_model_fitting.router)
# app.include_router(es_storing_csv_as_pickle.router)
# app.include_router(es_forecasting.router)
# app.include_router(es_visualization.router)
# app.include_router(swm_model_fitting.router)
# app.include_router(swm_storing_csv_as_pickle.router)
# app.include_router(swm_forecasting.router)
# app.include_router(swm_visualization.router)
# app.include_router(auth_endpoints.router)
app.include_router(es_endpoints.router)
# app.include_router(es_demo_endpoints.router)
# app.include_router(swm_endpoints.router)
# app.include_router(cctv_endpoints.router)
# app.include_router(crime_endpoints.router)
app.include_router(ahu_endpoints.router)



log_file_path = "/opt/siap/analytics/logs/"
log_file_name = datetime.now().strftime("uvicorn_log_file-%Y-%m-%d.log")

if not os.path.exists(log_file_path):
        os.makedirs(log_file_path)

config = configparser.ConfigParser()
config.read('uvicorn_config.ini')

# Update the args parameter in the handler section
config['handler_timed_rotating_file_handler']['args'] = f"('{log_file_path + log_file_name}', 'midnight', 1, 1, 'utf-8', True)"

# Save the updated configuration back to the file
with open('uvicorn_config.ini', 'w') as configfile:
    config.write(configfile)
# Run the FastAPI app using Uvicorn server
if __name__ == "__main__":
   uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level='info', log_config='uvicorn_config.ini',ssl_keyfile="/opt/siap/analytics/private.key",ssl_certfile="/opt/siap/analytics/certificate.crt")
