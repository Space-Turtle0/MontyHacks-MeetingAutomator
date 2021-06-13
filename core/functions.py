import json
import os
import shutil

import pymsgbox
from prompt_toolkit.validation import ValidationError, Validator
from PyInquirer import print_json, prompt

#Our Custom Traceback Class
class UnExpectedInputValue(Exception):
    def __init__(self, value: str, expect: str):
        self.msg = value
        self.expect = expect
        self.pre = f"Invalid Operation\nExpected {expect}, got:"
        self.message = f"{self.pre} {self.msg}"
        super().__init__(self.message)

#Checks if a specific input is an integer. 
class NumberValidator(Validator):
    def validate(self, document):
        try:
            int(document.text)
        except ValueError:
            raise ValidationError(
                message='Please enter a number',
                cursor_position=len(document.text))

#Unicodes for our colored text. 
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def notify(title, text):
    os.system("""
            osascript -e 'display notification "{}" with title "{}"'""".format(text, title))


def infoNotify(text):
    notify("Launching Session", text)
    pymsgbox.alert(text, 'AUTOMATED MESSAGE')

def checkForZoom():
    return shutil.which("Zoom")

def getInput(questions, value):
    try:
        answers = prompt(questions)
        y = json.dumps(answers)
        x = json.loads(y)
        return x[value]
    except:
        return

def retriveInput(answers, value):
    try:
        y = json.dumps(answers)
        x = json.loads(y)
        return x[value]
    except:
        return



"""JSON/Dict's for our CLI"""

#Setup

Setup1 = [
    {
        'type': "confirm",
        'name': "setup1",
        'message': "\nDo you use Block Scheduling? (Eg; alternating days with different schedules on each day)",
        'default': False
    }
]


Setup2 = [
    {
        'type': "list",
        'name': "setup2",
        'message': "\nWhat day is it today?\n(This in terms of your Block Scheduling, this still applies to you if you are on the weekend. For example if today is Saturday and Friday was a B day, Saturday would be an A day.)",
        'choices': ['A', 'B']
    }
]





#-
questions = [
    {
        'type': "list",
        'name': "startAction",
        'message': "\nWhat would you like to do today?",
        'choices': ['Launch Meeting', 'Create Meeting', 'Remove Meeting', "List Meetings", "Exit"]
    }
]



searchMeeting = [
    {
    'type': "input",
    'name': "meetingQuery",
    'message': "\nSearch Query: (Searching by period)"
    }
]



confirmRemove = [
    {
    'type': "confirm",
    'name': "modifyAction",
    'message': "\nAre you sure you want to remove this?",
    "default": False
    }
]

numberValue = [
    {
    'type': 'input',
    'name': 'quantity',
    'message': '\nHow many classes do you want to setup?',
    'validate': NumberValidator,
    'filter': lambda val: int(val)
    }
]

classSetup = [
    {
    'type': 'input',
    'name': 'period',
    'message': '\nWhen do you have this class? (Ex: 1A)'
    },

    {
    'type': 'input',
    'name': 'day',
    'message': "\nWhat day do you have this class? (Block Scheduling)\nEnter None if you don't have Block Scheduling."
    },

    {
    'type': 'list',
    'name': 'linkType',
    'message': '\nSelect the Meeting Provider',
    'choices': ['Zoom', 'Google Meet']
    },

    {
    'type': 'input',
    'name': 'link',
    'message': '\nEnter the Meeting URL:',
    },

    {
    'type': 'input',
    'name': 'timeStart',
    'message': '\nWhen does this class start? (24 Hour Time Format)'
    }
]




LaunchMeeting = [
    {
    'type': 'input',
    'name': 'periodRequest',
    'message': '\nEnter Period to Launch:'
    }
]
