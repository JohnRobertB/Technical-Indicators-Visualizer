import tkinter as tk
from Stocks import InvestmentAnalyzer
from Fundamental_analysis import FundamentalAnalyzer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class UserInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Stocks")
        self.root.geometry("1600x900")

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

        # Create a canvas to display the image
        canvas = tk.Canvas(new_window)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add a scrollbar
        scroll = tk.Scrollbar(new_window, command=canvas.yview)
        scroll.pack(side=tk.LEFT, fill=tk.Y)
        canvas.config(yscrollcommand=scroll.set)

        # Create a frame inside the canvas to hold the images
        frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor='nw')

        # For each stock, create graphs and a table
        for ticker in tickers:
            # Use matplotlib to create the graphs
            fig, axs = plt.subplots(3, 1, figsize=(10, 15))  # Create 3 subplots

            # Create a graph for the investment analysis results
            axs[0].plot(investment_analyzer.hist[ticker].index, investment_analyzer.hist[ticker]['Close'], label=ticker)
            axs[0].set_title(f"{ticker} Close Price")
            axs[0].legend()

            window_sizes = [200, 50]  # 10-day and 50-day moving averages
            for window_size in window_sizes:
                moving_avg = investment_analyzer.hist[ticker]['Close'].rolling(window=window_size).mean()
                axs[0].plot(investment_analyzer.hist[ticker].index, moving_avg, label=f'{window_size} Day MA')

            # Create the RSI graph
            axs[1].plot(investment_analyzer.rsi[ticker].index, investment_analyzer.rsi[ticker], label=f'RSI {ticker}',
                        color='blue')
            axs[1].set_title(f"{ticker} RSI")
            axs[1].legend()

            # Create the MACD graph
            axs[2].plot(investment_analyzer.macd[ticker].index, investment_analyzer.macd[ticker]['MACD_12_26_9'],
                        label=f'MACD Line {ticker}', color='blue')
            axs[2].plot(investment_analyzer.macd[ticker].index, investment_analyzer.macd[ticker]['MACDs_12_26_9'],
                        label=f'Signal Line {ticker}', color='red')
            axs[2].bar(investment_analyzer.macd[ticker].index, investment_analyzer.macd[ticker]['MACDh_12_26_9'],
                       label=f'MACD Histogram {ticker}', color='grey', alpha=0.7)
            axs[2].set_title(f"{ticker} MACD")
            axs[2].legend()

            # Add the figure to the canvas
            canvas_fig = FigureCanvasTkAgg(fig, master=frame)
            canvas_fig.draw()
            canvas_fig.get_tk_widget().pack(expand=tk.YES, fill=tk.BOTH)

            # Create a table for the fundamental analysis results
            cell_text = [[fundamental_results.loc[ticker, col]] for col in fundamental_results.columns]
            table_frame = tk.Frame(frame)
            table_frame.pack(expand=tk.YES, fill=tk.X)
            for i, col in enumerate(fundamental_results.columns):
                tk.Label(table_frame, text=col, borderwidth=1, relief="solid").grid(row=0, column=i)
                tk.Label(table_frame, text=str(cell_text[i][0]), borderwidth=1, relief="solid").grid(row=1, column=i)

        # Update the scroll region of the canvas
        frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox(tk.ALL))

        # Display the new window
        new_window.mainloop()


# Create an instance of the user interface
root = tk.Tk()
ui = UserInterface(root)
root.mainloop()
