import re

class IntentParser:
    INTENT_PATTERNS = {
        'schedule_plan': [
            r'schedule', r'daily plan', r'plan my day', r'routine', r'what should i do today', 
            r'time management', r'allocate time', r'organize my day', r'agenda'
        ],
        'productivity_inquiry': [
            r'productivity', r'score', r'how am i doing', r'performance', r'sleep', 
            r'stress', r'burnout', r'screen time', r'exercise', r'work hours'
        ],
        'expense_inquiry': [
            r'expense', r'spend', r'budget', r'money', r'cost', r'category', r'financial', r'how much'
        ],
        'task_inquiry': [
            r'task', r'todo', r'to-do', r'pending', r'priority', r'deadline', r'what tasks'
        ],
        'greeting': [
            r'hello', r'hi', r'hey', r'greetings', r'help', r'who are you', r'what can you do'
        ]
    }

    @staticmethod
    def parse_intent(user_text):
        """Categorizes natural language user text into intent and key tokens."""
        if not user_text:
            return 'greeting', []

        text_clean = user_text.lower().strip()

        # Check intent regex patterns
        matched_intents = []
        for intent, patterns in IntentParser.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_clean):
                    matched_intents.append(intent)

        primary_intent = matched_intents[0] if matched_intents else 'general_query'

        # Token extraction
        tokens = re.findall(r'\b\w+\b', text_clean)

        return primary_intent, tokens
