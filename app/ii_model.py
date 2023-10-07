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

import plotly.express as px
import pandas as pd


def update_options(option_raw):
    if option_raw == "Calculate Expected Return":
        option = 1
        price_predictions = predictions1['stock_prices']

    elif option_raw == "Suggest Ideal Divestment Date":
        option = 2
        price_predictions = predictions2['stock_prices']
    elif option_raw == "Show Future Direction":
        option = 3
        price_predictions = predictions3['stock_prices']
    return option, price_predictions

def model_run(option):
    if option == 1:
        returns = predictions1['expected_returns']
        profit = predictions1['profit']
        returns_text = f"Expected Returns: {returns}"
        profit_text = f"Expected Profit: {profit}"
        return returns_text, profit_text
    elif option == 2:
        returns = predictions2['returns']
        profit = predictions2['profit']
        divestment_month = predictions2['divestment_month']
        price_at_divestment = predictions2['price_at_divestment']
        divestment_month_text = f"Ideal Divestment Month: {divestment_month}"
        returns_text = f"Expected Returns: {returns}"
        profit_text = f"Expected Profit: {profit}"
        price_at_divestment_text = f"Expected Price at Divestment: {price_at_divestment}"
        return divestment_month_text, returns_text, profit_text, price_at_divestment_text
    elif option == 3:
        returns = predictions3['returns']
        profit = predictions3['profit']
        holding_period = predictions3['holding_period']
        sell_month = predictions3['sell_month']
        buy_month = predictions3['buy_month']
        returns_text = f"Expected Returns: {returns}"
        profit_text = f"Expected Profit: {profit}"
        buy_month_text = f"Ideal Buy Month: {buy_month}"
        sell_month_text = f"Ideal Sell Month: {sell_month}"
        holding_period_text = f"Ideal Holding Period: {holding_period}"
        return returns_text, profit_text, buy_month_text, sell_month_text, holding_period_text


# fig = px.line(stock_prices_df, x="Date", y="stock_price", title="Stock Price Over Time",
#               labels={"stock_price": "Stock Price"},
#               hover_data={"stock_price": ":.2f"})
# fig.update_traces(mode="lines+markers")

# fig.show()
