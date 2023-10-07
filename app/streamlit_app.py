import streamlit as st
import datetime
import requests
from ii_model import

st.title("InvestoInsight")
st.write("See Tomorrow's Profits Today")
curr_time_raw = datetime.datetime.now()
current_time = curr_time_raw.strftime("%Y-%m-%d %H:%M:%S")
ticker = "MMM"
returns = "10%"
atr_period = 14

with st.sidebar.form(key='params_for_api'):
    ticker = st.text_input('Enter Ticker Symbol', value=ticker)
    start_date = st.date_input('Investment Date', value=datetime.datetime(2012, 10, 6, 12, 10, 20))
    end_date = st.date_input('Divestment Date', value=datetime.datetime(2012, 10, 6, 12, 10, 20))
    txn_price = st.number_input('Previously transacted price (optional)', value=40.20)
    option_raw = st.radio("Select an objective", ["Calculate Expected Return", "Suggest Ideal Divestment Date", "Show Future Direction"])
    st.form_submit_button('Submit')

if option_raw == "Calculate Expected Return":
    option = 1
elif option_raw == "Suggest Ideal Divestment Date":
    option = 2
elif option_raw == "Show Future Direction":
    option = 3

# params = dict(
#     ticker=ticker,
#     start_date=start_date,
#     end_date=end_date,
#     txn_price=txn_price,
#     option=option)

# api_url = 'https://taxifare.lewagon.ai/predict'
# response = requests.get(api_url, params=params)

prediction = response.json()

pred = prediction['fare']

st.header(f'Fare amount: ${round(pred, 2)}')
st.write(f"returns: {returns}")

df = pd.DataFrame(response["stock_prices"])

# Define function to plot chart
def plot_stock_prices(df):
    st.title("Stock Price Plot")
    fig = px.line(stock_prices_df, x="Date", y="stock_price", title="Stock Price Over Time",
                  labels={"stock_price": "Stock Price"},
                  hover_data={"stock_price": ":.2f"})
    fig.update_traces(mode="lines+markers")

    st.plotly_chart(fig)
# plot figure
plot_stock_prices(response)

# display values
st.write(f"Expected Returns: {response['expected_returns']}")
st.write(f"Profit: {response['profit']}")


#     if option == "Calculate Expected Return":
#         returns = get_returns(end_date_price, txn_price)
#         st.write("return/loss:", returns)
#         end_date_price = values_as_float[target_idx]
#         if txn_price:
#             expected_returns = get_returns(end_date_price, txn_price)
#             profit = get_profit(end_date_price, txn_price)
#         else:
#             expected_returns = get_returns(end_date_price, input_date_price)
#             profit = get_profit(end_date_price, input_date_price)

#     elif option == "Suggest Ideal Divestment Date":
#         divestment_month, price_at_divestment, profit, returns, stock_prices =
#         predictions.
#         returns = get_returns(end_date_price, txn_price)
#         st.write(f"ideal divestment month: {divestment_month}")
#         st.write(f"returns: {divestment_month}")

#     elif option == "Show Future Direction":
#         buy_month, sell_month, holding_period = future_direction()
#         returns = get_returns(end_date_price, txn_price)
#         st.write(f"direction: {divestment_month}")
#         st.write(f"returns: {divestment_month}")


#     ticker_data = stock_prices[stock_prices['Tickers'] == ticker]
#     stock_prices = ..(ticker_data)
#     fig_cs = mpf.plot(ticker_data, type='candle', style='charles',figsize=(12, 6))
#     plt.title(f'Stock Prices for {ticker}')
#     plt.xlabel('Date')
#     plt.ylabel('Price')
#     plt.legend()
#     plt.grid(True)
#     st.pyplot(fig_cs)



# # Load the pre-trained model
# loaded_model = load_pretrained_model()

# # Make predictions using the loaded model
# res = make_predictions(loaded_model, st_ticker)
# prediction_fig = res[0]
# interpretation_fig = res[1]
# mae_score = res[2]
# smape_score = res[3]
# price_predictions = res[4]

# # Calculate profit or loss
# max_price = max(price_predictions)
# max_month = price_predictions.index(max_price)

#     st.write(f"Latest News for {st_ticker} 📰")
#     st.write("To Insert News Segment")

# # Tensorboard
# %load ext tensorboard
# %tensorboard --logdir "lightning_logs/version_98"
