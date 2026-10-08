import os
import json
import openai
from dotenv import load_dotenv
from openai import OpenAI
from IPython.display import Markdown, display
from logging_object import get_logger

load_dotenv("../.env")
logger = get_logger(__name__)
client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))
VARIOUS_MODELS = ["gpt-5.6-luna", "gpt-4o-mini", "gpt-5.4", "gpt-5.6"]

# Build an agentic calculator, that extracts the operation from the request and the operands in order to complete a calculation
def addition_method(number_1, number_2):
    logger.info("The function [addition_method] was used")
    return int(number_1) + int(number_2)

def subtraction_method(number_1, number_2):
    logger.info("The function [subtraction_method] was used")
    return int(number_1) - int(number_2)

def multiplication_method(number_1, number_2):
    logger.info("The function [multiplication_method] was used")
    return int(number_1) * int(number_2)

def division_method(number_1, number_2):
    logger.info("The function [division_method] was used")
    return round(float(int(number_1)/int(number_2)))

calculator_dictionary = {
    "addition": addition_method,
    "subtraction": subtraction_method,
    "multiplication": multiplication_method,
    "division": division_method
}

SYSTEM_INSTRUCTIONS = """You are a simple calculator agent that takes in an expression, extracts one part of the expression based on
BODMAS rules and returns a JSON response of the following sorts (for the current expression: 10*(9 + 10)):
        {
        "operation_type": "addition",
        "number_1": "9",
        "number_2": "10",
        "remaining_expression": "10*(result_of_previous_iteration)"
        }

Your input will come in the following format:
    [reamining_expression: 20 + 10 * (result_of_previous_iteration), result_of_previous_iteration: 17]
    the expression to be evaluated by you becomes: 20 + 10 * 17
    The JSON response in this case becomes:
        {
        "operation_type": "multiplication",
        "number_1": "10",
        "number_2": "17",
        "remaining_expression": "20 + result_of_previous_iteration"
        }

Start Case:
If an input comes something like: 
    remaining_expression: 20 + 3 / 2 * 4, meaning there is no variable, then consider it as the first iteration and ignore the 
    result_of_previous_iteration, and simply follow the steps, in this case:
        {
        "operation_type": "division",
        "number_1": "3",
        "number_2": "2",
        "remaining_expression": "20 + result_of_previous_iteration * 4"
        }

End Case:
If the input comes something like:
    remaining_expression: 10 * result_of_previous_iteration, result_of_previous_iteration: 31, meaning this will 
    be the last iteration of the calculation, then in this case
    expression becomes 10 * 31
        {
        "operation_type": "multiplication",
        "number_1": "10",
        "number_2": "31",
        "remaining_expression": "completed"
        }

"""

user_calculation_input = original_expression = input("Enter the calculation you want to perform: ").strip().lower()
value_be_filled = None
user_calculation_input = user_calculation_input.replace(" ", "")


for character in user_calculation_input:
    if not character.isdigit() and character not in "+-*/()":
        raise ValueError('Invalid Calculation Type')

while True:
    messages = [{"role": "user", "content": f"remaining_expression: {user_calculation_input}, result_of_previous_iteration: {value_be_filled}"}, 
                {"role": "system", "content": SYSTEM_INSTRUCTIONS}]
    llm_response = openai.chat.completions.create(model = "gpt-5.6-luna", messages = messages)
    calculation_response = json.loads(llm_response.choices[0].message.content)
    value_be_filled = calculator_dictionary[calculation_response["operation_type"]](calculation_response["number_1"], calculation_response["number_2"])
    user_calculation_input = calculation_response["remaining_expression"]
    if user_calculation_input.lower().strip() == "completed":
        break

print(f"The result of the expression [{original_expression}] is: {value_be_filled}") 
