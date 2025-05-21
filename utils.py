def calculate_enterprise_value(ebitda, multiple):
    return ebitda * multiple

def discount_cash_flows(cash_flows, discount_rate):
    return sum(cf / (1 + discount_rate) ** i for i, cf in enumerate(cash_flows, 1))
