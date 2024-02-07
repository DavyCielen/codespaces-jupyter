import os
import platform
import subprocess
import speech_recognition as sr
from abc import ABC, abstractmethod
from dotenv import load_dotenv
from colorama import Fore
from Markdown2docx import Markdown2docx
from docx import Document
from langchain_core.runnables import chain
from langchain_core.tools import tool
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Clear screen function
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
clear_screen()

print(Fore.GREEN + "Welcome to the BAI virtual assistant CLI")

# Recognizer for speech recognition
r = sr.Recognizer()

# Command Pattern Base Class
class Command(ABC):
    @abstractmethod
    def execute(self, data=None):
        pass




@tool
def print_to_screen(input:str) -> None:
    """print input to screen"""
    print('logging input')
    print(input)

@tool
def create_word_document_from_input(tool_input):
    """create a word doc"""
    print('creating word document')
    with open('intermediate.md', 'w') as f:
        f.write(tool_input)
    project = Markdown2docx('intermediate')
    project.eat_soup()
    project.save()

# Command Executor
class CommandExecutor:
    def __init__(self):
        self.commands = {
            "speak": SpeakCommand(),
            "listen": ListenCommand()
            # Add more commands as needed
        }

    def execute_command(self, command_name, data=None):
        command = self.commands.get(command_name)
        if command:
            return command.execute(data)

executor = CommandExecutor()

# Chain Function
@chain
def mychain(text):
    # The original logic of mychain here, slightly adjusted to use the CommandExecutor for speak and listen operations.
    pass

# Main interaction loop
user_input = ""
while user_input != "exit":
    try:
        user_input = input(Fore.WHITE + "Enter text: ")
        if user_input == "voice":
            user_input = executor.execute_command("listen")
            print(Fore.GREEN + user_input)
        response = mychain.invoke(user_input)
        executor.execute_command("speak", response)
        print(Fore.GREEN + response)
    except KeyboardInterrupt:
        break
