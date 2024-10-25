from statsmodels.tsa.arima.model import ARIMA
from pmdarima import auto_arima
import pandas as pd
from sklearn.metrics import mean_squared_error,mean_absolute_percentage_error
from statsmodels.tools.eval_measures import rmse
from statsmodels.tsa.stattools import adfuller
from utils.file_operations import *

class ES_TS_Data_Transformation:
    def __init__(self,es_data):
        """
        Initialize the Time series data transformation class.

        Parameters:
            es_data: The cleaned dataframe of ES with location and zone details
        This constructor initializes the ES_TS_Data_Transformation class with the provided DataFrame.
        """
        self.es_data = es_data

    def data_tranformation(self):

        # Check whether the data contain Zone column
        if 'Zone' in self.es_data.columns:
            # Resampling data as weekly data and resetting index
            data = Time_resampling_TS(self.es_data,['Zone'],'DateTime','W',{'AQI':'mean'})#, "ffill")
            # Rename the column 'AQI' as 'Value'
            data = rename_col(data,{'AQI':'Value'})
            return data
        else:
            # Resampling data as weekly data and resetting index
            data = Time_resampling_TS(self.es_data,['Location'],'DateTime','W',{'AQI':'mean'})#, "ffill")
            # Rename the column 'AQI' as 'Value'
            data = rename_col(data,{'AQI':'Value'})
            return data


class ES_Time_Series_Forecasting:
    def __init__(self,es_regionwise,region_name):
        """
        Initialize the Time_Series_Forecasting class.

        Parameters:
            es_regionwise (pd.DataFrame): The DataFrame containing the time series data for all regions.
            region_column (str): The column name in the DataFrame that represents the regions.
            region_name (str): The name of the specific region for which forecasting is to be performed.

        This constructor initializes the Time_Series_Forecasting class with the provided DataFrame, region(zone/location) column, and region name.
        """
        self.es_regionwise = es_regionwise
        # self.region_column = region_column
        self.region_name = region_name
    
    def es_regionwise_dataframe(self,region_column):
        """
        Get the DataFrame for the specified region.

        Returns:
            pd.DataFrame: The DataFrame containing data for the specified region.

        This method filters the DataFrame `self.es_regionwise` to retain only the rows where the value in the `self.region_column` column is equal to `self.region_name`.
        """
        
        self.es_regionwise = self.es_regionwise[self.es_regionwise[region_column] == self.region_name]
        self.es_regionwise = self.es_regionwise.fillna(method='ffill',axis='rows')
        # print(self.es_regionwise[self.region_column].value_counts())
        # print(self.es_regionwise)
        return self.es_regionwise

    def adf_test(self,value_column):
        """
        Perform Augmented Dickey-Fuller test on a time series.

        Returns:
             tuple: A tuple containing the test result ("Stationary" or "Non-stationary") 
             and the detailed output of the ADF test.
        """
        result = adfuller(self.es_regionwise[value_column].dropna(),autolag='AIC') # .dropna() handles differenced data
    
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

        This method uses `auto_arima` from `pmdarima` to automatically determine the optimal ARIMA order for the time series data in `self.es_locationwise[value_column]`.
        """
        stepwise_fit = auto_arima(self.es_regionwise[value_column], start_p=0, start_q=0,
                          error_action='ignore',   # we don't want to know if an order does not work
                          suppress_warnings=True,  # we don't want convergence warnings
                          stepwise=True)           # set to stepwise
        best_arima_order = stepwise_fit.get_params().get('order')
        return best_arima_order


    def get_es_model_and_validation_results(self, value_column,test_size,validation_size):
        """
        Perform time series forecasting and return model results and validation predictions.

        Parameters:
            value_column (str): The column name in the DataFrame that contains the time series values.
            test_size (int): The size of the test data for forecasting.
            validation_size (int): The size of the validation data for forecasting.

        Returns:
            dict: Dictionary containing model results (MSE, RMSE, MAPE, Accuracy) and validation predictions.

        This method splits the data into training, test, and validation sets and fits an ARIMA model to perform time series forecasting.
        It returns a dictionary with model results and the validation predictions.
        """
        train = self.es_regionwise[value_column][:len(self.es_regionwise[value_column])-(test_size+validation_size)]
    # creates a subset of the DataFrame starting from the first row and excluding the last 20 rows (8 for test_size + 12 for validation_size)
        test = self.es_regionwise[value_column][len(self.es_regionwise[value_column])-(test_size+validation_size):len(self.es_regionwise[value_column])-validation_size]
    # In the last 20 rows, first 8 rows selected for testing
        validation = self.es_regionwise[value_column][len(self.es_regionwise[value_column])-validation_size:]
    # In the last 20 rows, last 12 rows selected for validation

        prediction_start_index = len(train)
        prediction_end_index = len(train)+len(test)-1

        #print(prediction_start_index,prediction_end_index)
        
        fit_results = ARIMA(train,order=self.determine_ARIMA_order(value_column)).fit()
        predictions = fit_results.predict(start=prediction_start_index, end=prediction_end_index)
        validation_predictions = fit_results.predict(start=prediction_end_index+1, end=len(train)+len(test)+len(validation)-1)
        
        Mean_squared_error = mean_squared_error(test, predictions)
        Root_mean_squared_error = rmse(test, predictions)
        Mean_absolute_percentage_error = mean_absolute_percentage_error(test,predictions)
        
        model_results = {"Model":"ARIMA",'Location': self.region_name,"Stationary":self.adf_test(value_column),"X_train": str(len(train))+" Weeks", "X_test": str(len(test))+" Weeks", "X_validation": str(len(validation))+" Weeks", "ARIMA_order":str(self.determine_ARIMA_order(value_column)) , "MSE": Mean_squared_error,"RMSE": Root_mean_squared_error,"MAPE":Mean_absolute_percentage_error, "Accuracy":((1-Mean_absolute_percentage_error)*100).round(0)}
        return model_results,validation_predictions
    
    def fit_model(self,value_column):
        """
        Fit the ARIMA model to the time series data.

        Parameters:
            value_column (str): The column name in the DataFrame that contains the time series values.

        Returns:
             Fitted ARIMA model.

        This method fits an ARIMA model to the time series data in `self.es_regionwise[value_column]` and returns the fitted model.
        """

        fitted_results = ARIMA(self.es_regionwise[value_column], order=self.determine_ARIMA_order(value_column)).fit()
        return fitted_results
 
    def es_dataframe_creation(self, value_column,predictions,test_size,validation_size):
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
        last_20Weeks_Dataframe = pd.DataFrame(self.es_regionwise[value_column]).tail(20)
        last_20Weeks_Dataframe['Type'] = 'Actual'
        predicted_Dataframe = pd.DataFrame(predictions)
        predicted_Dataframe=predicted_Dataframe.rename(columns={'predicted_mean':value_column})
        predicted_Dataframe['Type'] = 'Predicted'

        actual_forecast_Dataframe = pd.concat([last_20Weeks_Dataframe,predicted_Dataframe]).reset_index()
        actual_forecast_Dataframe = actual_forecast_Dataframe.rename(columns={'index':'Date'})
        #actual_forecast_DF['Date']=pd.to_datetime(actual_forecast_DF['Date'])
        actual_forecast_Dataframe['Date'] = actual_forecast_Dataframe['Date'].astype('str')

        validation_Dataframe = pd.DataFrame(self.get_es_model_and_validation_results(value_column,test_size,validation_size)[1])
        validation_Dataframe = validation_Dataframe.reset_index()
        validation_Dataframe = validation_Dataframe.rename(columns={'index':'Date','predicted_mean':'Validation'})
        #validation_dataframe['Date']=pd.to_datetime(validation_dataframe['Date'])
        validation_Dataframe['Date'] = validation_Dataframe['Date'].astype('str')

        #final_dataframe = pd.concat([actual_forecast_DF,validation_dataframe])
        final_Dataframe =  actual_forecast_Dataframe.merge(validation_Dataframe, on='Date',how='outer')
        
        return final_Dataframe




