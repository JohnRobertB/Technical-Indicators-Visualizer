import tkinter as tk
from Stocks import InvestmentAnalyzer
from Fundamental_analysis import FundamentalAnalyzer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import subprocess
from matplotlib.backends.backend_pdf import PdfPages
import os


class UserInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Stocks")
        self.root.geometry("1600x900")

        # List of default stocks
        default_stocks = ["SOL.JO", "MSFT", "GOOGL", "AMZN", "TSLA"]

        # Create a Listbox for the default stocks
        self.listbox = tk.Listbox(root, selectmode=tk.MULTIPLE)
        for stock in default_stocks:
            self.listbox.insert(tk.END, stock)

        self.listbox.pack()
        # Create a scrollbar for the Listbox
        scrollbar = tk.Scrollbar(root)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)

        # Create an entry field for manual stock ticker input
        self.ticker_entry = tk.Entry(root)
        self.ticker_entry.pack()

        # Create a button to add stocks to the list
        add_button = tk.Button(root, text="Add Stock", command=self.add_stock)
        add_button.pack()

        # Create a button to start the analysis
        button = tk.Button(root, text="Analyze", command=self.analyze)
        button.pack()

    def add_stock(self):
        # Get the stock ticker from the entry field
        stock = self.ticker_entry.get().strip()

        # Add the stock to the listbox
        if stock:
            self.listbox.insert(tk.END, stock)

        # Clear the entry field
        self.ticker_entry.delete(0, tk.END)

    def analyze(self):
        tickers = self.get_selected_tickers()
        fundamental_results = self.run_fundamental_analysis(tickers)
        investment_analyzer = self.run_investment_analysis(tickers)
        self.display_analysis_results(tickers, fundamental_results, investment_analyzer)

    def get_selected_tickers(self):
        # Get selected stocks from the Listbox
        selected_stocks = [self.listbox.get(i) for i in self.listbox.curselection()]

        # Get stocks from the Entry widget and filter out empty strings
        manual_stocks = [stock.strip() for stock in self.ticker_entry.get().split(',') if stock.strip()]

        return selected_stocks + manual_stocks

    def run_fundamental_analysis(self, tickers):
        # Run the fundamental analysis
        fundamental_analyzer = FundamentalAnalyzer(tickers)
        return fundamental_analyzer.analyze_data()

    def run_investment_analysis(self, tickers):
        # Run the investment analysis
        investment_analyzer = InvestmentAnalyzer(tickers)
        investment_analyzer.analyze_data()
        return investment_analyzer

    def display_analysis_results(self, tickers, fundamental_results, investment_analyzer):


        with PdfPages('analysis_results.pdf') as pdf:
        # For each stock, create graphs and a table
            for ticker in tickers:
                # Use matplotlib to create the graphs
                fig, axs = plt.subplots(4, 1, figsize=(10, 15))  # Create 4 subplots

                # Create a graph for the investment analysis results
                axs[0].plot(investment_analyzer.hist[ticker].index, investment_analyzer.hist[ticker]['Close'], label=ticker)
                axs[0].set_title(f"{ticker} Close Price")
                axs[0].legend()

                window_sizes = [200, 50]  # 200-day and 50-day moving averages
                for window_size in window_sizes:
                    moving_avg = investment_analyzer.hist[ticker]['Close'].rolling(window=window_size).mean()
                    axs[0].plot(investment_analyzer.hist[ticker].index, moving_avg, label=f'{window_size} Day MA')

                    # Get the last close price and its date
                    last_close_price = investment_analyzer.hist[ticker]['Close'].iloc[-1]

                    axs[0].text(0.85, 1.02, f'Last Close: {last_close_price}', transform=axs[0].transAxes, ha='center',
                                fontsize=10)

                    # Calculate Bollinger Bands
                    rolling_mean = investment_analyzer.hist[ticker]['Close'].rolling(window=20).mean()
                    rolling_std = investment_analyzer.hist[ticker]['Close'].rolling(window=20).std()
                    upper_band = rolling_mean + (rolling_std * 2)
                    lower_band = rolling_mean - (rolling_std * 2)

                    # Plot Bollinger Bands
                    axs[0].plot(upper_band.index, upper_band, label='Upper Bollinger Band', color='lightgray')
                    axs[0].plot(lower_band.index, lower_band, label='Lower Bollinger Band', color='lightgray')

                    # Create the RSI graph
                    axs[1].plot(investment_analyzer.rsi[ticker].index, investment_analyzer.rsi[ticker],
                                label=f'RSI {ticker}',
                                color='blue')
                    axs[1].set_title(f"{ticker} RSI")
                    axs[1].legend()

                    last_rsi = investment_analyzer.rsi[ticker].iloc[-1]
                    # Add horizontal lines at 70 and 30
                    axs[1].axhline(70, color='red', linestyle='dashed', alpha=0.6, label='Overbought (70)')
                    axs[1].axhline(30, color='green', linestyle='dashed', alpha=0.6, label='Oversold (30)')

                    # Add buy/sell indicator based on RSI
                    if last_rsi < 30:
                        indicator = 'Potential Buy'
                    elif last_rsi > 70:
                        indicator = 'Potential Sell'
                    else:
                        indicator = 'Neutral'

                    # Add text at the top right of the RSI graph
                    axs[1].text(1, 1.02, f'Indicator: {indicator}', transform=axs[1].transAxes, ha='right', fontsize=10,
                                va='bottom')

                    # Create the MACD graph
                    macd_data = investment_analyzer.macd[ticker]
                    macd_line = investment_analyzer.macd[ticker]['MACD_12_26_9']
                    signal_line = investment_analyzer.macd[ticker]['MACDs_12_26_9']
                    dates = investment_analyzer.macd[ticker].index

                    axs[2].plot(dates, macd_line, label='MACD Line', color='blue')
                    axs[2].plot(dates, signal_line, label='Signal Line', color='red')
                    axs[2].bar(dates, investment_analyzer.macd[ticker]['MACDh_12_26_9'], label='MACD Histogram',
                               color='grey',
                               alpha=0.7)

                    # Check for crossovers
                    last_crossover = None
                    last_crossover_type = None
                    for i in range(1, len(macd_line)):
                        if macd_line[i] > signal_line[i] and macd_line[i - 1] <= signal_line[i - 1]:
                            axs[2].annotate('Buy', xy=(macd_data.index[i], macd_line[i]),
                                            xytext=(macd_data.index[i], macd_line[i] + 0.5),
                                            arrowprops=dict(facecolor='green', arrowstyle='->'), fontsize=8, color='green')
                            last_crossover = dates[i]
                            last_crossover_type = 'Buy'
                        elif macd_line[i] < signal_line[i] and macd_line[i - 1] >= signal_line[i - 1]:
                            axs[2].annotate('Sell', xy=(macd_data.index[i], macd_line[i]),
                                            xytext=(macd_data.index[i], macd_line[i] - 0.5),
                                            arrowprops=dict(facecolor='red', arrowstyle='->'), fontsize=8, color='red')
                            last_crossover = dates[i]
                            last_crossover_type = 'Sell'

                    # Annotate the last crossover at the top right corner of the graph
                    if last_crossover is not None:
                        color = 'green' if last_crossover_type == 'Buy' else 'red'
                        axs[2].text(1, 1.065, f'Last Signal: {last_crossover_type} ({last_crossover.strftime("%Y-%m-%d")})',
                                    color=color, fontsize=10,
                                    ha='right', va='top', transform=axs[2].transAxes)

                    axs[2].set_title(f"{ticker} MACD")
                    axs[2].legend()

                    # Create the Stochastic Oscillator graph
                    axs[3].plot(investment_analyzer.stoch[ticker].index, investment_analyzer.stoch[ticker]['STOCHk_14_3_3'],
                                label='K Line', color='blue')
                    axs[3].plot(investment_analyzer.stoch[ticker].index, investment_analyzer.stoch[ticker]['STOCHd_14_3_3'],
                                label='D Line', color='red')

                    # Add horizontal lines at 80 and 20
                    axs[3].axhline(80, color='gray', linestyle='dashed', alpha=0.6, label='Overbought (80)')
                    axs[3].axhline(20, color='gray', linestyle='dashed', alpha=0.6, label='Oversold (20)')

                    axs[3].set_title(f"{ticker} Stochastic Oscillator")
                    axs[3].legend()







                pdf.savefig(fig)

                # Create a new figure for the fundamental analysis results table
                fig, ax = plt.subplots(figsize=(10, 1))
                ax.axis('tight')
                ax.axis('off')

                # Create a table with fundamental analysis data
                columns = fundamental_results.columns.tolist()
                table_data = []
                indicators = []

                for i, col in enumerate(columns):
                    value = fundamental_results.loc[ticker, col]
                    indicator = ""

                    if col == "Market Cap":
                        # No specific rule for Market Cap, it's more for information
                        indicator = "Info"
                    elif col == "Trailing PE":
                        # Simplified rule: lower P/E might indicate undervalued
                        indicator = "Potential Buy" if value < 15 else "Potential Sell" if value > 30 else "Neutral"
                    elif col == "EPS":
                        # Positive EPS might be considered good
                        indicator = "Potential Buy" if value > 0 else "Potential Sell"
                    elif col == "Dividend Yield":
                        # Higher dividend yield might be considered good
                        indicator = "Potential Buy" if value > 0.03 else "Neutral"
                    elif col == "Price to Book":
                        # Lower P/B might indicate undervalued
                        indicator = "Potential Buy" if value < 1 else "Potential Sell"
                    elif col == "Debt to Equity":
                        # Lower debt-to-equity is generally considered better
                        indicator = "Potential Buy" if value < 0.5 else "Potential Sell"
                    elif col == "Return on Equity":
                        # Higher ROE indicates efficient use of equity to generate profits
                        indicator = "Potential Buy" if value > 0.15 else "Potential Sell"

                    # Add the indicator to the table
                    table_data.append([col, value, indicator])



                # Add the table to the figure
                ax.table(cellText=table_data, colLabels=["Metric", "Value", "Indicator"], cellLoc='center',
                         loc='center')

                # Save the table figure to the PDF
                pdf.savefig(fig, bbox_inches='tight')



        # Open the PDF file using the default PDF viewer
        if os.name == 'nt':  # For Windows
            os.startfile('analysis_results.pdf')
        elif os.name == 'posix':  # For MacOS and Linux
            subprocess.run(['open', 'analysis_results.pdf'])
        else:
            print("Could not open the PDF file. Please open 'analysis_results.pdf' manually.")






# Create an instance of the user interface
root = tk.Tk()
ui = UserInterface(root)
root.mainloop()
