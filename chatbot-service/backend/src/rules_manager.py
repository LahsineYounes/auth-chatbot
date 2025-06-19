import json
from pathlib import Path
from typing import Optional, Dict, List
import re

class RulesManager:
    def __init__(self, rules_file: str = "data/rules.json"):
        self.rules_file = Path(__file__).parent / rules_file
        self.rules: List[Dict[str, str]] = []
        self.load_rules()

    def load_rules(self) -> None:
        """Load rules from JSON file."""
        try:
            with open(self.rules_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.rules = data.get('questions', [])
        except Exception as e:
            print(f"Error loading rules: {e}")
            self.rules = []

    def find_matching_rule(self, message: str) -> Optional[str]:
        """
        Find a matching rule for the given message.
        Returns the answer if a match is found, None otherwise.
        """
        message = message.lower().strip()
        
        for rule in self.rules:
            pattern = rule['pattern'].lower()
            # Check for exact match or if pattern is contained in message
            if pattern == message or pattern in message:
                return rule['answer']
            
            # Check for similar patterns using fuzzy matching
            if self._is_similar(message, pattern):
                return rule['answer']
        
        return None

    def _is_similar(self, message: str, pattern: str) -> bool:
        """
        Check if message is similar to pattern using basic fuzzy matching.
        This can be enhanced with more sophisticated matching algorithms.
        """
        # Remove punctuation and extra spaces
        message = re.sub(r'[^\w\s]', '', message)
        pattern = re.sub(r'[^\w\s]', '', pattern)
        
        # Split into words
        message_words = set(message.split())
        pattern_words = set(pattern.split())
        
        # Check if most words match
        common_words = message_words.intersection(pattern_words)
        similarity = len(common_words) / max(len(message_words), len(pattern_words))
        
        return similarity > 0.7 