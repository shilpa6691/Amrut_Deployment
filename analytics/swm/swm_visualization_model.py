import pandas as pd
import datetime as dt
import numpy as np


class SWM_Data_Visualization:
    def __init__(self,df,base_col,first_col,second_col,value_col):
        #Initialize the SWM_Data_Visualization class with specified columns.
        ''' df: Name of the dataframe
            base_col: Name of the column whose values should come in the inner circle
            first_col: Name of the column whose values should come in the second circle
            second_col: Name of the column whose values should come in the third circle'
            value_col: Name of the column whose values should come in the outer circle
        '''
        self.df = df
        self.base_col = base_col
        self.first_col = first_col
        self.second_col = second_col
        self.value_col = value_col

    def sunburst_process_data(self):
        # Process data for sunburst visualization.
        self.df = self.df.sort_values('DateTime')
        self.df = self.df.reset_index(drop=True)

        self.df['Ward'] = self.df['Ward'].astype('str')
        data_zone_wotime = self.df.groupby(['Zone','Ward','Variable']).Value.last()
        data_zone_wotime = data_zone_wotime.reset_index()

        data_zone_wotime_wototal = data_zone_wotime[data_zone_wotime.Variable!='Complaint_Total']
        data_zone_wotime_wototal.reset_index(drop=True,inplace=True)
        data_zone_wotime_wototal['Ward'] = 'W_' + data_zone_wotime_wototal['Ward'].astype(str)

        return data_zone_wotime_wototal
    
    def sunburst_graph(self,df_cleaned):
        # Generate sunburst graph data.
        lst1 = df_cleaned[self.base_col].unique()

        sunburst_2 = []
        for i in lst1:
            sunburst_2.append({'id': i, 'parent': "", 'name': i})
            lst2=list(df_cleaned[df_cleaned[self.base_col]==i][self.first_col].unique())
            for j in lst2:
                sunburst_2.append({'id': '{}_{}'.format(j,i), 'parent': i, 'name': j})
                lst3=list(df_cleaned[(df_cleaned[self.base_col]==i) & (df_cleaned[self.first_col]==j)][self.second_col].unique())
                for k in lst3:
                    if df_cleaned[self.value_col].dtype == 'float64':
                        value=np.float64(df_cleaned[(df_cleaned[self.base_col]==i) & (df_cleaned[self.first_col]==j) & (df_cleaned[self.second_col]==k)][self.value_col]).round(3)
                    else:
                        value=int(df_cleaned[(df_cleaned[self.second_col]==k) & (df_cleaned[self.base_col]==i) & (df_cleaned[self.first_col]==j)][self.value_col])
                    sunburst_2.append({'id': k, 'parent': '{}_{}'.format(j,i), 'name': k , 'value':value })
        sunburst_2=str(sunburst_2)
        sunburst_2=sunburst_2.replace('[','{')
        sunburst_2=sunburst_2.replace(']','}')
        return sunburst_2

    
    def SWM_bargraph_process_data(self):
        # Process data for generating bar graphs related to SWM.
        # self.df['DateTime'] = self.df['DateTime'].dt.to_period('M').dt.to_timestamp('M')
        self.df = self.df.groupby(['MonthYear','Variable','Loc','Ward','Zone']).Value.last()
        self.df = self.df.reset_index()
        # self.df['Month & Year'] = pd.to_datetime(self.df['MonthYear']).dt.strftime('%B-%Y')
        # self.df = self.df[['MonthYear','Month & Year','Zone','Ward','Variable','Value']]
        self.df = self.df[['MonthYear','Zone','Ward','Variable','Value']]
        # df_pivot = self.df.pivot(index=['MonthYear','Month & Year','Zone','Ward'],columns='Variable',values='Value')
        df_pivot = self.df.pivot(index=['MonthYear','Zone','Ward'],columns='Variable',values='Value')
        df_pivot = df_pivot.reset_index()

        df_zones = df_pivot.rename(columns={'Complaint_Close': 'Closed Complaints','Complaint_Open':'Open Complaints',
                                    'Complaint_Total': 'Total Complaints'})

        df_zones = df_zones.groupby(['MonthYear','Zone']).agg({'Closed Complaints':sum,'Open Complaints':sum,'Total Complaints':sum})
        df_zones = df_zones.reset_index()
        df_zones['MonthYear'] = pd.to_datetime(df_zones['MonthYear']).dt.strftime('%B-%Y')
        # df_zones['Month & Year'] = df_zones['Month & Year'].astype('str')

        high_low_complaints = []
        for month_year in df_zones['MonthYear'].unique():
            month_data = df_zones[df_zones['MonthYear'] == month_year]

            highest_complaints_row = month_data[month_data['Total Complaints'] == month_data['Total Complaints'].max()]
            zone_highest_name = highest_complaints_row['Zone'].iloc[0]
            total_highest_complaints = int(highest_complaints_row['Total Complaints'].iloc[0])
            high_statement = f"In {month_year}, Zone {zone_highest_name} reported the highest number of complaints ({total_highest_complaints})"
            
            lowest_complaints_row = month_data[month_data['Total Complaints'] == month_data['Total Complaints'].min()]    
            zone_lowest_name = lowest_complaints_row['Zone'].iloc[0]    
            total_lowest_complaints = int(lowest_complaints_row['Total Complaints'].iloc[0])
            low_statement = f"In {month_year}, Zone {zone_lowest_name} reported the lowest number of complaints ({total_lowest_complaints})"
            
            high_low_complaints.append({
            "month": month_year,
            "highest_complaints": high_statement,
            "lowest_complaints": low_statement
        })

        
        # df_zones = df_zones.to_dict('records')
    
    # Create a list of text statements for each month
        return df_zones, high_low_complaints
    
    def map_creation_SWM(self,df_lat_long):
        data = self.df
        swm_open = data[data.Variable=='Complaint_Open']
        swm_open = swm_open.groupby(['Zone','Ward']).Value.last().reset_index()
        swm_open = swm_open.groupby('Zone').Value.sum().reset_index()
        swm_open = swm_open.rename(columns={'Value':'Complaint_Open'})
        swm_open = swm_open.merge(df_lat_long,on="Zone")
        swm_open = swm_open[['Zone','Latitude','Longitude','Complaint_Open']]

        swm_open = swm_open.to_dict('records')
        return swm_open


    
        


