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

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.command()
async def helloworld(ctx):
    await ctx.send("Hello World!")

@bot.command()
async def homework(ctx):
    now = datetime.datetime.now()
    min_date = datetime.datetime.now() - datetime.timedelta(days=240)
    # Get homework assignments from the Canvas API
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
    headers = {'Authorization': f'Bearer {CANVAS_ACCESS_TOKEN}'}
    courses_url = f'{CANVAS_API_URL}/courses'
    response = requests.get(courses_url, headers=headers, verify=certifi.where())

    if response.status_code == 200:
        courses = response.json()
        filtered_assignments = []

        for course in courses:
            course_id = course['id']
            assignments_url = f'{CANVAS_API_URL}/courses/{course_id}/assignments'
            assignments_response = requests.get(assignments_url, headers=headers, verify=certifi.where())

            if assignments_response.status_code == 200:
                assignments = assignments_response.json()

                for assignment in assignments:
                    due_date = assignment['due_at']

                    if due_date is not None:
                        due_date = datetime.datetime.strptime(due_date, "%Y-%m-%dT%H:%M:%SZ").date()

                        if due_date > min_date:
                            assignment_id = assignment['id']
                            submission_url = f'{CANVAS_API_URL}/courses/{course_id}/assignments/{assignment_id}/submissions/self'
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
    else:
        return []




bot.run(TOKEN)