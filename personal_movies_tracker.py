import os
import json
 
FILE_NAME = "movies.json"
MOVIE_ATTRIBUTES = ["Name", "Genre", "Rating"]

def attributes_getter_method(json_movies_data_list):
    for attribute in json_movies_data_list[0].keys():
        MOVIE_ATTRIBUTES.append(attribute)

def getting_all_movies(file_name):
    with open(file_name, "r", encoding = "utf-8") as json_file:
        json_movies_data_list = json.load(json_file)
    return json_movies_data_list
    
def dumping_list_to_json_file(file_name, list_be_dumped):
    with open(file_name, "w", encoding = "utf-8") as json_file:
        json.dump(list_be_dumped, json_file, indent = 4)
    
def movies_addition_method():
    """Adds a new movie to the movies file"""
    new_movie_dict = dict()
    json_movies_data_list = getting_all_movies(FILE_NAME)
    attributes_getter_method(json_movies_data_list)
    
    for attribute in MOVIE_ATTRIBUTES:
        new_movie_dict[attribute] = input(f"Enter the {attribute.lower()} of the movie: ").strip()
    json_movies_data_list.append(new_movie_dict)
    
    dumping_list_to_json_file(FILE_NAME, json_movies_data_list)
    print("The new movie has been successfully added to the file.")
         
def display_movies(json_movies_data_list):
    """Displays all movies being passed in the list"""
    for index, movie in enumerate(json_movies_data_list):
        print(f"\nMovie Number: {index + 1}")
        for attribute, value in movie.items():
            print(f"{attribute.upper()}: {value}")
            
def view_all_movies():
    """Displays all the movies currently present in the file"""
    json_movies_data_list = getting_all_movies(FILE_NAME)
    attributes_getter_method(json_movies_data_list)
    display_movies(json_movies_data_list)
            
 
def attribute_and_value_getter(key_word):
    print(f"You can {key_word} the following attributes: ")
    for index, attribute in enumerate(MOVIE_ATTRIBUTES):
        print(f"Select {index + 1} for {attribute.upper()}")
    user_attribute_choice = int(input("\nEnter the attribute number: ").strip())
    attribute = MOVIE_ATTRIBUTES[user_attribute_choice - 1]
    value_by_user = input(f"Enter the {attribute.lower()} value you want to {key_word} for: ").strip()
    return attribute, value_by_user
    
    
def search_or_filter_movies_method():
    """Helps a user search movies, by name, genre or rating range"""
    json_data_movies_list = getting_all_movies(FILE_NAME)
    attributes_getter_method(json_data_movies_list)
    user_data = list()
    attribute, value_be_searched = attribute_and_value_getter("search")
    
    for movie in json_data_movies_list:
        if attribute is "Rating":
            if float(movie[attribute]) >= float(value_be_searched):
                user_data.append(movie)
        else:
            if movie[attribute].lower() == value_be_searched.lower(): 
                user_data.append(movie)
            
    print(f"\nUser Criteria: {attribute.upper()} is {value_be_searched.upper()}")       
    print(f"Following are the movies that match your search criteria:")
    if len(user_data) == 0: print("No Movies found")
    else: display_movies(user_data)
        
    
def update_existing_movie():
    json_data_movies_list = getting_all_movies(FILE_NAME)
    attributes_getter_method(json_data_movies_list)
    name_of_movie = input("Enter the name of the movie you want to update: ").strip()
    attribute, updated_value = attribute_and_value_getter("update")
    movie_found_flag = 0
    for movie in json_data_movies_list:
        if movie["Name"].lower() == name_of_movie.lower(): 
            movie[attribute] = updated_value
            movie_found_flag += 1
            break
    if movie_found_flag == 0: 
        print("No such movie found.")
        return 
    print(f"The movie {attribute.upper()} attribute of {name_of_movie.upper()} has been updated to {updated_value.upper()}.")
    dumping_list_to_json_file(FILE_NAME, json_data_movies_list)
    
 
def add_new_movie_attribute():
    new_attribute = input("Enter the new attribute that you want to add: ").strip()
    json_movies_data_list = getting_all_movies(FILE_NAME)
    for movie in json_movies_data_list: movie[new_attribute] = ""
    MOVIE_ATTRIBUTES.append(new_attribute)
    dumping_list_to_json_file(FILE_NAME, json_movies_data_list)
    print(f"The new attribute {new_attribute} has been successfully added to every movie.")
        
 
def orchestrator_method():
    # checking if the file exists
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, "w", encoding = "utf-8") as json_file:
            pass
        json_file.close()
        print(f"The file with name {FILE_NAME} has been created successfully.")
    
    # checking if the file contains any data
    try:
        with open(FILE_NAME, "r", encoding = "utf-8") as json_file:
            json_movies_data_list = json.load(json_file)
            
    except: 
        temporary_movie_addition = dict()
        for attribute in MOVIE_ATTRIBUTES:
            temporary_movie_addition[attribute] = input(f"Enter the {attribute.lower()} of the movie: ").strip()
        dumping_list_to_json_file(FILE_NAME, [temporary_movie_addition])
        del temporary_movie_addition
        
    
    while True:
        app_capabilities = [
            {"Add A Movie": movies_addition_method},
            {"View All Movies": view_all_movies},
            {"Search For Movies": search_or_filter_movies_method},
            {"Update Movie Information": update_existing_movie},
            {"Add An Attribute": add_new_movie_attribute}
            ]
        
        # getting the user input
        print("You can perform the following operations on your movie list: ")
        for index, capability in enumerate(app_capabilities): 
            print(f"Select {index + 1} if you want to: [{"".join([key for key in capability.keys()])}]")
        user_input = int(input("Enter the number for the task: ").strip()) - 1
        
        # executing the actual function
        app_capabilities[user_input]["".join(key for key in app_capabilities[user_input].keys())]()
        
        continue_flag = input("DO you want to continue useing the app (y/n): ").lower().strip()
        if continue_flag == "n": break
        
orchestrator_method()
