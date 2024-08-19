import os
import time
import csv
from crewai import Crew
from agents import EmailPersonalizationAgents
from tasks import PersonalizeEmailTask
from langchain_groq import ChatGroq

# 0. Setup environment
from dotenv import load_dotenv
load_dotenv()

email_template = """
Hey [Name]!

Are you ready to lead in the AI-driven future of work? The Foregrounds invites you to join our exclusive global community of trailblazers who are reimagining their industries through AI. 

Introducting the Foregrounds Membership:
On-Demand Learning

    - Executive-focused primers on key AI topics
    - Comprehensive framework library
    - Detailed tool reviews and case studies

Global Leadership Network

    - Connect with senior members from leading companies worldwide
    - Engage in our private Slack community
    - Exclusive speaker series and summit invitations

Exclusive Perks

    - Software discounts from top AI providers
    - Access to vetted AI strategists and implementation specialists
    - Quick-win implementation guides for immediate impact

Additionally, don't miss this opportunity to enroll in one of our courses, set to start in Q1 2025!
    - AI for Marketers
    - AI for Finance

We look forward to hearing back from you!
Best regards,
The Foregrounds Team
"""

# 1. Create agents
agents = EmailPersonalizationAgents() # Creates instance of the EmailPersonalizationAgents class so we can create agents

# calls the two methods inside the agents.py file which will return agents for us.
email_personalizer = agents.personalize_email_agent() # this will be our email personalizer agent
ghostwriter = agents.ghostwriter_agent() # this will be our ghostwriter agent

# 2. Create tasks
tasks = PersonalizeEmailTask() # creates instance of PersonalizeEmailTask class

# we need to dynamically create our tasks depending on the number of clients we want to outreach.
#arrays to store all of our tasks
personalize_email_tasks = [] 
ghostwrite_email_tasks = []

# Path to the CSV file containing client information
csv_file_path = 'data/clients_medium.csv'

# Open the CSV file
with open(csv_file_path, mode='r', newline='') as file:
    # Create a CSV reader object
    csv_reader = csv.DictReader(file) # csv reader reads file, now we have access to the info in that file
    print(csv_reader)

    # Iterate over each row in the CSV file
    for row in csv_reader:
        # Access each field in the row
        recipient = { # recipient object
            'first_name': row['first_name'], # row[colname] denotes a column
            'last_name': row['last_name'],
            'email': row['email'],
            'bio': row['bio'],
            'last_conversation': row['last_conversation']
        }

        # Create a personalize_email task for each recipient
        personalize_email_task = tasks.personalize_email(
            agent=email_personalizer,
            recipient=recipient,
            email_template=email_template
        )

        # Create a ghostwrite_email task for each recipient
        ghostwrite_email_task = tasks.ghostwrite_email(
            agent=ghostwriter,
            draft_email=personalize_email_task,
            recipient=recipient
        )

        # Add the task to the crew
        personalize_email_tasks.append(personalize_email_task)
        ghostwrite_email_tasks.append(ghostwrite_email_task)


# Setup Crew
crew = Crew(
    agents=[
        email_personalizer,
        ghostwriter
    ],
    tasks=[
        *personalize_email_tasks, # similar to the spread operator in javascript, spreads the lists into another list
        *ghostwrite_email_tasks
    ],
    max_rpm=15 # SPECIFIC TO USING GROQ - RATE LIMIT OF 30 CALLS PER LIMIT. NEED TO BE CAREFUL NOT TO HIT LIMIT!
)

# Kick off the crew
start_time = time.time()

results = crew.kickoff()
print(results)

end_time = time.time()
elapsed_time = end_time - start_time

print(f"Crew kickoff took {elapsed_time} seconds.")
print("Crew usage", crew.usage_metrics)
