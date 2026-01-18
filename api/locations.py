"""
Location-based endpoints (shop, john_lewis, estate_agent, university, job_office, chat)
"""
from fastapi import HTTPException, Depends
from models import GameState
from actions.shop import get_shop_catalogue, purchase_item
from actions.john_lewis import get_john_lewis_catalogue, purchase_john_lewis_item
from actions.estate_agent import get_flat_catalogue, rent_flat
from actions.university import get_course_catalogue, get_available_courses, enroll_course, get_course_by_id
from actions.job_office import get_available_jobs, apply_for_job
from chatbot.llm_client import get_llm_response
from schemas import PurchaseRequest, RentFlatRequest, EnrollCourseRequest, ApplyJobRequest, ChatRequest


def register_location_routes(app, get_current_user, load_game_states, save_game_states):
    """Register location-based routes to FastAPI app"""

    # ===== SHOP ENDPOINTS =====
    @app.get('/api/shop/catalogue')
    async def get_catalogue(username: str = Depends(get_current_user)):
        """Get shop catalogue"""
        return {'success': True, 'items': get_shop_catalogue()}

    @app.post('/api/shop/purchase')
    async def handle_purchase(data: PurchaseRequest, username: str = Depends(get_current_user)):
        """Purchase a specific item from the shop"""
        from actions import execute_action_with_validation

        game_states = load_game_states()
        state = game_states[username]

        # Use generic action handler
        result = execute_action_with_validation(
            state=state,
            location='shop',
            action_handler=lambda s: purchase_item(s, data.item_name),
            check_opening_hours=False  # Shop is always open
        )

        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])

        # Save updated state
        game_states[username] = result['state']
        save_game_states(game_states)

        return {
            'success': True,
            'state': result['state'],
            'message': result['message'],
            'burnout': result['burnout'],
            'bankruptcy': result['bankruptcy'],
            'turn_summary': result['turn_summary']
        }

    # ===== JOHN LEWIS ENDPOINTS =====
    @app.get('/api/john_lewis/catalogue')
    async def get_john_lewis_cat(username: str = Depends(get_current_user)):
        """Get John Lewis catalogue"""
        return {'success': True, 'items': get_john_lewis_catalogue()}

    @app.post('/api/john_lewis/purchase')
    async def handle_john_lewis_purchase(data: PurchaseRequest, username: str = Depends(get_current_user)):
        """Purchase a specific item from John Lewis"""
        from actions import execute_action_with_validation

        game_states = load_game_states()
        state = game_states[username]

        # Use generic action handler with update_look callback for clothing purchases
        result = execute_action_with_validation(
            state=state,
            location='john_lewis',
            action_handler=lambda s: purchase_john_lewis_item(s, data.item_name),
            check_opening_hours=False,  # John Lewis is always open
            post_action_callback=lambda game_state_obj: game_state_obj.update_look()
        )

        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])

        # Save updated state
        game_states[username] = result['state']
        save_game_states(game_states)

        return {
            'success': True,
            'state': result['state'],
            'message': result['message'],
            'burnout': result['burnout'],
            'bankruptcy': result['bankruptcy'],
            'turn_summary': result['turn_summary']
        }

    # ===== CHAT ENDPOINT =====
    @app.post('/api/chat')
    async def handle_chat(data: ChatRequest, username: str = Depends(get_current_user)):
        """Handle chat messages with LLM and execute any triggered actions"""
        if not data.action or not data.message:
            raise HTTPException(status_code=400, detail='Missing action or message')

        # Get current game state for context
        game_states = load_game_states()
        state = game_states.get(username)

        # Get LLM response with potential tool calls
        result = get_llm_response(data.action, data.message, state)

        # If tools were called and state was updated, save the new state
        if result.get('updated_state'):
            # Use GameState class to handle turn increment and per-turn updates
            game_state_obj = GameState(result['updated_state'])
            game_state_obj.increment_turn()
            game_states[username] = game_state_obj.to_dict()
            save_game_states(game_states)

        return {
            'success': True,
            'response': result['response'],
            'tool_calls': result.get('tool_calls', []),
            'state': result.get('updated_state') or state
        }

    # ===== ESTATE AGENT ENDPOINTS =====
    @app.get('/api/estate_agent/catalogue')
    async def get_flats_catalogue(username: str = Depends(get_current_user)):
        """Get available flats for rent"""
        return {'success': True, 'flats': get_flat_catalogue()}

    @app.post('/api/estate_agent/rent')
    async def handle_rent_flat(data: RentFlatRequest, username: str = Depends(get_current_user)):
        """Rent a flat of the specified tier"""
        from actions import execute_action_with_validation

        game_states = load_game_states()
        state = game_states[username]

        # Use generic action handler
        result = execute_action_with_validation(
            state=state,
            location='estate_agent',
            action_handler=lambda s: rent_flat(s, data.tier),
            check_opening_hours=True
        )

        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])

        # Save updated state
        game_states[username] = result['state']
        save_game_states(game_states)

        return {
            'success': True,
            'state': result['state'],
            'message': result['message'],
            'burnout': result['burnout'],
            'bankruptcy': result['bankruptcy'],
            'turn_summary': result['turn_summary']
        }

    # ===== UNIVERSITY ENDPOINTS =====
    @app.get('/api/university/catalogue')
    async def get_courses_catalogue(username: str = Depends(get_current_user)):
        """Get available courses based on player's education"""
        game_states = load_game_states()
        state = game_states[username]

        completed_courses = state.get('completed_courses', [])
        enrolled_course = state.get('enrolled_course', None)
        lectures_completed = state.get('lectures_completed', 0)

        # Get courses with eligibility info
        courses = get_available_courses(completed_courses)

        # Add current enrollment info
        enrolled_info = None
        if enrolled_course:
            course = get_course_by_id(enrolled_course)
            if course:
                enrolled_info = {
                    'id': course['id'],
                    'name': course['name'],
                    'lectures_completed': lectures_completed,
                    'lectures_required': course['lectures_required'],
                    'cost_per_lecture': course['cost_per_lecture']
                }

        return {
            'success': True,
            'courses': courses,
            'completed_courses': completed_courses,
            'enrolled_course': enrolled_info
        }

    @app.post('/api/university/enroll')
    async def handle_enroll_course(data: EnrollCourseRequest, username: str = Depends(get_current_user)):
        """Enroll in a course"""
        from actions import execute_action_with_validation

        game_states = load_game_states()
        state = game_states[username]

        # Use generic action handler - enrollment now consumes time like other actions
        result = execute_action_with_validation(
            state=state,
            location='university',
            action_handler=lambda s: enroll_course(s, data.course_id),
            check_opening_hours=True
        )

        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])

        # Save updated state
        game_states[username] = result['state']
        save_game_states(game_states)

        return {
            'success': True,
            'state': result['state'],
            'message': result['message'],
            'burnout': result['burnout'],
            'bankruptcy': result['bankruptcy'],
            'turn_summary': result['turn_summary']
        }

    # ===== JOB OFFICE ENDPOINTS =====
    @app.get('/api/job_office/jobs')
    async def get_jobs_list(username: str = Depends(get_current_user)):
        """Get available jobs based on player's education and appearance"""
        game_states = load_game_states()
        state = game_states[username]

        completed_courses = state.get('completed_courses', [])
        current_look = state.get('look', 1)
        jobs = get_available_jobs(completed_courses, current_look)

        return {
            'success': True,
            'jobs': jobs,
            'current_job': state.get('current_job', 'Unemployed'),
            'current_wage': state.get('job_wage', 0)
        }

    @app.post('/api/job_office/apply')
    async def handle_apply_job(data: ApplyJobRequest, username: str = Depends(get_current_user)):
        """Apply for a specific job"""
        from actions import execute_action_with_validation

        game_states = load_game_states()
        state = game_states[username]

        # Use generic action handler
        result = execute_action_with_validation(
            state=state,
            location='job_office',
            action_handler=lambda s: apply_for_job(s, data.job_title),
            check_opening_hours=True
        )

        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])

        # Save updated state
        game_states[username] = result['state']
        save_game_states(game_states)

        return {
            'success': True,
            'state': result['state'],
            'message': result['message'],
            'burnout': result['burnout'],
            'bankruptcy': result['bankruptcy'],
            'turn_summary': result['turn_summary']
        }
