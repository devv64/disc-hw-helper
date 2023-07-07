import discord
import requests
from discord.ext import commands
import certifi
import datetime
from config import TOKEN, CANVAS_API_URL, CANVAS_ACCESS_TOKEN


# Initialize the bot with intents
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Define headers globally
headers = {'Authorization': f'Bearer {CANVAS_ACCESS_TOKEN}'}

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.command()
async def helloworld(ctx):
    await ctx.send("Hello World!")

@bot.command()
async def homework(ctx):
    now = datetime.datetime.now()
    min_date = datetime.datetime.now() - datetime.timedelta(days=220)
    # Get homework assignments from the cache
    assignments = get_homework_assignments(min_date.date())

    if assignments:
        # Create a formatted todo list
        todo_list = '\n'.join([f'Assignment: {assignment["title"]}\n'
                      f'Due Date: {assignment["due_date"]}\n'
                      f'Course: {assignment["course"]}\n'
                      f'Status: {assignment["status"]}\n'
                      f'{"-" * 30}\n'
                      for assignment in assignments])
        response = f'Homework assignments:\n{todo_list}'
    else:
        response = 'No homework assignments found.'

    # Split the response into multiple messages if needed
    messages = [response[i:i+2000] for i in range(0, len(response), 2000)]
    
    # Send each message to the Discord channel
    for message in messages:
        await ctx.send(message)
    print(datetime.datetime.now() - now)

def get_homework_assignments(min_date):
    filtered_assignments = []

    for course in course_cache:
        course_id = course['id']
        assignments = [assignment for assignment in assignment_cache if assignment['course_id'] == course_id]

        for assignment in assignments:
            due_date = assignment['due_at']

            if due_date is not None:
                due_date = datetime.datetime.strptime(due_date, "%Y-%m-%dT%H:%M:%SZ").date()

                if due_date > min_date:
                    submission_url = f'{CANVAS_API_URL}/courses/{course_id}/assignments/{assignment["id"]}/submissions/self'
                    submission_response = requests.get(submission_url, headers=headers, verify=certifi.where())

                    if submission_response.status_code == 200:
                        submission_info = submission_response.json()
                        status = submission_info.get('workflow_state', '')
                        filtered_assignments.append({
                            'title': assignment['name'],
                            'due_date': assignment['due_at'],
                            'status': status,
                            'course': course['name']
                        })

    return filtered_assignments

def fetch_courses():
    courses_url = f'{CANVAS_API_URL}/courses'
    response = requests.get(courses_url, headers=headers, verify=certifi.where())

    if response.status_code == 200:
        return response.json()
    else:
        return []

def fetch_assignments(course_id):
    assignments_url = f'{CANVAS_API_URL}/courses/{course_id}/assignments'
    response = requests.get(assignments_url, headers=headers, verify=certifi.where())

    if response.status_code == 200:
        return response.json()
    else:
        return []

# Fetch courses and assignments when the bot starts up
course_cache = fetch_courses()
assignment_cache = []

for course in course_cache:
    course_id = course['id']
    assignments = fetch_assignments(course_id)

    for assignment in assignments:
        assignment['course_id'] = course_id

    assignment_cache.extend(assignments)

bot.run(TOKEN)
