import streamlit as st
import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt

# Load the pickle files
with open('store_forecasts.pkl', 'rb') as f:
    store_forecasts = pickle.load(f)

with open('actual_sales.pkl', 'rb') as f:
    actual_sales_dict = pickle.load(f)

def main():
    st.title("Sales Forecasting")

    store_key = st.selectbox("Select Store Key:", list(store_forecasts.keys()))
    
    if store_key:
        forecast_df = store_forecasts.get(store_key)
        if forecast_df is not None:
            st.write(f"Forecasted Sales for Store Key: {store_key}")

            # Extract actual sales for the selected store
            actual_sales = actual_sales_dict[store_key][-90:]

            # Extract forecasted sales for the selected store
            forecasted_sales = forecast_df[['Forecast_Sales', 'lower', 'upper']]

            # Combine actual and forecasted sales into a single DataFrame
        
            combined_sales = pd.concat([actual_sales, forecasted_sales], axis=1)
            combined_sales.columns = ['Actual Sales', 'Forecasted Sales', 'lower', 'upper']
        
            mape = np.mean(np.abs((actual_sales - forecasted_sales['Forecast_Sales']) / actual_sales)) * 100
            print(f"MAPE: {mape:.2f}%")
        
        
            smape = np.mean(np.abs(actual_sales - forecasted_sales['Forecast_Sales'])*2 / (actual_sales + forecasted_sales['Forecast_Sales'])) * 100
            print(f"sMAPE: {smape:.2f}%")
        
            # Define dates to exclude
            exclude_dates = pd.to_datetime(['2023-11-23', '2023-12-25'])
        
            # Filter out the excluded dates
            mask = ~combined_sales.index.isin(exclude_dates)
        
            actual = combined_sales['Actual Sales']
            actual_excl = combined_sales.loc[mask, 'Actual Sales']
        
            mape_excl = np.mean(np.abs((actual_excl - forecasted_sales['Forecast_Sales'][mask]) / actual_excl)) * 100
            print(f"MAPE excluding the 2 spikes: {mape_excl:.2f}%")
        
            # Plot the actual and forecasted sales
            plt.figure(figsize = (14, 7))
            plt.plot(combined_sales['Actual Sales'], label = 'Actual Sales')
            plt.plot(combined_sales['Forecasted Sales'], label = 'Forecasted Sales', linestyle = '--')
            plt.fill_between(combined_sales.index, combined_sales['lower'], combined_sales['upper'], 
                             color = 'orange', alpha = 0.2)
            plt.title(f'Actual vs Forecasted Sales for Store {store_key}')
            plt.xlabel('Date')
            plt.ylabel('Sales')
            plt.legend()
            st.pyplot(plt)

if __name__ == "__main__":
    main()
