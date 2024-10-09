import json
import webbrowser
import numpy as np
from datetime import datetime
import numpy_financial as npf  # Import numpy-financial for IRR calculation

def load_transaction_data(file_path):
    """Load JSON data from the specified file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def process_portfolio_summary(summary_data):
    """Process the summary data to initialize portfolio entries."""
    portfolio = {}
    for summary in summary_data:
        scheme = summary['schemeName']
        nav = float(summary['nav'])
        balance = float(summary['closingBalance'])
        market_value = balance * nav  # Market Value = Closing Balance * Current NAV
        portfolio[scheme] = {
            'current_nav': nav,
            'closing_balance': balance,
            'market_value': market_value,
            'total_acquisition_cost': 0,
            'net_units': 0,
            'transactions': []
        }
    return portfolio

def process_transactions(transaction_data, portfolio):
    """Process transactions and apply FIFO for redemptions."""
    for txn in transaction_data:
        scheme = txn['schemeName']
        units = float(txn['trxnUnits'])
        price = float(txn['purchasePrice']) if txn['purchasePrice'] else 0
        transaction_date = datetime.strptime(txn['trxnDate'], '%d-%b-%Y')
        
        if 'purchase' in txn['trxnDesc'].lower():
            portfolio[scheme]['transactions'].append({
                'units': units,
                'purchase_price': price,
                'date': transaction_date
            })
            portfolio[scheme]['net_units'] += units
            portfolio[scheme]['total_acquisition_cost'] += units * price  # Update acquisition cost
            
        elif 'redemption' in txn['trxnDesc'].lower() or 'sell' in txn['trxnDesc'].lower():
            to_sell = abs(units)
            while to_sell > 0 and portfolio[scheme]['transactions']:
                first = portfolio[scheme]['transactions'][0]
                if first['units'] <= to_sell:
                    to_sell -= first['units']
                    portfolio[scheme]['total_acquisition_cost'] -= first['units'] * first['purchase_price']
                    portfolio[scheme]['net_units'] -= first['units']
                    portfolio[scheme]['transactions'].pop(0)
                else:
                    first['units'] -= to_sell
                    portfolio[scheme]['total_acquisition_cost'] -= to_sell * first['purchase_price']
                    portfolio[scheme]['net_units'] -= to_sell
                    to_sell = 0
    return portfolio

def calculate_xirr(portfolio):
    """Calculate the XIRR of the portfolio."""
    cash_flows = []
    transaction_dates = []
    
    # Collect cash flows and transaction dates
    for scheme, info in portfolio.items():
        # Cash outflows for purchases
        for txn in info['transactions']:
            cash_flows.append(-txn['units'] * txn['purchase_price'])  # Cash outflow for purchases
            transaction_dates.append(txn['date'])

        # Cash inflows for redemptions
        if info['net_units'] < 0:  # If we sold units
            cash_flows.append(info['net_units'] * info['current_nav'])  # Cash inflow from selling
            transaction_dates.append(datetime.now())  # Today's date for the inflow
        
    # Current portfolio value as the final cash inflow
    total_current_value = sum(info['market_value'] for info in portfolio.values())
    cash_flows.append(total_current_value)  # Final inflow
    transaction_dates.append(datetime.now())  # Date of final inflow

    # Calculate XIRR using numpy-financial's irr function
    xirr = npf.irr(cash_flows)

    return xirr * 100 if xirr is not None else None  # Convert to percentage

def generate_report(portfolio, xirr):
    """Generate and display a report showing detailed calculations."""
    total_value = total_gain = 0
    report_lines = []

    # Add CSS styling
    report_lines.append("""
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f7f7f7; }
            h2 { text-align: center; }
            table { border-collapse: collapse; width: 100%; margin: 20px 0; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: center; }
            th { background-color: #4CAF50; color: white; }
            tr:nth-child(even) { background-color: #f2f2f2; }
            tr:hover { background-color: #ddd; }
            .calculation { text-align: left; }
        </style>
    </head>
    <body>
    <h2>Portfolio Summary</h2>
    <table>
        <tr>
            <th>Scheme</th>
            <th>Net Units</th>
            <th>Current NAV</th>
            <th>Market Value</th>
            <th>Total Acquisition Cost</th>
            <th>Gain</th>
        </tr>
    """)

    for scheme, info in portfolio.items():
        current_value = info['market_value']
        acquisition_cost = info['total_acquisition_cost']
        gain = current_value - acquisition_cost
        total_value += current_value
        total_gain += gain
        
        # Prepare row for HTML table
        report_lines.append(f"""
        <tr>
            <td class='calculation'>{scheme}</td>
            <td class='calculation'>{info['net_units']:.2f}</td>
            <td class='calculation'>₹{info['current_nav']:.2f}</td>
            <td class='calculation'>₹{current_value:.2f}</td>
            <td class='calculation'>₹{acquisition_cost:.2f}</td>
            <td class='calculation'>₹{gain:.2f}</td>
        </tr>
        """)
        
        # Add detailed calculations
        report_lines.append(f"<tr><td colspan='6' class='calculation'><strong>Calculations for {scheme}:</strong><br>")
        report_lines.append(f"Market Value = Closing Balance × Current NAV = {info['closing_balance']} × {info['current_nav']:.2f}<br>")
        report_lines.append(f"Total Acquisition Cost = Σ (Units × Purchase Price)<br>")

        for txn in info['transactions']:
            cost = txn['units'] * txn['purchase_price']
            report_lines.append(f"{txn['units']} units at ₹{txn['purchase_price']:.2f} = ₹{cost:.2f}<br>")
        
        report_lines.append(f"Gain = Market Value - Total Acquisition Cost = {current_value:.2f} - {acquisition_cost:.2f}<br>")
        report_lines.append("</td></tr>")

    # Final totals
    report_lines.append(f"""
        <tr style='background-color: #e6ffe6;'><td colspan='3'><strong>Total Portfolio Value:</strong></td>
        <td colspan='3'>₹{total_value:.2f}</td>
        </tr>
        <tr style='background-color: #e6ffe6;'><td colspan='3'><strong>Total Portfolio Gain:</strong></td>
        <td colspan='3'>₹{total_gain:.2f}</td>
        </tr>
        <tr style='background-color: #e6ffe6;'><td colspan='3'><strong>XIRR:</strong></td>
        <td colspan='3'>{xirr:.2f}%</td>
        </tr>
    </table>
    </body>
    </html>
    """)

    # Write to HTML file
    html_content = "".join(report_lines)
    with open('portfolio_summary.html', 'w', encoding='utf-8') as file:
        file.write(html_content)
    
    webbrowser.open('portfolio_summary.html')  # Open the report in Chrome

def main():
    file_path = 'transaction_detail.json'  # Specify the path to your JSON file here
    data = load_transaction_data(file_path)
    dt_summary = data['data'][0]['dtSummary']
    dt_transactions = data['data'][0]['dtTransaction']
    
    portfolio = process_portfolio_summary(dt_summary)
    portfolio = process_transactions(dt_transactions, portfolio)
    
    # Calculate XIRR
    xirr = calculate_xirr(portfolio)
    print(f"The XIRR of the portfolio is: {xirr:.2f}%")  # Output XIRR in the console
    
    generate_report(portfolio, xirr)

if __name__ == "__main__":
    main()
