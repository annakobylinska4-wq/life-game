"""
Job office action - handles player employment based on education and appearance
"""
from utils.function_logger import log_function_call
from .university import get_jobs_for_education, get_course_by_id
from .base import Action


class JobOfficeAction(Action):
    """Job office location for finding employment"""
    BUTTON_LABEL = 'Get a new job'
    LOCATION_DISPLAY_NAME = 'The job office'
    LOCATION_OPENING_HOURS = (6, 20)  # 6am - 8pm


# Create instance for backward compatibility
job_office_action = JobOfficeAction()

# Export for backward compatibility
BUTTON_LABEL = JobOfficeAction.BUTTON_LABEL

# Look requirements for jobs based on wage tiers
# Higher paying jobs require better appearance (look level 1-5)
# Look labels: 1=Shabby, 2=Scruffy, 3=Presentable, 4=Smart, 5=Very well groomed
LOOK_REQUIREMENTS = {
    # Wage range: required look level
    (0, 25): 1,      # Entry level jobs - any appearance
    (26, 50): 2,     # Basic jobs - at least scruffy
    (51, 80): 3,     # Professional jobs - presentable
    (81, 120): 4,    # Senior roles - smart
    (121, 999): 5,   # Executive positions - very well groomed
}

LOOK_LABELS = {
    1: 'Shabby',
    2: 'Scruffy',
    3: 'Presentable',
    4: 'Smart',
    5: 'Very well groomed'
}


def get_required_look_for_wage(wage):
    """Get the minimum look level required for a job with given wage."""
    for (min_wage, max_wage), look_level in LOOK_REQUIREMENTS.items():
        if min_wage <= wage <= max_wage:
            return look_level
    return 5  # Default to highest for very high wages


def get_available_jobs(completed_courses, current_look=None):
    """
    Get all jobs available based on completed courses.
    If current_look is provided, also includes eligibility based on appearance.

    Args:
        completed_courses: List of completed course IDs
        current_look: Player's current look level (1-5), optional

    Returns:
        list: List of job dictionaries with title, wage, and look requirements
    """
    jobs = get_jobs_for_education(completed_courses)

    # Convert to list of dicts for frontend
    job_list = []
    seen = set()
    for title, wage in jobs:
        if title not in seen:
            seen.add(title)
            required_look = get_required_look_for_wage(wage)
            job_info = {
                'title': title,
                'wage': wage,
                'required_look': required_look,
                'required_look_label': LOOK_LABELS.get(required_look, 'Shabby')
            }
            # Add eligibility if look level provided
            if current_look is not None:
                job_info['meets_look_requirement'] = current_look >= required_look
            job_list.append(job_info)

    # Sort by wage descending
    job_list.sort(key=lambda x: x['wage'], reverse=True)
    return job_list


@log_function_call
def visit_job_office(state):
    """
    Player visits job office to find employment based on qualifications and appearance.
    Shows available jobs and gets the best one the player qualifies for automatically.

    Args:
        state: Current game state dictionary

    Returns:
        tuple: (updated_state, message, success)
    """
    # Initialize education state if not present
    if 'completed_courses' not in state:
        state['completed_courses'] = []

    completed_courses = state.get('completed_courses', [])
    current_look = state.get('look', 1)

    # Get available jobs with look requirements
    jobs = get_available_jobs(completed_courses, current_look)

    if not jobs or (len(jobs) == 1 and jobs[0]['title'] == 'Unemployed'):
        return state, "No jobs available! Complete some education first.", False

    # Get best job that player qualifies for (highest wage they can get)
    best_job = None
    for job in jobs:
        if job.get('meets_look_requirement', True) and job['title'] != 'Unemployed':
            best_job = job
            break

    if not best_job:
        return state, "No suitable jobs available. Improve your appearance by buying clothes at John Lewis!", False

    job_title = best_job['title']
    wage = best_job['wage']

    state['current_job'] = job_title
    state['job_wage'] = wage

    message = f"You secured a job as {job_title} earning £{wage} per full working day!"
    return state, message, True


@log_function_call
def apply_for_job(state, job_title):
    """
    Apply for a specific job. Requires both education and appropriate appearance.

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
    current_look = state.get('look', 1)

    # Get available jobs with look requirements
    jobs = get_available_jobs(completed_courses, current_look)

    # Find the requested job
    job = None
    for j in jobs:
        if j['title'] == job_title:
            job = j
            break

    if not job:
        return state, f"You don't qualify for {job_title}. Get more education!", False

    # Check look requirement
    required_look = job.get('required_look', 1)
    if current_look < required_look:
        required_label = LOOK_LABELS.get(required_look, 'Presentable')
        current_label = LOOK_LABELS.get(current_look, 'Shabby')
        return state, f"You need to look '{required_label}' for this job, but you look '{current_label}'. Buy better clothes at John Lewis!", False

    state['current_job'] = job['title']
    state['job_wage'] = job['wage']

    message = f"Congratulations! You're now working as {job['title']} earning £{job['wage']} per full working day!"
    return state, message, True
