import streamlit as st
import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
import gdown

# File ID from the Google Drive shareable link
file_id = '1sk2yygfI-cYunRJ4AelViKirNbBtbnkY'

# Create the download URL
url = f'https://drive.google.com/uc?id={file_id}'

# Download the file
output = 'sales_store_promotions.csv'
gdown.download(url, output, quiet=False)

# Read the CSV file into a DataFrame
df = pd.read_csv(output)

promo_features = ['PLATFORM_DD',
       'PLATFORM_Inhouse', 'PLATFORM_UE', 'FREQUENCY_Weekday', 'PromotionCash',
       'PromotionKind', 'PROMOTION_ITEM_DeliveryFee',
       'PROMOTION_COVERAGE_Regional']


df[promo_features] = df[promo_features].fillna(0)
df[promo_features] = df[promo_features].astype(int)
df['BUSINESS_DATE'] = pd.to_datetime(df['BUSINESS_DATE'], format = '%d-%m-%Y')

# Forecast only for stores that we have enough data on (at least 90 days)
stores = df[df['BUSINESS_DATE'] <= '2023-07-04']['STORE_KEY'].unique()
df = df[df['STORE_KEY'].isin(stores)]

# Load the pickle files
with open('store_forecasts.pkl', 'rb') as f:
    store_forecasts = pickle.load(f)



def main():
    st.title("Sales Forecasting")

    store_key = st.selectbox("Select Store Key:", list(store_forecasts.keys()))
    
    if store_key:
        forecast_df = store_forecasts.get(store_key)
        if forecast_df is not None:
            st.write(f"Forecasted Sales for Store Key: {store_key}")

            # Extract actual sales for the selected store
            actual_sales = df[df['STORE_KEY'] == store_key].set_index('BUSINESS_DATE')['NET_SALES_FINAL_USD_AMOUNT'].sort_index()[-90:]

            # Extract forecasted sales for the selected store
            forecasted_sales = forecast_df['Forecast_Sales']

            # Combine actual and forecasted sales into a single DataFrame
            combined_sales = pd.concat([actual_sales, forecasted_sales], axis=1)
            combined_sales.columns = ['Actual Sales', 'Forecasted Sales']

            # MAPE & sMAPE
            mape = np.mean(np.abs((actual_sales - forecasted_sales) / actual_sales)) * 100
            smape = np.mean(np.abs(actual_sales - forecasted_sales) * 2 / (actual_sales + forecasted_sales)) * 100

            st.write(f"MAPE: {mape:.2f}%")
            st.write(f"sMAPE: {smape:.2f}%")

            # Define dates to exclude
            exclude_dates = pd.to_datetime(['2023-11-23', '2023-12-25'])

            # Filter out the excluded dates
            mask = ~combined_sales.index.isin(exclude_dates)

            actual_excl = combined_sales.loc[mask, 'Actual Sales']
            mape_excl = np.mean(np.abs((actual_excl - forecasted_sales[mask]) / actual_excl)) * 100
            st.write(f"MAPE excluding the 2 spikes: {mape_excl:.2f}%")

            # Plot the actual and forecasted sales            
            plt.figure(figsize = (14, 7))
            plt.plot(combined_sales['Actual Sales'], label = 'Actual Sales', color = 'blue')
            plt.plot(combined_sales['Forecasted Sales'], label = 'Forecasted Sales', color = 'red', linestyle = '--')
            plt.title(f'Actual vs Forecasted Sales for Store {store_key}')
            plt.xlabel('Date')
            plt.ylabel('Sales')
            plt.legend()
            st.pyplot(plt)

if __name__ == "__main__":
    main()
