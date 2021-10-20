import yfinance as yf
import pandas as pd
# from sklearn.linear_model import LinearRegression
# from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
import numpy as np

how_many_stocks = input("How many stocks you want to analyse? Enter atleast 10 and max 500\n")
correct = False
while not correct:
    try:
        how_many_stocks = int(how_many_stocks)
        if how_many_stocks > 500 or how_many_stocks < 10:
            raise ValueError
        correct = True
    except: 
        print("Please enter a correct number. ")
        how_many_stocks = input("How many stocks you want to analyse? Enter atleast 10 and max 500..\n")

data = pd.read_csv("constituents_csv.csv")

listOfSymbols = []
for symbol in data.Symbol:
    listOfSymbols.append(symbol)

symbols_not_found = ["BRK.B", "OGN", "BF.B"]

today = "2021-10-17"

def make_X_and_Y(close_prices,period = 6):
    X = []
    y = []
    for i in range(len(close_prices)-period):
        X.append(close_prices[i:i+period])
        y.append(close_prices[i+period])
    return X,y

def return_model(X,y):
    clf = RandomForestRegressor()
    clf.fit(X,y)
    return clf

period = 6
predicted_prices_for_tommorrow = []
today_prices = []
volatility_for_stocks = []
new_symbols_for_df = []
for current_symbol in listOfSymbols[0:how_many_stocks]:
    # Getting the past 6 months of data
    if current_symbol not in symbols_not_found:
        print("Currenly, analysing " + current_symbol, " .......")
        new_symbols_for_df.append(current_symbol)
        current_data = yf.download(current_symbol, start="2021-04-16", end="2021-10-16")
        close_prices = current_data.Close
        volatility = close_prices.std()
        volatility_for_stocks.append(volatility)
        features, dependent_variable = make_X_and_Y(list(close_prices))
        features = np.array(features)
        dependent_variable = np.array(dependent_variable)
        clf = return_model(features, dependent_variable)
        latest_feat = np.array(list(close_prices)[-period:]).reshape((1,-1))
        tommorow_prediction = clf.predict(latest_feat)
        predicted_prices_for_tommorrow.append(tommorow_prediction[0])
        today_prices.append(close_prices[-1])
    
full_data = pd.DataFrame({"symbol":new_symbols_for_df, "volatility":volatility_for_stocks,
                        "today":today_prices, "tommorrow":predicted_prices_for_tommorrow})

strategy = input("Which strategy do you want to use? \nEnter 1 for Conservatibe\nEnter 2 for Aggressive\n")
has_given_response = False
while not has_given_response:
    if strategy == "1":
        has_given_response = True
        new = full_data.sort_values(by="volatility", ascending=True)
        new = new[new.tommorrow > new.today]
        print("Top conservative stocks are...")
        print(new.head())
    elif strategy == "2":
        has_given_response = True
        new = full_data.sort_values(by="volatility", ascending=False)
        new = new[new.tommorrow > new.today]
        print("Top aggressive stocks are...")
        print(new.head())
    else:
        print("Please enter a correct number. ")
        strategy = input("Which strategy do you want to use? \nEnter 1 for Conservatibe\nEnter 2 for Aggressive\n")
