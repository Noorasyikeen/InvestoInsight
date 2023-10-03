def profit(end_price, start_price):
    profit = (end_price / start_price) -1
    return profit

def returns(end_price, start_price):
    returns = (end_price - start_price) / start_price * 100
    return returns
