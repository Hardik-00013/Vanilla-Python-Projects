# Daily Learning Journal Logger
from datetime import datetime, date
ENTRY_NUMBER = 0

class InvalidInputError(Exception): 
    pass

def daily_learning_journal_logger():
    global ENTRY_NUMBER
    user_learning = input("What did you learn today?: ").strip()

    try: 
        with open("daily_learnings.txt", "a", encoding = "utf-8") as learning_file:
            learning_file.write(f"\n\nEntry Number: {ENTRY_NUMBER}")
            learning_file.write(f"\nUser Learning: {user_learning}")
            add_productivity = input("Do you wish to add a productivity rating? (y/n): ").strip().lower()
            if add_productivity == "y":
                productivity_rate = int(input("On a scale of 1-5, how productive was your day?: ").strip())
                if productivity_rate not in [1, 2, 3, 4, 5]: raise InvalidInputError("The number should be between 1-5")
                learning_file.write(f"\nProductivity: {productivity_rate}")
            learning_file.write(f"\nDate of Entry: {date.today().isoformat()}")
            learning_file.write(f"\nTime of Entry: {str(datetime.now().time())[0:8]}")

    except InvalidInputError as error:
        print(f"The following error occured: {error}")
    except ValueError as error:
        print(f"The following error occured: {error}")
    except Exception as error:
        print(f"The following error occured: {error}")
    else: 
        print("The entry has been successfully added")
        ENTRY_NUMBER += 1

while True:
    daily_learning_journal_logger()
    more_entries = input("Do you want to make more entries (y/n): ").lower().strip(" .,?")
    if more_entries != "y": break
