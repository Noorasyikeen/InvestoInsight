import streamlit as st
import datetime
import requests
import time
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd

st.title("InvestoInsight")
st.write("See Tomorrow's Profits Today")
curr_time_raw = datetime.datetime.now()
current_time = curr_time_raw.strftime("%Y-%m-%d %H:%M:%S")
ticker = "MMM"
returns = "10%"

# Option 1

predictions1 = {
'expected_returns': -14.706674270412186,
'profit': -26.53153432210283,
'stock_prices': {
'Date': {
0: "2022-10",
1: "2022-11",
2: "2022-12",
3: "2023-01",
4: "2023-02",
5: "2023-03",
6: "2023-04",
7: "2023-05",
8: "2023-06",
9: "2023-07",
10: "2023-08",
11: "2023-09",
12: "2023-10",
13: "2023-11",
14: "2023-12",
15: "2024-01",
16: "2024-02",
17: "2024-03"
},
'stock_price': {
0: 145.54059600830078,
1: 146.02073720296224,
2: 140.34157180786133,
3: 133.7596524556478,
4: 146.6453857421875,
5: 153.10020395914714,
6: 162.50614267985026,
7: 170.56929575602214,
8: 180.4047185262044,
9: 180.4047185262044,
10: 180.4047185262044,
11: 180.4047185262044,
12: 150.46664428710938,
13: 154.19998168945312,
14: 153.02330017089844,
15: 153.87318420410156,
16: 154.6261444091797,
17: 155.0585174560547
}
}
}

# Option 2
predictions2 = {

'returns': -14.049633112267006,
'profit': -25.346201070149704,
'price_at_divestment': 155.0585174560547,
'divestment_month': "2024-03",
'stock_prices':
{
'Date':
{
0: "2022-10",
1: "2022-11",
2: "2022-12",
3: "2023-01",
4: "2023-02",
5: "2023-03",
6: "2023-04",
7: "2023-05",
8: "2023-06",
9: "2023-07",
10: "2023-08",
11: "2023-09",
12: "2023-10",
13: "2023-11",
14: "2023-12",
15: "2024-01",
16: "2024-02",
17: "2024-03"
},
'stock_price':
{
0: 145.54059600830078,
1: 146.02073720296224,
2: 140.34157180786133,
3: 133.7596524556478,
4: 146.6453857421875,
5: 153.10020395914714,
6: 162.50614267985026,
7: 170.56929575602214,
8: 180.4047185262044,
9: 180.4047185262044,
10: 180.4047185262044,
11: 180.4047185262044,
12: 150.46664428710938,
13: 154.19998168945312,
14: 153.02330017089844,
15: 153.87318420410156,
16: 154.6261444091797,
17: 155.0585174560547
}
}
}

# Option 3
predictions3 = {

'returns': 3.051754886075241,
'profit': 4.5918731689453125,
'holding_period': 5,
'stock_prices':
{
'Date':
{
0: "2022-10",
1: "2022-11",
2: "2022-12",
3: "2023-01",
4: "2023-02",
5: "2023-03",
6: "2023-04",
7: "2023-05",
8: "2023-06",
9: "2023-07",
10: "2023-08",
11: "2023-09",
12: "2023-10",
13: "2023-11",
14: "2023-12",
15: "2024-01",
16: "2024-02",
17: "2024-03"
},
'stock_price':
{
0: 145.54059600830078,
1: 146.02073720296224,
2: 140.34157180786133,
3: 133.7596524556478,
4: 146.6453857421875,
5: 153.10020395914714,
6: 162.50614267985026,
7: 170.56929575602214,
8: 180.4047185262044,
9: 180.4047185262044,
10: 180.4047185262044,
11: 180.4047185262044,
12: 150.46664428710938,
13: 154.19998168945312,
14: 153.02330017089844,
15: 153.87318420410156,
16: 154.6261444091797,
17: 155.0585174560547
}
},
'index_diff': 5,
'sell_month': "2023-03",
'buy_month': "2022-10"
}




def update_options(option_raw):
    if option_raw == "Calculate Expected Return":
        option = 1
        # price_predictions = response['stock_prices']

    elif option_raw == "Suggest Ideal Divestment Date":
        option = 2
        # price_predictions = response['stock_prices']
    elif option_raw == "Show Future Direction":
        option = 3
        # price_predictions = response['stock_prices']
    return option #, price_predictions

# fig = px.line(stock_prices_df, x="Date", y="stock_price", title="Stock Price Over Time",
#               labels={"stock_price": "Stock Price"},
#               hover_data={"stock_price": ":.2f"})
# fig.update_traces(mode="lines+markers")

# fig.show()


with st.sidebar.form(key='params_for_api'):
    option_raw = st.radio("Select an objective", ["Calculate Expected Return", "Suggest Ideal Divestment Date", "Show Future Direction"])
    ticker = st.text_input('Enter Ticker Symbol', value=ticker)
    investment_date = st.date_input('Investment Date', value=datetime.datetime(2023, 8, 5, 12, 10, 20))
    divestment_date = st.date_input('Divestment Date', value=datetime.datetime(2023, 12, 6, 12, 10, 20))
    txn_price = st.number_input('Previously transacted price (optional)', value=40.20)
    if st.form_submit_button("Submit"):
        # option, price_predictions = update_options(option_raw)
        option = update_options(option_raw=option_raw)

# Function to simulate data loading
def simulate_data_loading():
    # Simulate a time-consuming data loading process
    for _ in range(5):
        time.sleep(1)

# Display the loading animation
loading_placeholder = st.empty()
loading_placeholder.image("loading_indicator.gif",
                          use_column_width=True,
                          caption="Crunching the latest data, just for you...")

# Simulate data loading (replace this with your actual data loading code)
simulate_data_loading()

uvicorn_server_url = "http://localhost:8050/predict/"

investment_date = investment_date.strftime("%Y-%m")
divestment_date = divestment_date.strftime("%Y-%m")

params = {
    "ticker": ticker,
    "input_date": investment_date,
    "option": update_options(option_raw=option_raw),
}

if divestment_date is not None:
    params["end_date"] = divestment_date

if txn_price is not None:
    params["txn_price"] = txn_price

# response = requests.get("http://localhost:8050/predict?ticker=AAPL&input_date=2023-08&option=2")
response = requests.get(uvicorn_server_url, params=params)

# Check the response status code and content
if response.status_code == 200:
    # If the status code is 200 (OK), you can access the response content
    response_content = response.text
    print("Response Content:")
    print(response_content)
else:
    # Handle other status codes (e.g., 404 for not found, 500 for internal server error)
    print(f"Received status code: {response.status_code}")
print(response)
response = response.json()
df = pd.DataFrame(response["stock_prices"])

def model_run(option):
    if option == 1:
        returns = round(response['expected_returns'], 2)
        profit = round(response['profit'], 2)
        returns_text = f"Expected Returns: {returns}%"
        profit_text = f"Expected Profit: {profit} per share"

        return returns_text, profit_text

    elif option == 2:
        returns = round(response['returns'], 2)
        profit = round(response['profit'], 2)
        divestment_month = response['divestment_month']
        price_at_divestment = round(response['price_at_divestment'], 3)
        divestment_month_text = f"Ideal Divestment Month: {divestment_month}"
        returns_text = f"Expected Returns: {returns}%"
        profit_text = f"Expected Profit: {profit} per share"
        price_at_divestment_text = f"Expected Price at Divestment: USD{price_at_divestment}"

        return divestment_month_text, returns_text, profit_text, price_at_divestment_text

    elif option == 3:
        returns = round(response['returns'], 2)
        profit = round(response['profit'], 2)
        holding_period = response['holding_period']
        sell_month = response['sell_month']
        buy_month = response['buy_month']
        returns_text = f"Expected Returns: {returns}%"
        profit_text = f"Expected Profit: {profit} per share"
        buy_month_text = f"Ideal Buy Month: {buy_month}"
        sell_month_text = f"Ideal Sell Month: {sell_month}"
        holding_period_text = f"Ideal Holding Period: {holding_period}"

        return returns_text, profit_text, buy_month_text, sell_month_text, holding_period_text


# Remove the loading animation once data is loaded
loading_placeholder.empty()

if 'option' in locals():
    # result = model_run(option)
    st.title(f"Result for {ticker}")
    st.write(f"Results for {ticker} last refreshed on {current_time}")
    tab1, tab2, tab3 = st.tabs(["Show Results", "Show Trends", "Dataset"])
    result = model_run(option=option)

    with tab1:
        for i in range(len(result)):
            st.write(result[i])
    with tab2:
        fig = plt.figure(figsize=(12, 6))
        fig = px.line(df, x="Date", y="stock_price", title=f"Stock Price for {ticker}",
                    labels={"stock_price": "Stock Price"},
                    hover_data={"stock_price": ":.2f"})
        fig.update_traces(mode="lines+markers")
        st.plotly_chart(fig)
    with tab3:
        st.write(df)
