import yfinance as yf
import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


class InvestmentAnalyzer:
    def __init__(self, tickers,time_period):
        self.tickers = tickers
        self.time_period = time_period
        self.hist = {}
        self.rsi = {}
        self.macd = {}
        self.stoch = {}

    def calculate_sma(self, data, window):
        return data.rolling(window=window).mean()

    def analyze_ticker(self, ticker):
        data = yf.Ticker(ticker)
        hist = data.history(period=self.time_period)

        # Check if any data was returned
        if hist.empty:
            print(f"No data for {ticker}, skipping.")
            return None
        self.hist[ticker] = hist

        # Calculate the 14-day RSI
        self.rsi[ticker] = ta.rsi(hist['Close'], length=14)

        # Calculate the MACD
        self.macd[ticker] = ta.macd(hist['Close'])

        # Calculate the Stochastic Oscillator
        stoch = ta.stoch(hist['High'], hist['Low'], hist['Close'])
        self.stoch[ticker] = stoch

        return None

    def analyze_data(self):
        for ticker in self.tickers:
            self.analyze_ticker(ticker)


