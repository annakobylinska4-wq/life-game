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
    # Better qualifications = better jobs - Career ladder from Intern to CEO
    jobs = {
        'None': ('Janitor', 15),
        'High School': ('Intern', 25),
        'Bachelor - Part 1': ('Junior Associate', 40),
        'Bachelor - Part 2': ('Associate', 55),
        'Bachelor - Part 3': ('Senior Associate', 70),
        'Master - Part 1': ('Team Lead', 90),
        'Master - Part 2': ('Manager', 115),
        'Master - Part 3': ('Senior Manager', 140),
        'PhD - Part 1': ('Director', 180),
        'PhD - Part 2': ('Vice President', 230),
        'PhD - Part 3': ('CEO', 300)
    }

    job_title, wage = jobs.get(state['qualification'], ('Unemployed', 0))
    state['current_job'] = job_title
    state['job_wage'] = wage

    message = "You secured a job as {} earning ${} per turn!".format(job_title, wage)
    return state, message, True
