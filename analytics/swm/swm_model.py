from statsmodels.tsa.arima.model import ARIMA
from pmdarima import auto_arima
import pandas as pd
from sklearn.metrics import mean_squared_error,mean_absolute_percentage_error
from statsmodels.tools.eval_measures import rmse
from statsmodels.tsa.stattools import adfuller
from utils.file_operations import *


class SWM_TS_Data_Transformation:
    def __init__(self,swm_data):
        """
        Initialize the Time series data transformation class.

        Parameters:
            swm_data: The cleaned dataframe of SWM with location and zone details
        This constructor initializes the SWM_TS_Data_Transformation class with the provided DataFrame.
        """
        self.swm_data = swm_data

    def data_tranformation(self):

        # Selecting feature
        data = self.swm_data[self.swm_data["Variable"]=='Complaint_Total']

        # Splitting location as Zone and Ward
        data[['Zone','Ward']]= TagName_split(data['Loc'], 'W', 1)

        data['Ward'] = data['Ward'].replace('\_','',regex=True)
        data['Zone'] = data['Zone'].replace('\_','',regex=True)
        data['Ward'].fillna(value='N',inplace=True)
        # Resampling data as weekly data and resetting index
        data = Time_resampling_TS(data,['Zone','Ward'],'DateTime','W',{'Value':'last'})#,'ffill')
        # print(data.head())
        # print(data['Ward'].unique())
        

        # Grouping data zone wise and taking the sum of values for each zone
        data = data.groupby([data.index,'Zone']).Value.sum()
        data = data.reset_index()
        # print('zonewise data:', data)
        data = data.set_index('DateTime')
        data = data.sort_index()

        # Resetting index 
        # cleaned_data = data.reset_index()
        # cleaned_data = data.rename(columns={'index':'Date'})

        return data    


class SWM_Time_Series_Forecasting:
    def __init__(self,swm_zonewise,zone_column, zone_name):
        """
        Initialize the Time_Series_Forecasting class.

        Parameters:
            swm_zonewise (pd.DataFrame): The DataFrame containing the time series data for all zones.
            zone_column (str): The column name in the DataFrame that represents the zones.
            zone_name (str): The name of the specific zone for which forecasting is to be performed.

        This constructor initializes the Time_Series_Forecasting class with the provided DataFrame, zone column, and zone name.
        """
        self.swm_zonewise = swm_zonewise
        self.zone_column = zone_column
        self.zone_name = zone_name
    
    def swm_zonewise_dataframe(self):
        """
        Get the DataFrame for the specified zone.

        Returns:
            pd.DataFrame: The DataFrame containing data for the specified zone.

        This method filters the DataFrame `self.swm_zonewise` to retain only the rows where the value in the `self.zone_column` column is equal to `self.zone_name`.
        """
        self.swm_zonewise = self.swm_zonewise[self.swm_zonewise[self.zone_column] == self.zone_name]
        self.swm_zonewise = self.swm_zonewise.fillna(method='ffill',axis='rows')
        return self.swm_zonewise
    
    def adf_test(self,value_column):
        """
    #    Perform Augmented Dickey-Fuller test on a time series.

    #    Returns:
    #         tuple: A tuple containing the test result ("Stationary" or "Non-stationary") 
    #         and the detailed output of the ADF test.
    #    """
        result = adfuller(self.swm_zonewise[value_column].dropna(),autolag='AIC') # .dropna() handles differenced data
    
        labels = ['ADF test statistic','p-value','# lags used','# observations']
        out = pd.Series(result[0:4],index=labels)

        for key,value in result[4].items():
            out[f'critical value ({key})']=value
    
        if result[1] <= 0.05:
             # print("Strong evidence against the null hypothesis")
    #         # print("Reject the null hypothesis")
    #         # print("Data has no unit root and is stationary")
            state = "Stationary"
        else:
    #         # print("Weak evidence against the null hypothesis")
    #         # print("Fail to reject the null hypothesis")
    #         # print("Data has a unit root and is non-stationary")
            state = "Non-stationary"
        if state == "Stationary":
            return "Yes"
        else:
            return "No"

    def determine_ARIMA_order(self, value_column):
        """
        Determine the optimal ARIMA order for the time series data.

        Parameters:
            value_column (str): The column name in the DataFrame that contains the time series values.

        Returns:
            tuple: The optimal ARIMA order as a tuple (p, d, q).

        This method uses `auto_arima` from `pmdarima` to automatically determine the optimal ARIMA order for the time series data in `self.df_zonewise[value_column]`.
        """
        stepwise_fit = auto_arima(self.swm_zonewise[value_column], start_p=1, start_q=1,trace=True,
                          error_action='ignore',   # we don't want to know if an order does not work
                          suppress_warnings=True,  # we don't want convergence warnings
                          stepwise=True)           # set to stepwise
        best_arima_order = stepwise_fit.get_params().get('order')
        return best_arima_order


    def get_swm_model_and_validation_results(self,value_column,test_size,validation_size):
        # Split the data into training, testing, and validation sets.
        train = self.swm_zonewise[value_column][:len(self.swm_zonewise[value_column])-(test_size+validation_size)]
        # creates a subset of the DataFrame starting from the first row and excluding the last 16 rows (8 for test_size + 8 for validation_size)
        test = self.swm_zonewise[value_column][len(self.swm_zonewise[value_column])-(test_size+validation_size):len(self.swm_zonewise[value_column])-validation_size]
        # In the last 16 rows, first 8 rows selected for testing
        validation = self.swm_zonewise[value_column][len(self.swm_zonewise[value_column])-validation_size:]
    
        # Define the indices for prediction.
        prediction_start_index = len(train)
        prediction_end_index = len(train)+len(test)-1
       
        # Fit an ARIMA model to the training data.
        fit_results = ARIMA(train,order=self.determine_ARIMA_order(value_column)).fit()
        # Generate predictions for the test and validation sets.
        predictions = fit_results.predict(start=prediction_start_index, end=prediction_end_index)
        validation_predictions = fit_results.predict(start=prediction_end_index+1, end=len(train)+len(test)+len(validation)-1).round(0)
        
        # Calculate model performance metrics.
        Mean_squared_error = mean_squared_error(test, predictions)
        Root_mean_squared_error = rmse(test, predictions)
        Mean_absolute_percentage_error = mean_absolute_percentage_error(test,predictions)

        # Check if all values in the 'Value' column of the SWM DataFrame are equal to 0.
        if len(self.swm_zonewise[self.swm_zonewise[value_column]!=0])==0:
            # If all values are 0, indicate that there is insufficient data for analysis.
            model_results = {self.zone_name:"Data is insufficient for analysis"}
            validation_predictions = {"No data for validation"}
        else:
            model_results = {"Model":"ARIMA",'Zone': self.zone_name,"Stationary":self.adf_test(value_column),"X_train": str(len(train))+" Weeks", "X_test": str(len(test))+" Weeks", "X_validation": str(len(validation))+" Weeks", "ARIMA_order":str(self.determine_ARIMA_order(value_column)) , "MSE": Mean_squared_error,"RMSE": Root_mean_squared_error,"MAPE":Mean_absolute_percentage_error, "Accuracy":((1-Mean_absolute_percentage_error)*100).round(0)}
            return model_results,validation_predictions
        return model_results,validation_predictions
        # If data is insufficient, return the message indicating that.
    
    def fit_model(self,value_column):
        """
        Fit the ARIMA model to the time series data.

        Parameters:
            value_column (str): The column name in the DataFrame that contains the time series values.

        Returns:
             Fitted ARIMA model.

        This method fits an ARIMA model to the time series data in `self.df_zonewise[value_column]` and returns the fitted model.
        """
        # Check if there is sufficient data for analysis.
        if len(self.swm_zonewise[self.swm_zonewise[value_column]!=0])!=0:
            # Fit an ARIMA model and return the fitted results.
            fitted_results = ARIMA(self.swm_zonewise[value_column], order=self.determine_ARIMA_order(value_column)).fit()
        
            return fitted_results
        return None
         # If data is insufficient, return None.

    def swm_dataframe_creation_with_zero_values(self, value_column):
        """
        Create a DataFrame with actual values.

        Parameters:
            value_column (str): The column name in the DataFrame that contains the time series values.

        Returns:
            pd.DataFrame: DataFrame containing actual values.

        This method creates a DataFrame containing actual values.
        """
        # Create a DataFrame containing actual values.
        actual_forecast_Dataframe = pd.DataFrame(self.swm_zonewise[value_column])
        # Add a 'Type' column to label the data as 'Actual'.
        actual_forecast_Dataframe['Type'] = 'Actual'
        # Reset the index and rename the 'DateTime' column to 'Date'.
        actual_forecast_Dataframe = actual_forecast_Dataframe.reset_index()
        actual_forecast_Dataframe = actual_forecast_Dataframe.rename(columns={'DateTime':'Date'})
        # Convert the 'Date' column to a string type.
        actual_forecast_Dataframe['Date'] = actual_forecast_Dataframe['Date'].astype('str')
        return actual_forecast_Dataframe

    def swm_dataframe_creation_without_zero_values(self, value_column,predictions,test_size,validation_size):
        """
        Create a DataFrame with actual, predicted, and validation values.

        Parameters:
            value_column (str): The column name in the DataFrame that contains the time series values.
            predictions (pd.Series): The predicted values from the ARIMA model.
            test_size (int): The size of the test data for forecasting.
            validation_size (int): The size of the validation data for forecasting.

        Returns:
            pd.DataFrame: DataFrame containing actual, predicted, and validation values.

        This method creates a DataFrame containing actual, predicted, and validation values.
        It concatenates the last 20 weeks of actual data with the predicted values from the ARIMA model.
        The DataFrame also includes validation predictions from the ARIMA model.
        """
        # Create a DataFrame with the last 20 weeks of actual data labeled as 'Actual'.
        last_20Weeks_Dataframe = pd.DataFrame(self.swm_zonewise[value_column]).tail(20)
        last_20Weeks_Dataframe['Type'] = 'Actual'
        # Create a DataFrame with predicted values labeled as 'Predicted'.
        predicted_Dataframe = pd.DataFrame(predictions)
        predicted_Dataframe['Type'] = 'Predicted'
        predicted_Dataframe=predicted_Dataframe.rename(columns={'predicted_mean':value_column})

        # Concatenate the actual and predicted DataFrames, reset the index, and rename the 'index' column to 'Date'.
        actual_forecast_Dataframe = pd.concat([last_20Weeks_Dataframe,predicted_Dataframe]).reset_index()
        actual_forecast_Dataframe = actual_forecast_Dataframe.rename(columns={'index':'Date'})
        actual_forecast_Dataframe['Date'] = actual_forecast_Dataframe['Date'].astype('str')

        # Create a DataFrame with validation predictions.
        validation_Dataframe = pd.DataFrame(self.get_swm_model_and_validation_results(value_column,test_size,validation_size)[1])
        validation_Dataframe = validation_Dataframe.reset_index()
        validation_Dataframe = validation_Dataframe.rename(columns={'index':'Date','predicted_mean':'Validation'})
        validation_Dataframe['Date'] = validation_Dataframe['Date'].astype('str')

        #final_dataframe = pd.concat([actual_forecast_DF,validation_dataframe])
        # Merge the actual/predicted DataFrame with the validation DataFrame using an outer join on the 'Date' column.
        final_Dataframe =  actual_forecast_Dataframe.merge(validation_Dataframe, on='Date',how='outer')
        
        return final_Dataframe




