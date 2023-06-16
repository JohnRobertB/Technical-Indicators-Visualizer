import yfinance as yf
import pandas as pd

class InvestmentAnalyzer:
    def __init__(self, tickers):
        self.tickers = tickers

    def calculate_sma(self, data, window):
        return data.rolling(window=window).mean()

    def analyze_data(self):
        # Create a DataFrame to store the analysis results
        results = pd.DataFrame(columns=["Ticker", "Current Price", "50-day SMA", "200-day SMA"])

        # Fetch data for all tickers at once
        data = yf.download(self.tickers, period="1y")

        for ticker in self.tickers:
            # Check if any data was returned
            if data['Close', ticker].empty:
                print(f"No data for {ticker}, skipping.")
                continue

            # Calculate the 50-day and 200-day simple moving averages
            sma_50 = self.calculate_sma(data['Close', ticker], 50)
            sma_200 = self.calculate_sma(data['Close', ticker], 200)

            # Get the most recent price
            current_price = data['Close', ticker].iloc[-1]

            # If the current price is higher than both SMAs, add the data to the results DataFrame
            if current_price > sma_50.iloc[-1] and current_price > sma_200.iloc[-1]:
                results = results._append({"Ticker": ticker, "Current Price": current_price, "50-day SMA": sma_50.iloc[-1], "200-day SMA": sma_200.iloc[-1]}, ignore_index=True)

        return results

# List of tickers to analyze
# This would be replaced with a list of all tickers in the exchange
tickers = ["AAPL", "MSFT", "GOOGL", "AMZN"]

analyzer = InvestmentAnalyzer(tickers)
print(analyzer.analyze_data())
