# Countdown Timer
import time 
class NegativeInputError(Exception):
    pass
 
class InvalidInputError(Exception):
    pass
 
def countdown_timer(minutes, seconds):
    all_seconds = (minutes * 60 + seconds)
    print("Starting the countdown timer....")
    time.sleep(3)
    for _ in range(all_seconds): 
        minutes_remaining = f"{'0' + str(int(all_seconds/60)) if len(str(int(all_seconds/60))) == 1 else int(all_seconds/60)}"
        seconds_remaining = f"{'0' + str(int(all_seconds % 60)) if len(str(int(all_seconds % 60))) == 1 else int(all_seconds % 60)}"
        print(f"{minutes_remaining}:{seconds_remaining} remaining.", end = "\r")
        all_seconds -= 1
        time.sleep(1)
    print("\a")
    print("The countdown timer has stopped.")
    
try: 
    user_minutes = int(input("Enter the timer minutes: "))
    if user_minutes < 0:
        raise NegativeInputError(
            "Minutes cannot be negative or float."
            )
            
    user_seconds = int(input("Enter the timer seconds: "))
    if user_seconds < 0:
        raise NegativeInputError(
            "The seconds cannot be negative or float."
            )
    if user_seconds < 0 or user_seconds > 60:
        raise InvalidInputError(
            "Seconds value must lie between 0 and 60. (both inclusive)"
            )
            
except NegativeInputError as error:
    print(f"The following error occured: {error}")
except InvalidInputError as error:
    print(f"The following error occured: {error}")
except ValueError as error:
    print(f"The following error occured: {error}")
else: 
    countdown_timer(user_minutes, user_seconds)
finally: 
    print("The program has termindated.")
