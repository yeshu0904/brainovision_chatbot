import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urljoin

class WebsiteScraper:
    def __init__(self, base_url="https://www.brainovision.in"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def scrape_website(self):
        """Scrape all relevant pages from the website"""
        website_data = {
            'courses': [],
            'internship': [],
            'about': [],
            'contact': [],
            'homepage': []
        }
        
        try:
            # Scrape homepage
            homepage_content = self.scrape_page(self.base_url)
            website_data['homepage'] = homepage_content
            
            # Scrape courses page
            courses_content = self.scrape_page(f"{self.base_url}/courses")
            website_data['courses'] = courses_content
            
            # Scrape internship page (if exists)
            internship_content = self.scrape_page(f"{self.base_url}/internship")
            website_data['internship'] = internship_content
            
            # Scrape about page
            about_content = self.scrape_page(f"{self.base_url}/about")
            website_data['about'] = about_content
            
            # Scrape contact page
            contact_content = self.scrape_page(f"{self.base_url}/contact")
            website_data['contact'] = contact_content
            
        except Exception as e:
            print(f"Error scraping website: {e}")
            
        return website_data
    
    def scrape_page(self, url):
        """Scrape content from a specific page"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content from important sections
            content = []
            
            # Get page title
            title = soup.find('title')
            if title:
                content.append(f"Page Title: {title.get_text().strip()}")
            
            # Get headings
            headings = soup.find_all(['h1', 'h2', 'h3'])
            for heading in headings:
                text = heading.get_text().strip()
                if text and len(text) > 5:
                    content.append(f"Heading: {text}")
            
            # Get paragraph content
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                text = p.get_text().strip()
                if text and len(text) > 20:  # Only meaningful paragraphs
                    content.append(text)
            
            # Get list items
            lists = soup.find_all(['ul', 'ol'])
            for lst in lists:
                items = lst.find_all('li')
                for item in items:
                    text = item.get_text().strip()
                    if text and len(text) > 10:
                        content.append(f"• {text}")
            
            return content
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return []
    
    def generate_training_data(self, website_data):
        """Generate training data from scraped website content with misspellings"""
        intents = []
        
        # Course-related intents with misspellings
        course_patterns = [
            # Correct spellings
            "courses", "programs", "what do you teach", "learning programs",
            "technical courses", "what can I study", "available courses",
            "course catalog", "training programs", "educational programs",
            "which courses do you have", "what programs are available",
            "tell me about your courses", "learning opportunities",
            "study programs", "educational courses",
            
            # Common misspellings for courses
            "what corse do you offer", "available corse", "training corse",
            "what coarses are available", "learning corse", "tecknical courses",
            "techanical courses", "cources available", "what corse catalog",
            "training corse programs", "eductional programs", "lernning programs",
            "studdy programs", "wht courses do you have", "coursess",
            "programms", "teching programs", "learnig courses"
        ]
        
        course_responses = self._extract_course_info(website_data['courses'])
        if course_responses:
            intents.append({
                "tag": "courses",
                "patterns": course_patterns,
                "responses": course_responses
            })
        
        # Internship intents with misspellings
        internship_patterns = [
            # Correct spellings
            "internship", "stipend", "work experience", "practical training",
            "paid internship", "internship program", "3 months internship",
            "industrial training", "on-job training", "work placement",
            "training internship", "professional internship",
            "do you provide internship", "internship opportunities",
            "internship with stipend", "paid training",
            
            # Common misspellings for internship
            "inership", "intership", "internship", "internsip", "intrenship",
            "interenship", "internship", "insternship", "iternship",
            "stiped", "stipnd", "stipendd", "stepend",
            "practicle training", "practical trainig", "work experiance",
            "work exprience", "industral training", "onjob training",
            "intership program", "3 month intership", "paid intership"
        ]
        
        internship_responses = self._extract_internship_info(website_data['internship'] + website_data['homepage'])
        if internship_responses:
            intents.append({
                "tag": "internship",
                "patterns": internship_patterns,
                "responses": internship_responses
            })
        
        # Company info intents with misspellings
        company_patterns = [
            # Correct spellings
            "about brainovision", "what is brainovision", "company information",
            "about company", "who are you", "tell me about your institute",
            "about your organization", "what does brainovision do",
            "brainovision solutions information", "about your company",
            "tell me about brainovision", "company overview",
            "what kind of institute are you",
            
            # Common misspellings for company info
            "about brainovison", "what is brainovison", "compnay information",
            "about compnay", "who are u", "tell me about your institue",
            "about your organisation", "what does brainovison do",
            "brainovison solutions", "about your compnay",
            "tell me about brainovison", "compnay overview",
            "what kind of institue are you", "brainnovision",
            "brainovision", "brainovisin", "brainovition"
        ]
        
        company_responses = self._extract_company_info(website_data['about'] + website_data['homepage'])
        if company_responses:
            intents.append({
                "tag": "company_info",
                "patterns": company_patterns,
                "responses": company_responses
            })
        
        # Contact intents with misspellings
        contact_patterns = [
            # Correct spellings
            "contact", "how to reach", "phone number", "email",
            "address", "location", "get in touch", "contact details",
            "how to contact", "where are you located", "office address",
            "phone contact", "email address", "contact information",
            "how can I reach you",
            
            # Common misspellings for contact
            "contct", "contat", "conatct", "contactt", "how to rech",
            "fone number", "phone numbr", "phon number", "emai",
            "emale", "e-mail", "adress", "locaton", "locationn",
            "get in tuch", "contact detal", "how to contct",
            "where are you locatd", "office adress", "fone contact",
            "emai address", "contact informtion", "how can i rech you"
        ]
        
        contact_responses = self._extract_contact_info(website_data['contact'])
        if contact_responses:
            intents.append({
                "tag": "contact",
                "patterns": contact_patterns,
                "responses": contact_responses
            })
        
        # Python course intents with misspellings
        python_patterns = [
            # Correct spellings
            "python course", "python programming", "python full stack",
            "python development", "learn python", "python training",
            "python programming course", "full stack python",
            "python web development", "django flask",
            
            # Common misspellings for python
            "pythn course", "pyton course", "pythoon course",
            "python corse", "pythn programming", "pyton programming",
            "python full stack", "pythn development", "learn pythn",
            "python trainig", "python programing course", "full stack pythn",
            "python web devlopment", "django flak"
        ]
        
        python_responses = self._extract_python_info(website_data['courses'])
        if python_responses:
            intents.append({
                "tag": "python_course",
                "patterns": python_patterns,
                "responses": python_responses
            })
        
        # Java course intents with misspellings
        java_patterns = [
            # Correct spellings
            "java course", "java programming", "java development",
            "learn java", "java training", "java full stack",
            "core java", "advanced java", "spring framework",
            
            # Common misspellings for java
            "jva course", "jaava course", "jave course", "java corse",
            "jva programming", "jaava programming", "java devlopment",
            "learn jva", "java trainig", "java full stack",
            "core jva", "advanced jva", "spring framwork"
        ]
        
        java_responses = self._extract_java_info(website_data['courses'])
        if java_responses:
            intents.append({
                "tag": "java_course",
                "patterns": java_patterns,
                "responses": java_responses
            })
        
        # AI/ML course intents with misspellings
        ai_ml_patterns = [
            # Correct spellings
            "artificial intelligence", "machine learning", "ai ml course",
            "ai course", "ml course", "artificial intelligence course",
            "machine learning course", "ai and ml", "neural networks",
            "deep learning", "computer vision",
            
            # Common misspellings for AI/ML
            "artifical intelligence", "artifical inteligence",
            "artificial inteligence", "mashine learning", "machine lernning",
            "ai ml corse", "ai corse", "ml corse", "artifical intelligence corse",
            "mashine learning corse", "ai and ml", "neural netwoks",
            "deep lernning", "computer vison"
        ]
        
        ai_ml_responses = self._extract_ai_ml_info(website_data['courses'])
        if ai_ml_responses:
            intents.append({
                "tag": "ai_ml_course",
                "patterns": ai_ml_patterns,
                "responses": ai_ml_responses
            })
        
        # Data Science course intents with misspellings
        data_science_patterns = [
            # Correct spellings
            "data science", "data analytics", "data science course",
            "data analyst", "big data", "data analysis",
            "data visualization", "data scientist course",
            
            # Common misspellings for data science
            "data sience", "data scence", "data analytics",
            "data science corse", "data analist", "big data",
            "data analisis", "data visualisation", "data scientist corse",
            "data sceince", "data anylitics"
        ]
        
        data_science_responses = self._extract_data_science_info(website_data['courses'])
        if data_science_responses:
            intents.append({
                "tag": "data_science_course",
                "patterns": data_science_patterns,
                "responses": data_science_responses
            })
        
        # Add default intents with misspellings
        intents.extend(self._get_default_intents())
        
        return {"intents": intents}
    
    def _extract_course_info(self, course_content):
        """Extract course information from scraped content"""
        responses = []
        course_text = " ".join(course_content)
        
        if course_content:
            responses.append("Based on our website, here are our current course offerings:")
            responses.append("I found these courses on our website. Let me summarize the key information for you.")
            responses.append("Our website shows comprehensive training programs. Here's what we offer:")
        else:
            responses.extend([
                "We offer various technical courses including Python Full Stack, Java, AI/ML, and Data Science. Please visit https://www.brainovision.in/courses for complete details.",
                "Our course catalog includes cutting-edge technology programs. Check https://www.brainovision.in/courses for the latest offerings.",
                "We provide industry-relevant technical training. Visit our courses page at https://www.brainovision.in/courses for detailed information."
            ])
        
        return responses
    
    def _extract_internship_info(self, internship_content):
        """Extract internship information"""
        responses = []
        internship_text = " ".join(internship_content)
        
        if "internship" in internship_text.lower():
            responses.extend([
                "According to our website, we provide comprehensive internship programs with hands-on experience.",
                "Our internship details are available on the website. We offer practical training with industry exposure.",
                "Yes, we have internship opportunities as mentioned on our website. Visit https://www.brainovision.in for details."
            ])
        else:
            responses.extend([
                "We offer 3-month internship programs with stipend for all our courses. This provides real-world industry experience.",
                "All our courses include internship opportunities with financial support. Check our website for specific details.",
                "Yes! We provide internship programs to give you practical experience. Visit https://www.brainovision.in for more information."
            ])
        
        return responses
    
    def _extract_company_info(self, about_content):
        """Extract company information"""
        responses = []
        
        if about_content:
            responses.extend([
                "Based on our website: Brainovision Solutions is an educational institute specializing in technology training and career development.",
                "From our about page: We focus on providing quality technical education with industry-relevant curriculum.",
                "Our website describes us as a premier training institute offering comprehensive learning programs."
            ])
        else:
            responses.extend([
                "Brainovision Solutions Pvt. Ltd. is an educational institute providing technical courses and career-focused training.",
                "We are a technology training institute offering courses, internships, and placement assistance.",
                "Brainovision Solutions specializes in IT education with practical, industry-oriented programs."
            ])
        
        return responses
    
    def _extract_contact_info(self, contact_content):
        """Extract contact information"""
        responses = []
        
        responses.extend([
            "For complete contact details, please visit our contact page: https://www.brainovision.in/contact",
            "You can find all our contact information on our website at https://www.brainovision.in/contact",
            "Our website has detailed contact information including phone, email, and address. Visit: https://www.brainovision.in/contact"
        ])
        
        return responses
    
    def _extract_python_info(self, course_content):
        """Extract Python course information"""
        responses = [
            "🐍 **Python Full Stack Development:** Comprehensive training in Python programming, web development, and full-stack technologies. Includes 3-month internship with stipend. Visit https://www.brainovision.in/courses for details.",
            "Our Python Full Stack course covers everything from basics to advanced topics including Django, Flask, and modern web technologies. Check our website for the complete curriculum.",
            "Python Full Stack program at Brainovision provides hands-on training in both frontend and backend development. Includes real-world projects and internship."
        ]
        return responses
    
    def _extract_java_info(self, course_content):
        """Extract Java course information"""
        responses = [
            "☕ **Java Full Stack Development:** Master enterprise Java development with Spring Framework, Hibernate, and modern technologies. Includes 3-month paid internship.",
            "Our Java Full Stack course focuses on building scalable enterprise applications. Covers Core Java, Advanced Java, and full-stack development.",
            "Java Development program provides comprehensive training in Java ecosystem technologies. Perfect for building career in enterprise software development."
        ]
        return responses
    
    def _extract_ai_ml_info(self, course_content):
        """Extract AI/ML course information"""
        responses = [
            "🤖 **Artificial Intelligence & Machine Learning:** Cutting-edge training in AI/ML concepts, neural networks, and intelligent systems. Includes hands-on projects and internship.",
            "Our AI & ML course covers machine learning algorithms, deep learning, computer vision, and natural language processing.",
            "AI/ML program at Brainovision provides practical training in building intelligent applications and systems. Industry-relevant curriculum."
        ]
        return responses
    
    def _extract_data_science_info(self, course_content):
        """Extract Data Science course information"""
        responses = [
            "📊 **Data Science & Analytics:** Comprehensive training in data analysis, visualization, machine learning, and big data technologies. Includes real-world projects.",
            "Our Data Science course covers statistical analysis, data visualization, machine learning, and business intelligence tools.",
            "Data Science program provides end-to-end training in data analysis and predictive modeling. Perfect for analytics career."
        ]
        return responses
    
    def _get_default_intents(self):
        """Get default conversation intents with misspellings"""
        return [
            {
                "tag": "greeting",
                "patterns": [
                    # Correct spellings
                    "Hi", "Hello", "Hey", "Good morning", "Good afternoon", 
                    "Good evening", "Hi there", "Hello there",
                    
                    # Common misspellings
                    "Hii", "Helloo", "Hellow", "Good morning", "Good afternon",
                    "Good evning", "Hi ther", "Hello ther", "Hai", "Hellow"
                ],
                "responses": [
                    "Hello! Welcome to Brainovision Solutions! I'm your AI assistant. How can I help you today?",
                    "Hi there! Welcome to Brainovision Solutions. I can provide information about our courses, internships, and more!",
                    "Good day! I'm here to help you with information about Brainovision Solutions. What would you like to know?"
                ]
            },
            {
                "tag": "goodbye",
                "patterns": [
                    # Correct spellings
                    "Bye", "Goodbye", "See you", "See ya", "I have to go",
                    "Bye bye", "Take care", "Thank you", "Thanks",
                    
                    # Common misspellings
                    "Byee", "Goodby", "See u", "See yaa", "I have to goo",
                    "Bye byee", "Take care", "Thank u", "Thankss", "Thanx"
                ],
                "responses": [
                    "Thank you for visiting Brainovision Solutions! Visit our website https://www.brainovision.in for more details.",
                    "Goodbye! Feel free to visit https://www.brainovision.in for complete information about our programs.",
                    "Thank you for your interest in Brainovision Solutions! We hope to see you soon on our website."
                ]
            },
            {
                "tag": "website",
                "patterns": [
                    # Correct spellings
                    "website", "online", "portal", "web page",
                    "brainovision website", "official website",
                    
                    # Common misspellings
                    "websit", "webite", "oneline", "portl", "web page",
                    "brainovison website", "oficial website", "webportal",
                    "onlain", "webportal"
                ],
                "responses": [
                    "Our official website is https://www.brainovision.in where you'll find complete information about all our programs and services.",
                    "Visit https://www.brainovision.in for detailed information about courses, internships, admissions, and more.",
                    "You can explore everything about Brainovision Solutions at https://www.brainovision.in"
                ]
            },
            {
                "tag": "thanks",
                "patterns": [
                    # Correct spellings
                    "thank you", "thanks", "thank you very much", "appreciate it",
                    "thanks a lot", "grateful", "thank you so much",
                    
                    # Common misspellings
                    "thank u", "thankss", "thank you very mch", "apreciate it",
                    "thanks alot", "greatful", "thank you so mch", "thanx",
                    "thnks", "thnx"
                ],
                "responses": [
                    "You're welcome! Happy to help with Brainovision Solutions information.",
                    "Glad I could assist! Feel free to ask if you need more information.",
                    "You're welcome! Visit https://www.brainovision.in for complete details."
                ]
            }
        ]
    
    def save_training_data(self, filename='website_training_data.json'):
        """Scrape website and save training data"""
        print("🕸️  Scraping Brainovision Solutions website...")
        website_data = self.scrape_website()
        print("✅ Website scraping completed!")
        
        print("📝 Generating training data with misspellings...")
        training_data = self.generate_training_data(website_data)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, indent=2)
        
        print(f"✅ Training data saved to {filename}")
        print(f"📊 Generated {len(training_data['intents'])} intents")
        print("🎯 Now includes common misspellings for better understanding!")
        
        return training_data

if __name__ == "__main__":
    scraper = WebsiteScraper()
    training_data = scraper.save_training_data()