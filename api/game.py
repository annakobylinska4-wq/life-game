"""
Game state management endpoints
"""
from fastapi import HTTPException, Depends
from models import GameState
from models.game_state import ACTION_TIME_COSTS, format_time
from actions import perform_action, check_endgame_conditions
from schemas import ActionRequest


def register_game_routes(app, get_current_user, load_game_states, save_game_states, create_new_game_state):
    """Register game state routes to FastAPI app"""

    @app.get('/api/game_state')
    async def get_game_state(username: str = Depends(get_current_user)):
        """Get current game state for logged in user"""
        game_states = load_game_states()

        if username not in game_states:
            game_states[username] = create_new_game_state()
            save_game_states(game_states)

        # Ensure look is calculated (for existing players without look attribute)
        game_state_obj = GameState(game_states[username])
        game_state_obj.update_look()
        state_with_look = game_state_obj.to_dict()

        return {'success': True, 'state': state_with_look}

    @app.get('/api/time_info/{location}')
    async def get_time_info(location: str, username: str = Depends(get_current_user)):
        """Get time cost info for visiting a location"""
        game_states = load_game_states()
        state = game_states[username]
        game_state_obj = GameState(state)

        travel_time, action_time, total_time = game_state_obj.get_total_time_cost()
        has_time = game_state_obj.has_enough_time()

        return {
            'success': True,
            'location': location,
            'travel_time': travel_time,
            'action_time': action_time,
            'total_time': total_time,
            'has_enough_time': has_time,
            'time_remaining': game_state_obj.time_remaining,
            'current_time': format_time(game_state_obj.time_remaining),
            'arrival_time': format_time(game_state_obj.time_remaining - travel_time) if travel_time <= game_state_obj.time_remaining else None,
            'finish_time': format_time(game_state_obj.time_remaining - total_time) if total_time <= game_state_obj.time_remaining else None
        }

    @app.post('/api/action')
    async def handle_action(data: ActionRequest, username: str = Depends(get_current_user)):
        """Handle game action"""
        from actions import execute_action_with_validation

        game_states = load_game_states()
        state = game_states[username]

        location = data.action

        # Use generic action handler
        result = execute_action_with_validation(
            state=state,
            location=location,
            action_handler=lambda s: perform_action(data.action, s),
            check_opening_hours=True
        )

        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])

        # Save updated state
        game_states[username] = result['state']
        save_game_states(game_states)

        # Add time info to message for general actions
        message = result['message']
        if not result['burnout'] and not result['bankruptcy']:
            # Get action time from game state constants
            action_time = ACTION_TIME_COSTS
            action_str = f"{action_time // 60}h {action_time % 60}m" if action_time % 60 > 0 else f"{action_time // 60}h"
            time_info = f" (⏱ {action_str})"
            message = message + time_info

        return {
            'success': True,
            'state': result['state'],
            'message': message,
            'burnout': result['burnout'],
            'bankruptcy': result['bankruptcy'],
            'turn_summary': result['turn_summary']
        }

    @app.post('/api/pass_time')
    async def handle_pass_time(username: str = Depends(get_current_user)):
        """Pass enough time to start the next turn"""
        game_states = load_game_states()
        state = game_states[username]

        game_state_obj = GameState(state)

        # Calculate time needed to reach next turn (time_remaining < 15 triggers new turn)
        # Pass enough time to bring time_remaining to 14
        time_to_pass = game_state_obj.time_remaining - 14

        if time_to_pass <= 0:
            # Already at or below threshold, just need to trigger the turn
            time_to_pass = game_state_obj.time_remaining

        # Deduct time
        game_state_obj.time_remaining -= time_to_pass

        # Increment turn (will always happen since we passed enough time)
        turn_summary = game_state_obj.increment_turn()

        # Check for endgame conditions (burnout and bankruptcy)
        burnout, bankruptcy, message = check_endgame_conditions(game_state_obj)

        updated_state = game_state_obj.to_dict()

        # Save updated state
        game_states[username] = updated_state
        save_game_states(game_states)

        # Set message if no endgame condition occurred
        if not burnout and not bankruptcy:
            hours_passed = time_to_pass // 60
            minutes_passed = time_to_pass % 60
            if hours_passed > 0:
                message = f"You passed {hours_passed}h {minutes_passed}m and the day ended..."
            else:
                message = f"You passed {minutes_passed} minutes and the day ended..."

        return {'success': True, 'state': updated_state, 'message': message, 'burnout': burnout, 'bankruptcy': bankruptcy, 'turn_summary': turn_summary}
