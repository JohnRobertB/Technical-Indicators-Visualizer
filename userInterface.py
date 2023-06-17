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
        new_window.geometry("1600x900")

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
            axs[1].plot(investment_analyzer.rsi[ticker].index, investment_analyzer.rsi[ticker], label=f'RSI {ticker}',
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
            axs[2].bar(dates, investment_analyzer.macd[ticker]['MACDh_12_26_9'], label='MACD Histogram', color='grey',
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
                axs[2].text(1, 1.065, f'Last Signal: {last_crossover_type}', color=color, fontsize=10,
                            ha='right', va='top', transform=axs[2].transAxes)

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

                # Add indicators
                value = cell_text[i][0]
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
                tk.Label(table_frame, text=indicator, borderwidth=1, relief="solid").grid(row=2, column=i)

        # Update the scroll region of the canvas
        frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox(tk.ALL))

        # Display the new window
        new_window.mainloop()


# Create an instance of the user interface
root = tk.Tk()
ui = UserInterface(root)
root.mainloop()
