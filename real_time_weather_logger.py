import os
import csv
import requests
from datetime import date
 
FILE_NAME = "weather_log.csv"
WEATHER_ATTRIBUTES = ["City", "Date", "Temperature Deg C", "Weather Condition", "Condition Description"]
LATITUDE_LONGITUDE_URL = "https://nominatim.openstreetmap.org/search"
API_KEY = "PUT YOUR OWN API KEY"
 
def fetch_latitude_longitude(city_name):
    """Gets the latitude and longitude information for a particular city"""
    params = { "q": city_name, "format": "jsonv2", "limit": 1}
    headers = {"User-Agent": "my-app"}
    lat_long_response = requests.get(LATITUDE_LONGITUDE_URL, params = params, headers = headers)
    location_data = lat_long_response.json()
    if location_data:
        return location_data[0]["lat"], location_data[0]["lon"]
 
def fetch_current_weather_report(latitude, longitude):
    """Fetches the current weather data using lat and lon"""
    OPEN_WEATHER_URL = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={API_KEY}"
    weather_response = requests.get(OPEN_WEATHER_URL)
    return weather_response.json()
    
def farheniet_to_celcius(temp_in_k): return round(temp_in_k - 273.15, 2)
    
def check_city_date_combo_existance(city_name, date_be_checked):
    weather_data_list = store_csv_to_weather_list(FILE_NAME)
    for weather_report in weather_data_list:
        if weather_report["City"] == city_name and weather_report["Date"] == date_be_checked:
            print(f"The weather data for {city_name.upper()}, dated {date_be_checked} already exists.")
            return False
    return True

def save_current_weather_report():
    """Helps the user fetch the current weather for a particular city"""
    city_name = input("Enter the city name for which you want to fetch the report: ").strip()

    if check_city_date_combo_existance(city_name, str(date.today().isoformat())):
        latitude, longitude = fetch_latitude_longitude(city_name)
        weather_information = fetch_current_weather_report(latitude, longitude)

        weather_data_list   = [city_name, date.today().isoformat(), farheniet_to_celcius(weather_information["main"]["temp"]), weather_information["weather"][0]["main"], weather_information["weather"][0]["description"]]
                                
        with open(FILE_NAME, "a", newline = "", encoding = "utf-8") as weather_file:
            writer = csv.writer(weather_file)
            writer.writerow(weather_data_list)
        print(f"The weather report has been successfully added to {FILE_NAME}")
    
 
# These are the file-opening-closing functions
def store_csv_to_weather_list(file_name):
    """Helps the user store the updated weather list to csv"""
    weather_info_list = list()
    with open(file_name, "r", encoding = "utf-8") as weather_file:
        reader = csv.DictReader(weather_file)
        for row in reader: weather_info_list.append(row)
    return weather_info_list
 
def dump_weather_list_to_csv(file_name, list_be_stored):
    """Helps the user to create a list of dictionaries from csv"""
    with open(file_name, "w", encoding = "utf-8") as weather_file: 
        writer = csv.DictWriter(weather_file, fieldnames = WEATHER_ATTRIBUTES)
        writer.writerow(list_be_stored)
    weather_file.close()
    
# These are utility methods
def view_current_weather_list():
    """Helps the user view all weather information for a particular city"""
    city_name = input("Enter the city name for which you want to view details: ").strip()
    weather_data_list = store_csv_to_weather_list(FILE_NAME)
    info_be_displayed = list()
    for weather_report in weather_data_list:
        if weather_report["City"] == city_name: info_be_displayed.append(weather_report)
    output_table_formatter(info_be_displayed)

def highest_lowest_method(metric, weather_data_list):
    storage = float(-100) if metric == "highest" else float(1000)
    function_be_called = max if metric == "highest" else min
    for weather_report in weather_data_list:
        storage = function_be_called(storage, float(weather_report["Temperature Deg C"]))
    print(f"The {metric.lower()} temperature recorded is: {round(storage, 2)}")


def weather_stats_method():
    weather_data_list = store_csv_to_weather_list(FILE_NAME)
    user_input = input("Enter the metric you want to calculate: ").lower().strip()
    if user_input == "average":
        storage = float(0)
        for weather_report in weather_data_list: storage += float(weather_report["Temperature Deg C"])
        print(f"The average of all logged temperatures is: {round(storage/len(weather_data_list), 2)} Deg C")

    elif user_input == "highest":
        highest_lowest_method("highest", weather_data_list)

    elif user_input == "lowest":
        highest_lowest_method("lowest", weather_data_list)

    else: print("Invalid Metric!")
            
 
def output_table_formatter(weather_data_list):
    """Builds a dynamic table based on the passed list"""
    max_length = list()
    for attribute in WEATHER_ATTRIBUTES:
        max_length.append(len(attribute))
        
    for weather_report in weather_data_list:
        index_variable = 0
        for value in weather_report.values():
            if len(value) > max_length[index_variable]: 
                max_length[index_variable] = len(value)
                index_variable += 1
    total_length = 0
    for length in max_length: total_length += length
    
    print("-" * (total_length + 20))
    attribute_string_list = list()
    for index, attribute in enumerate(WEATHER_ATTRIBUTES):
        space_count = max_length[index] - len(attribute)
        attribute_string_list.append("| " + attribute + (" " * space_count) + " |")
    print("".join(attribute_string_list))
    print("-" * (total_length + 20))
    
    for weather_report in weather_data_list:
        index_variable = 0
        weather_report_string_list = list()
        for value in weather_report.values():
            space_count = max_length[index_variable] - len(value)
            weather_report_string_list.append("| " + value + (" " * space_count) + " |")
            index_variable += 1
        print("".join(weather_report_string_list))
    print("-" * (total_length + 20))
                
    
def orchestrator_method():
    
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, "w", encoding = "utf-8") as weather_file:
            writer = csv.DictWriter(weather_file, fieldnames = WEATHER_ATTRIBUTES)
            writer.writeheader()
        weather_file.close()
        print(f"A new file with the name {FILE_NAME} has been created.")
        save_current_weather_report()
    
    while True: 
        app_capabilities = [
            {"Save Weather Report For City": save_current_weather_report},
            {"View Weather Report For City": view_current_weather_list},
            {"See Weather Metrics": weather_stats_method}
        ]
        
        print("The app has the following capabilities: ")
        for index, capabilities in enumerate(app_capabilities):
            print(f"Select {index + 1} for {"".join([capability for capability in capabilities.keys()])}")
        
        user_input = int(input("Enter the functionality you want to leverage: ").strip()) - 1
        app_capabilities[user_input]["".join(capability for capability in app_capabilities[user_input].keys())]()
        
        continue_flag = input("Do you want to continue (y/n): ").lower().strip()
        if continue_flag == "n":
            print("The program has terminated.") 
            break
    
    
orchestrator_method()
