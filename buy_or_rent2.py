import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.font_manager as fm
from matplotlib.lines import Line2D
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
    savings_buy = personal["down_payment"] - property_details["down_payment"]

    for i in range(months):
        # Calculate tax savings from renting
        rent_tax_savings = calculate_rent_tax_savings(rent_details, personal)  # Placeholder - you need to implement this function

        # Calculate tax savings from buying
        buy_tax_savings = calculate_buy_tax_savings(property_details, personal, mortgage_payment)  # Placeholder - you need to implement this function

        monthly_savings_rent = personal["monthly_income"] - rent_details["monthly_rent"] - personal["monthly_expenses"] + rent_tax_savings
        monthly_savings_buy = personal["monthly_income"] - mortgage_payment - costs["insurance"] - costs["bank_fees"] - costs["misc_fees"] - property_details["maintenance"] - property_details["property_tax"] - personal["monthly_expenses"] + buy_tax_savings

        large_expense = random_expenses(0.05, 100000)
        monthly_savings_rent -= large_expense
        monthly_savings_buy -= large_expense

        savings_rent += monthly_savings_rent
        savings_buy += monthly_savings_buy

        # Investment growth for savings
        savings_rent = investment_growth(savings_rent, market["investment_rate"]/12, 1/12)
        savings_buy = investment_growth(savings_buy, market["investment_rate"]/12, 1/12)

        # Land appreciation and structure depreciation
        land_appreciation = property_details["land_value"] * ((1 + property_details["land_appreciation_rate"]) ** (i/12))
        structure_depreciation = max(0, property_details["structure_value"] * (1 - property_details["structure_depreciation_rate"]) ** (i/12))

        # Update net worth
        net_worth_rent[i] = savings_rent  # Savings are being invested
        net_worth_buy[i] = savings_buy + land_appreciation + structure_depreciation - (mortgage_payment * 12 * years - mortgage_payment * i)

    return net_worth_rent, net_worth_buy


def calculate_rent_tax_savings(rent_details, personal):
    monthly_rent_covered_by_company = rent_details['monthly_rent']
    
    # Assuming this is a non-taxable benefit, so your taxable income is reduced
    # by the rent amount. If it's partially taxable, you would adjust the 
    # monthly_rent_covered_by_company accordingly.

    # Estimate the tax rate - this would need to be based on the individual's 
    # specific income and tax bracket
    estimated_tax_rate = 0.20  # Placeholder, adjust based on actual tax brackets

    # The tax savings is the tax you would have paid on the income used to 
    # cover the rent
    tax_savings = monthly_rent_covered_by_company * estimated_tax_rate
    
    return tax_savings

def calculate_buy_tax_savings(property_details, personal, mortgage_payment):
    annual_mortgage_interest = mortgage_payment * personal['loan_interest'] * 12
    
    # Deducting mortgage interest
    interest_deduction = min(annual_mortgage_interest, 1000000)  # Interest deduction is capped at 1,000,000 JPY
    
    # Special deduction for housing loans, applicable for 10 years
    special_deduction = 0
    if property_details.get("loan_years", 0) <= 10:
        special_deduction = 400000  # This is an example, and the actual amount may vary
        
    total_annual_deduction = interest_deduction + special_deduction
    
    # Assuming a flat tax rate for simplicity
    tax_rate = 0.20  # This is a placeholder and should be adjusted based on actual tax brackets
    
    annual_tax_savings = total_annual_deduction * tax_rate
    
    return annual_tax_savings / 12  # Convert annual savings to monthly savings

# Visualizations 
    
def plot_histogram(rent_data, buy_data):
    plt.figure(figsize=(12, 6))

    # Use the alpha parameter to make the bars semi-transparent
    plt.hist(rent_data, bins=50, color="blue", edgecolor="black", alpha=0.7, label="賃貸")
    plt.hist(buy_data, bins=50, color="red", edgecolor="black", alpha=0.7, label="購入")

    plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: '{:,.0f}'.format(x)))
    plt.xlabel(f"{property_details['duration_rent']}年後の純資産 (JPY)")
    plt.ylabel("頻度")
    
    plt.title("賃貸対購入: 純資産の結果の分布")
    plt.legend()
    plt.grid(True)

    # Save the figure
    pdf_pages.savefig(plt.gcf())
    
    plt.close()

# You can call these visualization functions as needed.

def plot_net_worth_over_time(net_worth_rent, net_worth_buy):
    years = np.arange(len(net_worth_rent)) / 12  # Convert months to years

    plt.figure(figsize=(12, 6))
    plt.plot(years, net_worth_rent, label="賃貸", color="blue")
    plt.plot(years, net_worth_buy, label="購入", color="red")

    # Calculate monthly mortgage payment
    mortgage_payment = calculate_mortgage(property_details["purchase_price"] - property_details["down_payment"], personal["loan_interest"], property_details["duration_buy"])

    # 入力パラメータをプロットに追加
    input_params = [
        f"月収: {personal['monthly_income']:,}円",
        f"貯金残高: {personal['down_payment']:,}円",
        f"頭金: {property_details['down_payment']:,}円",
        f"月間の住宅ローン支払い: {mortgage_payment:,.0f}円",
        f"ローン利率: {personal['loan_interest']*12*100:.2f}%",
        f"月間の支出: {personal['monthly_expenses']:,}円",
        f"月額の家賃: {rent_details['monthly_rent']:,}円",
        f"物件購入価格: {property_details['purchase_price']:,}円",
        f"土地購入価格: {property_details['land_value']:,}円",
        f"建物購入価格: {property_details['structure_value']:,}円",
        f"土地の価値の増加率（年間）: {property_details['land_appreciation_rate']*100:.2f}%",
        f"投資利回り（年間）: {market['investment_rate']*100:.2f}%"
    ]

    # Create custom legend entries
    legend_elements = [Line2D([0], [0], color='blue', label='賃貸'),
                       Line2D([0], [0], color='red', label='購入')]

    # Append input parameters to the legend entries
    for param in input_params:
        legend_elements.append(Line2D([0], [0], color='white', label=param, markerfacecolor='white'))

    # Create the legend
    legend = plt.legend(handles=legend_elements, loc='upper left', frameon=True,
                        facecolor='white', edgecolor='black', bbox_to_anchor=(1, 1))

    # 軸のフォーマット
    plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: '{:,.0f}'.format(x)))
    plt.xlabel("年")
    plt.ylabel("純資産 (円)")

    plt.title(f"賃貸対購入: 純資産の時系列変化　{property_details['duration_rent']} 年")
    plt.grid(True)
    
    plt.tight_layout()
    plt.subplots_adjust(left=0.1, right=0.7)  # Adjust the plot area to make room for the annotations

    pdf_pages.savefig(plt.gcf())  
    plt.close()  

def monte_carlo_simulation(personal, rent_details, property_details, market, costs, simulations=10000):
    rent_outcomes = []
    buy_outcomes = []
    for _ in range(simulations):
        rent_outcome, buy_outcome = buy_vs_rent_outcome(personal, rent_details, property_details, market, costs)
        rent_outcomes.append(rent_outcome[-1])  # net worth after the last month
        buy_outcomes.append(buy_outcome[-1])  # net worth after the last month
    return rent_outcomes, buy_outcomes
    
def enhanced_sensitivity_analysis(personal, rent_details, property_details, market, costs, simulations=10000):
    parameters = {
        "purchase_price": np.linspace(30e6, 150e6, 10),
        "loan_interest": np.linspace(0.005, 0.05, 10),  # Adjust these values for a focused analysis on loan interest
        "investment_rate": np.linspace(0.03, 0.15, 10),
        "maintenance": np.linspace(10000, 50000, 10)
    }

    param_translations = {
        "purchase_price": ("購入価格", '{:,.0f}', 1e-6, "百万円"),
        "loan_interest": ("ローンの利率", '{:.2%}', 1, "%"),
        "investment_rate": ("投資利回り", '{:.2%}', 1, "%"),
        "maintenance": ("保守費", '{:,.0f}', 1, "円")
    }

    base_case_rent, base_case_buy = buy_vs_rent_outcome(personal, rent_details, property_details, market, costs)
    base_difference = base_case_buy[-1] - base_case_rent[-1]

    results = {}

    for param, values in parameters.items():
        diffs = []
        original_value = None

        for value in values:
            if param in personal:
                original_value = personal[param]
                if param == 'loan_interest':
                    personal[param] = value / 12  # Convert annual interest rate to monthly
                else:
                    personal[param] = value
            elif param in rent_details:
                original_value = rent_details[param]
                rent_details[param] = value
            elif param in property_details:
                original_value = property_details[param]
                property_details[param] = value
            elif param in market:
                original_value = market[param]
                market[param] = value
            elif param in costs:
                original_value = costs[param]
                costs[param] = value

            rent_outcome, buy_outcome = buy_vs_rent_outcome(personal, rent_details, property_details, market, costs)
            diff = buy_outcome[-1] - rent_outcome[-1]  # Calculate the difference in net worth
            diffs.append(diff)

            if original_value is not None:
                if param in personal:
                    personal[param] = original_value
                elif param in rent_details:
                    rent_details[param] = original_value
                elif param in property_details:
                    property_details[param] = original_value
                elif param in market:
                    market[param] = original_value
                elif param in costs:
                    costs[param] = original_value

        results[param] = diffs

    for param, diffs in results.items():
        plt.figure(figsize=(12, 6))
        values = parameters[param]
        title, format_str, scale, unit = param_translations[param]

        plt.plot(values * scale, diffs, marker='o', linestyle='-', label=f"{title} の変動")
        plt.axhline(y=base_difference, color="red", linestyle="--", label="基本ケースの差")

        plt.xlabel(f"{title} ({unit})")
        plt.ylabel(f"純資産の差 {property_details['duration_rent']} 年　(JPY)")

        plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: format_str.format(x)))
        plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: '{:,.0f}'.format(x)))

        plt.title(f"{title} に対する感度分析")
        plt.grid(True)
        plt.legend()

        pdf_pages.savefig(plt.gcf())  
        plt.close()
        
# Personal finance details
personal = {
    "monthly_income": 770833,  # Monthly income in yen
    "down_payment": 20000000,   # Amount saved for a down payment
    "loan_interest": 0.01 / 12,  # Monthly mortgage interest rate (annual rate of 1%)
    "monthly_expenses": 200000  # Other monthly expenses excluding rent/mortgage
}

# Renting details
rent_details = {
    "monthly_rent": 200000,           # Monthly rent in yen
    "annual_rent_increase": 0.00001     # Annual rate of increase in rent (0%)
}

# Property purchase details
property_details = {
    "land_value": 51800000,          # Land value of the property in yen
    "structure_value": 30000000,    # Structure value of the property in yen
    "down_payment": 0,              # Down payment on the property in yen
    "duration_buy": 35 * 12,        # Duration of the mortgage in months (35 years * 12 months/year)
    "land_appreciation_rate": 0.000, # Annual rate of land appreciation (0%)
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

enhanced_sensitivity_analysis(personal, rent_details, property_details, market, costs)
pdf_pages.close()