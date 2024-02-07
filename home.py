# import speech_recognition as sr
import platform
import os
import subprocess
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
from colorama import Fore
from langchain_core.runnables import chain
from langchain_core.tools import tool
from Markdown2docx import Markdown2docx

from langchain_core.output_parsers import JsonOutputParser

from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import AgentExecutor, Agent
from langchain.agents.agent import AgentExecutor
from langchain.agents.output_parsers import XMLAgentOutputParser
from langchain.agents import AgentExecutor, create_openai_tools_agent
from docx import Document


from langchain_core.output_parsers import StrOutputParser

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

clear_screen()

model = ChatOpenAI()

print(Fore.GREEN + "Welcome to the the BAI virtual assisant CLI")

# r = sr.Recognizer()


def speak(text):
    os_name = platform.system()
    if os_name == 'Darwin':  # macOS
        subprocess.call(['say', text])
    elif os_name == 'Windows':  # Windows
        powershell_command = f'Add-Type -AssemblyName System.speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Speak("{text}");'
        subprocess.call(["powershell", "-Command", powershell_command])

def listen():
    # with sr.Microphone() as source:
        # print("Talk")
        # audio_text = r.listen(source)
        # print("I think you stopped talking, I am trying to understand your text")    
        # try:
        # # using google speech recognition
        #     # print('i am trying to understand your text, this can take a while')
        #     text = r.recognize_google(audio_text)
        #     return text
        # except:
        #     speak("Sorry, I did not get that")
        #     return "error"
    raise NotImplemented


@tool
def print_to_screen(input:str) -> None:
    """Prints the input to the screen"""
    print('logging input')
    print(input)

@tool
def create_word_document_from_input(tool_input):
    """Create a new Word Document from input text in markdown format"""
    print(Fore.BLUE+'creating word document')
    with open('intermediate.md', 'w') as f:
        f.write(tool_input)
    project = Markdown2docx('intermediate')
    project.eat_soup()
    project.save()

@tool
def create_remarkjs_presentation_from_input(tool_input):
    """Create a new remark.js Presentation from input text in markdown format"""
    print(Fore.BLUE+'creating powerpoint presentation')
    output = """<!DOCTYPE html>
    <html>
    <head>
    <title>Title</title>
    <meta charset="utf-8">
    <style>
      @import url(https://fonts.googleapis.com/css?family=Yanone+Kaffeesatz);
      @import url(https://fonts.googleapis.com/css?family=Droid+Serif:400,700,400italic);
      @import url(https://fonts.googleapis.com/css?family=Ubuntu+Mono:400,700,400italic);

      body { font-family: 'Droid Serif'; }
      h1, h2, h3 {
        font-family: 'Yanone Kaffeesatz';
        font-weight: normal;
      }
      .remark-code, .remark-inline-code { font-family: 'Ubuntu Mono'; }
    </style>
  </head>
  <body>
    <textarea id="source">
""" + str(tool_input) + """

    </textarea>
    <script src="https://remarkjs.com/downloads/remark-latest.min.js">
    </script>
    <script>
      var slideshow = remark.create();
    </script>
  </body>
</html>
    """
    with open('index.html', 'w') as f:
        f.write(output)

search = DuckDuckGoSearchRun#S()    
from langchain_core.runnables import RunnablePassthrough

# chain = prompt | model | search | StrOutputParser 
# chain = {'input': RunnablePassthrough()}|prompt | model | search | StrOutputParser 

template = """turn the following user input into a search query for a search engine:
{input}"""

prompt1 = ChatPromptTemplate.from_template(template)
prompt2 = ChatPromptTemplate.from_template("summarize into 2 lines {input}")
prompt3 = ChatPromptTemplate.from_template("""
                                           create a logical document based upon the input, you can expand the document so it reads fluently.
                                           your output shoule be in markdown format
                                           input_text: {input_text} 
                                           """
                                           
                                           )
prompt4 = ChatPromptTemplate.from_template("""
                                           create the input for a remark.js document. The code is written but you need to provide the input for the textarea, the rest is done.
                                           your output is the markdown output only, prefer to create multiple slides. 
                                           input_text: {input_text} 
                                           """
                                           
                                           )






@chain
def mychain(text):
    output1 = ""
    if 'search>>' in text:
        text = text.replace('search>>', '')
        prompt_val1 = prompt1.invoke({"input": text})
        output1 = ChatOpenAI().invoke(prompt_val1)
        print(output1)
        parsed_output1 = StrOutputParser().invoke(output1)
        print(parsed_output1)
        try:
            output1 = search().run(parsed_output1)
        except:
            output1 = "there is a rate limit on the search engine, please try again later"
    else:
        output1 = text
    
    print_to_screen.invoke({"input":output1})

    # intermediate task with no output in the chain, but does an intermediate task
    from operator import itemgetter

    p = prompt3.invoke({"input_text":output1})
    output = ChatOpenAI().invoke(p)
    output = StrOutputParser().invoke(output)
    create_word_document_from_input.invoke({"tool_input":output})
    p = prompt4.invoke({"input_text":output1})
    output = ChatOpenAI().invoke(p)
    output = StrOutputParser().invoke(output)
    create_remarkjs_presentation_from_input.invoke({"tool_input":output})
    
    parsed_output1 = StrOutputParser().invoke(output1)
    chain2 = prompt2 | ChatOpenAI() | StrOutputParser()
    return chain2.invoke({"input": parsed_output1})

commands = []

user_input = ""
while user_input != "exit":
    try:
        user_input = input(Fore.WHITE + "Enter text: ")
        if user_input == "voice":
           user_input = listen()
           print(Fore.GREEN + user_input)      
        response = mychain.invoke(user_input)

        speak(response)
        print(Fore.GREEN + response)
    except KeyboardInterrupt:
        break


