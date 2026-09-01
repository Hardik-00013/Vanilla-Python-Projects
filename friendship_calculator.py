# Friendship Calculator
 
def friendship_calculator(friend_name_1, friend_name_2):
    
    # getting all the necessary variables
    combined_string = friend_name_1.lower().strip() + friend_name_2.lower().strip()
    combined_length = len(friend_name_1.strip()) + len(friend_name_2.strip())
    shorter_length = min(len(friend_name_1), len(friend_name_2))
    
    # getting the number of common character indices
    common_character_indices = 0
    for i in range(shorter_length):
        if friend_name_1[i].lower() == friend_name_2[i].lower():
            common_character_indices += 1
    common_char_index_score = float(common_character_indices/shorter_length)
            
    # getting all the distinct characters used in both the names
    all_distinct_characters = set()
    for character in combined_string:
        all_distinct_characters.add(character)
        
    # getting all the distinct common characters
    common_character_list = set()
    for character in friend_name_1.lower():
        if character in friend_name_2.lower():
            common_character_list.add(character)
    character_similarity_score = float(len(common_character_list)/len(all_distinct_characters))
    
    # getting all the vowels in both names
    distinct_vowels = set()
    for character in combined_string:
        if character in "aeiou": distinct_vowels.add(character)
    vowels_presence_score = float(len(distinct_vowels)/5)
    
    # checking the length
    length_difference = 0
    if len(friend_name_1) != len(friend_name_2):
        length_difference = abs(len(friend_name_1) - len(friend_name_2))
    length_difference_score = (1 if length_difference == 0 else 1 - (length_difference/20))
    
    # calculating and returning the final score
    final_score = (round(common_char_index_score * 30 + 
    character_similarity_score * 30 + length_difference_score * 30 + vowels_presence_score * 10))
    return final_score
    
def box_generator(user_string):
    print("\n" + "*" * (len(user_string) + 4))
    print("* " + user_string + " *")
    print("*" * (len(user_string) + 4))
    
    
friend_name_1 = input("Enter the name of friend 1: ").strip()
friend_name_2 = input("Enter the name of friend 2: ").strip()
friendship_score = friendship_calculator(friend_name_1, friend_name_2)
 
if friendship_score <= 34:
    box_generator(f"Score: {friendship_score} | Opposites attract, maybe?")
elif friendship_score > 34 and friendship_score < 75:
    box_generator(f"Score: {friendship_score} | You guys are closer than you think!")
else:
    box_generator(f"Score: {friendship_score} | Damn, you guys are more than just friends ;)")
