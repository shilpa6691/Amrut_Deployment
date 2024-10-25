import pandas as pd
import datetime as dt
from utils.file_operations import *

 
class Data_Processing:

    def __init__(self):
        """
        Initialize the Data_Processing class.
        This constructor initializes the Time_Series_Forecasting class with the provided DataFrame, zone column, and zone name.
        """
        # self.data = data

    def cameras_count(self,data,column_list,column_list2,agg_dict,cctv_name):
        """
        Counting the number of cameras in each locations
        Returns:
            pd.DataFrame: The DataFrame containing number of cameras.
        """
        df_cam = data.groupby(column_list).agg(agg_dict).reset_index()
        df_cam = df_cam.groupby(column_list2).LocCam.sum().reset_index(name=cctv_name)
        return df_cam
    
    def faulty_cam_count(self,data,column_list,agg_dict,column_list2,cctv_name):
        """
        Counting the number of faulty cameras in each locations in each day
        Returns:
            pd.DataFrame: The DataFrame containing number of faulty cameras in each day.
        """
        faulty_cam_day = data[(data["Type"]=='StsCameraFaulty')].groupby(column_list).agg(agg_dict).reset_index()
        #print(faulty_cam_day.head())
        faulty_cam_day = faulty_cam_day[faulty_cam_day.Value==1.0].groupby(column_list2).LocCam.nunique().reset_index(name=cctv_name+'_faulty')
        # faulty_cam_day = faulty_cam_day.to_dict('records')
        return faulty_cam_day
    
    # Last month data
    def calculate_last_month_date(dataframe):
        """
        Get the last month data
        Returns:
            pd.DataFrame: The DataFrame containing the data of last one month.
        """
        last_date = dataframe['Date'].max() - dt.timedelta(days=31)
        return dataframe[dataframe['Date'] >= last_date]
    
    def calculate_faulty_percent(self,df_total_cam, df_faulty_cam, cctv_name):
        """
        Get the percentage of faulty cameras
        Returns:
            pd.DataFrame: The DataFrame containing the total number of cameras and the percentage of faulty cameras.
        """
        df_cam_percent = df_total_cam.merge(df_faulty_cam, how='outer')
        df_cam_percent.fillna(0, inplace=True)
        # for i in range(len(df_cam_percent)):
        #     largest_total = max(df_cam_percent)
        df_cam_percent[cctv_name+'_faulty_percent'] = ((df_cam_percent[cctv_name+'_faulty'] / df_cam_percent[cctv_name].expanding().max()) * 100).round(2)
        return df_cam_percent
    
    def events_captured(self,data,column_list,agg_dict,column_list2,cctv_name):
        """
        Get the number of events captured in each camera
        Returns:
            pd.DataFrame: The DataFrame containing the number of events captured in each type of camera.
        """
        events_data = data[(data.Type=='CameraEvent')].groupby(column_list).agg(agg_dict).reset_index()#.sort_values('Value',ascending=False).reset_index(drop=True)
        events_data = events_data.groupby(column_list2).Value.sum().reset_index(name=cctv_name+'_events')
        return events_data

