import yfinance as yf
import pandas as pd
import concurrent.futures
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import FuncFormatter

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
            'Dividend Yield': info.get('dividendYield',0),
            'Price to Book': info.get('priceToBook'),
            'Debt to Equity': info.get('debtToEquity'),
            'Return on Equity': info.get('returnOnEquity')
        }

        # Validate the data
        for key, value in fundamentals.items():
            if value is None and key != "Dividend Yield":
                print(f"Missing {key} for {ticker}")
                return None

        return pd.Series(fundamentals, name=ticker)

    def analyze_data(self):
        results = pd.DataFrame()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.analyze_ticker, ticker) for ticker in self.tickers]

            for future in concurrent.futures.as_completed(futures):
                result = future.result()

                if result is not None:
                    results = results._append(result)

        # Perform some basic analysis
        print("Average values:")
        print(results.mean())

        # Create a PDF file to save the plots
        with PdfPages('fundamental_analysis_plots.pdf') as pdf:
            # Create a bar plot for each metric
            for column in results.columns:
                ax = results[column].plot(kind='bar', title=column)
                ax.set_ylabel(column)  # Set the y-axis label to the metric name
                ax.set_xlabel('Ticker')  # Set the x-axis label to 'Ticker'
                ax.legend()  # Add a legend

                # Format the y-axis labels
                if column == 'Market Cap':
                    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x / 1e12:.1f}T'))  # Format in trillions
                elif column in ['Trailing PE', 'Price to Book', 'Debt to Equity', 'Return on Equity']:
                    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.2f}'))  # Format with 2 decimal places
                elif column == 'EPS':
                    ax.yaxis.set_major_formatter(
                        FuncFormatter(lambda x, _: f'{x:.2f}$'))  # Format with 2 decimal places and a dollar sign
                elif column == 'Dividend Yield':
                    ax.yaxis.set_major_formatter(
                        FuncFormatter(lambda x, _: f'{x * 100:.2f}%'))  # Format as a percentage

                pdf.savefig()  # saves the current figure into a pdf page
                plt.close()

        return results


