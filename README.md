# fund_calculator
# Portfolio Calculator

This Python script calculates the total portfolio value and gain for mutual fund transactions based on transaction data provided in a JSON format. The script uses the `mstarpy` library to fetch the current Net Asset Value (NAV) for the funds involved.

## Features

- Load transaction data from a JSON file.
- Fetch the current NAV of funds based on their ISIN.
- Calculate the total portfolio value and gain using a First-In-First-Out (FIFO) approach for transactions.
- Display results in a user-friendly table using Tkinter.

## Requirements

Make sure you have the following libraries installed:

- `json`
- `datetime`
- `numpy`
- `numpy_financial`
- `mstarpy`
- `tkinter`

You can install `mstarpy` and other required libraries using pip:

```bash
pip install mstarpy numpy numpy-financial
