import pandas as pd
import datetime as dt

class ES_Data_Visualization:
    def __init__(self, data_ES):
        # Initialize the data processor with a CSV file containing pollutant data.
        self.data_ES = data_ES
        self.pollutants = ['PM10', 'PM25', 'SO2', 'CO', 'O3', 'NO2']

    def calculate_aqi_class(self,aqi_value):
        # Determine the AQI class based on the AQI value.
            if aqi_value <= 50:
                return "Good"
            elif aqi_value <= 100:
                return "Satisfactory"
            elif aqi_value <= 200:
                return "Moderate"
            elif aqi_value <= 300:
                return "Poor"
            elif aqi_value <= 400:
                return "Severe"
            else:
                return "Hazardous"  

    def classify_pollutant(self, row, pollutant_name):  
        # Classify the pollutant based on its concentration.
        concentration = row[pollutant_name] 

        if pollutant_name == "PM10":
            if concentration <= 50 and concentration >= 0:
                return "Good"
            elif concentration <= 100:
                return "Satisfactory"
            elif concentration <= 250:
                return "Moderate"
            elif concentration <= 350:
                return "Poor"
            elif concentration <= 430:
                return "Severe"
            else:
                return "Hazardous"

        elif pollutant_name == "PM25":
            if concentration <= 30 and concentration >= 0:
                return "Good"
            elif concentration <= 60:
                return "Satisfactory"
            elif concentration <= 90:
                return "Moderate"
            elif concentration <= 120:
                return "Poor"
            elif concentration <= 250:
                return "Severe"
            else:
                return "Hazardous"

        elif pollutant_name == "SO2":
            if concentration <= 40 and concentration >= 0:
                return "Good"
            elif concentration <= 80:
                return "Satisfactory"
            elif concentration <= 380:
                return "Moderate"
            elif concentration <= 800:
                return "Poor"
            elif concentration <= 1600:
                return "Severe"
            else:
                return "Hazardous"

        elif pollutant_name == "CO":
            if concentration <= 1.0 and concentration >= 0:
                return "Good"
            elif concentration <= 2.0:
                return "Satisfactory"
            elif concentration <= 10:
                return "Moderate"
            elif concentration <= 17:
                return "Poor"
            elif concentration <= 34:
                return "Severe"
            else:
                return "Hazardous"

        elif pollutant_name == "O3":
            if concentration <= 50 and concentration >= 0:
                return "Good"
            elif concentration <= 100:
                return "Satisfactory"
            elif concentration <= 250:
                return "Moderate"
            elif concentration <= 350:
                return "Poor"
            elif concentration <= 430:
                return "Severe"
            else:
                return "Hazardous"

        elif pollutant_name == "NO2":
            if concentration <= 40 and concentration >= 0:
                return "Good"
            elif concentration <= 80:
                return "Satisfactory"
            elif concentration <= 180:
                return "Moderate"
            elif concentration <= 280:
                return "Poor"
            elif concentration <= 400:
                return "Severe"
            else:
                return "Hazardous"
    
    def df_to_TS(self,df,datecol):
        # Convert a DataFrame to time series format based on the date column.
        df[datecol] = pd.to_datetime(df[datecol])
        df = df.set_index(datecol)
        return df

    def Time_resampling_TS(self,df,group_col_list,datecol,window_size,agg_dict):
        # Resample time series data based on specified columns and aggregation rules.
        df_new = df.groupby(group_col_list).resample(window_size).agg(agg_dict).round(2)
        df_new = df_new.reset_index()
        df_new = df_new.set_index(datecol)
        return df_new

    def location_and_zonewise_aqi_classifier(self):
        # Process data for generating a heatmap.
        self.data_ES['DateTime'] = pd.to_datetime(self.data_ES['DateTime'])
        range_max = self.data_ES['DateTime'].max()
        range_min = range_max - dt.timedelta(days=7)
        data_ES_lastweek = self.data_ES[self.data_ES.DateTime >= range_min]
        data_ES_lastweek = data_ES_lastweek.sort_values('DateTime')
        
        if 'Zone' in self.data_ES.columns:
            data_zone_aqi = data_ES_lastweek.groupby('Zone').agg({'AQI': 'last'})
            data_zone_aqi["AQI_Class"] = [self.calculate_aqi_class(aqi) for aqi in data_zone_aqi['AQI']]
            data_zone_aqi = data_zone_aqi.reset_index()
            # final_data_zone_aqi = data_zone_aqi.to_dict('records')

            data_loc_aqi = data_ES_lastweek.groupby(['id', 'Location']).agg({'AQI': 'last'})
            data_loc_aqi = data_loc_aqi.reset_index()
            data_loc_aqi["AQI_Class"] = [self.calculate_aqi_class(aqi) for aqi in data_loc_aqi['AQI']]
            # print(data_loc_aqi.shape)
            # final_data_loc_aqi = data_loc_aqi.to_dict('records')
            # return {'aqi_zonewise_classification':final_data_zone_aqi,'aqi_locationwise_classification':final_data_loc_aqi}
            return data_zone_aqi,data_loc_aqi
        else:
            data_loc_aqi = data_ES_lastweek.groupby(['id', 'Location']).agg({'AQI': 'last'})
            data_loc_aqi = data_loc_aqi.reset_index()
            data_loc_aqi["AQI_Class"] = [self.calculate_aqi_class(aqi) for aqi in data_loc_aqi['AQI']]
            # final_data_loc_aqi = data_loc_aqi.to_dict('records')
            # return {'aqi_locationwise_classification':final_data_loc_aqi}
            return data_loc_aqi

    def pollutants_valuecount_classifier(self,pollutant):
        # Process data for generating pie charts for pollutants.
        # pollutants = ['PM10', 'PM25', 'SO2', 'CO', 'O3', 'NO2']
        # for pollutant in pollutants:
        data = self.data_ES[['DateTime', 'id', pollutant]]
        data[f'{pollutant}_Class'] = data.apply(lambda row: self.classify_pollutant(row, pollutant), axis=1)
        data['DateTime'] = pd.to_datetime(data['DateTime']).dt.date
        
        data_pie = data.groupby('DateTime').agg({f'{pollutant}_Class': 'value_counts'})
        data_pie = data_pie.rename(columns={f'{pollutant}_Class': 'value_counts'}).reset_index()
        
        data_pivot = data_pie.pivot(index='DateTime', columns=f'{pollutant}_Class', values='value_counts')
        data_pivot = data_pivot.fillna(0).reset_index()
        pollutant_class_list = ["Good","Satisfactory","Moderate","Poor","Severe","Hazardous"]
        for i in pollutant_class_list:
            if i not in data_pivot.columns:
                data_pivot[i] = 0
        data_pivot['DateTime'] = data_pivot['DateTime'].astype('str')
        # data_pivot = data_pivot.to_dict('records')
        return data_pivot
        
        
    
    def average_value_of_variables(self):
        
         # Process data for generating bar graphs for pollutants and AQI.
        data_ES_avg = self.df_to_TS(self.data_ES,'DateTime')
        if 'Zone' in self.data_ES.columns:
            data_ES_avg = self.Time_resampling_TS(data_ES_avg,['id','Location','Area','Zone','Ward'],'DateTime','M',{'CO':'mean','NO2':'mean','O3':'mean','PM25':'mean',
                                                                    'PM10':'mean','SO2':'mean'})
        else:
            data_ES_avg = self.Time_resampling_TS(data_ES_avg,['id','Location'],'DateTime','M',{'CO':'mean','NO2':'mean','O3':'mean','PM25':'mean',
                                                                    'PM10':'mean','SO2':'mean'})
        data_ES_avg = data_ES_avg.reset_index()

        data_ES_avg = data_ES_avg[data_ES_avg.CO.notna()]
        data_ES_avg['PM25'].fillna(method='ffill',inplace=True)
        data_ES_avg['PM10'].fillna(method='ffill',inplace=True)
        data_ES_avg['SO2'].fillna(method='ffill',inplace=True)
        data_ES_avg['CO'].fillna(method='ffill',inplace=True)
        data_ES_avg['NO2'].fillna(method='ffill',inplace=True)
        data_ES_avg['O3'].fillna(method='ffill',inplace=True)
        
        df_id_pollutants = data_ES_avg[['DateTime','id','Location','PM25', 'PM10', 'SO2', 'CO', 'NO2', 'O3']]
        df_id_pollutants['DateTime'] = pd.to_datetime(df_id_pollutants['DateTime']).dt.strftime('%B-%Y')
        df_id_pollutants['DateTime'] = df_id_pollutants['DateTime'].astype('str')
        # df_id_pollutants = df_id_pollutants.to_dict('records')

        data_aqi_avg = self.df_to_TS(self.data_ES,'DateTime')
        if 'Zone' in self.data_ES.columns:
            data_aqi_avg = self.Time_resampling_TS(data_aqi_avg,['id','Location','Area','Zone','Ward'],'DateTime','M',{'AQI':'mean'})
        else:
            data_aqi_avg = self.Time_resampling_TS(data_aqi_avg,['id','Location'],'DateTime','M',{'AQI':'mean'})
        data_aqi_avg = data_aqi_avg.reset_index()
        data_aqi_avg = data_aqi_avg[data_aqi_avg['AQI'].notna()]
        data_aqi_avg['AQI'].fillna(method='ffill',inplace=True)

        df_id_aqi = data_aqi_avg[['DateTime','id','Location','AQI']]
        df_id_aqi["AQI_Class"] = [self.calculate_aqi_class(aqi) for aqi in df_id_aqi['AQI']]
        df_id_aqi.reset_index(inplace=True, drop=True)
        df_id_aqi['DateTime'] = pd.to_datetime(df_id_aqi['DateTime']).dt.strftime('%B-%Y')
        df_id_aqi['DateTime'] = df_id_aqi['DateTime'].astype('str')
        # df_id_aqi = df_id_aqi.to_dict('records')
        return df_id_aqi,df_id_pollutants
        # return {'pollutants_concentration_vs_id':df_id_pollutants,'aqi_vs_id':df_id_aqi}

    def outlier_detection(self,df_assetloc):

        self.data_ES['DateTime'] = pd.to_datetime(self.data_ES['DateTime'])
        
        self.data_ES = self.data_ES.sort_values('DateTime')
        # Process data to identify and count outliers based on pollutant concentrations.
        pm10 = self.data_ES[self.data_ES['PM10']>=500]['id'].value_counts()
        pm10_out = pm10.to_frame().reset_index().rename(columns={'id':'Loc id','count':'PM10'})
        pm25 = self.data_ES[self.data_ES['PM25']>=500]['id'].value_counts()
        PM25_out = pm25.to_frame().reset_index().rename(columns={'id':'Loc id','count':'PM25'})
        SO2 = self.data_ES[self.data_ES.SO2>=2000].id.value_counts()
        SO2_out = SO2.to_frame().reset_index().rename(columns={'id':'Loc id','count':'SO2'})
        NO2 = self.data_ES[self.data_ES['NO2']>=600]['id'].value_counts()
        NO2_out = NO2.to_frame().reset_index().rename(columns={'id':'Loc id','count':'NO2'})
        CO = self.data_ES[self.data_ES['CO']>=35]['id'].value_counts()
        CO_out = CO.to_frame().reset_index().rename(columns={'id':'Loc id','count':'CO'})
        O3 = self.data_ES[self.data_ES['O3']>=900]['id'].value_counts()
        O3_out = O3.to_frame().reset_index().rename(columns={'id':'Loc id','count':'O3'})
        aqi = self.data_ES[self.data_ES['AQI']>=500]['id'].value_counts()
        aqi_out = aqi.to_frame().reset_index().rename(columns={'id':'Loc id','count':'AQI'})

        value_count_data = PM25_out.merge(pm10_out,on='Loc id',how='outer')
        value_count_data = value_count_data.merge(SO2_out,on='Loc id',how='outer')
        value_count_data = value_count_data.merge(CO_out,on='Loc id',how='outer')
        value_count_data = value_count_data.merge(NO2_out,on='Loc id',how='outer')
        value_count_data = value_count_data.merge(O3_out,on='Loc id',how='outer')
        value_count_data = value_count_data.merge(aqi_out,on='Loc id',how='outer')
        value_count_data = value_count_data.fillna(0)
         

        outliers_list = list(value_count_data['Loc id'].unique())
        all_id = list(self.data_ES.id.unique())
        a = []
        for i in all_id:
            if i not in outliers_list:
                a.append(i)
        data_new = pd.DataFrame({'Loc id':a, 'PM25':0.0,'PM10':0.0,'SO2':0.0,'CO':0.0,'NO2':0.0,'O3':0.0,'AQI':0.0})
        if value_count_data.empty:
            value_count_data = data_new
        else:
            value_count_data = pd.concat([value_count_data,data_new],axis=0,join='outer')
        
        value_count_data_new = value_count_data.reset_index(drop=True)
        value_count_data_new['Total No.of Outliers'] = value_count_data_new.sum(axis=1,numeric_only=True)
        value_count_data_new = value_count_data_new.sort_values(by='Total No.of Outliers')

        value_count_data_new =df_assetloc.merge(value_count_data_new,on='Loc id')
        value_count_data_new = value_count_data_new[value_count_data_new.Location !='Durga Devi Park_Nigdi']

        return value_count_data_new
    
    def map_creation_AQI(self):
        data = self.data_ES
        # print(data.head(2))
        data['DateTime'] = pd.to_datetime(data['DateTime']).dt.date
        # print(data.head(1))
        last_date = data['DateTime'].max()
        days_start_31 = last_date - dt.timedelta(days=31)
        # print(days_start_31)
        data = data[data['DateTime'] >= days_start_31]
        if 'Zone' in self.data_ES.columns:
            aqi_current_values = data.groupby(['id','Latitude','Longitude','Location','Zone','Ward']).AQI.last()
        else:
            aqi_current_values = data.groupby(['id','Location']).AQI.last().round(2)
        aqi_current_values = aqi_current_values.reset_index()
        # aqi_current_values = aqi_current_values.to_dict('records')
        return aqi_current_values
    

