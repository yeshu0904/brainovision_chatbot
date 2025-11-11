import re
import random
import nltk
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Download NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

class AcademicChatbot:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.setup_knowledge_base()
    
    def setup_knowledge_base(self):
        """Prepare the training data from intents"""
        # Import here to avoid circular imports
        from chatbot import intents, responses
        
        self.intents = intents
        self.responses_module = responses
        
        self.patterns = []
        self.responses = []
        
        for intent in intents.INTENTS:
            for pattern in intent['patterns']:
                self.patterns.append(pattern)
                self.responses.append(intent['responses'])
        
        # Train TF-IDF vectorizer
        if self.patterns:
            self.tfidf_matrix = self.vectorizer.fit_transform(self.patterns)
    
    def preprocess_text(self, text):
        """Clean and preprocess input text"""
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        return text
    
    def get_response(self, user_input):
        """Get bot response for user input"""
        user_input = self.preprocess_text(user_input)
        
        if not user_input.strip():
            return random.choice(self.responses_module.GREETINGS)
        
        # Check for greetings
        greeting_words = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
        if any(greet in user_input for greet in greeting_words):
            return random.choice(self.responses_module.GREETINGS)
        
        # Check for goodbye
        goodbye_words = ['bye', 'goodbye', 'see you', 'quit', 'exit', 'thank you', 'thanks']
        if any(bye in user_input for bye in goodbye_words):
            return random.choice(self.responses_module.GOODBYES)
        
        # Check for company-specific keywords
        company_keywords = ['brainovision', 'brainovisionsolutions']
        if any(keyword in user_input for keyword in company_keywords):
            return random.choice(self.intents.INTENTS[0]['responses'])
        
        # Find best matching intent using cosine similarity
        if hasattr(self, 'tfidf_matrix') and self.patterns:
            user_vec = self.vectorizer.transform([user_input])
            similarities = cosine_similarity(user_vec, self.tfidf_matrix)
            best_match_idx = np.argmax(similarities)
            best_score = similarities[0, best_match_idx]
            
            if best_score > 0.3:
                return random.choice(self.responses[best_match_idx])
        
        return random.choice(self.responses_module.FALLBACK_RESPONSES)