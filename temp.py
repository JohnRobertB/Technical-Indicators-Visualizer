import tkinter as tk
from Stocks import InvestmentAnalyzer
from Fundamental_analysis import FundamentalAnalyzer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class UserInterface:
    def __init__(self, root):
        self.root = root

        # List of default stocks
        default_stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]

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

        # Create a button to start the analysis
        button = tk.Button(root, text="Analyze", command=self.analyze)
        button.pack()

    def analyze(self):
        # Get selected stocks from the Listbox
        selected_stocks = [self.listbox.get(i) for i in self.listbox.curselection()]

        # Get stocks from the Entry widget and filter out empty strings
        manual_stocks = [stock.strip() for stock in self.ticker_entry.get().split(',') if stock.strip()]

        tickers = selected_stocks + manual_stocks

        # Run the fundamental analysis
        fundamental_analyzer = FundamentalAnalyzer(tickers)
        fundamental_results = fundamental_analyzer.analyze_data()

        # Run the investment analysis
        investment_analyzer = InvestmentAnalyzer(tickers)
        investment_analyzer.analyze_data()

        # Create a new window
        new_window = tk.Toplevel(self.root)
        new_window.title("Analysis Results")

        # Use matplotlib to create the graphs
        fig, axs = plt.subplots(10, 1, figsize=(5, 50))  # Create 10 subplots

        # Create a graph for each fundamental analysis result
        for i, column in enumerate(fundamental_results.columns):
            axs[i].bar(fundamental_results.index, fundamental_results[column])
            axs[i].set_title(column)

        # Create a graph for the investment analysis results
        for ticker in tickers:
            axs[7].plot(investment_analyzer.hist[ticker].index, investment_analyzer.hist[ticker]['Close'], label=ticker)
        axs[7].set_title("Close Price")
        axs[7].legend()  # Add a legend to the graph

        # Create the RSI graph
        for ticker in tickers:
            axs[8].plot(investment_analyzer.rsi[ticker].index, investment_analyzer.rsi[ticker], label=f'RSI {ticker}',
                        color='blue')
        axs[8].set_title("RSI")
        axs[8].legend()  # Add a legend to the graph

        # Create the MACD graph
        for ticker in tickers:
            axs[9].plot(investment_analyzer.macd[ticker].index, investment_analyzer.macd[ticker]['MACD_12_26_9'],
                        label=f'MACD Line {ticker}', color='blue')
            axs[9].plot(investment_analyzer.macd[ticker].index, investment_analyzer.macd[ticker]['MACDs_12_26_9'],
                        label=f'Signal Line {ticker}', color='red')
            axs[9].bar(investment_analyzer.macd[ticker].index, investment_analyzer.macd[ticker]['MACDh_12_26_9'],
                       label=f'MACD Histogram {ticker}', color='grey', alpha=0.7)
        axs[9].set_title("MACD")
        axs[9].legend()  # Add a legend to the graph

        # Create a canvas to display the graphs
        canvas = FigureCanvasTkAgg(fig, master=new_window)  # A tk.DrawingArea.
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Display the new window
        new_window.mainloop()


# Create an instance of the user interface
root = tk.Tk()
ui = UserInterface(root)
root.mainloop()
