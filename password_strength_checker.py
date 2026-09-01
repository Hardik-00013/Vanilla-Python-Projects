import random
import getpass
import string
 
string_of_digits = "1234567890"
string_of_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
string_of_special_characters = "!@#$%^Z&*()"
SPACES_TO_CHOOSE = [string_of_digits, string_of_letters, string_of_letters.lower(), string_of_special_characters]
 
def password_strength_modifier(random_password, string_be_checked):
    count_of_check = 0
    for char in random_password:
        if char in string_be_checked: count_of_check += 1
    if count_of_check == 0:
        return random_password + string_be_checked[random.randint(0, len(string_be_checked) - 1)]
    else: return random_password
        
def random_password_generator() -> str:
    length_of_password = random.randint(10, 20)
    random_password_list = list()
    random_password = ""
    for i in range(length_of_password):
        random_password_list.append(random.sample(SPACES_TO_CHOOSE[random.randint(0, 3)], 1)[0])
    random_password = "".join(random_password_list)
    for index, space in enumerate(SPACES_TO_CHOOSE):
        random_password = password_strength_modifier(random_password, space)
    return random_password
    
def password_str_check_suggestor(password):
    issues_with_password = list()
    
    if len(password) < 8:
        issues_with_password.append("The password should be atleast 8 characters in length.")
        
    if not any(character.isupper() for character in password):
        issues_with_password.append("The password must contain atleast 1 uppercase letter.")
        
    if not any(character.islower() for character in password):
        issues_with_password.append("The password must contain atleast 1 lowercase letter.")
        
    if not any(character.isdigit() for character in password):
        issues_with_password.append("The password must contain atleast 1 digit.")
 
    if not any(character in string.punctuation for character in password):
        issues_with_password.append("The password must contain atleast 1 special character.")
        
    if not issues_with_password:
        print(f"Your password {password} is quite strong.")
    else:
        print("\nYour password has the following issues: ")
        for index, issue in enumerate(issues_with_password):
            print(f"{index + 1}. {issue}")
        print(f"\nHere is a strong password for your use: {random_password_generator()}")    
        
 
user_password = getpass.getpass(prompt="Enter your password: ")
password_str_check_suggestor(user_password)
