"""
University action - handles player education with course-based progression
"""
from config import config
from utils.function_logger import log_function_call

# Button label for this action
BUTTON_LABEL = 'Attend lecture'

# Education Course Catalogue
# Each course has: name, lectures_required, cost_per_lecture, prerequisites, jobs_unlocked, emoji
# All courses are free (cost_per_lecture = 0)
COURSE_CATALOGUE = [
    {
        'id': 'middle_school',
        'name': 'Middle School',
        'lectures_required': 3,
        'cost_per_lecture': 0,
        'prerequisites': [],
        'jobs_unlocked': [('Newspaper Delivery', 10), ('Babysitter', 12)],
        'emoji': '📚',
        'description': 'Basic education covering reading, writing, and arithmetic.'
    },
    {
        'id': 'high_school',
        'name': 'High School',
        'lectures_required': 5,
        'cost_per_lecture': 0,
        'prerequisites': ['middle_school'],
        'jobs_unlocked': [('Cashier', 18), ('Shop Assistant', 20), ('Warehouse Worker', 22)],
        'emoji': '🎒',
        'description': 'Secondary education preparing you for work or further study.'
    },
    {
        'id': 'vocational',
        'name': 'Vocational Training',
        'lectures_required': 4,
        'cost_per_lecture': 0,
        'prerequisites': ['high_school'],
        'jobs_unlocked': [('Electrician', 45), ('Plumber', 45), ('Mechanic', 42)],
        'emoji': '🔧',
        'description': 'Hands-on training for skilled trades. Quick path to decent wages.'
    },
    {
        'id': 'bachelor_arts',
        'name': 'Bachelor of Arts',
        'lectures_required': 8,
        'cost_per_lecture': 0,
        'prerequisites': ['high_school'],
        'jobs_unlocked': [('Marketing Assistant', 55), ('HR Coordinator', 52), ('Content Writer', 48)],
        'emoji': '🎨',
        'description': 'Undergraduate degree in humanities and social sciences.'
    },
    {
        'id': 'bachelor_science',
        'name': 'Bachelor of Science',
        'lectures_required': 10,
        'cost_per_lecture': 0,
        'prerequisites': ['high_school'],
        'jobs_unlocked': [('Junior Developer', 65), ('Lab Technician', 55), ('Data Analyst', 70)],
        'emoji': '🔬',
        'description': 'Rigorous undergraduate degree in STEM fields.'
    },
    {
        'id': 'bachelor_business',
        'name': 'Bachelor of Business',
        'lectures_required': 8,
        'cost_per_lecture': 0,
        'prerequisites': ['high_school'],
        'jobs_unlocked': [('Junior Accountant', 55), ('Sales Executive', 60), ('Business Analyst', 65)],
        'emoji': '💼',
        'description': 'Undergraduate degree preparing you for the corporate world.'
    },
    {
        'id': 'master_arts',
        'name': 'Master of Arts',
        'lectures_required': 6,
        'cost_per_lecture': 0,
        'prerequisites': ['bachelor_arts'],
        'jobs_unlocked': [('Marketing Manager', 95), ('HR Manager', 90), ('Senior Editor', 85)],
        'emoji': '📜',
        'description': 'Advanced study in humanities for leadership roles.'
    },
    {
        'id': 'master_science',
        'name': 'Master of Science',
        'lectures_required': 8,
        'cost_per_lecture': 0,
        'prerequisites': ['bachelor_science'],
        'jobs_unlocked': [('Senior Developer', 110), ('Research Scientist', 100), ('Data Science Lead', 115)],
        'emoji': '🧪',
        'description': 'Advanced STEM degree for specialized technical roles.'
    },
    {
        'id': 'mba',
        'name': 'MBA',
        'lectures_required': 10,
        'cost_per_lecture': 0,
        'prerequisites': ['bachelor_business', 'bachelor_arts', 'bachelor_science'],  # Any bachelor's
        'jobs_unlocked': [('Senior Manager', 140), ('Operations Director', 150), ('Strategy Consultant', 160)],
        'emoji': '📊',
        'description': 'Elite business degree opening doors to executive positions.'
    },
    {
        'id': 'phd',
        'name': 'PhD',
        'lectures_required': 15,
        'cost_per_lecture': 0,
        'prerequisites': ['master_science', 'master_arts'],  # Any master's
        'jobs_unlocked': [('Professor', 130), ('Chief Scientist', 180), ('Research Director', 170)],
        'emoji': '🎓',
        'description': 'The pinnacle of academic achievement. Years of research await.'
    },
    {
        'id': 'executive_mba',
        'name': 'Executive MBA',
        'lectures_required': 12,
        'cost_per_lecture': 0,
        'prerequisites': ['mba'],
        'jobs_unlocked': [('Vice President', 220), ('Chief Operating Officer', 250), ('CEO', 300)],
        'emoji': '👔',
        'description': 'The ultimate business qualification for C-suite executives.'
    }
]


def get_course_catalogue():
    """
    Get the list of available courses.

    Returns:
        list: List of course dictionaries
    """
    return COURSE_CATALOGUE


def get_course_by_id(course_id):
    """
    Get course details by ID.

    Args:
        course_id: Course identifier

    Returns:
        dict: Course details or None if not found
    """
    for course in COURSE_CATALOGUE:
        if course['id'] == course_id:
            return course
    return None


def check_prerequisites(course_id, completed_courses):
    """
    Check if a player has the prerequisites for a course.

    Args:
        course_id: Course to check
        completed_courses: List of completed course IDs

    Returns:
        tuple: (can_enroll, missing_prereqs)
    """
    course = get_course_by_id(course_id)
    if not course:
        return False, []

    prerequisites = course['prerequisites']
    if not prerequisites:
        return True, []

    # For courses with multiple prerequisites (like MBA), only need ONE of them
    # Check if any prerequisite is met
    if course_id in ['mba', 'phd']:
        # These courses require ANY of the listed prerequisites
        for prereq in prerequisites:
            if prereq in completed_courses:
                return True, []
        return False, prerequisites
    else:
        # Standard courses require ALL prerequisites
        missing = [p for p in prerequisites if p not in completed_courses]
        return len(missing) == 0, missing


def get_available_courses(completed_courses):
    """
    Get courses available for enrollment based on completed courses.

    Args:
        completed_courses: List of completed course IDs

    Returns:
        list: Available courses with enrollment eligibility
    """
    available = []
    for course in COURSE_CATALOGUE:
        if course['id'] in completed_courses:
            continue  # Already completed

        can_enroll, missing = check_prerequisites(course['id'], completed_courses)
        course_info = course.copy()
        course_info['can_enroll'] = can_enroll
        course_info['missing_prerequisites'] = missing
        available.append(course_info)

    return available


def get_jobs_for_education(completed_courses):
    """
    Get all jobs unlocked by completed courses.

    Args:
        completed_courses: List of completed course IDs

    Returns:
        list: List of (job_title, wage) tuples
    """
    # Base jobs available to everyone (no education required)
    jobs = [
        ('Unemployed', 0),
        ('Street Sweeper', 8),
        ('Dishwasher', 10),
        ('Cleaner', 12),
        ('Fast Food Worker', 14),
        ('Delivery Rider', 15),
    ]

    for course_id in completed_courses:
        course = get_course_by_id(course_id)
        if course:
            jobs.extend(course['jobs_unlocked'])

    return jobs


def get_best_job_for_education(completed_courses):
    """
    Get the best paying job available for the player's education.

    Args:
        completed_courses: List of completed course IDs

    Returns:
        tuple: (job_title, wage)
    """
    jobs = get_jobs_for_education(completed_courses)
    if not jobs:
        return ('Unemployed', 0)

    # Return highest paying job
    return max(jobs, key=lambda x: x[1])


@log_function_call
def visit_university(state):
    """
    Player attends a lecture at university.
    If enrolled, progresses toward completing the course.
    If not enrolled, shows a message to enroll first.

    Args:
        state: Current game state dictionary

    Returns:
        tuple: (updated_state, message, success)
    """
    # Initialize education state if not present
    if 'completed_courses' not in state:
        state['completed_courses'] = []
    if 'enrolled_course' not in state:
        state['enrolled_course'] = None
    if 'lectures_completed' not in state:
        state['lectures_completed'] = 0

    # Check if enrolled in a course
    if not state['enrolled_course']:
        return state, "You're not enrolled in any course. Browse the catalogue to enroll!", False

    course = get_course_by_id(state['enrolled_course'])
    if not course:
        state['enrolled_course'] = None
        state['lectures_completed'] = 0
        return state, "Invalid course enrollment. Please enroll in a new course.", False

    state['lectures_completed'] += 1

    lectures_remaining = course['lectures_required'] - state['lectures_completed']

    if lectures_remaining <= 0:
        # Course completed!
        state['completed_courses'].append(state['enrolled_course'])

        # Update qualification to show highest completed course
        state['qualification'] = course['name']

        course_name = course['name']
        state['enrolled_course'] = None
        state['lectures_completed'] = 0

        message = f"Congratulations! You've completed {course_name}! New job opportunities await at the Job Office."
    else:
        message = f"Lecture attended! {lectures_remaining} more to complete {course['name']}."

    return state, message, True


@log_function_call
def enroll_course(state, course_id):
    """
    Enroll in a course.

    Args:
        state: Current game state dictionary
        course_id: Course to enroll in

    Returns:
        tuple: (updated_state, message, success)
    """
    # Initialize education state if not present
    if 'completed_courses' not in state:
        state['completed_courses'] = []
    if 'enrolled_course' not in state:
        state['enrolled_course'] = None
    if 'lectures_completed' not in state:
        state['lectures_completed'] = 0

    course = get_course_by_id(course_id)
    if not course:
        return state, "Invalid course selection.", False

    # Check if already completed
    if course_id in state['completed_courses']:
        return state, f"You've already completed {course['name']}!", False

    # Check if already enrolled in this course
    if state['enrolled_course'] == course_id:
        return state, f"You're already enrolled in {course['name']}!", False

    # Check prerequisites
    can_enroll, missing = check_prerequisites(course_id, state['completed_courses'])
    if not can_enroll:
        missing_names = [get_course_by_id(m)['name'] for m in missing if get_course_by_id(m)]
        return state, f"Missing prerequisites: {', '.join(missing_names)}", False

    # Check if currently enrolled in another course
    if state['enrolled_course']:
        old_course = get_course_by_id(state['enrolled_course'])
        old_name = old_course['name'] if old_course else 'Unknown'
        # Allow switching but lose progress
        state['lectures_completed'] = 0
        message = f"Switched from {old_name} to {course['name']}. Previous progress lost."
    else:
        message = f"Enrolled in {course['name']}! Attend {course['lectures_required']} lectures to complete."

    state['enrolled_course'] = course_id

    return state, message, True
