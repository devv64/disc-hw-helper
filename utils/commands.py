import discord
from discord.ext import commands, tasks
import datetime
import requests
import certifi
from config import CANVAS_API_URL, CANVAS_ACCESS_TOKEN
from globals import assignment_cache, reminder_task, user_id
import asyncio

headers = {'Authorization': f'Bearer {CANVAS_ACCESS_TOKEN}'}

def setup_commands(bot):
    """
    Set up custom bot commands.

    Args:
        bot (commands.Bot): The bot instance to set up commands for.
    """
        
    @bot.command()
    async def helloworld(ctx):
        await ctx.send("Hello World!")

    @bot.command()
    async def homework(ctx):
        """
        Retrieves and displays homework assignments from Canvas.

        Args:
            ctx (commands.Context): The context in which the command is called.
        """
        now = datetime.datetime.now()
        min_date = datetime.datetime.now() - datetime.timedelta(days=20)
        assignments = get_homework_assignments(min_date.date())

        print(now, min_date, min_date.date(), assignments)

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
        """
        Retrieve filtered homework assignments based on the minimum due date.

        Args:
            min_date (datetime.date): The minimum due date to consider.

        Returns:
            list: List of filtered assignment details.
        """
        filtered_assignments = []

        print(course.get('name') for course in course_cache)
        for course in course_cache:
            course_id = course.get('id')
            assignments = [assignment for assignment in assignment_cache if assignment.get('course_id') == course_id]
            print(course.get('name'), course_id, assignments)

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
        """
        Fetches the list of courses from the Canvas API.

        Returns:
            list: List of courses retrieved from the API.
        """
        courses_url = f'{CANVAS_API_URL}/courses?per_page=100'
        response = requests.get(courses_url, headers=headers, verify=certifi.where())

        if response.status_code == 200:
            return response.json()
        else:
            return []

    def fetch_assignments(course_id):
        """
        Fetches assignments for a specific course from the Canvas API.

        Args:
            course_id (int): The ID of the course to fetch assignments for.

        Returns:
            list: List of assignments retrieved from the API for the specified course.
        """
        assignments_url = f'{CANVAS_API_URL}/courses/{course_id}/assignments'
        response = requests.get(assignments_url, headers=headers, verify=certifi.where())

        if response.status_code == 200:
            return response.json()
        else:
            return []

    def start_reminder_task():
        """
        Starts the reminder task for upcoming assignments.

        This function simulates and adds upcoming assignments to the assignment cache,
        then starts the remind_upcoming_assignments background task.
        """        
        global reminder_task
        if reminder_task and not reminder_task.is_cancelled():
            return

        # Simulate an upcoming assignment
        upcoming_assignments = [
        # {
        #     'title': 'Assignment 1',
        #     'due_date': datetime.datetime.now() + datetime.timedelta(days=7),  # 7 days from now
        #     'status': 'published',
        #     'course': 'Course A',
        # },
        # {
        #     'title': 'Assignment 2',
        #     'due_date': datetime.datetime.now() + datetime.timedelta(days=3),  # 3 days from now
        #     'status': 'published',
        #     'course': 'Course B',
        # },
        # {
        #     'title': 'Assignment 3',
        #     'due_date': datetime.datetime.now() + datetime.timedelta(days=1),  # 1 day from now
        #     'status': 'published',
        #     'course': 'Course C',
        # },
        # {
        #     'title': 'Assignment 4',
        #     'due_date': datetime.datetime.now() + datetime.timedelta(hours=12, seconds=60),  # 12 hours from now
        #     'status': 'published',
        #     'course': 'Course D',
        # }
        ]
        
        # Add the assignments to the assignment cache
        assignment_cache.extend(upcoming_assignments)
        print(upcoming_assignments)
        # print(len(assignment_cache))

        reminder_task = remind_upcoming_assignments.start()

    @tasks.loop(seconds=60)
    async def remind_upcoming_assignments():
        """
        This asynchronous function is a background task that periodically checks
        if there are any upcoming assignments and sends reminders if necessary.
        """
        now = datetime.datetime.now()

        # Define the intervals at which reminders should be sent
        reminder_intervals = [
            (5, "5 minutes"),
            (30, "30 minutes"),
            (1 * 60, "1 hour"),
            (2 * 60, "2 hours"),
            (3 * 60, "3 hours"),
            (6 * 60, "6 hours"),
            (12 * 60, "12 hours"),
            (1 * 24 * 60, "1 day"),
            (3 * 24 * 60, "3 days"),
            (7 * 24 * 60, "7 days"),
        ]

        # print(assignment_cache)
        for assignment in assignment_cache:
            # print(assignment)
            due_date = assignment.get('due_date')
            if due_date:
                time_difference = due_date - now
                time_difference_minutes = time_difference.total_seconds() / 60

                # Iterate over reminder intervals and check if it's time to send a reminder
                for interval, interval_name in reminder_intervals:
                    if 0 <= time_difference_minutes <= interval:
                        # Check if this assignment has already been reminded for this interval
                        if not assignment.get(f'reminded_{interval_name}'):
                            user = await bot.fetch_user(220278378228350977)
                            channel = bot.get_channel(1127058724754821241)
                            message = f"Reminder: The assignment '{assignment.get('title')}' is due in {interval_name}!"
                            await channel.send(message)

                            # Mark this assignment as reminded for this interval
                            assignment[f'reminded_{interval_name}'] = True
                        break

    def get_course_by_id(course_id):
        """
        Get course details by its ID.

        Args:
            course_id (int): The ID of the course to retrieve details for.

        Returns:
            dict or None: Course details if found, otherwise None.
        """    
        for course in course_cache:
            if course.get('id') == course_id:
                return course
        return None

    # Fetch courses and assignments when the bot starts up
    course_cache = fetch_courses()
    course_cache = [course for course in course_cache if course.get('name') and course.get('name').startswith('2023F')]
    courses = [course.get('name') for course in course_cache]
    print(courses)
    
    for course in course_cache:
        course_id = course.get('id')
        assignments = fetch_assignments(course_id)

        for assignment in assignments:
            assignment['course_id'] = course_id

        assignment_cache.extend(assignments)

    start_reminder_task()
