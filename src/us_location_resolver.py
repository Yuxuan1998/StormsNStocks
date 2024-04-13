import requests
from census import Census
from geopy.geocoders import Nominatim, Photon
from geopy.exc import GeocoderTimedOut
from us import states
import numpy as np
from typing import List
import time

class USLocationResolver:
    def __init__(self, user_agent="geoapiDemoTest1"):
        self.geolocator = Nominatim(user_agent=user_agent)
        self.census = Census("3ef8d931ff56364eff7c34be71f997524b96c866")
        self.bea_api_key = "E072F18E-4BB4-4A9A-9948-2BAA0A7A14B5"
        self.bea_url = "https://apps.bea.gov/api/data"
        self.state_to_region = {
            # Northeast
            'Connecticut': 'Northeast', 'Maine': 'Northeast', 'Massachusetts': 'Northeast',
            'New Hampshire': 'Northeast', 'Rhode Island': 'Northeast', 'Vermont': 'Northeast',
            'New Jersey': 'Northeast', 'New York': 'Northeast', 'Pennsylvania': 'Northeast',
            # Midwest
            'Illinois': 'Midwest', 'Indiana': 'Midwest', 'Iowa': 'Midwest', 'Kansas': 'Midwest',
            'Michigan': 'Midwest', 'Minnesota': 'Midwest', 'Missouri': 'Midwest', 'Nebraska': 'Midwest',
            'North Dakota': 'Midwest', 'Ohio': 'Midwest', 'South Dakota': 'Midwest', 'Wisconsin': 'Midwest',
            # South
            'Alabama': 'South', 'Arkansas': 'South', 'Delaware': 'South', 'District of Columbia': 'South',
            'Florida': 'South', 'Georgia': 'South', 'Kentucky': 'South', 'Louisiana': 'South',
            'Maryland': 'South', 'Mississippi': 'South', 'North Carolina': 'South', 'Oklahoma': 'South',
            'South Carolina': 'South', 'Tennessee': 'South', 'Texas': 'South', 'Virginia': 'South',
            'West Virginia': 'South',
            # West
            'Alaska': 'West', 'Arizona': 'West', 'California': 'West', 'Colorado': 'West',
            'Hawaii': 'West', 'Idaho': 'West', 'Montana': 'West', 'Nevada': 'West',
            'New Mexico': 'West', 'Oregon': 'West', 'Utah': 'West', 'Washington': 'West',
            'Wyoming': 'West'
        }

        self.population_2023 = {
            'Alabama': 5069940, 'Alaska': 733900, 'Arizona': 7230369, 'Arkansas': 3025718, 
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

    def get_location_by_address(self, address):
        try:
            location = self.geolocator.geocode(address, exactly_one=True)
            return location
        except GeocoderTimedOut:
            return self.get_location_by_address(address)

    def normalize_state_name(self, state_full_name):
        # Normalize state name (e.g., "New York" vs "New York State")
        return state_full_name.replace(" State", "")
    
    def fetch_state_data(self, state_fips, year):
        # Name, Area, Population
        state_data = self.census.acs5.get(('NAME', 'B01003_001E', 'B01002_001E'), {'for': 'state:{}'.format(state_fips)}, year=year)
        return state_data
    
    def fetch_state_gdp(self, state_fips, year):

        params = {
            "UserID": self.bea_api_key,
            "Method": "GetData",
            "DataSetName": "Regional",
            "TableName": "SAGDP2N",  # gdp in Millions by states
            "LineCode": 1,
            "GeoFips": state_fips + "000",
            "Year": year,
            "ResultFormat": "json",
        }
        retry = 10
        for attempt in range(retry+1):
            try:
                response = requests.get(self.bea_url, params=params)
            except requests.exceptions.RequestException as e:
                print(f"Connection error attempt {attempt+1}/{retry+1}: {e}")
                time.sleep(2)

        if response.status_code == 200:
            data = response.json()
            return data['BEAAPI']['Results']['Data'][0]['DataValue']
        else:
            return "API request failed"
    
    def convert_to_state_and_region(self, division_name: List[str], year: int):
        location = self.get_location_by_address(division_name)
        if location:
            address_components = location.address.split(", ")
            for component in address_components:
                normalized_state_name = self.normalize_state_name(component.strip())
                if normalized_state_name in self.state_to_region:
                    state_full_name = normalized_state_name
                    region = self.state_to_region[state_full_name]
                    state_fips = states.lookup(state_full_name).fips

                    if year == 2023:
                        state_data = self.fetch_state_data(state_fips, 2022)
                        population = self.population_2023[state_full_name]
                    else:
                        state_data = self.fetch_state_data(state_fips, year)
                        population = state_data[0]["B01002_001E"]

                    state_gdp = self.fetch_state_gdp(state_fips, year)

                    return {
                        'state': state_full_name,
                        'region': region,
                        "area": state_data[0]["B01003_001E"],
                        "GDP": state_gdp,
                        "population": population,
                        "longitude": location.longitude,
                        "latitude": location.latitude,
                    }
                
            return {"error": "State not found or data missing"}
        else:
            return {"error": "Location unknown"}


def main() -> None:
    resolver = USLocationResolver()
    division_names = ['oakland']
    for name in division_names:
        print(resolver.convert_to_state_and_region(name, year=2023))


if __name__ == "__main__":
    main()

