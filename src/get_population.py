import pandas as pd
import census
from us import states

# Configure your Census API key
c = census.Census("3ef8d931ff56364eff7c34be71f997524b96c866")

state_areas = {
    'Alabama': 52420, 'Alaska': 665384, 'Arizona': 113990, 'Arkansas': 53179,
    'California': 163695, 'Colorado': 104094, 'Connecticut': 5543, 'Delaware': 2489,
    'Florida': 65758, 'Georgia': 59425, 'Hawaii': 10932, 'Idaho': 83569,
    'Illinois': 57914, 'Indiana': 36420, 'Iowa': 56273, 'Kansas': 82278,
    'Kentucky': 40408, 'Louisiana': 52378, 'Maine': 35380, 'Maryland': 12406,
    'Massachusetts': 10554, 'Michigan': 96714, 'Minnesota': 86936, 'Mississippi': 48432,
    'Missouri': 69707, 'Montana': 147040, 'Nebraska': 77348, 'Nevada': 110572,
    'New Hampshire': 9349, 'New Jersey': 8723, 'New Mexico': 121590, 'New York': 54555,
    'North Carolina': 53819, 'North Dakota': 70698, 'Ohio': 44826, 'Oklahoma': 69899,
    'Oregon': 98379, 'Pennsylvania': 46054, 'Rhode Island': 1545, 'South Carolina': 32020,
    'South Dakota': 77116, 'Tennessee': 42144, 'Texas': 268596, 'Utah': 84897,
    'Vermont': 9616, 'Virginia': 42775, 'Washington': 71298, 'West Virginia': 24230,
    'Wisconsin': 65496, 'Wyoming': 97813
}

population_2023 = {
    'Alabama': 50.69940, 'Alaska': 733900, 'Arizona': 7230369, 'Arkansas': 3025718, 
    'California': 39408216, 'Colorado': 5832336, 'Connecticut': 3618847, 
    'Delaware': 1004989, 'Florida': 21901830, 'Georgia': 10831248, 'Hawaii': 1457900, 
    'Idaho': 1898211, 'Illinois': 12741911, 'Indiana': 6821660, 'Iowa': 3203090, 
    'Kansas': 2942757, 'Kentucky': 4518766, 'Louisiana': 4634801, 'Maine': 1375628, 
    'Maryland': 6202064, 'Massachusetts': 7023415, 'Michigan': 10083256, 'Minnesota': 5738092, 
    'Mississippi': 2951417, 'Missouri': 6170618, 'Montana': 1104742, 'Nebraska': 1972740, 
    'Nevada': 3152072, 'New Hampshire': 1388764, 'New Jersey': 9344477, 'New Mexico': 2117505, 
    'New York': 20091694, 'North Carolina': 10550532, 'North Dakota': 783177, 'Ohio': 11808175, 
    'Oklahoma': 3983705, 'Oregon': 4267071, 'Pennsylvania': 13039403, 'Rhode Island': 1103965, 
    'South Carolina': 5190665, 'South Dakota': 896980, 'Tennessee': 6993681, 'Texas': 29593169, 
    'Utah': 3346308, 'Vermont': 648657, 'Virginia': 8678024, 'Washington': 7790407, 
    'West Virginia': 1784058, 'Wisconsin': 5908394, 'Wyoming': 576960
}

us_population = {
    2019: {'Alabama': 4876250.0, 'Alaska': 737068.0, 'Arizona': 7050299.0, 'Arkansas': 2999370.0, 'California': 39283497.0, 'Colorado': 5610349.0, 'Delaware': 957248.0, 'Connecticut': 3575074.0, 'Florida': 20901636.0, 'Georgia': 10403847.0, 'Idaho': 1717750.0, 'Hawaii': 1422094.0, 'Illinois': 12770631.0, 'Indiana': 6665703.0, 'Iowa': 3139508.0, 'Kansas': 2910652.0, 'Kentucky': 4449052.0, 'Louisiana': 4664362.0, 'Maine': 1335492.0, 'Maryland': 6018848.0, 'Massachusetts': 6850553.0, 'Michigan': 9965265.0, 'Minnesota': 5563378.0, 'Mississippi': 2984418.0, 'Missouri': 6104910.0, 'Montana': 1050649.0, 'Nebraska': 1914571.0, 'Nevada': 2972382.0, 'New Hampshire': 1348124.0, 'New Jersey': 8878503.0, 'New Mexico': 2092454.0, 'New York': 19572319.0, 'North Carolina': 10264876.0, 'North Dakota': 756717.0, 'Ohio': 11655397.0, 'Oklahoma': 3932870.0, 'Oregon': 4129803.0, 'Pennsylvania': 12791530.0, 'Rhode Island': 1057231.0, 'South Carolina': 5020806.0, 'South Dakota': 870638.0, 'Tennessee': 6709356.0, 'Texas': 28260856.0, 'Vermont': 624313.0, 'Utah': 3096848.0, 'Virginia': 8454463.0, 'Washington': 7404107.0, 'West Virginia': 1817305.0, 'Wisconsin': 5790716.0, 'Wyoming': 581024.0}, 
    2020: {'Pennsylvania': 12794885.0, 'California': 39346023.0, 'West Virginia': 1807426.0, 'Utah': 3151239.0, 'New York': 19514849.0, 'Alaska': 736990.0, 'Florida': 21216924.0, 'South Carolina': 5091517.0, 'North Dakota': 760394.0, 'Maine': 1340825.0, 'Georgia': 10516579.0, 'Alabama': 4893186.0, 'New Hampshire': 1355244.0, 'Oregon': 4176346.0, 'Wyoming': 581348.0, 'Arizona': 7174064.0, 'Louisiana': 4664616.0, 'Indiana': 6696893.0, 'Idaho': 1754367.0, 'Connecticut': 3570549.0, 'Hawaii': 1420074.0, 'Illinois': 12716164.0, 'Massachusetts': 6873003.0, 'Texas': 28635442.0, 'Montana': 1061705.0, 'Nebraska': 1923826.0, 'Ohio': 11675275.0, 'Colorado': 5684926.0, 'New Jersey': 8885418.0, 'Maryland': 6037624.0, 'Virginia': 8509358.0, 'Vermont': 624340.0, 'North Carolina': 10386227.0, 'Arkansas': 3011873.0, 'Washington': 7512465.0, 'Kansas': 2912619.0, 'Oklahoma': 3949342.0, 'Wisconsin': 5806975.0, 'Mississippi': 2981835.0, 'Missouri': 6124160.0, 'Michigan': 9973907.0, 'Rhode Island': 1057798.0, 'Minnesota': 5600166.0, 'Iowa': 3150011.0, 'New Mexico': 2097021.0, 'Nevada': 3030281.0, 'Delaware': 967679.0, 'Kentucky': 4461952.0, 'South Dakota': 879336.0, 'Tennessee': 6772268.0}, 
    2021: {'Alabama': 4997675.0, 'Alaska': 735951.0, 'Arizona': 7079203.0, 'Arkansas': 3006309.0, 'California': 39455353.0, 'Colorado': 5723176.0, 'Connecticut': 3605330.0, 'Delaware': 981892.0, 'Florida': 21339762.0, 'Georgia': 10625615.0, 'Hawaii': 1453498.0, 'Idaho': 1811617.0, 'Illinois': 12821813.0, 'Indiana': 6751340.0, 'Iowa': 3179090.0, 'Kansas': 2932099.0, 'Kentucky': 4494141.0, 'Louisiana': 4657305.0, 'Maine': 1357046.0, 'Maryland': 6148545.0, 'Massachusetts': 6991852.0, 'Michigan': 10062512.0, 'Minnesota': 5670472.0, 'Mississippi': 2967023.0, 'Missouri': 6141534.0, 'Montana': 1077978.0, 'Nebraska': 1951480.0, 'Nevada': 3059238.0, 'New Hampshire': 1372175.0, 'New Jersey': 9234024.0, 'New Mexico': 2109366.0, 'New York': 20114745.0, 'North Carolina': 10367022.0, 'North Dakota': 773344.0, 'Ohio': 11769923.0, 'Oklahoma': 3948136.0, 'Oregon': 4207177.0, 'Pennsylvania': 12970650.0, 'Rhode Island': 1091949.0, 'South Carolina': 5078903.0, 'South Dakota': 881785.0, 'Tennessee': 6859497.0, 'Texas': 28862581.0, 'Utah': 3231370.0, 'Vermont': 641637.0, 'Virginia': 8582479.0, 'Washington': 7617364.0, 'West Virginia': 1801049.0, 'Wisconsin': 5871661.0, 'Wyoming': 576641.0}, 
    2022: {'Alabama': 5028092.0, 'Alaska': 734821.0, 'Arizona': 7172282.0, 'Arkansas': 3018669.0, 'California': 39356104.0, 'Colorado': 5770790.0, 'Connecticut': 3611317.0, 'Delaware': 993635.0, 'Florida': 21634529.0, 'Georgia': 10722325.0, 'Hawaii': 1450589.0, 'Idaho': 1854109.0, 'Illinois': 12757634.0, 'Indiana': 6784403.0, 'Iowa': 3188836.0, 'Kansas': 2935922.0, 'Kentucky': 4502935.0, 'Louisiana': 4640546.0, 'Maine': 1366949.0, 'Maryland': 6161707.0, 'Massachusetts': 6984205.0, 'Michigan': 10057921.0, 'Minnesota': 5695292.0, 'Mississippi': 2958846.0, 'Missouri': 6154422.0, 'Montana': 1091840.0, 'Nebraska': 1958939.0, 'Nevada': 3104817.0, 'New Hampshire': 1379610.0, 'New Jersey': 9249063.0, 'New Mexico': 2112463.0, 'New York': 19994379.0, 'North Carolina': 10470214.0, 'North Dakota': 776874.0, 'Ohio': 11774683.0, 'Oklahoma': 3970497.0, 'Oregon': 4229374.0, 'Pennsylvania': 12989208.0, 'Rhode Island': 1094250.0, 'South Carolina': 5142750.0, 'South Dakota': 890342.0, 'Tennessee': 6923772.0, 'Texas': 29243342.0, 'Utah': 3283809.0, 'Vermont': 643816.0, 'Virginia': 8624511.0, 'Washington': 7688549.0, 'West Virginia': 1792967.0, 'Wisconsin': 5882128.0, 'Wyoming': 577929.0}, 
    2023: {'Alabama': 5069940.0, 'Alaska': 733900.0, 'Arizona': 7230369.0, 'Arkansas': 3025718.0, 'California': 39408216.0, 'Colorado': 5832336.0, 'Connecticut': 3618847.0, 'Delaware': 1004989.0, 'Florida': 21901830.0, 'Georgia': 10831248.0, 'Hawaii': 1457900.0, 'Idaho': 1898211.0, 'Illinois': 12741911.0, 'Indiana': 6821660.0, 'Iowa': 3203090.0, 'Kansas': 2942757.0, 'Kentucky': 4518766.0, 'Louisiana': 4634801.0, 'Maine': 1375628.0, 'Maryland': 6202064.0, 'Massachusetts': 7023415.0, 'Michigan': 10083256.0, 'Minnesota': 5738092.0, 'Mississippi': 2951417.0, 'Missouri': 6170618.0, 'Montana': 1104742.0, 'Nebraska': 1972740.0, 'Nevada': 3152072.0, 'New Hampshire': 1388764.0, 'New Jersey': 9344477.0, 'New Mexico': 2117505.0, 'New York': 20091694.0, 'North Carolina': 10550532.0, 'North Dakota': 783177.0, 'Ohio': 11808175.0, 'Oklahoma': 3983705.0, 'Oregon': 4267071.0, 'Pennsylvania': 13039403.0, 'Rhode Island': 1103965.0, 'South Carolina': 5190665.0, 'South Dakota': 896980.0, 'Tennessee': 6993681.0, 'Texas': 29593169.0, 'Utah': 3346308.0, 'Vermont': 648657.0, 'Virginia': 8678024.0, 'Washington': 7790407.0, 'West Virginia': 1784058.0, 'Wisconsin': 5908394.0, 'Wyoming': 576960.0}
}



def fetch_population_data(year):
    data = c.acs5.get(('NAME', 'B01003_001E'), {'for': 'state:*'}, year=year)
    return {state['NAME']: state['B01003_001E'] for state in data}

# Main function to compile the dictionary
def compile_data():
    years = [2019, 2020, 2021, 2022, 2023]
    state_population = {}
    
    years = [2019, 2020, 2021, 2022, 2023]
    state_info = {year: {} for year in years}

    for year in years:
        if year == 2023:
            if state in state_areas:
                state_info[year][state] = population_2023[state]

        else:
            population_data = fetch_population_data(year)
            for state, pop in population_data.items():
                if state in state_areas:
                    state_info[year][state] = pop
    
    return state_info
    
    return state_population

def main():
    # state_data = compile_data()
    # print(state_data)
    df = pd.read_csv('updated_dataset_v3.csv')
 
    # Update 'population' and 'area' based on the 'year' and 'state' column
    for index, row in df.iterrows():
        year = int(row['pub_date'][:4])
        state = row['state']
        
        # Check if the year and state exist in the dictionary
        if year in us_population and state in us_population[year]:
            # Update population and area
            df.at[index, 'population'] = us_population[year][state]
            df.at[index, 'area'] = state_areas[state]
        else:
            # Handle cases where there is no data
            df.at[index, 'population'] = None
            df.at[index, 'area'] = None

    # Save the updated DataFrame back to CSV
    df.to_csv('updated_dataset_v4.csv', mode='w', index=False)


if __name__ == "__main__":
    main()