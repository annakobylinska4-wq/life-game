"""
Job office action - handles player employment
"""


def visit_job_office(state):
    """
    Player visits job office to find employment based on qualifications

    Args:
        state: Current game state dictionary

    Returns:
        tuple: (updated_state, message, success)
    """
    # Better qualifications = better jobs
    jobs = {
        'None': ('Janitor', 20),
        'High School': ('Cashier', 35),
        'Bachelor': ('Office Worker', 60),
        'Master': ('Manager', 100),
        'PhD': ('Executive', 150)
    }

    job_title, wage = jobs.get(state['qualification'], ('Unemployed', 0))
    state['current_job'] = job_title
    state['job_wage'] = wage

    message = "You secured a job as {} earning ${} per turn!".format(job_title, wage)
    return state, message, True
