import yfinance as yf
import pandas as pd
import concurrent.futures
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import FuncFormatter
import datetime

class FundamentalAnalyzer:
    def __init__(self, tickers):
        self.tickers = tickers

    def analyze_ticker(self, ticker):
        try:
            data = yf.Ticker(ticker)
            info = data.info
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return None

        fundamentals = {
            'Market Cap': info.get('marketCap'),
            'Trailing PE': info.get('trailingPE'),
            'EPS': info.get('trailingEps'),
            'Dividend Yield': info.get('dividendYield', 0),
            'Price to Book': info.get('priceToBook'),
            'Debt to Equity': info.get('debtToEquity'),
            'Return on Equity': info.get('returnOnEquity'),

        }

        return pd.Series(fundamentals, name=ticker)

    def analyze_data(self):
        results = pd.DataFrame()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.analyze_ticker, ticker) for ticker in self.tickers]

            for future in concurrent.futures.as_completed(futures):
                result = future.result()

                if result is not None:
                    results = results._append(result)


        return results


