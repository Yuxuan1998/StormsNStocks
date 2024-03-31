from geopy.geocoders import Nominatim, Photon
from geopy.exc import GeocoderTimedOut

class USLocationResolver:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="geoapiDemoTest1")
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

    def get_location_by_address(self, address):
        try:
            location = self.geolocator.geocode(address, exactly_one=True)
            return location
        except GeocoderTimedOut:
            return self.get_location_by_address(address)

    def normalize_state_name(self, state_full_name):
        # Normalize state name to handle different formats (e.g., "New York" vs "New York State")
        return state_full_name.replace(" State", "")

    def convert_to_state_and_region(self, division_name):
        location = self.get_location_by_address(division_name)
        if location:
            # print(location)
            address_components = location.address.split(", ")
            # print(address_components)
            # Iterate through the components to find the state
            for component in address_components:
                normalized_state_name = self.normalize_state_name(component.strip())
                if normalized_state_name in self.state_to_region:
                    state_full_name = normalized_state_name
                    region = self.state_to_region[state_full_name]
                    return state_full_name, region
            return "State not found", "Region not found"
        else:
            return "Unknown", "Unknown"


def main() -> None:
    resolver = USLocationResolver()
    division_names = ['Los Angeles', 'Cook County', 'Miami-Dade County', 'oakland']
    for name in division_names:
        state, region = resolver.convert_to_state_and_region(name)
        print(f"{name}: State - {state}, Region - {region}")


if __name__ == "__main__":
    main()

