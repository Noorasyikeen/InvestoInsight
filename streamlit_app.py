import streamlit as st
import datetime

import pandas as pd
import numpy as np


curr_time_raw = datetime.datetime.now()
current_time = curr_time_raw.strftime("%Y-%m-%d %H:%M:%S")

st.title("InvestoInsight")
st.write("See Tomorrow's Profits Today 😵‍")

st_ticker = st.sidebar.text_input('Enter ticker: ', 'AAPL')
start_date = st.sidebar.text_input('Enter investment date: ', '01/09/2021')
end_date = st.sidebar.text_input('Enter potential divestment date: ', '01/03/2024')
objective = st.sidebar.selectbox("Select an objective", ["Expected Return", "Ideal Divestment Date"])

# st.write("\nSee Results Below‍")
# st.text_input(f'Returns of {st_ticker} from start_date to end_date')


csv_df = pd.read_csv(r'/Users/zoeyneo/code/zoeyneo/investoinsight/SP500_bal_income.csv')
columns_to_keep = ['fiscalDateEnding', 'totalRevenue','Symbol', 'shortTermDebt', 'longTermDebt', 'totalShareholderEquity', 'commonStockSharesOutstanding', 'netIncome', 'operatingExpenses', 'reportedCurrency_y','inventory','totalCurrentAssets', 'totalCurrentLiabilities', 'currentNetReceivables', 'costofGoodsAndServicesSold']
df = csv_df.loc[:,columns_to_keep]
df['fiscalDateEnding'] = pd.to_datetime(df['fiscalDateEnding'])
df['shortTermDebt'] = pd.to_numeric(df['shortTermDebt'], errors='coerce').convert_dtypes()
df['longTermDebt'] = pd.to_numeric(df['longTermDebt'], errors='coerce').convert_dtypes()
df['totalShareholderEquity'] = pd.to_numeric(df['totalShareholderEquity'], errors='coerce').convert_dtypes()
df['netIncome'] = pd.to_numeric(df['netIncome'], errors='coerce').convert_dtypes()
df['commonStockSharesOutstanding'] = pd.to_numeric(df['commonStockSharesOutstanding'], errors='coerce').convert_dtypes()
df['netIncome'] = pd.to_numeric(df['netIncome'], errors='coerce').convert_dtypes()
df['totalCurrentLiabilities'] = pd.to_numeric(df['totalCurrentLiabilities'], errors='coerce').convert_dtypes()
df['totalCurrentAssets'] = pd.to_numeric(df['totalCurrentAssets'], errors='coerce').convert_dtypes()
df['inventory'] = pd.to_numeric(df['inventory'], errors='coerce').convert_dtypes()
df['operatingExpenses'] = pd.to_numeric(df['operatingExpenses'], errors='coerce').convert_dtypes()
df['totalRevenue'] = pd.to_numeric(df['totalRevenue'], errors='coerce').convert_dtypes()
df['currentNetReceivables'] = pd.to_numeric(df['currentNetReceivables'], errors='coerce').convert_dtypes()
df['costofGoodsAndServicesSold'] = pd.to_numeric(df['costofGoodsAndServicesSold'], errors='coerce').convert_dtypes()

#solvency ratio
df['debt_to_equity'] = (df['shortTermDebt'] + df['longTermDebt']) / df['totalShareholderEquity']
# print(df['debt_to_equity'].dtype)

#profitability
df['price'] = 1 #arbitrary number
df['Dividend'] = 2 #arbitrary number
df['eps'] =  (df['netIncome'] - df['Dividend']) / df['commonStockSharesOutstanding']
df['return_on_equity'] = df['netIncome'] / df['totalShareholderEquity']

#liquidity ratio
df['quick ratio'] = (df['totalCurrentAssets'] - df['inventory']) /  df['totalCurrentLiabilities']

#efficiency ratio
df['operating_ratio'] = (df['operatingExpenses'] + df['costofGoodsAndServicesSold']) / df['totalRevenue']
df['inventory_turnover'] = df['costofGoodsAndServicesSold'] / df['inventory']

if st.sidebar.button("Submit"):
    st.write(f"Results for {st_ticker} from {start_date} to {end_date}.")
    st.write(f"_last refreshed on {current_time}_")
    st.write(f"📈📉 to insert charts here. random df below for fun")
    st.write(df.head(5))
    if objective == "Expected Return":
        st.write(f"to insert expected returns")
    if objective == "Ideal Divestment Date":
        st.write(f"to insert ideal end date")

    st.write(f"Latest News for {st_ticker} 📰")
    st.write("To Insert News Segment")
