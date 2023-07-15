import discord
import requests
from discord.ext import commands, tasks
import certifi
import datetime
from config import TOKEN, CANVAS_API_URL, CANVAS_ACCESS_TOKEN

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

headers = {'Authorization': f'Bearer {CANVAS_ACCESS_TOKEN}'}

# Define the global assignment cache and reminder task
assignment_cache = []
reminder_task = None
user_id = 220278378228350977

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    start_reminder_task()

@bot.command()
async def helloworld(ctx):
    await ctx.send("Hello World!")

@bot.command()
async def homework(ctx):
    now = datetime.datetime.now()
    min_date = datetime.datetime.now() - datetime.timedelta(days=230)
    assignments = get_homework_assignments(min_date.date())

    if assignments:
        embed = discord.Embed(title="Homework Assignments", color=discord.Color.blue())

        for assignment in assignments:
            embed.add_field(name="Assignment", value=f"**{assignment['title']}**", inline=False)
            embed.add_field(name="Due Date", value=assignment["due_date"], inline=True)
            embed.add_field(name="Course", value=assignment["course"], inline=True)
            embed.add_field(name="Status", value=assignment["status"], inline=False)
            embed.add_field(name="\u200b", value="\u200b", inline=False)

        embed.set_footer(text="Created by: @devv64")

        await ctx.send(embed=embed)
    else:
        await ctx.send("No homework assignments found.")

    print(datetime.datetime.now() - now)

def get_homework_assignments(min_date):
    filtered_assignments = []

    for course in course_cache:
        course_id = course.get('id')
        assignments = [assignment for assignment in assignment_cache if assignment.get('course_id') == course_id]

        for assignment in assignments:
            due_date = assignment.get('due_at')

            if due_date:
                due_date = datetime.datetime.strptime(due_date, "%Y-%m-%dT%H:%M:%SZ").date()

                if due_date > min_date:
                    print(assignment.get('user_id'))
                    filtered_assignments.append({
                        'title': assignment.get('name'),
                        'due_date': due_date,
                        'status': assignment.get('workflow_state'),
                        'course': course.get('name')
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

def start_reminder_task():
    global reminder_task
    if reminder_task and not reminder_task.is_cancelled():
        return

    # Simulate an upcoming assignment
    upcoming_assignment = {
        'title': 'PA6: Red-Black Trees',
        'due_date': datetime.datetime(2023, 7, 15).date(),
        'status': 'published',
        'course': '2022F CS 385-A/B/C/D',
    }

    # Add the assignment to the assignment cache
    assignment_cache.append(upcoming_assignment)
    print(upcoming_assignment)
    # print(len(assignment_cache))

    reminder_task = remind_upcoming_assignments.start()

@tasks.loop(minutes=1)
async def remind_upcoming_assignments():
    now = datetime.datetime.now().date()
    upcoming_assignments = [assignment for assignment in assignment_cache if assignment.get('due_date') and now <= assignment.get('due_date') <= now + datetime.timedelta(days=3)]
    print(f'Found {len(upcoming_assignments)} upcoming assignments.')
    print(upcoming_assignments)

    if upcoming_assignments:
        for assignment in upcoming_assignments:
            course = get_course_by_id(assignment.get('course_id'))
            
            # if course:
            if 1:
                user_mention = f"<@{user_id}>" 
                # message = f"Reminder: The assignment '{assignment.get('title')}' is due today for the course '{course.get('name')}'!"
                message = f"Reminder: {user_mention} The assignment '{assignment.get('title')}' is due today for the course!"

                channel = bot.get_channel(1127058724754821241)
                print(channel)
                await channel.send(message)
            else:
                print(f"Course not found for assignment: {assignment.get('title')}")

def get_course_by_id(course_id):
    for course in course_cache:
        if course.get('id') == course_id:
            return course
    return None

# Fetch courses and assignments when the bot starts up
course_cache = fetch_courses()

for course in course_cache:
    course_id = course.get('id')
    assignments = fetch_assignments(course_id)

    for assignment in assignments:
        assignment['course_id'] = course_id

    assignment_cache.extend(assignments)

bot.run(TOKEN)
