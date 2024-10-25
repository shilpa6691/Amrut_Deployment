import logging
import os
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

# Create and configure logger
# def log_file_setup():
#     logging.basicConfig(filename="logs/log_testing.log",
#                     format='%(asctime)s-%(levelname)s-%(message)s',
#                     datefmt='%d-%b-%y %H:%M:%S',
#                     filemode='w')
# # Creating an object
#     logger = logging.getLogger()
# # Setting the threshold of logger to DEBUG
#     logger.setLevel(logging.DEBUG)
#     return logger

def setup_logger(log_file_path,log_file_name):
    
    """
    Function for setting up a logger with date-wise rotation.

    Parameters:
        log_filepath: The base filename of the log file.

    Returns:
        A logger instance.

    This function creates and configures a logger instance that writes log messages to a rotating log file.
    The log messages are formatted with the timestamp, log level, and the log message itself.
    The logger is set to log messages with a minimum level of DEBUG.
    """

    if not os.path.exists(log_file_path):
        os.makedirs(log_file_path)
    # Define the log file path with date-wise rotation
    # log_filepath_with_date =  os.path.join(log_file_path+log_file_name)
    log_filepath_with_date =  os.path.join(log_file_path+datetime.now().strftime(log_file_name+"_%Y_%m_%d.log"))
    # Create a rotating file handler
    handler = TimedRotatingFileHandler(
        filename=log_filepath_with_date,
        when="midnight",  # Rotate daily
        interval=1,        # One day interval
        backupCount=0,     # Keep logs for 0 days (remove logs after one day)
        encoding="utf-8",
        delay=True
    )

    # Set the log format
    formatter = logging.Formatter('%(asctime)s %(levelname)s [%(filename)s] %(message)s', datefmt='%d-%b-%y %H:%M:%S')
    handler.setFormatter(formatter)

    # Create and configure the logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # Set the logger level to the lowest level you want to log

    # Clear existing handlers to avoid duplicate logs when re-running the script
    logger.handlers.clear()
    # Add the handler to the logger
    logger.addHandler(handler)

    return logger





def time_resample(df,window,agg_dict):
        ''' Resampling a time series with resample function to the preferred window size.
        df: Name of the dataframe
        window_size: size of the time window like "H", "W", "D", "M", "MS"
        agg_dict: key-value pair of column name and its aggregate function as a dictionary. eg: {column:mean}
        '''
        data = df.resample(window).agg(agg_dict)
        return data