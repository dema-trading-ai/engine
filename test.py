funds = 1000
available_funds = 900
profit = -0.1

starting_capital = 100

# Calculate profit and update total-, and available funds
profit = starting_capital * profit
available_funds += profit + starting_capital
funds += profit
print(funds)
print(available_funds)