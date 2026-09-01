import random
layout_styles = [{"Style Number": 1,
                  "Style Structure": "\nEmoji| Name | Profession | Passion/Goal | Website/Handle",
                  "Example": "\n:) | Hardik Gupta | Software Engineer | Coding | www.linked-hardik-gupta.com"},
                  
                  {"Style Number": 2,
                  "Style Structure": "\nEmoji| Name | Profession |\nPassion/Goal | Website/Handle",
                  "Example": "\n:) | Hardik Gupta | Software Engineer |\nCoding | www.linked-hardik-gupta.com"}]
 
def dont_repeat_yourself(layout_styles):
    for style in layout_styles: 
        print(f"\nLayout Style {style["Style Number"]}")
        print(f"Following is the structure of style {style["Style Number"]} followed by an instance")
        print(f"{style["Style Structure"]}")
        print(f"{style["Example"]}")
 
def format_user_bio(user_dictionary, layout_preference):
    
    user_fields = ["Fav Emoji", "Name", "Profession", "Passion or Goal", "Website/Handle"]
    # hashtag generator
    hashtags = ["#" + word for word in f"{user_dictionary["Passion or Goal"] +" "+ user_dictionary["Profession"]}".split(" ")]
    hashtag_string = " ".join(random.sample(hashtags, random.randint(1, len(hashtags))))
    list_of_info = [key for key in user_fields if key in user_dictionary.keys()]
    # for preference 1
    if layout_preference == 1: 
        user_bio = []
        for info in list_of_info: user_bio.append(user_dictionary[info])
        return " | ".join(user_bio)
    # for preference 2 
    elif layout_preference == 2: 
        count_of_info = 0
        formatted_string = ""
        for info in list_of_info:
            count_of_info += 1
            if count_of_info == 4: formatted_string += "\n"
            formatted_string += f"{user_dictionary[info]}" + " | "
        return formatted_string
        
def stylish_bio_generator():
    global layout_styles
    user_dictionary = dict()
    list_of_requirements = {"Name": "Hey, What's your name?: ", 
                            "Profession": "What do you do for a living?: ", 
                            "Passion or Goal": "What's your passion, something you wanna acheive (one liner): ",
                            "Fav Emoji": "Which emoji describes you the best (emoji/ignore): ",
                            "Website/Handle": "Where else can someone find you (link/ignore): "}
                    
    for requirement in list_of_requirements.keys():
        if requirement in ["Website/Handle", "Fav Emoji"]:
            test_input = input(f"{list_of_requirements[requirement]}").strip().lower()
            if test_input == "ignore": continue
            else: user_dictionary[requirement] = test_input
        
        else: user_dictionary[requirement] = input(f"{list_of_requirements[requirement]}: ").strip()
        
    print("\nYou can style your bio in the following ways:")
    dont_repeat_yourself(layout_styles)
    
    user_preference = int(input("\nWhich layout style do you prefer?: ").strip())
    user_bio = format_user_bio(user_dictionary, user_preference)
    print(f"\nFollowing is the generated user bio:\n{user_bio}")

    save_to_file = input("\nDo you want to save this bio to a file (y/n): ").strip().lower()
    try:
        if save_to_file == "y":
            filename = f"{user_dictionary["Name"].lower().replace(" ", "_")}_bio.txt"
            with open (filename, "w", encoding = "utf") as file:
                file.write(user_bio)
    except Exception as error: print(f"The following error occured: {error}")
    else: print("Your file has been saved successfully!")
    finally: print("The program has terminated.")

    
stylish_bio_generator()
