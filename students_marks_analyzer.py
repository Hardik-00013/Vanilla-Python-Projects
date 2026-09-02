import os 
import csv
 
FILE_NAME = "students_marks_list.csv"
FILE_HEADERS = ["Name", "Statistics", "Machine Learning", "Database Programming"]
 
def students_list_generator(file_name):
    student_list = list()
    with open(file_name, "r", encoding = "utf-8") as students_marks_file:
        reader = csv.DictReader(students_marks_file)
        for row in reader: student_list.append(row)
    return student_list
 
def students_marks_collector():
    student_dict = dict()
    student_dict["Name"] = input("\nEnter the name of student: ").strip()
    student_subjects = ["Statistics", "Machine Learning", "Database Programming"]
    for subject in student_subjects:
        student_dict[subject] = int(input(f"Enter the marks of [{subject.lower()}]: ").strip())
    with open(FILE_NAME, "a", newline = "") as students_marks_file:
        writer = csv.DictWriter(students_marks_file, 
                    fieldnames = FILE_HEADERS)
        writer.writerow(student_dict)
    
    
def highest_lowest_calculator(calculation_type, subject_name, students_dict_list):
    
    type_score = -1 if calculation_type == "highest" else 101
    type_scoring_students = list()
    for student_dict in students_dict_list:
        condition = (int(student_dict[subject_name]) > type_score if calculation_type == "highest" 
                     else int(student_dict[subject_name]) < type_score)
        if condition:
            type_score = student_dict[subject_name]
            type_scoring_students.clear()
            type_scoring_students.append(student_dict["Name"])
        elif student_dict[subject_name] == type_score:
            type_scoring_students.append(student_dict["Name"])
    print(f"\nThe {calculation_type.lower()} score for the subject of {subject_name.lower()} is {type_score}")
    print(f"The {calculation_type.lower()} scoring students are: ")
    for index, name in enumerate(type_scoring_students): 
        print(f"{index + 1}. {name.upper()}")
        
    
def various_stats_calculator():
    calculation_type = input("Enter the calculation type: ").lower().strip()
    subject_name = " ".join([name.capitalize() for name in input("Enter the subject name: ").strip().split(" ")])
    students_dict_list = students_list_generator(FILE_NAME)
    
    if calculation_type == "average":
        marks_storage = 0
        for student_dict in students_dict_list:
            marks_storage += int(student_dict[subject_name])
        print(f"The average score for {subject_name.upper()} is {round(marks_storage/len(students_dict_list))}")
        
    elif calculation_type == "highest":
        highest_lowest_calculator("highest", subject_name, students_dict_list)
        
    elif calculation_type == "lowest":
        highest_lowest_calculator("lowest", subject_name, students_dict_list)
        
    else: print("Invalid calculation type.")
    
def orchestrator_method():
    
    while True: 
        if not os.path.exists(FILE_NAME):
            with open(FILE_NAME, "w", encoding = "utf-8") as students_marks_file:
                writer = csv.DictWriter(students_marks_file, fieldnames = FILE_HEADERS)
                writer.writeheader()
            students_marks_file.close()
            print(f"A new file with the name {FILE_NAME} has been created.")
        
        if len(students_list_generator(FILE_NAME)) == 0:
            number_of_students = int(input("\nEnter the number of students: ").strip())
            for _ in range(number_of_students): students_marks_collector()
            
        print("\nWelcome To Students Marks Analyzer")
        print("Select 1: For adding a new student\nSelect 2: For student marks statistics")
        user_input = int(input("Enter the task: ").strip())
        if user_input == 1: students_marks_collector()
        elif user_input == 2: various_stats_calculator()
        
        continue_flag = input("Do you want to continue (y/n) ").strip().lower()
        if continue_flag == "n": break
    
orchestrator_method()
