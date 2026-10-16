import sys
import spacy
import re
import string
from typing import List, Dict, Set
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Ensure UTF-8 output encoding on Windows
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class ResumeParser:
    """
    A class to parse resumes and extract relevant skills and keywords.
    Uses spaCy for NLP processing and NLTK for additional text processing.
    """
    
    def __init__(self):
        """Initialize the resume parser with spaCy model."""
        try:
            self.nlp = spacy.load("en_core_web_sm")
            print("[OK] spaCy model loaded successfully")
        except Exception as e:
            print(f"[WARN] spaCy model failed to load: {e}")
            print("Using fallback skill extraction method")
            self.nlp = None
        
        # Common technical skills and keywords
        self.technical_skills = {
            'programming_languages': [
                'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin',
                'go', 'rust', 'scala', 'r', 'matlab', 'perl', 'bash', 'powershell'
            ],
            'frameworks': [
                'react', 'angular', 'vue', 'django', 'flask', 'spring', 'express', 'laravel',
                'asp.net', 'ruby on rails', 'fastapi', 'tornado', 'bootstrap', 'tailwind'
            ],
            'databases': [
                'mysql', 'postgresql', 'mongodb', 'redis', 'sqlite', 'oracle', 'sql server',
                'cassandra', 'dynamodb', 'elasticsearch', 'neo4j'
            ],
            'cloud_platforms': [
                'aws', 'azure', 'google cloud', 'gcp', 'heroku', 'digitalocean', 'linode',
                'vultr', 'ibm cloud', 'oracle cloud'
            ],
            'tools': [
                'git', 'docker', 'kubernetes', 'jenkins', 'github actions', 'gitlab ci',
                'jira', 'confluence', 'slack', 'teams', 'zoom', 'figma', 'sketch'
            ]
        }
        
        # Get stopwords
        self.stop_words = set(stopwords.words('english'))
        
    def clean_text(self, text: str) -> str:
        """
        Clean and preprocess the input text.
        
        Args:
            text (str): Raw text input
            
        Returns:
            str: Cleaned text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and extra whitespace
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        # Remove numbers (optional - you might want to keep them for experience)
        # text = re.sub(r'\d+', '', text)
        
        return text.strip()
    
    def _extract_skills_fallback(self, text: str) -> Dict[str, List[str]]:
        """
        Fallback skill extraction without spaCy.
        
        Args:
            text (str): Resume text
            
        Returns:
            Dict[str, List[str]]: Dictionary of categorized skills
        """
        cleaned_text = self.clean_text(text)
        tokens = word_tokenize(cleaned_text)
        filtered_tokens = [token for token in tokens if token not in self.stop_words and len(token) > 2]
        
        # Combine all extracted terms
        all_terms = set(filtered_tokens)
        
        # Categorize skills
        extracted_skills = {}
        for category, skills in self.technical_skills.items():
            category_skills = []
            for skill in skills:
                if skill in cleaned_text:
                    category_skills.append(skill)
            if category_skills:
                extracted_skills[category] = category_skills
        
        # Add uncategorized skills
        uncategorized = []
        for term in all_terms:
            if len(term) > 3 and term not in self.stop_words:
                # Check if it's not already categorized
                categorized = False
                for skills in self.technical_skills.values():
                    if term in skills:
                        categorized = True
                        break
                if not categorized:
                    uncategorized.append(term)
        
        if uncategorized:
            extracted_skills['other_skills'] = uncategorized[:20]  # Limit to top 20
        
        return extracted_skills
    
    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        """
        Extract technical skills from resume text using NLP.
        
        Args:
            text (str): Resume text
            
        Returns:
            Dict[str, List[str]]: Dictionary of categorized skills
        """
        if not self.nlp:
            # Fallback skill extraction without spaCy
            return self._extract_skills_fallback(text)
        
        try:
            cleaned_text = self.clean_text(text)
            doc = self.nlp(cleaned_text)
        except Exception as e:
            print(f"spaCy processing failed: {e}, using fallback method")
            return self._extract_skills_fallback(text)
        
        # Extract named entities (organizations, skills, etc.)
        entities = [ent.text.lower() for ent in doc.ents]
        
        # Extract noun chunks and important words
        nouns = [chunk.text.lower() for chunk in doc.noun_chunks]
        
        # Tokenize and filter words
        tokens = word_tokenize(cleaned_text)
        filtered_tokens = [token for token in tokens if token not in self.stop_words and len(token) > 2]
        
        # Combine all extracted terms
        all_terms = set(entities + nouns + filtered_tokens)
        
        # Categorize skills
        extracted_skills = {}
        for category, skills in self.technical_skills.items():
            category_skills = []
            for skill in skills:
                if skill in cleaned_text:
                    category_skills.append(skill)
            if category_skills:
                extracted_skills[category] = category_skills
        
        # Add uncategorized skills
        uncategorized = []
        for term in all_terms:
            if len(term) > 3 and term not in self.stop_words:
                # Check if it's not already categorized
                categorized = False
                for skills in self.technical_skills.values():
                    if term in skills:
                        categorized = True
                        break
                if not categorized:
                    uncategorized.append(term)
        
        if uncategorized:
            extracted_skills['other_skills'] = uncategorized[:20]  # Limit to top 20
        
        return extracted_skills
    
    def extract_keywords(self, text: str, max_keywords: int = 50) -> List[str]:
        """
        Extract important keywords from the resume text.
        
        Args:
            text (str): Resume text
            max_keywords (int): Maximum number of keywords to return
            
        Returns:
            List[str]: List of extracted keywords
        """
        if not self.nlp:
            # Fallback keyword extraction without spaCy
            cleaned_text = self.clean_text(text)
            tokens = word_tokenize(cleaned_text)
            filtered_tokens = [token for token in tokens if token not in self.stop_words and len(token) > 3]
            
            # Count frequency
            keyword_freq = {}
            for keyword in filtered_tokens:
                keyword_freq[keyword] = keyword_freq.get(keyword, 0) + 1
            
            # Sort by frequency and return top keywords
            sorted_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)
            return [keyword for keyword, freq in sorted_keywords[:max_keywords]]
        
        cleaned_text = self.clean_text(text)
        doc = self.nlp(cleaned_text)
        
        # Extract keywords based on POS tags and frequency
        keywords = []
        
        # Get nouns, verbs, and adjectives
        for token in doc:
            if (token.pos_ in ['NOUN', 'VERB', 'ADJ'] and 
                not token.is_stop and 
                len(token.text) > 2 and
                token.text.isalpha()):
                keywords.append(token.text.lower())
        
        # Remove duplicates and get most common
        keyword_freq = {}
        for keyword in keywords:
            keyword_freq[keyword] = keyword_freq.get(keyword, 0) + 1
        
        # Sort by frequency and return top keywords
        sorted_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)
        return [keyword for keyword, freq in sorted_keywords[:max_keywords]]
    
    def get_skill_summary(self, text: str) -> Dict[str, any]:
        """
        Get a comprehensive summary of skills and keywords from the resume.
        
        Args:
            text (str): Resume text
            
        Returns:
            Dict[str, any]: Summary containing skills, keywords, and statistics
        """
        skills = self.extract_skills(text)
        keywords = self.extract_keywords(text)
        
        # Count total skills
        total_skills = sum(len(skill_list) for skill_list in skills.values())
        
        # Get top skills by category
        top_skills = {}
        for category, skill_list in skills.items():
            if skill_list:
                top_skills[category] = skill_list[:5]  # Top 5 skills per category
        
        return {
            'skills': skills,
            'keywords': keywords,
            'top_skills': top_skills,
            'total_skills': total_skills,
            'keyword_count': len(keywords),
            'categories': list(skills.keys())
        }
    
    def parse_resume(self, resume_text: str) -> Dict[str, any]:
        """
        Main method to parse a resume and extract all relevant information.
        
        Args:
            resume_text (str): The resume text to parse
            
        Returns:
            Dict[str, any]: Complete parsing results
        """
        if not resume_text:
            return {"error": "No resume text provided"}
        
        try:
            summary = self.get_skill_summary(resume_text)
            
            return {
                'success': True,
                'parsed_data': summary,
                'resume_length': len(resume_text),
                'processing_time': 'N/A'  # Could add timing if needed
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'resume_length': len(resume_text) if resume_text else 0
            }


# Example usage and testing
if __name__ == "__main__":
    # Sample resume text
    sample_resume = """
    EXPERIENCE
    Senior Software Engineer at TechCorp (2020-2023)
    - Developed web applications using Python, Django, and React
    - Managed AWS infrastructure and implemented CI/CD pipelines
    - Led a team of 5 developers in agile development process
    
    SKILLS
    Programming: Python, JavaScript, Java, SQL
    Frameworks: Django, React, Spring Boot
    Cloud: AWS, Docker, Kubernetes
    Tools: Git, Jenkins, Jira
    
    EDUCATION
    Bachelor's in Computer Science from University of Technology
    """
    
    parser = ResumeParser()
    result = parser.parse_resume(sample_resume)
    
    print("Resume Parsing Results:")
    print("=" * 50)
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Total Skills: {result['parsed_data']['total_skills']}")
        print(f"Keywords: {result['parsed_data']['keyword_count']}")
        print("\nExtracted Skills:")
        for category, skills in result['parsed_data']['skills'].items():
            print(f"  {category}: {', '.join(skills)}")
        print(f"\nTop Keywords: {', '.join(result['parsed_data']['keywords'][:10])}")
    else:
        print(f"Error: {result['error']}") 