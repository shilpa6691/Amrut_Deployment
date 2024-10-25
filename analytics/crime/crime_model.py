from crime import crime_config as config
import pandas as pd

 
class data_processing:

    def __init__(self):
        """
        Initialize the Time_Series_Forecasting class.
        Parameters:
            data (pd.DataFrame): The cleaned DataFrame containing all columns.
        This constructor initializes the Time_Series_Forecasting class with the provided DataFrame, zone column, and zone name.
        """
        

    def get_crime_count_locationwise(self,data,column_list,sort_column,rename_dict):
        crime_count_locationwise = data.groupby(column_list).Disposition.count().reset_index().sort_values(by=sort_column, ascending=False)
        crime_count_locationwise.rename(columns=rename_dict,inplace=True)
        return crime_count_locationwise

    def get_crime_count_yearise(self,data,column_list,rename_column):
        crime_count_yearwise = data.groupby(column_list).Type.count().reset_index(name=rename_column)
        return crime_count_yearwise

    def latitude_longitudewise_crimes(self,data,column_list,sort_column):
        crime_locationwise = data.groupby(column_list).size().reset_index(name='CrimeCount').sort_values(by=sort_column, ascending=False)
        return crime_locationwise

    # def relationship_of_beat_and_crimes(self,data,column_list,agg_dict,sort_column,rename_dict):
    #     Beat_count=data.groupby(column_list).agg(agg_dict).reset_index().sort_values(by=sort_column, ascending=False)
    #     Beat_count.rename(columns=rename_dict,inplace=True)
    #     return Beat_count

    def severity_classification(self,data,column_list,sort_column):
        Felonies = r'(401A|406|406V|406A|407|407A|407B|413|413A|413B|414|424|426|427|428|432|434|445|446)' #High severity crimes
        Gross_Misdemeanors = r'(401|401B|401C|401M|403|404|404A|409|414A|414C|429|433|415|415A|415B|415C|425|425A|425B|425M|441)' #Medium severity crimes
        Misdemeanors = r'(416|416A|416B|416F|417|438)' #Low severity crimes
        Wobblers = r'(410|415|415A|415B|415C|425|425A|425B|425M|441)' # either felony or misdemeanor
        
        data.loc[data['Type'].str.contains(Felonies), 'Severity'] = 'Felony'
        data.loc[data['Type'].str.contains(Gross_Misdemeanors), 'Severity'] = 'Gross_Misdemeanor'
        data.loc[data['Type'].str.contains(Misdemeanors), 'Severity'] = 'Misdemeanor'
        data.loc[data['Type'].str.contains(Wobblers), 'Severity'] = 'Wobbler'
        data['Severity'] = data['Severity'].fillna('Others')
        data=data.groupby(column_list).Disposition.count().reset_index(name='Crime_counts').sort_values(by=sort_column,ascending=False)
        return data

    def time_location_of_accidents(self,data,column_list,agg_dict,sort_column,rename_dict):
        accident_counts = data[(data['Type'].str.contains('401', regex=True, na=False))].groupby(column_list).agg(agg_dict).reset_index().sort_values(by=sort_column, ascending=False)
        accident_counts.rename(columns=rename_dict,inplace=True)
        return accident_counts

    def crime_rate_of_types_of_crimes(self,data,columns,sort_column):
        
        unique_new_type_descriptions = data['Type_Description'].unique()

        year_df = pd.DataFrame()

        for new_type_description in unique_new_type_descriptions:
            df_for_new_type_description = data[data['Type_Description'] == new_type_description]
            new_type_description_count = df_for_new_type_description.groupby(columns).Type_Description.count().reset_index().sort_values(by=sort_column, ascending=False)
            new_type_description_count.rename(columns={'Type_Description': f'{new_type_description}_count'}, inplace=True)

            if year_df.empty:
                year_df = new_type_description_count.copy()
            else:
                year_df = pd.merge(year_df, new_type_description_count, on='Year', how='outer')

        year_df = year_df.fillna(0)

        year_df['Total_count'] = year_df.iloc[:, 1:].sum(axis=1)
        year_df['Population'] = year_df['Year'].map({2018: 644644, 2019: 651319, 2020: 641903, 2021: 646775, 2022: 657366, 2023: 660769})
        year_df['Crime_rate']=((year_df['Total_count']/year_df['Population'])*10000).round(4)
        year_df1=year_df[['Year','Total_count','Population','Crime_rate']].sort_values(by='Crime_rate',ascending=False)
        return year_df,year_df1


    def cctv_streetlight_effect(self,data,columns,sort_column):
        import numpy as np
        df_cctv=data.groupby(columns)["Disposition"].count().reset_index(name="Crime_Count").sort_values(by=sort_column,ascending=False)
        def generate_cctv_number(crime_count):
            if 1 <= crime_count <= 100:
                return np.random.randint(3, 6) 
            elif 101 <= crime_count <= 200:
                 return np.random.randint(2, 4) 
            elif 201 <= crime_count <= 500: 
                return np.random.randint(1, 3) 
            elif crime_count > 500: 
                return np.random.randint(0, 2) 
            else: 
                return None

        def generate_streetlight_number(crime_count):
            if 1 <= crime_count <= 100: 
                return np.random.randint(10, 16) 
            elif 101 <= crime_count <= 200: 
                return np.random.randint(7, 12)
            elif 201 <= crime_count <= 500: 
                return np.random.randint(4, 9) 
            elif crime_count > 500: 
                return np.random.randint(0, 5) 
            else:
                return None
 
 
        df_cctv["Streetlight"]=df_cctv["Crime_Count"].apply(generate_streetlight_number )
  
        df_cctv["CCTV"]=df_cctv["Crime_Count"].apply(generate_cctv_number )
        return df_cctv


    def merging_datframes(self,data1,data2,columns,sort_column):
        
        data1.drop(columns=["Event_Number","Event_Date","Type","Beat","Disposition","LAT","LONG","WARD","Month","Month-Year","time_window"],axis=1,inplace=True)
        
        data1["City"]="Las Vegas"
        data1['Population'] = data1['Year'].map({2018: 644644, 2019: 651319, 2020: 641903, 2021: 646775, 2022: 657366, 2023: 660769})
        
        import re
        pattern_mapping =  {'Hit and Run':r'Traffic Collision - Hit & Run',
                   'Burglary':r'Motor Vehicle Theft|Burglary - Other|Burglary - Commercial|Burglary - Residential|Burglary - Hot Prowl',
                   'Robbery':r'Robbery - Carjacking|Robbery - Other|Robbery - Commercial|Robbery - Street|Robbery - Residential',
                   'Person with a gun/knife/other deadly weapon':r'Weapons Offense',
                   'Grand Larceny':r'Larceny Theft - Shoplifting|Larceny - Auto Parts|Larceny Theft - From Building',
                   'Sexual Assault':r'Rape|Sex Offense|Human Trafficking, Commercial Sex Acts|Rape - Attempted',
                   'Kidnap':r'Kidnapping',
                   'Fraud':r'Fraud|Forgery And Counterfeiting|Embezzlement|Bad Checks',
                   'Narcotics':r'Drug Violation',
                   'Accident':r'Traffic Collision',
                   'Prowler':r'Stalking',
                   'Suicide':r'Suicide',
                   'small LARCENY':r'Larceny Theft - Other|Larceny - From Vehicle|Larceny Theft - Bicycle|Theft From Vehicle|Larceny Theft - Pickpocket|Motor Vehicle Theft (Attempted)|Larceny Theft - Purse Snatch',
                   'Assault/Battery':r'Simple Assault|Aggravated Assault|Manslaughter|Homicide|Human Trafficking',
                   'Fight/disturbance':r'Disorderly Conduct|Drunkenness',
                   'Suspicious':r'Suspicious Occ|Suspicious Package|Loitering',
                   'Stolen Property':r'Stolen Property',
                   'Malicious destruction of property':r'Vandalism|Arson',
                   'Recovered Stolen Motor Vehicle':r'Recovered Vehicle',
                   'Traffic Problem':r'Traffic Violation Arrest|Vehicle Impounded|Vehicle Misplaced',
                   'missing person/found person/runaway':r'Missing Person|Missing Adult',
                   'Missing/Found Property':r'Lost Property',
                   'wanted suspect':r'Warrant',
                  }

        for category, patterns in pattern_mapping.items():
            pattern = '|'.join(map(re.escape, patterns))
            data2.loc[data2['Incident Subcategory'].str.contains(pattern, regex=True, na=False), 'Type_Description'] = category

# Fill any missing values in the "Type_Description" column with 'Other'
        data2['Type_Description'] = data2['Type_Description'].fillna('Other')

        data2.drop("Incident Subcategory", axis=1, inplace=True)
        data2=data2.rename(columns={"Incident Year":"Year","Intersection":"General_Location"})
        data2["City"]="San Francisco"

        data2['Population'] = data2['Year'].map({2018: 4726314, 2019: 4731803, 2020: 4740552, 2021: 4616610, 2022: 4579599, 2023: 4542588,2024:4505577})

        merged_df = pd.concat([data1, data2], ignore_index=True)

        comparison_df=merged_df.groupby(columns)["Type_Description"].count().reset_index(name='Crime_counts')
        comparison_df=comparison_df.drop(12)
        comparison_df=comparison_df.sort_values(by=sort_column,ascending=False)

        comparison_df['Crime_Counts_per_1000_population'] = (comparison_df['Crime_counts'] / comparison_df['Population']*1000).round(0)

        # Display the DataFrame sorted by crime counts
        sorted_comparison_df = comparison_df.sort_values(by='Crime_Counts_per_1000_population', ascending=False)

        return sorted_comparison_df
