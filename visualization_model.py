from utils.file_operations import *
import config as config
import pandas as pd

logger=setup_logger(config.LOG_FILE_PATH['logs_path'],config.LOG_FILE_PATH['logs_name'])



class Data_Visualization:
    def __init__(self, data):
        self.data = data

    def recovery_percentage_capacity_utilization_finder(self):
        data=self.data
        data_day = time_resample(data,'D',{'RAW WATER FLOW IN ML':'sum',
                                   'CLEAR WATER SUMP LEVEL IN Meter':'mean',
                                   'CLEAR WATER PUMPING FLOW ML':'sum',
                                   'TREATED WATER PRODUCTION IN ML':'sum', 'remarks category':'unique'})

        data_day['Recovery_percentage'] = ((data_day['TREATED WATER PRODUCTION IN ML']/data_day['RAW WATER FLOW IN ML'])*100).round(2)
        data_day['Capacity_utilization'] = ((data_day['TREATED WATER PRODUCTION IN ML']/93)*100).round(2)
        data_day['Recovery_percentage'].fillna(0.0,inplace=True)
        # Convert 'remarks category' to a serializable format (list of unique values)
        data_day['remarks category'] = data_day['remarks category'].apply(lambda x: list(x))
        data_day=data_day.reset_index()
        data_day['Standardized_Date'] = data_day['Standardized_Date'].astype('str')
        return data_day
    

    def plant_status(self, row):
        if row == 'No remarks':
            return True
        else:
            return False

    def plant_availability_finder(self):
        data=self.data
        data['plant status'] = data['remarks category'].apply(self.plant_status)
        data=data.reset_index()
        data['Hour'] = pd.to_datetime(data['STANDARDIZED_TIME']).dt.hour
        data['Year'] = data['Standardized_Date'].dt.year
        data['Month'] = data['Standardized_Date'].dt.month
        data['days_in_month'] = data['Standardized_Date'].dt.days_in_month
        data['total_hours_in_month'] = data['days_in_month'] * 24
        df_monthly = data.groupby(['Year', 'Month']).agg(hours_of_operation=('plant status', 'sum'),  # Sum of True values (hours the plant was working)
                            total_hours=('total_hours_in_month', 'first')).reset_index()  # Total hours in the month
        df_monthly['plant_availability'] = df_monthly['hours_of_operation'] / df_monthly['total_hours']
        return df_monthly

    def assign_shift(self,row):
        if 6 <= row < 14:
            return '1'
        elif 14 <= row < 22:
            return '2'
        else:
            return '3'


    def assign_zone(self,row):
        if 6 <= row < 18:
            return 'Z1'
        elif 18 <= row < 22:
            return 'Z2'
        else:
            return 'Z3'


    def shift_and_zone_water_production_finder(self):
        data=self.data
        data['Hour'] = pd.to_datetime(data['STANDARDIZED_TIME']).dt.hour
        data['Zone'] = data['Hour'].apply(self.assign_zone)
        data['Shift'] = data['Hour'].apply(self.assign_shift)
        data=data.reset_index()
        data['Standardized_Date'] = data['Standardized_Date'].astype('str')
        data=data[(data['Standardized_Date']>='2024-06-01') & (data['Standardized_Date']<='2024-08-28')]
        return data

    def ebill_new_columns_adder(self,data_ebill):
        data=self.data
        data['Hour'] = pd.to_datetime(data['STANDARDIZED_TIME']).dt.hour
        data['Zone'] = data['Hour'].apply(self.assign_zone)
        data_month_start = data.groupby(['Zone']).resample('M').agg({'RAW WATER FLOW IN ML':'sum',

                                   'CLEAR WATER SUMP LEVEL IN Meter':'mean',

                                   'CLEAR WATER PUMPING FLOW ML':'sum',

                                   'TREATED WATER PRODUCTION IN ML':'sum',
                                   'remarks category':lambda x: x.unique()}).reset_index()
        data_month_start['remarks category'] = data_month_start['remarks category'].apply(lambda x: list(x))

        data_month_start_pivot = data_month_start.pivot(index='Standardized_Date',columns=['Zone'],values=['RAW WATER FLOW IN ML','CLEAR WATER SUMP LEVEL IN Meter','CLEAR WATER PUMPING FLOW ML','TREATED WATER PRODUCTION IN ML','remarks category'])
        # Flatten the MultiIndex columns except for 'Standardized_Date'
        data_month_start_pivot.columns = [
            '_'.join(col).strip() if isinstance(col, tuple) else col for col in data_month_start_pivot.columns]

        # Optionally, replace spaces with underscores for easier access
        data_month_start_pivot.columns = [col.replace(' ', '_') for col in data_month_start_pivot.columns]

        data_month_ebill = data_month_start_pivot.merge(data_ebill,on='Standardized_Date')
        # Convert columns to numeric and handle any non-numeric values
        data_month_ebill['Units_kWh'] = pd.to_numeric(data_month_ebill['Units_kWh'], errors='coerce')

        data_month_ebill['TREATED_WATER_PRODUCTION_IN_ML_Z1'] = pd.to_numeric(data_month_ebill['TREATED_WATER_PRODUCTION_IN_ML_Z1'], errors='coerce')
        data_month_ebill['TREATED_WATER_PRODUCTION_IN_ML_Z2'] = pd.to_numeric(data_month_ebill['TREATED_WATER_PRODUCTION_IN_ML_Z2'], errors='coerce')
        data_month_ebill['TREATED_WATER_PRODUCTION_IN_ML_Z3'] = pd.to_numeric(data_month_ebill['TREATED_WATER_PRODUCTION_IN_ML_Z3'], errors='coerce')

        data_month_ebill['RAW_WATER_FLOW_IN_ML_Z1'] = pd.to_numeric(data_month_ebill['RAW_WATER_FLOW_IN_ML_Z1'], errors='coerce')
        data_month_ebill['RAW_WATER_FLOW_IN_ML_Z2'] = pd.to_numeric(data_month_ebill['RAW_WATER_FLOW_IN_ML_Z2'], errors='coerce')
        data_month_ebill['RAW_WATER_FLOW_IN_ML_Z3'] = pd.to_numeric(data_month_ebill['RAW_WATER_FLOW_IN_ML_Z3'], errors='coerce')

        data_month_ebill['CLEAR_WATER_PUMPING_FLOW_ML_Z1'] = pd.to_numeric(data_month_ebill['CLEAR_WATER_PUMPING_FLOW_ML_Z1'], errors='coerce')
        data_month_ebill['CLEAR_WATER_PUMPING_FLOW_ML_Z2'] = pd.to_numeric(data_month_ebill['CLEAR_WATER_PUMPING_FLOW_ML_Z2'], errors='coerce')
        data_month_ebill['CLEAR_WATER_PUMPING_FLOW_ML_Z3'] = pd.to_numeric(data_month_ebill['CLEAR_WATER_PUMPING_FLOW_ML_Z3'], errors='coerce')

        data_month_ebill['CLEAR_WATER_SUMP_LEVEL_IN_Meter_Z1'] = pd.to_numeric(data_month_ebill['CLEAR_WATER_SUMP_LEVEL_IN_Meter_Z1'], errors='coerce')
        data_month_ebill['CLEAR_WATER_SUMP_LEVEL_IN_Meter_Z2'] = pd.to_numeric(data_month_ebill['CLEAR_WATER_SUMP_LEVEL_IN_Meter_Z2'], errors='coerce')
        data_month_ebill['CLEAR_WATER_SUMP_LEVEL_IN_Meter_Z3'] = pd.to_numeric(data_month_ebill['CLEAR_WATER_SUMP_LEVEL_IN_Meter_Z3'], errors='coerce')



        # Perform the specific energy consumption calculation and round to 2 decimal places
        data_month_ebill['specific_energy_consumption'] = (
            data_month_ebill['Units_kWh'] / (
                data_month_ebill['TREATED_WATER_PRODUCTION_IN_ML_Z1'] +
                data_month_ebill['TREATED_WATER_PRODUCTION_IN_ML_Z2'] +
                data_month_ebill['TREATED_WATER_PRODUCTION_IN_ML_Z3']
            )
        ).round(2)

        data_month_ebill['charge_per_unit'] = data_month_ebill['Energy Charge (Rs)']/ data_month_ebill['Units_kWh']
        data_month_ebill['unit_cost'] = (data_month_ebill['Energy Charge (Rs)']/(
                data_month_ebill['TREATED_WATER_PRODUCTION_IN_ML_Z1'] +
                data_month_ebill['TREATED_WATER_PRODUCTION_IN_ML_Z2'] +
                data_month_ebill['TREATED_WATER_PRODUCTION_IN_ML_Z3']
            )).round(2)
        data_month_ebill=data_month_ebill.reset_index()
        data_month_ebill['Standardized_Date'] = data_month_ebill['Standardized_Date'].astype('str')
        
        return data_month_ebill


    def calculate_voltage_imbalance(self,row):
        ##### Pump considered off when Phase current and volatge = 0
        currents_volt = [row['Phase1_I'], row['Phase2_I'], row['Phase3_I'],row['Phase1_V_RY'], row['Phase2_V_YB'], row['Phase3_V_BR']]
        if all(i != 0 for i in currents_volt): 
            # print("if")
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
        # em_data.to_json(config.JSON_FILE_PATH['upload_file_path']+'em_data.json',orient='records')
        # em_data = em_data.to_dict('records')
        return em_data
    


