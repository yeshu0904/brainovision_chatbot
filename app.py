from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import json
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import random
from difflib import SequenceMatcher
import Levenshtein

app = Flask(__name__)

class SmartChatbot:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.model_data = None
        self.website_url = "https://www.brainovision.in"
        
        # Common misspellings and their corrections
        self.common_misspellings = {
            'internship': ['internship', 'intership', 'internship', 'internsip', 'intrenship', 'interenship'],
            'course': ['course', 'corse', 'cource', 'coarse', 'coruse'],
            'python': ['python', 'pythn', 'pyton', 'pythoon'],
            'java': ['java', 'jva', 'jaava', 'jave'],
            'machine': ['machine', 'machin', 'mashine', 'machiene'],
            'learning': ['learning', 'lernning', 'learnig', 'lerning'],
            'artificial': ['artificial', 'artifical', 'artficial', 'artifitial'],
            'intelligence': ['intelligence', 'inteligence', 'intelligance', 'intelgence'],
            'brainovision': ['brainovision', 'brainovison', 'brainovision', 'brainovisin'],
            'program': ['program', 'programme', 'progrm', 'progam'],
            'training': ['training', 'trainig', 'trainning', 'traning'],
            'stipend': ['stipend', 'stiped', 'stipnd', 'stepend'],
            'workshop': ['workshop', 'workshp', 'workshop', 'wrokshop'],
            'hackathon': ['hackathon', 'hakathon', 'hackaton', 'hackathon'],
            'admission': ['admission', 'admission', 'admision', 'admisson'],
            'contact': ['contact', 'contct', 'contat', 'conatct']
        }
        
        # Keywords for intent detection
        self.keyword_groups = {
            'internship': ['internship', 'stipend', 'work experience', 'practical training', 'industrial training', 'on-job training'],
            'courses': ['course', 'program', 'training', 'learn', 'study', 'subject', 'curriculum', 'syllabus'],
            'python': ['python', 'django', 'flask', 'full stack'],
            'java': ['java', 'spring', 'hibernate', 'j2ee'],
            'ai_ml': ['artificial intelligence', 'machine learning', 'ai', 'ml', 'neural network', 'deep learning'],
            'data_science': ['data science', 'data analytics', 'big data', 'data analysis'],
            'contact': ['contact', 'phone', 'email', 'address', 'location', 'reach'],
            'about': ['about', 'company', 'brainovision', 'who are you', 'what is']
        }
        
        self.load_model()
    
    def load_model(self):
        """Load the trained model"""
        try:
            with open('website_training_data.pkl', 'rb') as f:
                self.model_data = pickle.load(f)
            print("✅ Smart chatbot model loaded!")
        except:
            print("⚠️  Model not found. Please train the chatbot first.")
            self.model_data = None
    
    def correct_spelling(self, text):
        """Correct common spelling mistakes in the text"""
        words = text.lower().split()
        corrected_words = []
        
        for word in words:
            # Remove special characters
            clean_word = re.sub(r'[^\w\s]', '', word)
            
            if len(clean_word) < 3:  # Skip very short words
                corrected_words.append(word)
                continue
            
            # Check against common misspellings
            best_match = clean_word
            highest_similarity = 0
            
            for correct_word, variations in self.common_misspellings.items():
                for variation in variations + [correct_word]:
                    similarity = SequenceMatcher(None, clean_word, variation).ratio()
                    if similarity > highest_similarity and similarity > 0.7:  # 70% similarity threshold
                        highest_similarity = similarity
                        best_match = correct_word
            
            # Use Levenshtein distance as fallback
            if highest_similarity < 0.8:
                for correct_word in self.common_misspellings.keys():
                    distance = Levenshtein.distance(clean_word, correct_word)
                    if distance <= 2 and len(clean_word) >= 4:  # Allow 2 character differences
                        best_match = correct_word
                        break
            
            corrected_words.append(best_match)
        
        corrected_text = ' '.join(corrected_words)
        print(f"🔤 Spelling correction: '{text}' -> '{corrected_text}'")
        return corrected_text
    
    def detect_intent_from_keywords(self, text):
        """Detect intent based on keyword matching with fuzzy matching"""
        text_lower = text.lower()
        intent_scores = {}
        
        for intent, keywords in self.keyword_groups.items():
            score = 0
            for keyword in keywords:
                # Exact match
                if keyword in text_lower:
                    score += 2
                # Fuzzy match for individual words
                else:
                    words_in_text = text_lower.split()
                    for word in words_in_text:
                        if len(word) > 3:  # Only check words longer than 3 characters
                            for kw in keyword.split():
                                similarity = SequenceMatcher(None, word, kw).ratio()
                                if similarity > 0.8:
                                    score += 1
                                    break
            
            if score > 0:
                intent_scores[intent] = score
        
        if intent_scores:
            best_intent = max(intent_scores.items(), key=lambda x: x[1])
            print(f"🎯 Detected intent: {best_intent[0]} (score: {best_intent[1]})")
            return best_intent[0]
        
        return None
    
    def get_website_answer(self, question):
        """Get specific answers from the website based on corrected intent"""
        # First correct spelling
        corrected_question = self.correct_spelling(question)
        print(f"🔍 Original: '{question}' -> Corrected: '{corrected_question}'")
        
        # Detect intent from corrected question
        intent = self.detect_intent_from_keywords(corrected_question)
        
        try:
            if intent == 'internship':
                return self._scrape_internship_info()
            elif intent == 'courses':
                return self._scrape_courses_page()
            elif intent == 'python':
                return self._scrape_python_info()
            elif intent == 'java':
                return self._scrape_java_info()
            elif intent == 'ai_ml':
                return self._scrape_ai_ml_info()
            elif intent == 'data_science':
                return self._scrape_data_science_info()
            elif intent == 'contact':
                return self._scrape_contact_page()
            elif intent == 'about':
                return self._scrape_about_page()
            else:
                return None
                
        except Exception as e:
            print(f"Error getting website answer: {e}")
            return None
    
    def _scrape_internship_info(self):
        """Scrape internship information"""
        try:
            # Try to scrape actual internship page
            response = requests.get(f"{self.website_url}/internship", timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # Extract internship-specific content
                internship_text = soup.get_text().lower()
                if 'internship' in internship_text:
                    return f"💼 **Internship Program at Brainovision:**\n\nBased on our website, we offer comprehensive internship programs. Please visit {self.website_url}/internship for detailed information about:\n• Duration and structure\n• Stipend details\n• Project opportunities\n• Application process"
            
            # Fallback to general internship info
            return f"💼 **Internship Program:**\n\nAt Brainovision Solutions, we provide:\n\n✅ **3-Month Paid Internship**\n• Hands-on industry projects\n• Professional mentorship\n• Monthly stipend\n• Certificate of completion\n• Placement assistance\n\n🎯 **All our courses include internship opportunities**\n\n📋 **Learn more:** {self.website_url}"
                
        except:
            return f"💼 **Internship Opportunities:**\n\nWe offer comprehensive internship programs with:\n• Real-world project experience\n• Industry expert guidance\n• Financial support through stipend\n• Career development opportunities\n\n🌐 **Details at:** {self.website_url}"
    
    def _scrape_courses_page(self):
        """Scrape courses page for current information"""
        try:
            response = requests.get(f"{self.website_url}/courses", timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract course information
            courses_info = []
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
            
            for heading in headings[:8]:
                text = heading.get_text().strip()
                if text and len(text) > 3 and len(text) < 100:
                    courses_info.append(text)
            
            if courses_info:
                course_list = "\n".join([f"• {course}" for course in courses_info[:6]])
                return f"🎯 **Courses at Brainovision:**\n\n{course_list}\n\n📚 **Complete course details:** {self.website_url}/courses"
            else:
                return f"📚 **Our Course Catalog:**\n\nWe offer industry-relevant programs including:\n• Python Full Stack Development\n• Java Full Stack\n• Artificial Intelligence & ML\n• Data Science & Analytics\n• Cloud Computing\n• DevOps\n\n🔗 **Explore all courses:** {self.website_url}/courses"
                
        except:
            return f"📚 **Technical Courses:**\n\nBrainovision Solutions offers cutting-edge technology programs designed for career success.\n\n🌐 **Visit our courses page:** {self.website_url}/courses"
    
    def _scrape_python_info(self):
        return f"🐍 **Python Full Stack Development:**\n\nComprehensive training in:\n• Python Programming\n• Django & Flask Frameworks\n• Frontend Technologies\n• Database Management\n• REST APIs & Deployment\n\n💼 Includes 3-month internship\n💰 Stipend provided\n\n📖 **Details:** {self.website_url}/courses"
    
    def _scrape_java_info(self):
        return f"☕ **Java Full Stack Development:**\n\nMaster enterprise development with:\n• Core & Advanced Java\n• Spring Framework\n• Microservices Architecture\n• Frontend Integration\n• Database Technologies\n\n💼 Includes 3-month internship\n💰 Stipend provided\n\n📖 **Details:** {self.website_url}/courses"
    
    def _scrape_ai_ml_info(self):
        return f"🤖 **AI & Machine Learning:**\n\nCutting-edge training in:\n• Machine Learning Algorithms\n• Deep Learning & Neural Networks\n• Computer Vision\n• Natural Language Processing\n• TensorFlow & PyTorch\n\n💼 Includes 3-month internship\n💰 Stipend provided\n\n📖 **Details:** {self.website_url}/courses"
    
    def _scrape_data_science_info(self):
        return f"📊 **Data Science & Analytics:**\n\nComprehensive data training:\n• Data Analysis & Visualization\n• Statistical Modeling\n• Machine Learning for Data\n• Big Data Technologies\n• Business Intelligence\n\n💼 Includes 3-month internship\n💰 Stipend provided\n\n📖 **Details:** {self.website_url}/courses"
    
    def _scrape_about_page(self):
        return f"🏢 **About Brainovision Solutions:**\n\nWe are a premier technology education institute committed to bridging the gap between academic learning and industry requirements.\n\n🌟 **Our Mission:** To provide quality technical education with hands-on experience.\n\n🔗 **Learn more:** {self.website_url}/about"
    
    def _scrape_contact_page(self):
        return f"📞 **Contact Brainovision:**\n\nGet in touch with us for:\n• Course inquiries\n• Admission procedures\n• Partnership opportunities\n• Career guidance\n\n📍 **Visit our contact page:** {self.website_url}/contact\n\n📧 **Email:** info@brainovision.in\n🌐 **Website:** {self.website_url}"
    
    def get_response(self, user_input):
        """Get intelligent response with spelling correction"""
        user_input = user_input.lower().strip()
        
        print(f"👤 Original input: '{user_input}'")
        
        # First, try to get specific answer from website with spelling correction
        website_answer = self.get_website_answer(user_input)
        if website_answer:
            return website_answer
        
        # Then use AI model with corrected text
        if self.model_data:
            try:
                corrected_input = self.correct_spelling(user_input)
                user_vec = self.model_data['vectorizer'].transform([corrected_input])
                similarities = cosine_similarity(user_vec, self.model_data['tfidf_matrix'])
                best_match_idx = np.argmax(similarities)
                best_score = similarities[0, best_match_idx]
                
                print(f"🎯 AI Model score: {best_score:.3f}")
                
                if best_score > 0.15:  # Lower threshold for better matching
                    predicted_tag = self.model_data['tags'][best_match_idx]
                    response = random.choice(self.model_data['responses'][predicted_tag])
                    print(f"🏷️  Matched tag: {predicted_tag}")
                    return response
                    
            except Exception as e:
                print(f"AI model error: {e}")
        
        # Final fallback with context-aware response
        return self._get_context_fallback(user_input)
    
    def _get_context_fallback(self, user_input):
        """Get context-aware fallback response"""
        corrected_input = self.correct_spelling(user_input)
        intent = self.detect_intent_from_keywords(corrected_input)
        
        if intent == 'internship':
            return self._scrape_internship_info()
        elif intent == 'courses':
            return self._scrape_courses_page()
        elif intent in ['python', 'java', 'ai_ml', 'data_science']:
            return f"🎓 **Course Information:**\n\nI understand you're asking about our {intent.replace('_', ' ').title()} program. Please visit {self.website_url}/courses for complete details about this course, including curriculum, duration, and admission process."
        else:
            fallbacks = [
                f"🔍 I want to make sure I understand your question correctly. Could you rephrase it? Meanwhile, you can visit {self.website_url} for comprehensive information about Brainovision Solutions.",
                f"💡 I specialize in providing information about Brainovision's courses, internships, and programs. For specific details, please visit our website: {self.website_url}",
                f"🎯 At Brainovision Solutions, we offer technical courses with internship opportunities. Visit {self.website_url} to explore our programs and get accurate information."
            ]
            return random.choice(fallbacks)

# Initialize chatbot
chatbot = SmartChatbot()

@app.route('/')
def home():
    return render_template('professional_index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message', '').strip()
        print(f"👤 User: {user_message}")
        
        if not user_message:
            return jsonify({
                'status': 'success',
                'response': "Welcome to Brainovision Solutions! 🎓 I'm your smart AI assistant. I can understand your questions even with small spelling mistakes. Ask me about courses, internships, or anything else!"
            })
        
        bot_response = chatbot.get_response(user_message)
        print(f"🤖 Bot: {bot_response}")
        
        return jsonify({
            'status': 'success',
            'response': bot_response
        })
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({
            'status': 'error',
            'response': f"I apologize for the inconvenience. Please visit our website directly: https://www.brainovision.in"
        })

@app.route('/train', methods=['GET'])
def train_chatbot():
    """Train the chatbot with website data"""
    try:
        from website_scraper import WebsiteScraper
        import pickle
        from sklearn.feature_extraction.text import TfidfVectorizer
        
        # Scrape website and generate training data
        scraper = WebsiteScraper()
        training_data = scraper.save_training_data()
        
        # Prepare training data for AI model
        patterns = []
        tags = []
        responses_dict = {}
        
        for intent in training_data['intents']:
            tag = intent['tag']
            responses_dict[tag] = intent['responses']
            
            for pattern in intent['patterns']:
                patterns.append(pattern.lower())
                tags.append(tag)
        
        # Train TF-IDF
        vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(patterns)
        
        # Save model
        model_data = {
            'vectorizer': vectorizer,
            'patterns': patterns,
            'tags': tags,
            'responses': responses_dict,
            'tfidf_matrix': tfidf_matrix
        }
        
        with open('website_training_data.pkl', 'wb') as f:
            pickle.dump(model_data, f)
        
        # Reload chatbot
        global chatbot
        chatbot = SmartChatbot()
        
        return jsonify({
            'status': 'success', 
            'message': 'Smart chatbot trained successfully! Now understands spelling mistakes.',
            'intents_count': len(training_data['intents'])
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    print("🚀 Starting Smart Brainovision Chatbot...")
    print("🎯 Now with spelling correction and fuzzy matching!")
    print("🌐 Website: https://www.brainovision.in")
    print("📍 Chat: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)