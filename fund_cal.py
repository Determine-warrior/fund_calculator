import json
import datetime
import numpy as np
import numpy_financial as npf
from mstarpy import Funds
from concurrent.futures import ThreadPoolExecutor
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

# Cache to store NAV results
nav_cache = {}

# Load Transaction Data from the JSON File
def load_transactions(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        return data['data']

# Fetch the current NAV of a fund using ISIN (with caching)
def get_current_nav(isin):
    if isin in nav_cache:
        return nav_cache[isin]
    
    try:
        fund = Funds(term=isin, country="in")
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=365)
        history = fund.nav(start_date=start_date, end_date=end_date, frequency="daily")

        if history:
            nav_cache[isin] = history[-1]['nav']
            return history[-1]['nav']
    except Exception as e:
        print(f"Error fetching NAV for {isin}: {e}")
    
    return None

# Parallel NAV fetch
def fetch_nav_parallel(isins):
    with ThreadPoolExecutor() as executor:
        navs = list(executor.map(get_current_nav, isins))
    return navs

# FIFO method to handle sell transactions and remaining units
def apply_fifo(purchase_history, units_sold, current_nav):
    gain = 0
    while units_sold > 0 and purchase_history:
        purchase_units, purchase_price = purchase_history[0]
        if purchase_units > units_sold:
            gain += units_sold * (current_nav - purchase_price)
            purchase_history[0] = (purchase_units - units_sold, purchase_price)
            units_sold = 0
        else:
            gain += purchase_units * (current_nav - purchase_price)
            purchase_history.pop(0)
            units_sold -= purchase_units
    return gain

# Process transactions and calculate portfolio values
def process_transactions(transactions):
    portfolio = {}
    total_portfolio_value = 0
    total_portfolio_gain = 0

    isins = {trxn['isin'] for data in transactions for trxn in data['dtSummary']}
    nav_results = fetch_nav_parallel(list(isins))
    
    for isin, nav in zip(isins, nav_results):
        nav_cache[isin] = nav

    for data in transactions:
        for trxn in data['dtSummary']:
            isin = trxn['isin']
            folio = trxn['folio']
            units = float(trxn['closingBalance'])
            purchase_price = float(trxn['nav'])

            if (isin, folio) not in portfolio:
                portfolio[(isin, folio)] = {
                    'remaining_units': 0,
                    'purchase_history': [],
                    'current_nav': nav_cache.get(isin, 0)
                }

            if units > 0:
                portfolio[(isin, folio)]['remaining_units'] += units
                portfolio[(isin, folio)]['purchase_history'].append((units, purchase_price))
            elif units < 0:
                current_nav = portfolio[(isin, folio)]['current_nav']
                gain = apply_fifo(portfolio[(isin, folio)]['purchase_history'], -units, current_nav)
                portfolio[(isin, folio)]['remaining_units'] += units
                total_portfolio_gain += gain

    for (isin, folio), data in portfolio.items():
        remaining_units = data['remaining_units']
        current_nav = data['current_nav']

        if remaining_units > 0 and current_nav:
            current_value = remaining_units * current_nav
            acquisition_cost = sum(units * price for units, price in data['purchase_history'])
            gain = current_value - acquisition_cost
            total_portfolio_value += current_value
            total_portfolio_gain += gain

    return total_portfolio_value, total_portfolio_gain, portfolio

# Function to create and display results in a table
def display_results(total_value, total_gain, portfolio):
    # Create a new window for displaying results
    results_window = tk.Tk()
    results_window.title("Portfolio Summary")
    
    # Create a Treeview for the table
    tree = ttk.Treeview(results_window, columns=("ISIN", "Folio", "Remaining Units", "Current Value"), show="headings")
    
    # Define the column headings
    tree.heading("ISIN", text="Fund ISIN")
    tree.heading("Folio", text="Folio Number")
    tree.heading("Remaining Units", text="Remaining Units")
    tree.heading("Current Value", text="Current Value")
    
    # Add scrollbar
    scrollbar = ttk.Scrollbar(results_window, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    
    # Pack the scrollbar
    scrollbar.pack(side='right', fill='y')

    # Insert data into the treeview
    for (isin, folio), data in portfolio.items():
        remaining_units = data['remaining_units']
        current_value = remaining_units * data['current_nav']
        tree.insert("", "end", values=(isin, folio, f"{remaining_units:.2f}", f"{current_value:.2f}"))

    # Pack the Treeview
    tree.pack(expand=True, fill='both')

    # Display total value and gain
    total_label = tk.Label(results_window, text=f"Total Portfolio Value: {total_value:.2f}\nTotal Portfolio Gain: {total_gain:.2f}")
    total_label.pack(pady=10)

    # Run the Tkinter main loop
    results_window.mainloop()

# Main function
def main():
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Open a file dialog to choose a JSON file
    file_path = filedialog.askopenfilename(
        title="Select Transaction JSON File",
        filetypes=[("JSON files", "*.json")]
    )

    if not file_path:
        print("No file selected. Exiting.")
        return

    try:
        transactions = load_transactions(file_path)
        total_value, total_gain, portfolio = process_transactions(transactions)
        display_results(total_value, total_gain, portfolio)  # Display the results in a table

    except KeyError as e:
        messagebox.showerror("Error", f"Key error: {e}. Check the structure of the JSON file.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Run the program
if __name__ == "__main__":
    main()
