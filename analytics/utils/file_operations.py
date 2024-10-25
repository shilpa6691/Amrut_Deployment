import pickle
import logging
import os
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
from cryptography.fernet import Fernet
from io import BytesIO

def save_pickle_file(data, file_path, filename):
    """
    Save data as a pickle file.

    Parameters:
        data: The data to be saved in the pickle file.
        file_path: The path of the destination folder
        filename: The filename of the pickle file.

    This function saves the data as a pickle file with the specified filename.
    """
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    with open(file_path+filename, 'wb') as f:
        pickle.dump(data, f)

def load_pickle_file(filename):
    """
    Load data from a pickle file.

    Parameters:
        filename: The filename of the pickle file which contain the file path.

    Returns:
        The data loaded from the pickle file.

    This function loads data from a pickle file with the specified filename and returns it.
    """
    with open(filename, 'rb') as f:
        data = pickle.load(f)
    return data

# def setup_logger(log_file_path,log_file_name):
#     """
#     Function for setting up a logger.

#     Parameters:
#         log_file_path: The path of the destination folder
#         log_file_name: The filename of the log file.

#     Returns:
#         A logger instance.

#     This function creates and configures a logger instance that writes log messages to the specified log file.
#     The log messages are formatted with the timestamp, log level, and the log message itself.
#     The logger is set to log messages with a minimum level of DEBUG.
#     """
#     if not os.path.exists(log_file_path):
#         os.makedirs(log_file_path)
#     # Configure logging only if not already configured
#     logging.basicConfig(
#             filename=log_file_path+log_file_name,
#             level= logging.INFO,
#             format='%(asctime)s %(levelname)s %(message)s',
#             filemode='a',
#             datefmt='%d-%b-%y %H:%M:%S'
#         )
#     logger = logging.getLogger()
#     # logger.propagate = False
#     # logger.setLevel(logging.INFO)
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


# Method to split the values in a column with respect to a separator(ex: '.' , '_es', etc) 
# and returns the number of splits specified
def TagName_split(x,separator,n1):
    ''' Splitting the TagName column to different columns
        x: A series which should be in the form "dataframe_name['column_name']"
        separator: Optional. Specifies the separator to use when splitting the string. By default any whitespace is a separator
        n1: Specifies how many splits to do
    '''
    return x.str.split(pat=separator,n=n1,expand=True)


def Time_resampling_TS(df,group_col_list,datecol,window_size,agg_dict):#,method):
    ''' Resampling a time series with resample function to the preferred window size and reset the index.
        df: Name of the dataframe
        group_col_list: List of the columns for groupby function
        datecol: Name of the date column
        window_size: size of the time window like "H", "W", "D", "M", "MS"
        agg_dict: key-value pair of column name and its aggregate function as a dictionary. eg: {column:mean}
        method:method of filling the null values. eg:ffill,bfill etc.
    '''
    df_new = df.groupby(group_col_list).resample(window_size).agg(agg_dict)
    df_new = df_new.reset_index()
    df_new = df_new.set_index(datecol)
    # df_new = df_new.fillna(method=method,axis='rows')
    return df_new

def rename_col(df,dict_col):
    ''' Function for renaming a column.
        df: Name of the dataframe
        dict_col: dictionary of column names in which old name as key and new column name as value'''
    df = df.rename(columns=dict_col)
    return df


def remove_null_values(df):
        """
        Remove rows with null values from the dataframe.
        """
        return df.dropna(inplace=True)

def drop_columns(df,columns):
    """
    Drop specified columns from the dataframe.
    Parameters:
    columns: List of columns to drop.
    """
    return df.drop(columns, axis=1,inplace=True)

# Removing duplicates
def remove_duplicates(df):
    '''
    Remove duplicates from a DataFrame based on the specified columns.
    df: Name of the DataFrame.
    col_list: List of columns to consider for duplicate removal.
    '''
    return df.drop_duplicates(inplace=True)

def fill_null_values(df,columns, fill_value):
        """
        Fill null values in specified columns with a given fill value.
        Parameters:
        columns: List of columns to fill null values.
        fill_value: Value to fill null values (default is 'NoData')..
        """
        df[columns] = df[columns].fillna(fill_value)
        return df[columns]

# Decrypt a file
def file_decrypt(file_name,key):
    # using the key
    fernet = Fernet(key)

    # opening the encrypted file
    with open(file_name, 'rb') as enc_file:
        encrypted = enc_file.read()
 
    # decrypting the file
    decrypted_data = fernet.decrypt(encrypted)
    decrypted_file_object = BytesIO(decrypted_data)
    return decrypted_file_object