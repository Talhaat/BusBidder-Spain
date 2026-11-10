# Data generation for project - loads/generates everything the app needs

import loader
import models
import routes

canvas_width = 3000
canvas_height = 2000


#---------------------------DICT-------------------------------------------
#Categories for each destination. Destinations not listed here get no categories.
destination_categories = {
    "Barcelona": ["major city"],
    "Cordoba": ["small town", "historic"],
    "Murcia": ["city"],
    "Valencia": ["major city", "beach", "coastal"],
    "Bilbao": ["city"],
    "Salamanca": ["small town", "historic", "coastal"],
    "Seville": ["major city", "historic", "coastal"],
    "San Sebastian": ["city", "beach"],
    "Toledo": ["small town", "historic"],
    "Malaga": ["city", "beach"],
    "Zaragoza": ["major city"],
    "Santiago de Compostela": ["city", "historic", "coastal"],
    "Granada": ["city", "coastal"],
    "Alicante": ["city", "beach"],
    "Cadiz": ["small town", "beach"],
}

#How many destinations each company should have. Companies not listed here get 5.
destination_counts = {
    "SolRuta": 8,
    "Camino Express": 3,
    "CostaLink": 6,
    "VerdeBus": 4,
    "NocheVia": 5,
}

#Destinations that must be included for a company, counted towards total destination_counts
custom_destinations = {
    "CostaLink": ["Granada", "Valencia", "Santiago de Compostela", "Malaga", "Salamanca", "Seville"]
}

#One line colour per company, for the map
company_colors = {
    "SolRuta": "red",
    "Camino Express": "blue",
    "CostaLink": "green",
    "VerdeBus": "purple",
    "NocheVia": "orange",
}
#---------------------------DICT-------------------------------------------


#Function to load or generate every piece of data the app needs
# Input is none, return dict with destinations, companies, connections, coordinates,
# Madrid's x and y, company colours and the canvas size.
def generate_data():
    # Read destinations from destination.csv
    destinations = loader.load_destinations()
    # Read companies as full Company objects (name, Profile with price range)
    companies = models.load_companies(loader.company_path)
    company_names = [company.name for company in companies]

    # Generate or load bus connections, save to bus_connections.csv
    connections = loader.load_or_generate_connections(company_names, destinations, destination_counts, custom_destinations)
    loader.save_connections(connections)

    # Generate or load coordinates for each destination, save to map_destination.csv
    coordinates = loader.load_or_generate_coordinates(destinations, canvas_width, canvas_height)

    #Madrid is the hub every bus line starts from, fixed in the middle of the canvas
    madrid_x, madrid_y = canvas_width // 2, canvas_height // 2

    # Assign any destination with no company to whichever company has the nearest point
    routes.assign_unassigned_destinations(connections, destinations, coordinates, madrid_x, madrid_y)

    # Give each Company object its own list of the destinations it serves
    for company in companies:
        company.destinations = connections.get(company.name, [])

    # Generate or load destination profiles, save to destination_profile.csv
    destination_profiles = loader.load_or_generate_destination_profiles(destinations, destination_categories)
    loader.save_destination_profiles(destination_profiles)

    return {
        "destinations": destinations,
        "companies": companies,
        "connections": connections,
        "coordinates": coordinates,
        "madrid_x": madrid_x,
        "madrid_y": madrid_y,
        "company_colors": company_colors,
        "canvas_width": canvas_width,
        "canvas_height": canvas_height,
        "destination_profiles": destination_profiles,
    }


if __name__ == "__main__":
    from gui.map_view import show_map

    data = generate_data()
    show_map(
        data["connections"], data["coordinates"], data["madrid_x"], data["madrid_y"],
        data["company_colors"], data["canvas_width"], data["canvas_height"]
    )
    loader.save_coordinates(data["coordinates"])
