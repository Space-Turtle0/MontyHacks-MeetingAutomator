'''
MeetingAutomator by Rohit Penta

I'll quickly go over what this does and how it works.

First off the program uses a SQLite Database in order to store information
and it uses a library called PyInquirer to display the Command Line Interface.

MeetingAutomator is supposed to be a program that allows you to join meetings automatically
without having to manually open the link. This helps prevent you from being tardy
from any time sensitive meetings. There are 2 major functions that power the program,
the CLI and the backgroundTask. The backgroundTask is responsible for querying the current
time in the database and opening any associated meetings while the CLI is responsible
for providing the user interface and actually allowing the user (you) to manage the database.

'''

from __future__ import print_function, unicode_literals

import asyncio
import json
import logging
import os
import platform
import shutil
import subprocess
import sys
import threading
import time
import webbrowser
from datetime import date, datetime, timedelta
from pprint import pprint
from re import L
from threading import Thread
from turtle import back
from types import LambdaType

import pandas as pd
import pymsgbox
import regex
import timeboard as tb
from prompt_toolkit.shortcuts import confirm
from prompt_toolkit.validation import ValidationError, Validator
from pygments.lexer import default
from PyInquirer import print_json, prompt
from tqdm import tqdm

from core import database
from core.functions import *

now = datetime.now()

#We create a loading bar so we can give some time for peewee to create our database. 
for i in tqdm(range(10)):
    time.sleep(0.5)


#Let's start off by checking if the user has already created and setup the program, the conditions below are the deciding factors.
try:
    query = database.SetupStatus.select().where((database.SetupStatus.id == 1) & (database.SetupStatus.setupStatus == True)).get()

#If we get an Exception, that means there isn't a valid query so we know the user hasn't setup the database yet.
except Exception:

    print("[WARNING] No Setup Database Found\nEnterting Interactive Setup...")
    UseBlock = bool(getInput(Setup1, "setup1")) #Allows us to get input from the CLI
    print(UseBlock)

    if UseBlock == True:
        StartDay = getInput(Setup2, "setup2")

    else:
        UseBlock = False
        StartDay = "None"

    yearInt = int(now.strftime(r"%Y"))

    S: database.SetupStatus = database.SetupStatus.create(setupStatus = True, blockSchedule = UseBlock, startDate = now, startDay = StartDay, yearInteger = yearInt)
    S.save()

    P: database.PreviousRecord = database.PreviousRecord.create(lastDay = S.startDay)
    P.save()

    print("Setup Complete!\nProceeding to CLI...\n")
    
else:
    pass
    

query = database.SetupStatus.select().where((database.SetupStatus.id == 1) & (database.SetupStatus.setupStatus == True))
query = query.get()

#Alright our setup is complete and we KNOW that the user has a valid setup by now, lets start by creating our timetable for the users that have block scheduling.  
blockSchedule = query.blockSchedule

nextYear = str(int(query.yearInteger) + 1)
beforeYear = str(int(query.yearInteger) - 1)

daysBefore = query.startDate - timedelta(days = 1)

#This won't be used if they didn't opt in for block scheduling.
clnd = tb.Timeboard(base_unit_freq='B',start=daysBefore, end=f'13 June 2222',layout=["A", "B"])

#Logging stuff, not really important but its used by peewee for SQL statements. 
logging.basicConfig(filename='logs.log', encoding='utf-8', level=logging.DEBUG)

#This is our background task. 
def backgroundTask():
    while True:
        now = datetime.now()

        database.db.connect(reuse_if_open=True)
        cached_day = date.today().weekday()

        if blockSchedule:
            day = clnd(now).label #Get the letter of the day today. 


            if day not in ['A', 'B']:
                raise UnExpectedInputValue(day, "A or B")

            print(f"Today is an {day} day.\n")
            
            
        else:
            day = None
            

        while date.today().weekday() == cached_day:
            now = datetime.now()

            timestr = datetime.now().strftime("%H:%M")
            print("\nCurrent Time", timestr)

            #Okay so this is disabled because when the instructors are testing, its going to be a weekend which with this enabled its going to ignore any meetings. 
            #Although this is still a thing you can enable for production usage.

            #if date.today().weekday() == 5 or date.today().weekday() == 6:
                #break

            #Generate appropriate query statements to either include block scheduling or not. 
            if blockSchedule:
                query = database.MeetingSession.select().where((database.MeetingSession.timeStarted == timestr) & (database.MeetingSession.day == day))

            else:
                query = database.MeetingSession.select().where(database.MeetingSession.timeStarted == timestr)
            

            #If our query actually exists, we'll retrive the values with the .get() attribute. 
            if query.exists():
                try:
                    Details: database.MeetingSession = database.MeetingSession.select().where(database.MeetingSession.timeStarted == timestr).get()
                except:
                    break

                
                URL = Details.URL

                print(f"Launching {URL}\n")

                #Open the URL, in our browser. 
                subprocess.run(["open", URL]) 
                try:
                    #Creates a notification for you, this may fail due to how unstable it is so we'll wrap it under a try statement. 
                    infoNotify(f"Opening {URL}!")
                except:
                    print("Failed to Notify...")


            #Lets wait for 60 seconds for the next minute. (Refreshing Query)
                
                time.sleep(60)
            else:
                time.sleep(60)
        time.sleep(60)


#Our Command Line Interface. 
def CLI():
    while True:

        #Let's establish a connection to our database. 
        database.db.connect(reuse_if_open=True)
        values = getInput(questions, "startAction")

        #Determine what option the user selected. 
        if values == "Create Meeting":
            num = getInput(numberValue, "quantity")
            for x in range(num):
                answers = prompt(classSetup)

                #Get Independent Values: 
                period = retriveInput(answers, "period")
                day = retriveInput(answers, "day")
                timeStart = retriveInput(answers, "timeStart")
                linktype = retriveInput(answers, "linkType")
                URL = retriveInput(answers, "link")

                if linktype == "Zoom":
                    #This URL automatically opens zoom and joins the meeting. Basically a 0-touch feature. 
                    URL = URL.replace("https://", "zoommtg://")
                
                elif linktype == "Google Meet":
                    #Google Meet does not support 0-touch as it is a web browser type meeting and does not have a waiting room.
                    pass

                else:
                    raise UnExpectedInputValue(linktype, "Zoom or Google Meet")

                try:
                    q: database.MeetingSession = database.MeetingSession.create(period = period, day = day, timeStarted = timeStart, URL = URL)
                    q.save()
                except Exception as e:
                    #bcolors gives us *color* to our text to make it more beautiful.

                    print(f"{bcolors.WARNING}WARNING: Unable to register details!{bcolors.ENDC}\n{e}")

                else:
                    print(f"{bcolors.OKGREEN}INFO: Registered Details for{bcolors.ENDC} {period}!")
                    database.db.close()
            
            print(f"{bcolors.OKGREEN}INFO:{bcolors.ENDC} Completed Meeting Setup!")


        elif values == "Remove Meeting":
            query = getInput(searchMeeting, "meetingQuery")

            CONFIRM_REMOVE = getInput(confirmRemove, "modifyAction")
            if CONFIRM_REMOVE == True:
                try:
                    #Deletes our entry.
                    MeetingDetails: database.MeetingSession = database.MeetingSession.select().where(database.MeetingSession.period == query).get()
                    MeetingDetails.delete_instance()
                except Exception as e:
                    print(f"{bcolors.WARNING}WARNING: Unable to launch meeting!{bcolors.ENDC}\n{e}")
                else:
                    print("Successfully deleted meeting!")
            else:
                break

        elif values == "Launch Meeting":
            #This launches the meeting manually. 
            period = getInput(searchMeeting, "meetingQuery")
            query = database.MeetingSession.select().where(database.MeetingSession.period == period)
            if query.exists():
                query = query.get()
                subprocess.run(["open", query.URL])
            else:
                print("Invalid Period. No results found!")


            
        
        elif values == "List Meetings":
            totalMeets = []
            for meet in database.MeetingSession:
                totalMeets.append(f"Period: {meet.period} > Link: {meet.URL}")

            totalOutput = '\n'.join(totalMeets)
            print(totalOutput)


        elif values == "Exit":
            #NOTE: This does not exit out of EVERYTHING. This will only kill the CLI Python Process, the background task will still be running. 
            #You must enter control + C in order to kill the background task.

            print("Exiting CLI, Goodbye!")
            sys.exit(0)

        else:
            #Placeholder for user customization.
            pass

#Multi threading, this allows us to run our functions in parallel. 

Thread(target = CLI).start() 
Thread(target = backgroundTask).start() 

