import yfinance as yf
import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


class InvestmentAnalyzer:
    def __init__(self, tickers):
        self.tickers = tickers

    def calculate_sma(self, data, window):
        return data.rolling(window=window).mean()

    def analyze_ticker(self, ticker):
        data = yf.Ticker(ticker)
        hist = data.history(period="1y")

        # Check if any data was returned
        if hist.empty:
            print(f"No data for {ticker}, skipping.")
            return None

        # Calculate the 50-day and 200-day simple moving averages
        sma_50 = self.calculate_sma(hist['Close'], 50)
        sma_200 = self.calculate_sma(hist['Close'], 200)

        # Calculate the 14-day RSI
        rsi = ta.rsi(hist['Close'], length=14)

        # Calculate the MACD
        macd = ta.macd(hist['Close'])

        # Get the most recent price
        current_price = hist['Close'].iloc[-1]

        # If the current price is higher than both SMAs, plot the data
        if current_price > sma_50.iloc[-1] and current_price > sma_200.iloc[-1]:
            # Create a new PDF file
            with PdfPages(f'{ticker}_plots.pdf') as pdf:
                # Plot the current price, 50-day SMA, and 200-day SMA
                plt.figure(figsize=(14, 7))
                plt.plot(hist.index, hist['Close'], label='Close Price', color='blue')
                plt.plot(sma_50.index, sma_50, label='50-day SMA', color='red')
                plt.plot(sma_200.index, sma_200, label='200-day SMA', color='green')
                plt.title(f'{ticker} Price and SMAs')
                plt.legend()
                pdf.savefig()  # saves the current figure into a pdf page
                plt.close()

                # Plot the RSI
                plt.figure(figsize=(14, 7))
                plt.title(f'{ticker} Relative Strength Index')
                plt.plot(rsi.index, rsi, label='RSI', color='blue')
                plt.axhline(0, linestyle='--', alpha=0.1, color='black')
                plt.axhline(20, linestyle='--', alpha=0.5, color='orange')
                plt.axhline(30, linestyle='--', color='red')
                plt.axhline(70, linestyle='--', color='red')
                plt.axhline(80, linestyle='--', alpha=0.5, color='orange')
                plt.axhline(100, linestyle='--', alpha=0.1, color='black')
                plt.legend()
                pdf.savefig()  # saves the current figure into a pdf page
                plt.close()

                # Plot the MACD
                plt.figure(figsize=(14, 7))
                plt.plot(macd.index, macd['MACD_12_26_9'], label='MACD Line', color='blue')
                plt.plot(macd.index, macd['MACDs_12_26_9'], label='Signal Line', color='red')
                plt.bar(macd.index, macd['MACDh_12_26_9'], label='MACD Histogram', color='grey', alpha=0.7)
                plt.title(f'{ticker} MACD')
                plt.legend()
                pdf.savefig()  # saves the current figure into a pdf page
                plt.close()

        return None

    def analyze_data(self):
        for ticker in self.tickers:
            self.analyze_ticker(ticker)

# List of tickers to analyze
# This would be replaced with a list of all tickers in the exchange
tickers = ["AAPL", "MSFT", "GOOGL", "AMZN"]

analyzer = InvestmentAnalyzer(tickers)
analyzer.analyze_data()
