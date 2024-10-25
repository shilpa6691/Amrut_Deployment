import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.ensemble import IsolationForest

class AnomalyDetection:
    def __init__(self,df,col):
        '''
        Initialize the AnomalyDetection class.
        Parameters:
            df: the cleaned dataframe of AHU
            col: column name as string
        '''
        self.df = df
        self.col = col
    def contamination_parameter_control_chart(self):
        col_mean = self.df[self.col].describe()['mean']
        col_std = self.df[self.col].describe()['std']
        ucl = col_mean + (3*col_std)
        lcl = col_mean - (3*col_std)
        anomalies = self.df.loc[(self.df[self.col] < lcl) | (self.df[self.col] > ucl)].index
        contamination_parameter = round((len(anomalies)/len(self.df)),4)
        return contamination_parameter
    def isolation_forest(self):
        column_df = self.df[["Time",self.col]]
        contamination_parameter = self.contamination_parameter_control_chart()
        model = IsolationForest(contamination=contamination_parameter,random_state=5)
        model.fit(column_df[[self.col]])
#         print(model.fit(column_df))
        column_df["Anomaly"] = pd.Series(model.predict(column_df[[self.col]]))
        column_df["Anomaly"]= column_df["Anomaly"].replace({1:'False', -1:'True'})
        # return pd.DataFrame(column_df["Anomaly"].value_counts())
        return column_df
