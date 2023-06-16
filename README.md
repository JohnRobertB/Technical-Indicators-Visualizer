# Technical-Indicators-Visualizer


This project is a Python script that analyzes stocks and visualizes several key technical indicators. It uses data from Yahoo Finance and the pandas_ta library to calculate these indicators.

Features

The script analyzes the following technical indicators:

50-day and 200-day Simple Moving Averages (SMA): These are used to identify potential buy and sell signals.
Relative Strength Index (RSI): This momentum oscillator is used to identify overbought or oversold conditions.
Moving Average Convergence Divergence (MACD): This trend-following momentum indicator shows the relationship between two moving averages of a stock's price.
For each stock that meets certain conditions, the script generates a PDF file with plots of these indicators.


Usage

Clone this repository.
Install the required Python packages: pandas, yfinance, pandas_ta, and matplotlib.
In the script, replace the tickers list with the list of tickers you want to analyze.
Run the script. For each analyzed ticker, a PDF file will be generated in the same directory as the script.


Disclaimer

This script is for informational purposes only and should not be used as the sole basis for making investment decisions. Always conduct your own research and consider consulting with a qualified financial advisor.
