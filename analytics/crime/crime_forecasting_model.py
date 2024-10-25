from statsmodels.tsa.arima.model import ARIMA
from pmdarima import auto_arima
import pandas as pd
from sklearn.metrics import mean_squared_error,mean_absolute_percentage_error
from statsmodels.tools.eval_measures import rmse
from statsmodels.tsa.stattools import adfuller
from utils.file_operations import *

class CRIME_TS_Data_Transformation:
    def __init__(self,data):
        """
        Initialize the Time series data transformation class."""

        self.data = data

    def data_tranformation(self,group_col_list,datecol,window_size,agg_dict,rename_dict):
        # Resampling data as weekly data and resetting index
        data = Time_resampling_TS(self.data,group_col_list,datecol,window_size,agg_dict)
        data = rename_col(data,rename_dict)
        return data


class CRIME_Time_Series_Forecasting:
    def __init__(self,data,column_name,column_type):
        """
        Initialize the Time_Series_Forecasting class.

        """
        self.data = data
        self.column_name = column_name
        self.column_type = column_type
    
    def column_type_dataframe(self):
        """
        Get the DataFrame for the specified column_type.

        Returns:
            pd.DataFrame: The DataFrame containing data for the specified column_type.

        """
        
        self.data = self.data[self.data[self.column_name] == self.column_type]
        self.data = self.data.fillna(method='ffill',axis='rows')

        return self.data

    def column_type_dataframe_for_2_columns(self,column_name1,column_type1,column_name2,column_type2):
        
        self.data = self.data[(self.data[column_name1] == column_type1) & (self.data[column_name2] == column_type2)]
        self.data = self.data.fillna(method='ffill',axis='rows')

        return self.data

    def adf_test(self,value_column):
        """
        Perform Augmented Dickey-Fuller test on a time series.

        Returns:
             tuple: A tuple containing the test result ("Stationary" or "Non-stationary") 
             and the detailed output of the ADF test.
        """
        result = adfuller(self.data[value_column].dropna(),autolag='AIC') # .dropna() handles differenced data
    
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
        stepwise_fit = auto_arima(self.data[value_column], start_p=0, start_q=0,
                          error_action='ignore',   # we don't want to know if an order does not work
                          suppress_warnings=True,  # we don't want convergence warnings
                          stepwise=True)           # set to stepwise
        best_arima_order = stepwise_fit.get_params().get('order')
        return best_arima_order


    def get_model_and_validation_results(self, value_column,test_size,validation_size):
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
        train = self.data[value_column][:len(self.data[value_column])-(test_size+validation_size)]
    # creates a subset of the DataFrame starting from the first row and excluding the last 20 rows (8 for test_size + 12 for validation_size)
        test = self.data[value_column][len(self.data[value_column])-(test_size+validation_size):len(self.data[value_column])-validation_size]
    # In the last 20 rows, first 8 rows selected for testing
        validation = self.data[value_column][len(self.data[value_column])-validation_size:]
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
        
        model_results = {"Model":"ARIMA",'Location/crime_type': self.column_type,"Stationary":self.adf_test(value_column),"X_train": str(len(train))+" Weeks", "X_test": str(len(test))+" Weeks", "X_validation": str(len(validation))+" Weeks", "ARIMA_order":str(self.determine_ARIMA_order(value_column)) , "MSE": Mean_squared_error,"RMSE": Root_mean_squared_error,"MAPE":Mean_absolute_percentage_error, "Accuracy":((1-Mean_absolute_percentage_error)*100).round(0)}
        return model_results,validation_predictions
    
    def fit_model(self,value_column):
        """
        Fit the ARIMA model to the time series data.

        Parameters:
            value_column (str): The column name in the DataFrame that contains the time series values.

        Returns:
             Fitted ARIMA model.

        """

        fitted_results = ARIMA(self.data[value_column], order=self.determine_ARIMA_order(value_column)).fit()
        return fitted_results
 
    def dataframe_creation(self, value_column,predictions,test_size,validation_size):
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
        last_20Weeks_Dataframe = pd.DataFrame(self.data[value_column]).tail(20)
        last_20Weeks_Dataframe['Type'] = 'Actual'
        predicted_Dataframe = pd.DataFrame(predictions)
        predicted_Dataframe=predicted_Dataframe.rename(columns={'predicted_mean':value_column})
        predicted_Dataframe['Type'] = 'Predicted'
        

        actual_forecast_Dataframe = pd.concat([last_20Weeks_Dataframe,predicted_Dataframe]).reset_index()
        actual_forecast_Dataframe = actual_forecast_Dataframe.rename(columns={'index':'Date'})
        #actual_forecast_DF['Date']=pd.to_datetime(actual_forecast_DF['Date'])
        actual_forecast_Dataframe['Date'] = actual_forecast_Dataframe['Date'].astype('str')
        

        validation_Dataframe = pd.DataFrame(self.get_model_and_validation_results(value_column,test_size,validation_size)[1])
        validation_Dataframe = validation_Dataframe.reset_index()
        validation_Dataframe = validation_Dataframe.rename(columns={'index':'Date','predicted_mean':'Validation'})
        #validation_dataframe['Date']=pd.to_datetime(validation_dataframe['Date'])
        validation_Dataframe['Date'] = validation_Dataframe['Date'].astype('str')

        #final_dataframe = pd.concat([actual_forecast_DF,validation_dataframe])
        final_Dataframe =  actual_forecast_Dataframe.merge(validation_Dataframe, on='Date',how='outer')
        
        return final_Dataframe



