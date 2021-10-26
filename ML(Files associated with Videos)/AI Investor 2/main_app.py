from typing import Final
from pandas.core.reshape.pivot import pivot_table
import yfinance as yf
import pandas as pd
import time
import math   
from sklearn.ensemble import RandomForestClassifier
import numpy as np
data = pd.read_csv("constituents_csv.csv")

listOfSymbols = []
for symbol in data.Symbol:
    listOfSymbols.append(symbol)

symbols_not_found = ["BRK.B", "OGN", "BF.B"]

def get_correct_input_from_user(text_to_use):
    i = input(text_to_use)
    got_response = False
    while not got_response:
        try:
            a = int(i)
            got_response = True
        except ValueError:
            print("Please enter a correct number...")
            i = input(text_to_use)
    return i

def get_user_selected_stocks():
    u = input("Please enter the tickers of stocks seperated by space..")
    return u.split(" ")

def user_selected_analysis(selected, income):
    market_cap = []
    closing_price = []
    for symbol in selected:
        current_data = yf.download(symbol, start="2021-09-16", end="2021-10-16")
        closing_price.append(current_data.Close[-1])
        market_cap.append(current_data.Close[-1]*current_data.Volume[-1])
    s = sum(market_cap)
    stocks_to_purchase = []
    for i,cap in enumerate(market_cap):
        portion = (income * cap )/s
        stocks_to_purchase.append(math.floor(portion / closing_price[i]))
    df = pd.DataFrame({"Ticker":selected,"stocks_to_buy":stocks_to_purchase})
    return df

def get_num_of_stocks():
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
    return how_many_stocks

def calculate_label(parameter):
    changes = []
    for j in range(len(parameter)-1):
        changes.append(parameter[j+1] - parameter[j])
    for i in changes:
        if i > 0:
            return 1
        elif i <= 0:
            return -1

def make_X_and_Y(close_prices,period = 6,in_future = 3):
    X = []
    y = []
    for i in range(len(close_prices)-period-in_future):
        X.append(close_prices[i:i+period])
        l = list(close_prices[i + period :i+period+in_future])
        y.append(calculate_label(l))
    return X,y

def return_model(X,y):
    clf = RandomForestClassifier()
    clf.fit(X,y)
    return clf

period = 6
predicted_prices_for_tommorrow = []
volatility_for_stocks = []
new_symbols_for_df = []
end_day_price = []
volumnes = []
def stock_data_loop():
    print("Wait for some time, I am analyzing " +str(how_many_stocks)+ " stocks")
    for current_symbol in listOfSymbols[0:how_many_stocks]:
        # Getting the past 6 months of data
        if current_symbol not in symbols_not_found:
            print("Currently, analysing " + current_symbol, " .......")
            new_symbols_for_df.append(current_symbol)
            current_data = yf.download(current_symbol, start="2021-04-16", end="2021-10-16")
            close_prices = current_data.Close
            volumnes.append(current_data.Volume[-1])
            volatility = close_prices.std()
            volatility_for_stocks.append(volatility)
            features, dependent_variable = make_X_and_Y(list(close_prices))
            features = np.array(features)
            dependent_variable = np.array(dependent_variable)
            clf = return_model(features, dependent_variable)
            latest_feat = np.array(list(close_prices)[-period:]).reshape((1,-1))
            tommorow_prediction = clf.predict(latest_feat)
            end_day_price.append(close_prices[-1])
            if tommorow_prediction[0] == 1:
                predicted_prices_for_tommorrow.append("BUY NOW")
            elif tommorow_prediction[0] == -1:
                predicted_prices_for_tommorrow.append("SELL NOW")
    full_data = pd.DataFrame({"symbol":new_symbols_for_df, "volatility":volatility_for_stocks,
                    "tommorrow":predicted_prices_for_tommorrow, "price":end_day_price, "Volumne":volumnes})
    return full_data

def allot_funds(data,income):
    if data.shape[0] > 5:
        new_data = data.head(5)
        vols = new_data.Volumne
        price = new_data.price
        mar_cap = vols * price
        portion = mar_cap / sum(mar_cap)
        income_distribution = portion*income
        stocks_to_buy = income_distribution / price
        stocks_to_buy = [math.floor(i) for i in stocks_to_buy]
        new_data["number_of_stocks_to_buy"] = stocks_to_buy
        print(new_data)
    else:
        vols = data.Volumne
        price = data.price
        mar_cap = vols * price
        portion = mar_cap / sum(mar_cap)
        income_distribution = portion*income
        stocks_to_buy = income_distribution / price
        stocks_to_buy = [math.floor(i) for i in stocks_to_buy]
        data["number_of_stocks_to_buy"] = stocks_to_buy
        print(data)

income = get_correct_input_from_user(text_to_use="How much money do you have to invest? ")
time.sleep(2)
print("Do you wish to add your own stocks or want ML to recommend you one?")
do_you_know_your_portfolio = get_correct_input_from_user("\nEnter 1 for adding your own stocks\nEnter 2 for ML recommendations. ")
if int(do_you_know_your_portfolio) == 1:
    your_stocks = get_user_selected_stocks()
    c = user_selected_analysis(your_stocks, int(income))
    print(c)
elif int(do_you_know_your_portfolio) == 2:
    how_many_stocks = get_num_of_stocks()
    final_data = stock_data_loop()
    print("Stocks you should consider purchasing right now.....")
    print(final_data[final_data.tommorrow == "BUY NOW"])
    print("Stocks you should consider selling right now.....")
    print(final_data[final_data.tommorrow == "SELL NOW"])
    print("Top 5 stocks recommendation for you are....")
    to_buy_data = final_data[final_data.tommorrow == "BUY NOW"]
    allot_funds(to_buy_data, int(income))
else:
    print("Enter only 1 or 2. No other numbers are accepted")