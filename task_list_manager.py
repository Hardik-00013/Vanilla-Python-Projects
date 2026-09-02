FILENAME = "tasks.txt"
TASK_ATTRIBUTES = ["task_id", "task_name", "task_description", "task_priority", "completion_status"]
NUMBER_OF_ATTRIBUTES = len(TASK_ATTRIBUTES)

class Task():
    # Also acts as task addition method
    def __init__(self, task_id, task_name, task_description, task_priority = "Low", completion_status = False):
        """Creates a new task and adds that to the tasks.txt file"""
        self.task_id = task_id
        self.task_name = task_name
        self.task_description = task_description
        self.task_priority = task_priority 
        self.completion_status = completion_status
        try:
            with open(FILENAME, "a") as task_file:
                task_file.write("\n")
                for attribute in TASK_ATTRIBUTES: task_file.write(f"\n{attribute.upper()}: {getattr(self, attribute)}")
        except Exception as error: print(f"An error occured: {error}")
        else: print("The task has been added successfully.")
            

def view_current_tasks():
    """Displays the tasks that are currently present in the tasks.txt file"""
    with open(FILENAME, 'r') as open_file: tasks_list = open_file.readlines()
    seperation_counter = 0
    print(tasks_list)
    for task in tasks_list:
        if task == "\n": continue
        if seperation_counter % 5 == 0: print("-" * 40)
        print(task)
        seperation_counter += 1

def helper_function_1(filename, task_id):
    """Returns the index of required task along with list of all the tasks"""
    with open(filename, "r", encoding = "utf-8") as task_file: 
        task_list = task_file.readlines()
    task_file.close()
    for index, task in enumerate(task_list):
        if task == "\n": continue
        if task in ["TASK_ID: " + task_id + "\n", "TASK_ID: " + task_id + " ✅" + "\n"]: 
            return index, task_list

def helper_function_2(filename, task_list):
    """Takes a filename and task list and compiles it back"""
    with open(filename, "w", encoding = "utf-8") as task_file: 
        task_file.write("".join(task_list))
    task_file.close()
  
def delete_tasks_from_list(task_id):
    """Deletes the tasks present in the tasks.txt file"""
    index_of_task, task_list = helper_function_1(FILENAME, task_id)   
    for _ in range(5): task_list.pop(index_of_task)
    helper_function_2(FILENAME, task_list)
    print(f"The task with id {task_id} has been deleted.")


def update_task_present_in_list(task_id):
    """Updates a certain attribute of an already existing task"""
    update_variables = {1: "TASK_NAME", 2: "TASK_DESCRIPTION", 3: "TASK_PRIORITY"}
    index_of_task, task_list = helper_function_1(FILENAME, task_id)
    print("\nFor Updating:\nTASK_NAME: Enter 1\nTASK_DISCRIPTION: Enter 2\n TASK_PRIORITY: Enter 3")

    user_input = int(input("What do you want to update: ").strip())
    new_variable = input(f"Enter the new {update_variables[user_input].replace("_", " ").lower()}: ").strip()
    task_list[index_of_task + user_input] = update_variables[user_input] + ": " + new_variable + "\n"
    print("The task has been updates successfully")
    helper_function_2(FILENAME, task_list)


def mark_task_as_completed(task_id):
    """Marks task with the specified id as completed"""
    index_of_task, task_list = helper_function_1(FILENAME, task_id)
    task_list[index_of_task] = task_list[index_of_task][:len(task_list[index_of_task]) - 1] + " ✅" + "\n"
    task_list[index_of_task + 4] = "Task_Priority: " + "True\n"
    helper_function_2(FILENAME, task_list)
    print(f"The task with task id {task_id} has been marked as completed.")

def user_task_creation_method():
    """Takes input of task information from user"""
    attributes_list = []
    task_attributes = ["TASK_ID", "TASK_NAME", "TASK_DESCRIPTION", "TASK_PRIORITY", "COMPLETION_STATUS"]
    for attribute in task_attributes:
        user_input = input(f"Enter the {attribute.replace("_", " ").lower()}: ")
        attributes_list.append(user_input)
    new_task = Task(attributes_list[0], attributes_list[1], attributes_list[2], attributes_list[3], attributes_list[4])
    del new_task

def orchestrator_method():
    """Bring everything together"""
    # Checking if the file is empty 
    with open(FILENAME, "r", encoding = "utf-8") as task_file:
        task_list = task_file.readlines()
    task_file.close()
    if len(task_list) == 0:
        print("No task exists in the file as of now. First add a task.")
        user_task_creation_method()
    
    user_options = {1: "Add a new task to the list",
                    2: "View all tasks",
                    3: "Modify an already existing task",
                    4: "Mark the task as completed",
                    5: "Delete task from the list",
                    6: "Exit the application"
                    }
    while True:
        print("Hi, you can do the following things in your list:")
        for index, option in user_options.items():
            print(f"Select {index} to: [{option}]")
        user_input = int(input("Enter the operation that you want to perform: ").strip())
        if user_input == 1: user_task_creation_method()
        elif user_input == 2: view_current_tasks()
        elif user_input == 3:
            task_be_modified = input("Enter the id of task you want to modify: ").strip()
            update_task_present_in_list(task_be_modified)
        elif user_input == 4:
            task_be_marked_comp = input("Enter the id of task you want to mark as completed: ").strip()
            mark_task_as_completed(task_be_marked_comp)
        elif user_input == 5:
            task_be_deleted = input("Enter the id of task you want to delete: ").strip()
            delete_tasks_from_list(task_be_deleted)
        else: 
            print("The current session has ended")
            break



orchestrator_method()
    






    









