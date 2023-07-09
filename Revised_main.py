import json
import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox, Button
from ttkthemes import ThemedTk
from tkinter import font as tkfont
from Stocks import InvestmentAnalyzer
from Fundamental_analysis import FundamentalAnalyzer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import subprocess
from matplotlib.backends.backend_pdf import PdfPages
import os
import easygui


class UserInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Investment Analyser")
        self.root.geometry("550x250")


        # Load stocks
        self.load_stocks()
        self.selected_stocks = {}
        self.stock_vars = {}

        # Frame for stocks with scrollbar
        stock_frame = ttk.Frame(root)
        stock_frame.grid(row=0, column=0, sticky='nsew', rowspan=4)
        canvas = tk.Canvas(stock_frame)
        scrollbar = ttk.Scrollbar(stock_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')


        # Button font
        button_font = tkfont.Font(size=40,font=("Helvetica"))
        #add stock item button
        self.add_button = Button(root, text="New Stock", font=button_font, command= self.add_stock,relief="flat")
        self.add_button.grid(column=0, row=5, sticky="SEW")

        #remove stock item button
        self.remove_button = Button(root,text='x',font=button_font, command = self.remove_stock,relief='flat')
        self.remove_button.grid(row=5, column=0, sticky='SE')

        # Button for analyzing stocks
        self.analyze_button = Button(root, text="Analyze", command=self.analyze,relief='flat',font=button_font)
        self.analyze_button.grid(row=5, column=1, sticky='SEW')

        # Treeview for displaying stocks
        style = ttk.Style(root)
        style.configure("Treeview",font=(None,13))
        style.configure("Treeview.Heading",font=(None,15,'bold'))
        self.tree = ttk.Treeview(root)
        self.tree["columns"] = ("Stocks")
        self.tree.column("#0", width=0, stretch="NO")
        self.tree.column("Stocks", anchor="w", width=100)
        self.tree.heading("#0", text="", anchor="w")
        self.tree.heading("Stocks", text="Stocks", anchor="center")
        self.tree.grid(row=0, column=0, rowspan=4, padx=5, pady=5, sticky='nsew')

        #time period selection
        self.time_period = ttk.Combobox(root,
                                        values=["3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"])
        self.time_period.grid(row=0, column=1, sticky='NEW', padx=5, pady=5)
        self.time_period.set("1y")  # default value

        # Add stocks to the scrollable area
        for index, stock in enumerate(self.stocks):
            self.add_stock_to_gui(stock, index)

        #bind the event handlers for defined buttons
        self.add_button.bind("<Enter>", lambda e: self.on_enter(e, self.add_button))
        self.add_button.bind("<Leave>", lambda e: self.on_leave(e, self.add_button))

        self.remove_button.bind("<Enter>", lambda e: self.on_enter(e, self.remove_button))
        self.remove_button.bind("<Leave>", lambda e: self.on_leave(e, self.remove_button))

        self.analyze_button.bind("<Enter>", lambda e: self.on_enter(e, self.analyze_button))
        self.analyze_button.bind("<Leave>", lambda e: self.on_leave(e, self.analyze_button))

    def on_enter(self, e, button):
        button['background'] = 'lightgrey'

    def on_leave(self, e, button):
        button['background'] = 'SystemButtonFace'

    def add_stock(self):
        def callback(stock):
            if stock and stock not in self.stocks:
                self.stocks.append(stock)
                self.add_stock_to_gui(stock, len(self.stocks) - 1)
                self.save_stocks()
            else:
                messagebox.showerror("Error", "Please enter a valid stock ticker.")

        AddStockDialog(self.root, callback)

    def remove_stock(self):
        selected_ticker = self.tree.selection()[0]
        item = self.tree.item(selected_ticker)
        ticker_to_remove = item['values'][0].lower()  # Convert to lowercase

        if ticker_to_remove in self.stocks:
            self.stocks.remove(ticker_to_remove)  # Update self.stocks list
        else:
            print(f"Error: '{ticker_to_remove}' not found in self.stocks list")
        self.tree.delete(selected_ticker)
        self.save_stocks()  # Save updated list


    def load_stocks(self):
        if os.path.exists("stocks.json"):
            with open("stocks.json", 'r') as file:
                try:
                    self.stocks = json.load(file)
                except json.JSONDecodeError:
                    self.stocks = []
        else:
            self.stocks = []

    def save_stocks(self):
        with open("stocks.json", 'w') as file:
            json.dump(self.stocks, file)

    def add_stock_to_gui(self, stock, index):
        # Add stock to Treeview

        self.tree.insert("", "end", values=(stock.upper(),))


    def analyze(self):
        selected_tickers = [self.tree.item(item, "values")[0] for item in self.tree.selection()]


        if selected_tickers:
            time_period = self.time_period.get()
            fundamental_results = self.run_fundamental_analysis(selected_tickers)
            investment_analyzer = self.run_investment_analysis(selected_tickers,time_period)
            self.display_analysis_results(selected_tickers, fundamental_results, investment_analyzer)
        else:
            print("no stocks selected ")

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

    def run_investment_analysis(self, tickers,time_period):
        # Run the investment analysis
        investment_analyzer = InvestmentAnalyzer(tickers,time_period)
        investment_analyzer.analyze_data()
        return investment_analyzer

    def display_analysis_results(self, tickers, fundamental_results, investment_analyzer):
        try:


            with PdfPages('analysis_results.pdf') as pdf:
            # For each stock, create graphs and a table
                for ticker in tickers:
                    # Use matplotlib to create the graphs
                    fig, axs = plt.subplots(4, 1, figsize=(10, 15))  # Create 4 subplots

                    if '.jo' in ticker.lower():
                        close_prices = investment_analyzer.hist[ticker]['Close']/100
                        currency_label  = "Price (ZAR)"
                    else:
                        close_prices = investment_analyzer.hist[ticker]['Close']
                        currency_label = 'Price (USD)'



                    # Create a graph for the investment analysis results
                    axs[0].plot(investment_analyzer.hist[ticker].index, close_prices)
                    axs[0].set_title(f"{ticker} Close Price")
                    axs[0].set_ylabel(currency_label)

                    if self.time_period == "1y":
                        window_sizes = [200, 50]
                    elif self.time_period == "6mo":
                        window_sizes = [120, 30]
                    elif self.time_period == "3mo":
                        window_sizes = [60, 15]
                    else:
                        window_sizes = [200, 50]  # Default to 200 and 50 if time period is not recognized

                    # Plot the moving averages
                    for window_size in window_sizes:
                        moving_avg = close_prices.rolling(window=window_size).mean()
                        axs[0].plot(investment_analyzer.hist[ticker].index, moving_avg, label=f'{window_sizes} Day MA')

                    # Get the last close price and its date
                    last_close_price = close_prices.iloc[-1]
                    last_close_price= round(last_close_price,2)

                    axs[0].text(0.85, 1.02, f'Last Close: {last_close_price}{currency_label[6:]}', transform=axs[0].transAxes, ha='center',
                                fontsize=10)

                    # Calculate Bollinger Bands

                    rolling_mean = close_prices.rolling(window=20).mean()
                    rolling_std = close_prices.rolling(window=20).std()
                    upper_band = rolling_mean + (rolling_std * 2)
                    lower_band = rolling_mean - (rolling_std * 2)

                    # Plot Bollinger Bands
                    if self.time_period.get() in ['3mo','6mo','1y']:
                        axs[0].plot(upper_band.index, upper_band, color='lightgray')
                        axs[0].plot(lower_band.index, lower_band, color='lightgray')

                    # Create the RSI graph
                    axs[1].plot(investment_analyzer.rsi[ticker].index, investment_analyzer.rsi[ticker],color='blue')
                    axs[1].set_title(f"{ticker} RSI")
                    axs[1].set_ylabel("RSI")


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
                    axs[2].set_ylabel("MACD Value")


                    # Create the Stochastic Oscillator graph
                    axs[3].plot(investment_analyzer.stoch[ticker].index, investment_analyzer.stoch[ticker]['STOCHk_14_3_3'],
                                label='K Line', color='blue')
                    axs[3].plot(investment_analyzer.stoch[ticker].index, investment_analyzer.stoch[ticker]['STOCHd_14_3_3'],
                                label='D Line', color='red')

                    # Add horizontal lines at 80 and 20
                    axs[3].axhline(80, color='gray', linestyle='dashed', alpha=0.6, label='Overbought (80)')
                    axs[3].axhline(20, color='gray', linestyle='dashed', alpha=0.6, label='Oversold (20)')

                    axs[3].set_title(f"{ticker} Stochastic Oscillator")
                    axs[3].set_ylabel("%K and %D")


                    axs[0].legend()
                    axs[1].legend()
                    axs[2].legend()
                    axs[3].legend()



                    pdf.savefig(fig)

                    # Create a new figure for the fundamental analysis results table
                    fig, ax = plt.subplots(figsize=(12.65, 1))
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
                            indicator = "Positive" if value < 15 else "Negative" if value > 30 else "Neutral"
                        elif col == "EPS":
                            # Positive EPS might be considered good
                            indicator = "Positive" if value > 0 else "Negative"
                        elif col == "Dividend Yield":
                            # Higher dividend yield might be considered good
                            indicator = "Positive" if value > 0.03 else "Neutral"
                        elif col == "Price to Book":
                            # Lower P/B might indicate undervalued
                            indicator = "Positive" if value < 1 else "Negative"
                        elif col == "Debt to Equity":
                            # Lower debt-to-equity is generally considered better
                            indicator = "Positive" if value < 0.5 else "Negative"
                        elif col == "Return on Equity":
                            # Higher ROE indicates efficient use of equity to generate profits
                            indicator = "Positive" if value > 0.15 else "Negative"

                        # Add the indicator to the table
                        table_data.append([col, value, indicator])



                    # Add the table to the figure
                    ax.table(cellText=table_data, colLabels=["Metric", "Value", "Indicator"], cellLoc='center',
                             loc='center')

                    # Save the table figure to the PDF
                    pdf.savefig(fig, bbox_inches='tight')

        except FileNotFoundError as e:
            print(f"Error: File not found. Details: {e}")
        except ValueError as e:
            print(f"Error: Invalid value. Details {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        try:
            # Open the PDF file using the default PDF viewer
            if os.name == 'nt':  # For Windows
                os.startfile('analysis_results.pdf')
            elif os.name == 'posix':  # For MacOS and Linux
                subprocess.run(['open', 'analysis_results.pdf'])
            else:
                print("Could not open the PDF file. Please open 'analysis_results.pdf' manually.")

        except Exception as e:
            print(f"Error opening the PDF file: {e}")

class AddStockDialog(ttk.Frame):
    def __init__(self, parent, callback):
        self.top = tk.Toplevel(parent)
        self.top.title("New Stock")
        self.top.geometry('160x110')
        ttk.Label(self.top, text="Please enter new stock:",font=('Helvetica')).grid(row=0, column=0, padx=5, pady=5)

        self.stock_entry = ttk.Entry(self.top)
        self.stock_entry.grid(row=1, column=0, padx=5, pady=5)

        add_button = Button(self.top, text="Add", command=self.add_stock,relief='flat')
        add_button.grid(row=2, column=0,sticky='SW')

        cancel_button = Button(self.top,text="cancel",command=self.top.destroy,relief='flat')
        cancel_button.grid(row=2,column=0,sticky='SE')

        self.callback = callback

        # Center the dialog
        self.top.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.top.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.top.winfo_height() // 2)
        self.top.geometry("+%d+%d" % (x, y))

    def add_stock(self):
        stock = self.stock_entry.get()
        self.callback(stock)
        self.top.destroy()

# Create an instance of the user interface
root = ThemedTk(theme='breeze')
root.minsize(550, 250)
#root.resizable(False, False)
ui = UserInterface(root)


# Configure the grid column and row to fill the entire window
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.mainloop()
