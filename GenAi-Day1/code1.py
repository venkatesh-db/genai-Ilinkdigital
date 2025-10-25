

from datetime import datetime

'''
Flow of code 

1.  list of dict 
2.  Loop through each row
3.  Convert Date Convert numerical fields
4.  add to new list if valid
5.   doing same process for energy data
6.   doing same process for stock_data 
7.  print cleaned data


'''


# ------------------------------
# Sample data as lists of dictionaries
stock_data = [
    {"Date": "2025-10-19", "Stock": "AAPL", "Open": "170.5", "Close": "", "Volume": "50000"},
    {"Date": "2025-10-20", "Stock": "GOOGL", "Open": "", "Close": "2900.0", "Volume": ""},
    {"Date": "invalid", "Stock": "MSFT", "Open": "330.0", "Close": "335.0", "Volume": "100000"},
]

energy_data = [
    {"Date": "2025-10-19", "Energy_Type": "Solar ", "Consumption": "1000", "Price": "50"},
    {"Date": "2025-10-20", "Energy_Type": "wind", "Consumption": "", "Price": ""},
    {"Date": "", "Energy_Type": "Hydro", "Consumption": "500", "Price": "30"},
]

# ------------------------------
# Clean stock data
clean_stock = []
for row in stock_data:
    # Convert Date
    try:
        row['Date'] = datetime.strptime(row['Date'], "%Y-%m-%d")
    except:
        row['Date'] = None
    
    # Convert numerical fields
    row['Open'] = float(row['Open']) if row['Open'] else 0.0
    row['Close'] = float(row['Close']) if row['Close'] else 0.0
    row['Volume'] = int(row['Volume']) if row['Volume'] else 0
    
    # Keep only valid rows
    if row['Date'] and row['Stock']:
        clean_stock.append(row)

# ------------------------------
# Clean energy data
clean_energy = []
for row in energy_data:
    # Convert Date
    try:
        row['Date'] = datetime.strptime(row['Date'], "%Y-%m-%d")
    except:
        row['Date'] = None
    
    # Convert numerical fields
    row['Consumption'] = float(row['Consumption']) if row['Consumption'] else 0.0
    row['Price'] = float(row['Price']) if row['Price'] else 0.0
    
    # Clean categorical
    row['Energy_Type'] = row['Energy_Type'].strip().lower() if row['Energy_Type'] else "unknown"
    
    # Keep only valid rows
    if row['Date'] and row['Energy_Type']:
        clean_energy.append(row)

# ------------------------------
# Print cleaned data
print("Clean Stock Data:")
for row in clean_stock:
    print(row)

print("\nClean Energy Data:")
for row in clean_energy:
    print(row)
