# Creating a digital twin, that does a lot of agentic things autonomously
import os
import json
import openai
from dotenv import load_dotenv
from openai import OpenAI
from IPython.display import Markdown, display
from pypdf import PdfReader
from logging_object import get_logger
from various_system_prompts import SYSTEM_INSTRUCTIONS_1, SYSTEM_INSTRUCTIONS_2, SYSTEM_INSTRUCTIONS_3
import gradio as gr

load_dotenv("../.env")
logger = get_logger(__name__)
client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))
User_Infromation_Dictionary = dict()


# --------- Data Extractor Tool
def extract_data_from_pdf_document():
    logger.info("The function [extract_data_from_pdf_document] was used")
    pdf_reader = PdfReader("Hardik_Gupta_Resume (3).pdf")
    resume_information = ""
    personal_information = ""

    for page in pdf_reader.pages:
        text = page.extract_text()
        if text: resume_information += text

    with open('user_personal_summary.txt', 'r', encoding = 'utf-8') as personal_file:
        all_lines_in_summary = personal_file.readlines()
        personal_information += "".join(all_lines_in_summary)

    all_user_information = f"resume_information: {resume_information}, personal_information: {personal_information}"
    
    messages = [{"role": "user", "content": all_user_information}, {"role": "system", "content": SYSTEM_INSTRUCTIONS_1}]
    response = openai.chat.completions.create(model = "gpt-5.6-luna", messages = messages)
    json_response = json.loads(response.choices[0].message.content)
    for key, value in json_response.items():
        User_Infromation_Dictionary[key] = value
    print("The user data has been extracted and saved in the system")


# --------- Contact Deatils Fetcher Tool
def get_contact_details(keys_required: str, User_Info: dict = User_Infromation_Dictionary) -> str:
    logger.info("The function [get_contact_details] was used")
    various_keys = keys_required.strip().lower().split(", ")
    for key in various_keys:
        if key not in ['name_of_person', 'email_id', 'phone_number']:
            logger.error("Wrong Function Called")
            raise ValueError("Wrong Function Called")
    get_all_required_info = []
    for key in various_keys:
        get_all_required_info.append(f"Key: {key}, Information: {User_Infromation_Dictionary[key]}")
    return "\n".join(get_all_required_info)


# --------- Educational Deatils Fetcher Tool
def get_educational_details(keys_required: str, User_Info: dict = User_Infromation_Dictionary) -> str:
    logger.info("The function [get_educational_details] was used")
    various_keys = keys_required.strip().lower().split(", ")
    for key in various_keys:
        if key not in ['educational_qualifications']:
            logger.error("Wrong Function Called")
            raise ValueError("Wrong Function Called")
    get_all_required_info = []
    for key in various_keys:
        get_all_required_info.append(f"Key: {key}, Information: {User_Infromation_Dictionary[key]}")
    return "\n".join(get_all_required_info)

    
# --------- Experience Deatils Fetcher Tool
def get_experience_details(keys_required: str, User_Info: dict = User_Infromation_Dictionary):
    logger.info("The function [get_expereince_details] was used")
    various_keys = keys_required.split(", ")
    for key in various_keys:
        if key not in ['experience_details', 'years_of_experience']:
            logger.error("Wrong Function Called")
            raise ValueError("Wrong Function Called")
    get_all_required_info = []
    for key in various_keys:
        get_all_required_info.append(f"Key: {key}, Information: {User_Infromation_Dictionary[key]}")
    return "\n".join(get_all_required_info)


# --------- Project Deatils Fetcher Tool
def get_projects_details(keys_required: str, User_Info: dict = User_Infromation_Dictionary):
    logger.info("The function [get_project_details] was used")
    various_keys = keys_required.split(", ")
    for key in various_keys:
        if key not in ['project_details']:
            logger.error("Wrong Function Called")
            raise ValueError("Wrong FUnction Called")
    get_all_required_info = []
    for key in various_keys:
        get_all_required_info.append(f"Key: {key}, Information: {User_Infromation_Dictionary[key]}")
    return "\n".join(get_all_required_info)


# --------- Skills Deatils Fetcher Tool
def get_skills_details(keys_required: str, User_Info: dict = User_Infromation_Dictionary):
    logger.info("The function [get_skills_details] was used")
    various_keys = keys_required.split(", ")
    for key in various_keys:
        if key not in ['skills_details']:
            logger.error("Wrong Function Called")
            raise ValueError("Wrong Function Called")
    get_all_required_info = []
    for key in various_keys:
        get_all_required_info.append(f"Key: {key}, Information: {User_Infromation_Dictionary[key]}")
    return "\n".join(get_all_required_info)


# --------- Personal Deatils Fetcher Tool
def get_personal_details(keys_required: str, User_Info: dict = User_Infromation_Dictionary):
    logger.info("The function [get_personal_details] was used")
    various_keys = keys_required.split(", ")
    for key in various_keys:
        if key not in ['all_personal_information']:
            logger.error("Wrong Function Called")
            raise ValueError("Wrong Function Called")
    get_all_required_info = []
    for key in various_keys:
        get_all_required_info.append(f"Key: {key}, Information: {User_Infromation_Dictionary[key]}")
    return "\n".join(get_all_required_info)


# --------- Miscellenious Deatils Fetcher Tool
def get_miscellenious_details(keys_required: str, User_Info: dict = User_Infromation_Dictionary):
    logger.info("The function [get_miscellenious_details] was used")
    various_keys = keys_required.split(", ")
    for key in various_keys:
        if key not in ['miscellenious_details']:
            logger.error("Wrong Function Called")
            raise ValueError("Wrong Function Called")
    get_all_required_info = []
    for key in various_keys:
        get_all_required_info.append(f"Key: {key}, Information: {User_Infromation_Dictionary[key]}")
    return "\n".join(get_all_required_info)

various_agent_tools = {
    "extract_details": extract_data_from_pdf_document,
    "contact_details": get_contact_details,
    "educational_details": get_educational_details,
    "experience_details": get_experience_details,
    "project_details": get_projects_details,
    "skills_details": get_skills_details,
    "personal_details": get_personal_details,
    "miscellenious_details": get_miscellenious_details
}

extract_data_from_pdf_document()

while True:

    # Getting the relavent function and keys based on the user's intent
    user_question = input("Ask your question: ").strip()
    if user_question.lower() == "end": break
    messages = [{"role": "user", "content": user_question}, {"role": "system", "content": SYSTEM_INSTRUCTIONS_2}]
    response = openai.chat.completions.create(model = "gpt-5.6-luna", messages = messages)
    llm_json_response = json.loads(response.choices[0].message.content)

    # Processing the LLM response in order to make it usable by the pipeline
    various_tools_be_used = llm_json_response['tools_to_be_used'].split("; ")
    tool_specific_keys = llm_json_response['keys_to_be_used'].split("; ")
    print(various_tools_be_used)
    print(tool_specific_keys)
    all_user_information = ""
    index_adjustor = 0

    # Calling the relavent functions in order to get the desired information
    for index, tool in enumerate(various_tools_be_used):
        if index == 0 and tool.lower().strip() == 'extract_details':
            extract_data_from_pdf_document()
            index_adjustor -= 1
        else:
            all_user_information += various_agent_tools[tool](keys_required = tool_specific_keys[index + index_adjustor])

    # Generating a well-formatted markdown response from the LLM
    if not (index_adjustor == -1 and len(various_tools_be_used) == 1):
        final_content = f"Question: {user_question}, Answer: {all_user_information}"
        messages = [{"role": "user", "content": final_content}, {"role": "system", "content": SYSTEM_INSTRUCTIONS_3}]
        response = openai.chat.completions.create(model = "gpt-5.6-luna", messages = messages)
        final_markdown_text = response.choices[0].message.content
        display(Markdown(final_markdown_text))
