# Portfolio Value and Gain Calculation

**Total Portfolio Value**: ₹4089696.79  
**Total Portfolio Gain**: ₹1577193.56  
**XIRR**: 0.34%  

This project calculates the current portfolio value and gain based on transaction data using Python. The script processes transaction details to compute the total portfolio value, total gain, and optionally the XIRR (Extended Internal Rate of Return).

## Objective

The main objectives of this project are:

1. **Calculate the Total Portfolio Value**:
   - The total portfolio value is calculated as:
     \[
     \text{Total Portfolio Value} = \sum (\text{Leftover Units} \times \text{NAV of Scheme})
     \]
   - Here, NAV (Net Asset Value) is the price per unit of the scheme, and leftover units refer to the units still held after all transactions have been processed.

2. **Calculate the Total Portfolio Gain**:
   - Total portfolio gain is calculated as:
     \[
     \text{Total Portfolio Gain} = \sum (\text{Current Unit Value} - \text{Unit Acquisition Cost})
     \]
   - Where:
     - Current Unit Value is given by:
       \[
       \text{Current Unit Value} = \text{Current NAV} \times \text{Number of Units}
       \]
     - Unit Acquisition Cost is calculated as:
       \[
       \text{Unit Acquisition Cost} = \text{Units} \times \text{Purchase Price}
       \]

3. **Calculate XIRR (Optional)**:
   - XIRR is calculated based on the following:
     - **Date of Transaction**
     - **Amount of Transaction** (cash flow)
     - **Current Portfolio Value** (final cash flow)
   - The formula for calculating XIRR considers the timing of cash flows and their respective amounts.

## Requirements

- Python 3.x
- Libraries:
  - `numpy`
  - `numpy-financial`
  - `mstarpy`

You can install the required libraries using pip:

```bash
pip install numpy numpy-financial mstarpy
