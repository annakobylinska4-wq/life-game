"""
Game logger - tracks all game events and state changes
"""
import os
import json
from datetime import datetime


class GameLogger:
    """Handles logging of game events and state changes"""

    def __init__(self, log_dir='data/logs'):
        """
        Initialize the game logger

        Args:
            log_dir: Directory where log files will be stored
        """
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)

    def _get_log_file_path(self, username):
        """Get the log file path for a specific user"""
        return os.path.join(self.log_dir, f"{username}_game.log")

    def _format_log_entry(self, event_type, data):
        """
        Format a log entry with timestamp and event data

        Args:
            event_type: Type of event (action, chat, purchase, state_change, etc.)
            data: Dictionary containing event details

        Returns:
            Formatted log entry string
        """
        timestamp = datetime.now().isoformat()
        log_entry = {
            'timestamp': timestamp,
            'event_type': event_type,
            'data': data
        }
        return json.dumps(log_entry, indent=2)

    def log_action(self, username, action_name, state_before, state_after, message, success):
        """
        Log a game action

        Args:
            username: Player username
            action_name: Name of the action performed
            state_before: Game state before action
            state_after: Game state after action
            message: Result message
            success: Whether action was successful
        """
        data = {
            'action': action_name,
            'success': success,
            'message': message,
            'state_before': {
                'turn': state_before.get('turn'),
                'money': state_before.get('money'),
                'hunger': state_before.get('hunger'),
                'happiness': state_before.get('happiness'),
                'tiredness': state_before.get('tiredness'),
                'job': state_before.get('current_job'),
                'qualification': state_before.get('qualification')
            },
            'state_after': {
                'turn': state_after.get('turn'),
                'money': state_after.get('money'),
                'hunger': state_after.get('hunger'),
                'happiness': state_after.get('happiness'),
                'tiredness': state_after.get('tiredness'),
                'job': state_after.get('current_job'),
                'qualification': state_after.get('qualification')
            },
            'changes': self._calculate_changes(state_before, state_after)
        }

        self._write_log(username, self._format_log_entry('action', data))

    def log_chat(self, username, action_context, user_message, llm_response, tool_calls, state_changed):
        """
        Log a chat interaction

        Args:
            username: Player username
            action_context: Context action (e.g., 'shop', 'university')
            user_message: User's message
            llm_response: LLM's response
            tool_calls: List of tools called during interaction
            state_changed: Whether the game state was modified
        """
        data = {
            'context': action_context,
            'user_message': user_message,
            'llm_response': llm_response,
            'tool_calls': tool_calls,
            'state_changed': state_changed
        }

        self._write_log(username, self._format_log_entry('chat', data))

    def log_purchase(self, username, item_name, cost, calories, hunger_before, hunger_after, money_before, money_after):
        """
        Log an item purchase

        Args:
            username: Player username
            item_name: Name of purchased item
            cost: Cost of item
            calories: Calorie value
            hunger_before: Hunger level before purchase
            hunger_after: Hunger level after purchase
            money_before: Money before purchase
            money_after: Money after purchase
        """
        data = {
            'item': item_name,
            'cost': cost,
            'calories': calories,
            'hunger_reduction': hunger_before - hunger_after,
            'money_spent': money_before - money_after,
            'state_changes': {
                'hunger': {'before': hunger_before, 'after': hunger_after},
                'money': {'before': money_before, 'after': money_after}
            }
        }

        self._write_log(username, self._format_log_entry('purchase', data))

    def log_session(self, username, event_type, details=None):
        """
        Log session events (login, logout, registration)

        Args:
            username: Player username
            event_type: Type of session event
            details: Optional additional details
        """
        data = {
            'session_event': event_type,
            'details': details or {}
        }

        self._write_log(username, self._format_log_entry('session', data))

    def _calculate_changes(self, state_before, state_after):
        """Calculate the differences between two states"""
        changes = {}

        # Numeric changes
        for key in ['turn', 'money', 'hunger', 'happiness', 'tiredness', 'job_wage']:
            before = state_before.get(key, 0)
            after = state_after.get(key, 0)
            if before != after:
                changes[key] = {
                    'before': before,
                    'after': after,
                    'delta': after - before if isinstance(after, (int, float)) else None
                }

        # String changes
        for key in ['current_job', 'qualification']:
            before = state_before.get(key)
            after = state_after.get(key)
            if before != after:
                changes[key] = {
                    'before': before,
                    'after': after
                }

        # Items changes
        items_before = set(state_before.get('items', []))
        items_after = set(state_after.get('items', []))
        if items_before != items_after:
            changes['items'] = {
                'added': list(items_after - items_before),
                'removed': list(items_before - items_after)
            }

        return changes

    def _write_log(self, username, log_entry):
        """
        Write a log entry to the user's log file

        Args:
            username: Player username
            log_entry: Formatted log entry string
        """
        log_file = self._get_log_file_path(username)

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')
            f.write('-' * 80 + '\n')

    def get_user_logs(self, username, limit=None):
        """
        Retrieve logs for a specific user

        Args:
            username: Player username
            limit: Optional limit on number of entries to return (most recent)

        Returns:
            List of log entries as dictionaries
        """
        log_file = self._get_log_file_path(username)

        if not os.path.exists(log_file):
            return []

        entries = []
        current_entry = []

        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip() == '-' * 80:
                    if current_entry:
                        try:
                            entry_text = ''.join(current_entry)
                            entries.append(json.loads(entry_text))
                        except json.JSONDecodeError:
                            pass
                        current_entry = []
                else:
                    current_entry.append(line)

        # Handle last entry if file doesn't end with separator
        if current_entry:
            try:
                entry_text = ''.join(current_entry)
                entries.append(json.loads(entry_text))
            except json.JSONDecodeError:
                pass

        # Return most recent entries if limit specified
        if limit:
            return entries[-limit:]

        return entries
