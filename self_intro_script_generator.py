# Self-Intro Script Generator 
# Main challenge is wrapping the intro in block of stars
def self_intro_script_generator():
    user_dictionary = dict()
    required_fields = ["Name", "Age", "City", "Profession", "Hobbies"]
    
    for field in required_fields:
        if field == "Hobbies": 
            # use of list comprehension
            user_dictionary["Hobbies"] = [hobby.lower() for hobby in input("Enter your hobbies (sep by commas): ").split(",")]
        else: user_dictionary[field] = input(f"Enter your {field.lower()}: ")
    
    self_intro_script_1 = f"Hello,my name is {user_dictionary["Name"].upper()}. I am {user_dictionary["Age"]} years old."
    self_intro_script_2 = f"I'm a {user_dictionary["Profession"].upper()} by profession. My hobbies are {",".join(user_dictionary["Hobbies"])}."
    
    script_lengths = [len(self_intro_script_1), len(self_intro_script_2)]
    
    diff_in_length = abs(script_lengths[0] - script_lengths[1])
    if script_lengths[0] > script_lengths[1]: self_intro_script_2 += " " * diff_in_length
    else: self_intro_script_1 += " " * diff_in_length
        
    print("\n")
    print("*" * (max(script_lengths[0], script_lengths[1]) + 4))
    print("* " + self_intro_script_1 + " *")
    print("* " + self_intro_script_2 + " *")
    print("*" * (max(script_lengths[0], script_lengths[1]) + 4))
 
self_intro_script_generator() 
