"""
Job office action - handles player employment based on education
"""
from utils.function_logger import log_function_call
from .university import get_jobs_for_education, get_course_by_id

# Button label for this action
BUTTON_LABEL = 'Get a new job'


def get_available_jobs(completed_courses):
    """
    Get all jobs available based on completed courses.

    Args:
        completed_courses: List of completed course IDs

    Returns:
        list: List of job dictionaries with title and wage
    """
    jobs = get_jobs_for_education(completed_courses)

    # Convert to list of dicts for frontend
    job_list = []
    seen = set()
    for title, wage in jobs:
        if title not in seen:
            seen.add(title)
            job_list.append({'title': title, 'wage': wage})

    # Sort by wage descending
    job_list.sort(key=lambda x: x['wage'], reverse=True)
    return job_list


@log_function_call
def visit_job_office(state):
    """
    Player visits job office to find employment based on qualifications.
    Shows available jobs and gets the best one automatically.

    Args:
        state: Current game state dictionary

    Returns:
        tuple: (updated_state, message, success)
    """
    # Initialize education state if not present
    if 'completed_courses' not in state:
        state['completed_courses'] = []

    completed_courses = state.get('completed_courses', [])

    # Get available jobs
    jobs = get_available_jobs(completed_courses)

    if not jobs or (len(jobs) == 1 and jobs[0]['title'] == 'Unemployed'):
        return state, "No jobs available! Complete some education first.", False

    # Get best job (highest wage)
    best_job = jobs[0]
    job_title = best_job['title']
    wage = best_job['wage']

    state['current_job'] = job_title
    state['job_wage'] = wage

    message = f"You secured a job as {job_title} earning £{wage} per turn!"
    return state, message, True


@log_function_call
def apply_for_job(state, job_title):
    """
    Apply for a specific job.

    Args:
        state: Current game state dictionary
        job_title: Title of the job to apply for

    Returns:
        tuple: (updated_state, message, success)
    """
    # Initialize education state if not present
    if 'completed_courses' not in state:
        state['completed_courses'] = []

    completed_courses = state.get('completed_courses', [])

    # Get available jobs
    jobs = get_available_jobs(completed_courses)

    # Find the requested job
    job = None
    for j in jobs:
        if j['title'] == job_title:
            job = j
            break

    if not job:
        return state, f"You don't qualify for {job_title}. Get more education!", False

    state['current_job'] = job['title']
    state['job_wage'] = job['wage']

    message = f"Congratulations! You're now working as {job['title']} earning £{job['wage']} per turn!"
    return state, message, True
