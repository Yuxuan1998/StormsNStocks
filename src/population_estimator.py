import pandas as pd
import numpy as np
from census import Census
import us
import os

c = Census("3ef8d931ff56364eff7c34be71f997524b96c866")

def fetch_historical_population(state_fips, years):
    population_data = []
    for year in years:
        data = c.acs5.get(('NAME', 'B01003_001E'), {'for': 'state:{}'.format(state_fips)}, year=int(year))
        if data:
            population = int(data[0]['B01003_001E'])
            print(population)
            population_data.append(population)
    return population_data

def estimate_future_population(historical_data):
    if len(historical_data) < 2:
        return None
    # Calculate year-over-year growth rates
    growth_rates = [((historical_data[i] - historical_data[i-1]) / historical_data[i-1]) for i in range(1, len(historical_data))]
    # Calculate average growth rate
    average_growth_rate = np.mean(growth_rates)
    # Estimate future population
    future_population = historical_data[-1] * (1 + average_growth_rate)
    return int(future_population)

def main():
    years = ['2018', '2019', '2020', '2021', '2022']  # Modify as per the latest available data
    states = us.states.STATES
    estimated_population_dict = {}

    for state in states:
        historical_pop = fetch_historical_population(state.fips, years)
        estimated_pop_2023 = estimate_future_population(historical_pop)

        estimated_population_dict[state.name] = estimated_pop_2023

    return estimated_population_dict




estimated_population_dict = main()

print(estimated_population_dict)