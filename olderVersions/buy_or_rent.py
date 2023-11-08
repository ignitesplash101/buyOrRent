import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.font_manager as fm
from matplotlib.backends.backend_pdf import PdfPages
import os

os.chdir(r'C:\Users\ignit\OneDrive\Desktop\Python\personal projects\buy or rent')

pdf_pages = PdfPages('output_graphs.pdf')

fm.findSystemFonts(fontpaths=None, fontext='ttf')
plt.rcParams['font.family'] = 'Meiryo'

def calculate_mortgage(PV, r, n):
    """Calculate monthly mortgage given loan amount, monthly interest rate, and number of months."""
    return PV * r * (1 + r)**n / ((1 + r)**n - 1)

def investment_growth(principal, rate, years):
    """Calculate growth of an investment over a period."""
    return principal * ((1 + rate)**years)

def random_expenses(probability, size):
    return np.random.binomial(n=1, p=probability) * np.random.randint(1, size)

# main function

def buy_vs_rent_outcome(personal, rent_details, property_details, market, costs, property_type="house"):
    years = property_details["duration_rent"]
    months = years * 12
    
    # Track outcomes over time
    net_worth_rent = np.zeros(months)
    net_worth_buy = np.zeros(months)

    # Calculate mortgage monthly payment
    mortgage_payment = calculate_mortgage(property_details["purchase_price"] - property_details["down_payment"], personal["loan_interest"], property_details["duration_buy"])
    
    # Initial savings
    savings_rent = personal["down_payment"]
    savings_buy = personal["down_payment"] - property_details["purchase_price"]

    for i in range(months):
        # Tax credit calculation
        tax_credit = 0
        if property_type == "house" or property_type == "manshon":
            if 0 < i <= 10*12:  # First 10 years
                tax_credit = personal["loan_interest"] * 0.007 * property_details["purchase_price"]

        monthly_savings_rent = personal["monthly_income"] - rent_details["monthly_rent"] - personal["monthly_expenses"] + rent_details["annual_rent_increase"]
        monthly_savings_buy = personal["monthly_income"] - mortgage_payment + tax_credit - costs["insurance"] - costs["bank_fees"] - costs["misc_fees"] - property_details["maintenance"] - property_details["property_tax"] - personal["monthly_expenses"]
        
        # Random large expenses
        large_expense = random_expenses(0.05, 100000)  # 5% chance of a random large expense up to 100,000 yen
        monthly_savings_rent -= large_expense
        monthly_savings_buy -= large_expense

        # Savings after expenses
        savings_rent += monthly_savings_rent
        savings_buy += monthly_savings_buy
        
        # Investment growth
        savings_rent = investment_growth(savings_rent, market["investment_rate"]/12, 1/12)
        savings_buy = investment_growth(savings_buy, market["investment_rate"]/12, 1/12)
        land_appreciation = property_details["land_value"] * ((1 + property_details["land_appreciation_rate"]) ** (i/12))
        structure_depreciation = max(0, property_details["structure_value"] * (1 - property_details["structure_depreciation_rate"]) ** (i/12))
        # Update net worth
        net_worth_rent[i] = savings_rent
        net_worth_buy[i] = savings_buy + land_appreciation + structure_depreciation - (mortgage_payment * 12 * years - mortgage_payment * i)

    return net_worth_rent, net_worth_buy

# Visualizations 
    
def plot_histogram(rent_data, buy_data):
    plt.figure(figsize=(12, 6))
    plt.hist(rent_data, bins=50, color="blue", edgecolor="black", alpha=0.5, label="賃貸")
    plt.hist(buy_data, bins=50, color="red", edgecolor="black", alpha=0.5, label="購入")

    # Formatting the axes
    plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: '{:,.0f}'.format(x)))
    plt.xlabel(f"{property_details['duration_rent']}年後の純資産 (JPY)")
    plt.ylabel("頻度")
    
    plt.title("賃貸対購入: 純資産の結果の分布")
    plt.legend()
    plt.grid(True)
    pdf_pages.savefig(plt.gcf())  # gcf stands for "get current figure"
    plt.close()  # Close the figure after saving to free up memory

# You can call these visualization functions as needed.

def plot_net_worth_over_time(net_worth_rent, net_worth_buy):
    years = np.arange(len(net_worth_rent)) / 12  # Convert months to years

    plt.figure(figsize=(12, 6))
    plt.plot(years, net_worth_rent, label="賃貸", color="blue")
    plt.plot(years, net_worth_buy, label="購入", color="red")
    
    # Formatting the axes
    plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: '{:,.0f}'.format(x)))
    plt.xlabel("年")
    plt.ylabel("純資産 (JPY)")
    
    plt.legend()
    plt.title(f"賃貸対購入: 純資産の時系列変化　{property_details['duration_rent']} 年")
    plt.grid(True)
    pdf_pages.savefig(plt.gcf())  # gcf stands for "get current figure"
    plt.close()  # Close the figure after saving to free up memory

def monte_carlo_simulation(personal, rent_details, property_details, market, costs, simulations=5000):
    rent_outcomes = []
    buy_outcomes = []
    for _ in range(simulations):
        rent_outcome, buy_outcome = buy_vs_rent_outcome(personal, rent_details, property_details, market, costs)
        rent_outcomes.append(rent_outcome[-1])  # net worth after the last month
        buy_outcomes.append(buy_outcome[-1])  # net worth after the last month
    return rent_outcomes, buy_outcomes
    
def sensitivity_analysis(personal, rent_details, property_details, market, costs, simulations=5000):
    base_case_rent, base_case_buy = buy_vs_rent_outcome(personal, rent_details, property_details, market, costs)
    base_difference = base_case_buy[-1] - base_case_rent[-1]
    
    # Vary purchase price
    diffs = []
    purchase_prices = np.linspace(30e6, 120e6, 10)
    
    original_purchase_price = property_details["purchase_price"]  # Store the original purchase price

    for price in purchase_prices:
        property_details["purchase_price"] = price
        rent_outcome, buy_outcome = buy_vs_rent_outcome(personal, rent_details, property_details, market, costs)
        diff = buy_outcome[-1] - rent_outcome[-1]
        diffs.append(diff)
        
        property_details["purchase_price"] = original_purchase_price  # Reset to original value after each iteration
    
    plt.figure(figsize=(12, 6))
    plt.plot(purchase_prices, diffs, marker='o', linestyle='-', color="green")
    plt.axhline(y=base_difference, color="red", linestyle="--", label="基本ケースの差")
    
    # Formatting the axes
    plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: '{:,.0f}'.format(x)))
    plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: '{:,.0f}'.format(x)))
    plt.xlabel("購入価格 (JPY)")
    plt.ylabel("純資産の差 (JPY)")
    
    plt.title(f"感度分析: 購入価格対純資産の差 {property_details['duration_rent']} 年")
    plt.grid(True)
    plt.legend()
    pdf_pages.savefig(plt.gcf())  # gcf stands for "get current figure"
    plt.close()  # Close the figure after saving to free up memory
# You can call these visualization functions as needed.

# Personal finance details
personal = {
    "monthly_income": 600000,  # Monthly income in yen
    "down_payment": 0,   # Amount saved for a down payment
    "loan_interest": 0.005 / 12,  # Monthly mortgage interest rate (annual rate of 0.5%)
    "monthly_expenses": 150000  # Other monthly expenses excluding rent/mortgage
}

# Renting details
rent_details = {
    "monthly_rent": 200000,           # Monthly rent in yen
    "annual_rent_increase": 0     # Annual rate of increase in rent (0%)
}

# Property purchase details
property_details = {
    "land_value": 30000000,          # Land value of the property in yen
    "structure_value": 20000000,    # Structure value of the property in yen
    "down_payment": 0,              # Down payment on the property in yen
    "duration_buy": 35 * 12,        # Duration of the mortgage in months (35 years * 12 months/year)
    "land_appreciation_rate": 0.02, # Annual rate of land appreciation (2%)
    "structure_depreciation_rate": 0.0455, # Annual rate of structure depreciation (5%)
    "maintenance": 10000,           # Monthly maintenance fee for the property
    "property_tax": 10000,          # Monthly property tax
    "duration_rent": 35             # Number of years for which the rent vs buy scenario is considered
}
property_details["purchase_price"] = property_details["land_value"] + property_details["structure_value"]


# Market details
market = {
    "investment_rate": 0.07  # Annual rate of return from investing (7% - average for S&P 500 historically)
}

# Other costs when buying
costs = {
    "insurance": 6000,       # Monthly insurance cost
    "bank_fees": 3000,       # Monthly bank fees
    "misc_fees": 2000        # Miscellaneous monthly fees
}

# Manshon details (if considering buying a manshon instead of a house)
# manshon_details = property_details.copy()  # Start with same details as house
# manshon_details["purchase_price"] = 30000000  # Adjust this and other details as required

# Calculate net worth outcomes
net_worth_rent, net_worth_buy = buy_vs_rent_outcome(personal, rent_details, property_details, market, costs)

# Plot the net worth over time for both renting and buying scenarios
plot_net_worth_over_time(net_worth_rent, net_worth_buy)

rent_outcomes, buy_outcomes = monte_carlo_simulation(personal, rent_details, property_details, market, costs)
plot_histogram(rent_outcomes, buy_outcomes)

sensitivity_analysis(personal, rent_details, property_details, market, costs)
pdf_pages.close()