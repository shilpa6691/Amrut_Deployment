import pandas as pd
import numpy as np
from utils.file_operations import *
import config

logger = log_file_setup(config.LOG_FILE_PATH['analytics_logs_path'],config.LOG_FILE_PATH['analytics_logs_name'])

class Analysis:
    def __init__(self,data):
        self.data = data

    def plant_availability(self,remarks_category):
        if remarks_category == 'No remarks':
            return True
        else:
            return False
        
    def plant_availabilty_dataframe(self):
        data = self.data
        data['plant status'] = data['remarks category'].apply(self.plant_availability)
        data = data.reset_index()
        data['Standardized_Date'] = data['Standardized_Date'].astype('str')
        data.to_json(config.JSON_FILE_PATH['upload_file_path']+'plant_status.json',orient='records')
        print(data.head())
        data = data.to_dict('records')
        return data
    
    def monthly_plant_availabilty_dataframe(self):
        data = self.data
        data['plant status'] = data['remarks category'].apply(self.plant_availability)
        monthly_dataframe = time_resample(data,'ME',{'RAW WATER FLOW IN ML':'sum',
                                   'CLEAR WATER SUMP LEVEL IN Meter':'mean',
                                   'CLEAR WATER PUMPING FLOW ML':'sum',
                                   'TREATED WATER PRODUCTION IN ML':'sum',
                                   'remarks category':'unique',
                                    'plant status':'sum'})
        monthly_dataframe.rename(columns={'plant status':'No_of_hours_of_operation'},inplace=True)
        monthly_dataframe['remarks category'] = monthly_dataframe['remarks category'].apply(lambda x: list(x))
        monthly_dataframe = monthly_dataframe.reset_index()
        monthly_dataframe['total_hours'] = (monthly_dataframe['Standardized_Date'].dt.days_in_month)*24
        monthly_dataframe['plant_availability'] = monthly_dataframe['No_of_hours_of_operation'] / monthly_dataframe['total_hours']
        monthly_dataframe['Standardized_Date'] = monthly_dataframe['Standardized_Date'].astype('str')
        monthly_dataframe.to_json(config.JSON_FILE_PATH['upload_file_path']+'monthly_plant_availability.json',orient='records')
        logger.info(monthly_dataframe.head())
        monthly_dataframe = monthly_dataframe.to_dict('records')
        return monthly_dataframe
 
    def recovery_percentage_capacity_utilization_finder(self):
        data=self.data
        data_day = time_resample(data,'D',{'RAW WATER FLOW IN ML':'sum',
                                   'CLEAR WATER SUMP LEVEL IN Meter':'mean',
                                   'CLEAR WATER PUMPING FLOW ML':'sum',
                                   'TREATED WATER PRODUCTION IN ML':'sum', 'remarks category':'unique'})
        data_day['remarks category'] = data_day['remarks category'].apply(lambda x: list(x))
        data_day['Recovery_percentage'] = ((data_day['TREATED WATER PRODUCTION IN ML']/data_day['RAW WATER FLOW IN ML'])*100).round(2)
        data_day['Recovery_percentage'] = data_day['Recovery_percentage'].fillna(0.0)
        data_day['Capacity_utilization'] = ((data_day['TREATED WATER PRODUCTION IN ML']/93)*100).round(2)
        data_day=data_day.reset_index()
        data_day['Standardized_Date'] = data_day['Standardized_Date'].astype('str')
        data_day.to_json(config.JSON_FILE_PATH['upload_file_path']+'recovery_percentage_and_capacity_utilization.json',orient='records')
        data_day = data_day.to_dict('records')
        return data_day
    
    def assign_shift(self,hour):
        if 6 <= hour < 14:
            return '1'
        elif 14 <= hour < 22:
            return '2'
        else:
            return '3'
        
    def assign_zone(self,hour):
        if 6 <= hour < 18:
            return 'Z1'
        elif 18 <= hour < 22:
            return 'Z2'
        else:
            return 'Z3'

    def shift_zone_data_calculator(self):
        data = self.data
        data['Hour'] = pd.to_datetime(data['STANDARDIZED_TIME']).dt.hour
        data['Shift'] = data['Hour'].apply(self.assign_shift)
        data['Zone'] = data['Hour'].apply(self.assign_zone)
        # shift_data = groupby_time_resample(data,['Shift'],'D',{'RAW WATER FLOW IN ML':'sum',
        #                            'CLEAR WATER PUMPING FLOW ML':'sum',
        #                            'TREATED WATER PRODUCTION IN ML':'sum',
        #                            'remarks category':lambda x: x.unique()}).reset_index()
        # data['remarks category'] = data['remarks category'].apply(lambda x: list(x))
        logger.info(data.head)
        # shift_data = shift_data[['Standardized_Date','Shift','RAW WATER FLOW IN ML',
        #                            'CLEAR WATER PUMPING FLOW ML',
        #                            'TREATED WATER PRODUCTION IN ML',
        #                            'remarks category']].sort_values(['Standardized_Date','Shift']).reset_index(drop=True)
        data = data.reset_index()
        data = data[data['Standardized_Date']>='2024-06-01']
        data['Standardized_Date'] = data['Standardized_Date'].astype('str')
        data.to_json(config.JSON_FILE_PATH['upload_file_path']+'data_with_shift_and_zone.json',orient='records')
        logger.info(data.head())
        data = data.to_dict('records')
        return data
    
    def ebill_calculator(self,ebill_data):
        data = self.data
        data['Hour'] = pd.to_datetime(data['STANDARDIZED_TIME']).dt.hour
        data['Zone'] = data['Hour'].apply(self.assign_zone)
        zone_data = groupby_time_resample(data,['Zone'],'ME',{'RAW WATER FLOW IN ML':'sum',
                                   'CLEAR WATER PUMPING FLOW ML':'sum',
                                   'TREATED WATER PRODUCTION IN ML':'sum',
                                   'remarks category':lambda x: x.unique()}).reset_index()
        zone_data['remarks category'] = zone_data['remarks category'].apply(lambda x: list(x))
        zone_data_pivot = zone_data.pivot(index='Standardized_Date',columns=['Zone'],values=['RAW WATER FLOW IN ML','CLEAR WATER PUMPING FLOW ML','TREATED WATER PRODUCTION IN ML','remarks category'])
        # Flatten the MultiIndex columns except for 'Standardized_Date'
        zone_data_pivot.columns = [
            '_'.join(col).strip() if isinstance(col, tuple) else col for col in zone_data_pivot.columns
        ]

        # Optionally, replace spaces with underscores for easier access
        zone_data_pivot.columns = [col.replace(' ', '_') for col in zone_data_pivot.columns]

        merged_data = zone_data_pivot.merge(ebill_data,on='Standardized_Date')
        merged_data['Month-Year'] = merged_data['Standardized_Date'].dt.strftime('%m-%Y')
        # Convert columns to numeric and handle any non-numeric values
        merged_data['Units_kWh'] = pd.to_numeric(merged_data['Units_kWh'], errors='coerce')
        merged_data['TREATED_WATER_PRODUCTION_IN_ML_Z1'] = pd.to_numeric(merged_data['TREATED_WATER_PRODUCTION_IN_ML_Z1'], errors='coerce')
        merged_data['TREATED_WATER_PRODUCTION_IN_ML_Z2'] = pd.to_numeric(merged_data['TREATED_WATER_PRODUCTION_IN_ML_Z2'], errors='coerce')
        merged_data['TREATED_WATER_PRODUCTION_IN_ML_Z3'] = pd.to_numeric(merged_data['TREATED_WATER_PRODUCTION_IN_ML_Z3'], errors='coerce')

        # Replace NaN values with 0 for water production columns to ensure valid calculation
        merged_data[['TREATED_WATER_PRODUCTION_IN_ML_Z1', 'TREATED_WATER_PRODUCTION_IN_ML_Z2', 'TREATED_WATER_PRODUCTION_IN_ML_Z3']] = merged_data[['TREATED_WATER_PRODUCTION_IN_ML_Z1', 'TREATED_WATER_PRODUCTION_IN_ML_Z2', 'TREATED_WATER_PRODUCTION_IN_ML_Z3']].fillna(0)

        # Perform the specific energy consumption calculation and round to 2 decimal places
        merged_data['specific_energy_consumption'] = (
            merged_data['Units_kWh'] / (
                merged_data['TREATED_WATER_PRODUCTION_IN_ML_Z1'] +
                merged_data['TREATED_WATER_PRODUCTION_IN_ML_Z2'] +
                merged_data['TREATED_WATER_PRODUCTION_IN_ML_Z3']
            )
        ).round(2)
        merged_data['charge_per_unit'] = merged_data['Energy Charge (Rs)']/ merged_data['Units_kWh']
        merged_data['unit_cost'] = (merged_data['Energy Charge (Rs)']/(
                merged_data['TREATED_WATER_PRODUCTION_IN_ML_Z1'] +
                merged_data['TREATED_WATER_PRODUCTION_IN_ML_Z2'] +
                merged_data['TREATED_WATER_PRODUCTION_IN_ML_Z3']
            )).round(2)
        merged_data['RAW_WATER_FLOW_IN_ML_Z1'] = merged_data['RAW_WATER_FLOW_IN_ML_Z1'].astype(float)
        merged_data['RAW_WATER_FLOW_IN_ML_Z2'] = merged_data['RAW_WATER_FLOW_IN_ML_Z2'].astype(float)
        merged_data['RAW_WATER_FLOW_IN_ML_Z3'] = merged_data['RAW_WATER_FLOW_IN_ML_Z3'].astype(float)
        # merged_data['CLEAR WATER SUMP LEVEL IN Meter_Z1'] = merged_data['CLEAR WATER SUMP LEVEL IN Meter_Z1'].astype(float)
        # merged_data['CLEAR WATER SUMP LEVEL IN Meter_Z2'] = merged_data['CLEAR WATER SUMP LEVEL IN Meter_Z2'].astype(float)
        # merged_data['CLEAR WATER SUMP LEVEL IN Meter_Z3'] = merged_data['CLEAR WATER SUMP LEVEL IN Meter_Z3'].astype(float)
        merged_data['CLEAR_WATER_PUMPING_FLOW_ML_Z1'] = merged_data['CLEAR_WATER_PUMPING_FLOW_ML_Z1'].astype(float)
        merged_data['CLEAR_WATER_PUMPING_FLOW_ML_Z2'] = merged_data['CLEAR_WATER_PUMPING_FLOW_ML_Z2'].astype(float)
        merged_data['CLEAR_WATER_PUMPING_FLOW_ML_Z3'] = merged_data['CLEAR_WATER_PUMPING_FLOW_ML_Z3'].astype(float)
        # merged_data['TREATED_WATER_PRODUCTION_IN_ML_Z1'] = merged_data['TREATED_WATER_PRODUCTION_IN_ML_Z1'].astype(float)
        # merged_data['TREATED WATER PRODUCTION IN ML_Z2'] = merged_data['TREATED WATER PRODUCTION IN ML_Z2'].astype(float)
        # merged_data['TREATED WATER PRODUCTION IN ML_Z3'] = merged_data['TREATED WATER PRODUCTION IN ML_Z3'].astype(float)

        merged_data['Standardized_Date'] = merged_data['Standardized_Date'].astype('str')
        merged_data.to_json(config.JSON_FILE_PATH['upload_file_path']+'merged_ebill_data.json',orient='records')
        logger.info(merged_data.head())
        merged_data = merged_data.to_dict('records')
        return merged_data
    
    def calculate_voltage_imbalance(self,row):
        ##### Pump considered off when Phase current and volatge = 0
        currents_volt = [row['Phase1_I'], row['Phase2_I'], row['Phase3_I'],row['Phase1_V_RY'], row['Phase2_V_YB'], row['Phase3_V_BR']]
        if all(i != 0 for i in currents_volt): 
            voltages = [row['Phase1_V_RY'], row['Phase2_V_YB'], row['Phase3_V_BR']]
        #  if all(v != 0 for v in voltages):  # not applicable hen the Pump is off
            avg_voltage = sum(voltages) / len(voltages)
            max_deviation = max(voltages) - avg_voltage
            voltage_imbalance = (max_deviation / avg_voltage) * 100
            return voltage_imbalance
        else:
            return None
        
    def calculate_current_imbalance(self,row):
        currents = [row['Phase1_I'], row['Phase2_I'], row['Phase3_I']]
        if all(i != 0 for i in currents):  # doesnot apply when the pump is off
            avg_current = sum(currents) / len(currents)
            max_current_deviation = max(currents)-avg_current
            current_imbalance = ((max_current_deviation) / avg_current) * 100
            return current_imbalance
        else:
            return None

    def meter_id_correction(self,row):
        if row['MeterId'] == 1:
            return row['Phase1_W']+row['Phase2_W']+row['Phase3_W']
        else:
            return row['W']
    
    def energy_meter_calculator(self,em_data):
        check = ['Phase1_I', 'Phase2_I', 'Phase3_I', 'Phase1_V_RY', 'Phase2_V_YB', 'Phase3_V_BR']
        em_data['Status'] = (em_data[check] >= 10).all(axis=1)
        em_data.rename(columns={'Phase1_W':'Phase1_kW','Phase2_W':'Phase_kW', 'Phase3_W':'Phase3_kW', 'W':'kW'})
        list1 = ['Phase1_W', 'Phase2_W', 'Phase3_W', 'W','VA']
        list2 =['Phase1_W','Phase2_W','Phase3_W','W','PF']
        list_negative = ['Phase1_pf','Phase2_pf','Phase3_pf','Phase1_W','Phase2_W','Phase3_W','PF']
        em_data[list1] = em_data[list1].apply(lambda x: x / 1000)
        em_data[list2] = em_data[list2].apply(lambda x: x *-1)
        em_data[list_negative] = em_data[list_negative].apply(lambda x: x.where(x >= 0.000000, abs(x)))
        em_data['Voltage_Imbalance_%'] = em_data.apply(self.calculate_voltage_imbalance, axis=1)
        em_data['Current_Imbalance_%'] = em_data.apply(self.calculate_current_imbalance, axis=1)
        em_data['W'] = em_data.apply(self.meter_id_correction,axis=1)

        head= 39 ## m
        flow_rate = 932/3600 ## m3/s
        density = 1000 ### kg/m3
        g = 9.8 ## m/s2
        P_out= (density*g*flow_rate*head)/1000    # power in kW
        em_data['Efficiency'] = (P_out/em_data['W'])*100
        em_data = em_data[em_data['Status']!=False]

        em_data = em_data[['MeterId', 'Time', 'Phase1_W', 'Phase1_I',
       'Phase1_V_RY', 'Phase1_pf', 'Phase2_W', 'Phase2_I', 'Phase2_V_YB',
       'Phase2_pf', 'Phase3_W', 'Phase3_I', 'Phase3_V_BR', 'Phase3_pf', 'W',
       'VA', 'PF', 'KWh_Im', 'KWh_Ex', 'KVAh', 'Lh', 'Status',
       'Voltage_Imbalance_%', 'Current_Imbalance_%', 'Efficiency']]
        logger.info(em_data)
        em_data = em_data[em_data['Time']>'2024-10-13'].reset_index(drop=True)
        em_data['Time'] = em_data['Time'].astype('str')
        em_data.to_json(config.JSON_FILE_PATH['upload_file_path']+'em_data.json',orient='records')
        em_data = em_data.to_dict('records')
        return em_data