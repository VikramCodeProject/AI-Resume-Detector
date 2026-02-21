"""
Resume Truth Verification System - Verification Engines
Multi-source verification: GitHub, LinkedIn, Certificates, Timeline
"""

import logging
import requests
import json
from typing import Dict, List, Tuple, Any
from datetime import datetime, timedelta
import re
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

# ===================== BASE VERIFICATION ENGINE =====================

class VerificationEngine(ABC):
    """Abstract base class for verification engines"""
    
    @abstractmethod
    def verify(self, claim: str, **kwargs) -> Dict[str, Any]:
        """Verify a claim and return score + evidence"""
        pass

# ===================== GITHUB VERIFICATION =====================

class GitHubVerificationEngine(VerificationEngine):
    """Verify claimed programming skills against GitHub profile"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"token {api_key}"})
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def get_user_profile(self, username: str) -> Dict[str, Any]:
        """Fetch GitHub user profile"""
        try:
            url = f"{self.base_url}/users/{username}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Error fetching GitHub profile {username}: {str(e)}")
            return {}
    
    def get_user_repositories(self, username: str) -> List[Dict[str, Any]]:
        """Fetch user's repositories with language info"""
        try:
            url = f"{self.base_url}/users/{username}/repos"
            params = {"per_page": 100, "sort": "updated"}
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Error fetching repositories for {username}: {str(e)}")
            return []
    
    def analyze_language_usage(self, repos: List[Dict]) -> Dict[str, int]:
        """Analyze programming languages used in repositories"""
        languages = {}
        
        for repo in repos:
            language = repo.get('language')
            if language:
                languages[language] = languages.get(language, 0) + 1
        
        return languages
    
    def calculate_activity_score(self, profile: Dict) -> float:
        """Calculate GitHub activity score (0-1)"""
        score = 0.0
        
        # Public repos
        public_repos = profile.get('public_repos', 0)
        score += min(public_repos / 50, 0.3)
        
        # Followers (indication of influence)
        followers = profile.get('followers', 0)
        score += min(followers / 100, 0.3)
        
        # Public gists
        public_gists = profile.get('public_gists', 0)
        score += min(public_gists / 50, 0.2)
        
        # Contributions (if available from profile)
        if 'contributions' in profile:
            contributions = profile.get('contributions', 0)
            score += min(contributions / 10000, 0.2)
        
        return min(score, 1.0)
    
    def calculate_recency_score(self, profile: Dict) -> float:
        """Calculate recency of recent activity (0-1)"""
        updated_at = profile.get('updated_at')
        if not updated_at:
            return 0.0
        
        try:
            last_update = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            days_since_update = (datetime.now(last_update.tzinfo) - last_update).days
            
            # Recent activity in last 30 days = high score
            if days_since_update <= 7:
                return 1.0
            elif days_since_update <= 30:
                return 0.8
            elif days_since_update <= 90:
                return 0.5
            else:
                return 0.2
        except Exception as e:
            self.logger.error(f"Error calculating recency: {str(e)}")
            return 0.0
    
    def verify(self, claimed_skill: str, username: str = None, **kwargs) -> Dict[str, Any]:
        """Verify skill claim against GitHub profile"""
        
        if not username:
            username = kwargs.get('github_username')
        
        result = {
            'source': 'github',
            'claim': claimed_skill,
            'username': username,
            'score': 0.0,
            'evidence': {
                'repositories': 0,
                'languages': {},
                'activity_level': 'none',
                'last_activity': None
            }
        }
        
        if not username:
            result['error'] = "GitHub username not provided"
            return result
        
        try:
            # Get user profile
            profile = self.get_user_profile(username)
            if not profile:
                result['error'] = f"GitHub user {username} not found"
                return result
            
            # Get repositories
            repos = self.get_user_repositories(username)
            
            # Analyze language usage
            languages = self.analyze_language_usage(repos)
            
            # Check if claimed skill matches any repository language
            skill_lower = claimed_skill.lower()
            matching_repos = 0
            
            for language, count in languages.items():
                if skill_lower in language.lower():
                    matching_repos = count
                    break
            
            # Calculate scores
            activity_score = self.calculate_activity_score(profile)
            recency_score = self.calculate_recency_score(profile)
            
            # Language match score
            language_score = min(matching_repos / 10, 1.0) if matching_repos > 0 else 0.0
            
            # Combined score
            combined_score = (activity_score * 0.4) + (language_score * 0.4) + (recency_score * 0.2)
            
            result['score'] = combined_score
            result['evidence'] = {
                'repositories': len(repos),
                'languages': languages,
                'matching_repositories': matching_repos,
                'activity_level': 'high' if activity_score > 0.7 else 'medium' if activity_score > 0.4 else 'low',
                'last_activity': profile.get('updated_at'),
                'followers': profile.get('followers', 0),
                'public_repos': profile.get('public_repos', 0)
            }
            
            self.logger.info(f"GitHub verification for {username}: {combined_score:.2f}")
            return result
            
        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"GitHub verification error: {str(e)}")
            return result

# ===================== TIMELINE VALIDATOR =====================

class TimelineValidator(VerificationEngine):
    """Validate resume timeline consistency"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def extract_dates(self, text: str) -> List[Tuple[str, str]]:
        """Extract date ranges from text"""
        # Pattern: Month Year - Month Year or YYYY-YYYY
        date_pattern = r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December|20\d{2}))\s+(20\d{2})\s*(?:[-–]|to|–)\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December|20\d{2}))\s+(20\d{2})|20\d{2}\s*(?:[-–]|to|–)\s*(?:20\d{2}|Present|Current)'
        
        matches = re.findall(date_pattern, text, re.IGNORECASE)
        return matches
    
    def parse_date(self, month: str, year: str) -> datetime:
        """Parse month and year string to datetime"""
        month_map = {
            'jan': 1, 'january': 1,
            'feb': 2, 'february': 2,
            'mar': 3, 'march': 3,
            'apr': 4, 'april': 4,
            'may': 5,
            'jun': 6, 'june': 6,
            'jul': 7, 'july': 7,
            'aug': 8, 'august': 8,
            'sep': 9, 'september': 9,
            'oct': 10, 'october': 10,
            'nov': 11, 'november': 11,
            'dec': 12, 'december': 12
        }
        
        try:
            month_num = month_map.get(month.lower(), 1)
            year_num = int(year)
            return datetime(year_num, month_num, 1)
        except Exception as e:
            self.logger.error(f"Error parsing date {month} {year}: {str(e)}")
            return None
    
    def check_timeline_conflicts(self, experiences: List[Dict]) -> List[Dict]:
        """Check for timeline conflicts (overlapping jobs, impossible dates)"""
        conflicts = []
        
        # Sort by start date
        sorted_exp = sorted(experiences, key=lambda x: x.get('start_date', ''))
        
        for i, exp in enumerate(sorted_exp):
            start = exp.get('start_date')
            end = exp.get('end_date')
            
            # Check if end date is before start date
            if end and start and end < start:
                conflicts.append({
                    'type': 'invalid_date_range',
                    'experience': exp.get('title', 'Unknown'),
                    'message': f"End date {end} is before start date {start}"
                })
            
            # Check for overlaps with other experiences
            for j, other_exp in enumerate(sorted_exp):
                if i == j:
                    continue
                
                other_start = other_exp.get('start_date')
                other_end = other_exp.get('end_date')
                
                if other_start and end:
                    if other_start < end:
                        conflicts.append({
                            'type': 'overlapping_positions',
                            'experience1': exp.get('title', 'Unknown'),
                            'experience2': other_exp.get('title', 'Unknown'),
                            'message': f"Overlapping employment detected"
                        })
        
        return conflicts
    
    def verify(self, resume_text: str, **kwargs) -> Dict[str, Any]:
        """Verify timeline consistency"""
        
        result = {
            'source': 'timeline',
            'score': 1.0,  # Start with perfect score
            'evidence': {
                'conflicts': [],
                'total_experience_years': 0
            }
        }
        
        try:
            # Extract date ranges
            date_ranges = self.extract_dates(resume_text)
            
            if not date_ranges:
                return result
            
            # Parse into experiences (simplified)
            experiences = []
            for match in date_ranges:
                if match[0] and match[1] and match[2] and match[3]:
                    start = self.parse_date(match[0], match[1])
                    end = self.parse_date(match[2], match[3])
                    if start and end:
                        experiences.append({
                            'start_date': start,
                            'end_date': end,
                            'title': 'Job'
                        })
            
            # Check for conflicts
            conflicts = self.check_timeline_conflicts(experiences)
            
            # Score reduction based on conflicts
            penalty = len(conflicts) * 0.15
            result['score'] = max(0.0, 1.0 - penalty)
            result['evidence']['conflicts'] = conflicts
            
            # Calculate total experience years
            if experiences:
                years = sum((exp['end_date'] - exp['start_date']).days / 365.25 for exp in experiences)
                result['evidence']['total_experience_years'] = round(years, 1)
            
            self.logger.info(f"Timeline validation: {result['score']:.2f} (conflicts: {len(conflicts)})")
            return result
            
        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"Timeline validation error: {str(e)}")
            return result

# ===================== CERTIFICATE DETECTOR =====================

class CertificateDetector(VerificationEngine):
    """Detect certificate authenticity using image analysis"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def detect_certificate_features(self, image_path: str) -> Dict[str, Any]:
        """Detect certificate features using image analysis"""
        
        # This is a placeholder - in production, use:
        # - Tesseract OCR for text extraction
        # - OpenCV for template matching
        # - QR code detection
        
        features = {
            'has_logo': True,
            'has_qr_code': False,
            'has_security_features': True,
            'text_clarity': 0.8,
            'authenticity_indicators': []
        }
        
        return features
    
    def verify(self, cert_name: str, image_path: str = None, **kwargs) -> Dict[str, Any]:
        """Verify certificate authenticity"""
        
        result = {
            'source': 'certificate',
            'claim': cert_name,
            'score': 0.5,  # Default uncertain score
            'evidence': {
                'image_provided': bool(image_path),
                'features': {}
            }
        }
        
        if not image_path:
            result['message'] = "No certificate image provided"
            return result
        
        try:
            features = self.detect_certificate_features(image_path)
            result['evidence']['features'] = features
            
            # Scoring logic
            score = 0.0
            if features.get('has_logo'):
                score += 0.3
            if features.get('has_qr_code'):
                score += 0.3
            if features.get('has_security_features'):
                score += 0.2
            score += features.get('text_clarity', 0) * 0.2
            
            result['score'] = min(score, 1.0)
            
            self.logger.info(f"Certificate verification: {result['score']:.2f}")
            return result
            
        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"Certificate detection error: {str(e)}")
            return result

# ===================== LINKEDIN VERIFICATION =====================

class LinkedInVerificationEngine(VerificationEngine):
    """Verify claimed education and experience against LinkedIn"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def verify(self, claimed_education: str, linkedin_url: str = None, **kwargs) -> Dict[str, Any]:
        """Verify education claim against LinkedIn"""
        
        result = {
            'source': 'linkedin',
            'claim': claimed_education,
            'score': 0.5,
            'evidence': {
                'linkedin_url': linkedin_url,
                'status': 'unverified'
            }
        }
        
        if not linkedin_url:
            result['message'] = "LinkedIn URL not provided"
            return result
        
        # In production, use Selenium + Puppeteer to scrape LinkedIn
        # For now, return simulated results
        
        result['score'] = 0.75  # Simulated match
        result['evidence']['status'] = 'partially_matched'
        
        self.logger.info(f"LinkedIn verification: {result['score']:.2f}")
        return result

# ===================== SKILL ASSESSOR =====================

class SkillAssessor(VerificationEngine):
    """Generate dynamic skill assessments"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.mcq_questions = {
            'Python': [
                {
                    'question': 'What is the output of len([1, 2, 3])?',
                    'options': ['2', '3', '4', 'Error'],
                    'correct': '3'
                },
                {
                    'question': 'Which keyword is used to create a function?',
                    'options': ['function', 'def', 'lambda', 'func'],
                    'correct': 'def'
                }
            ],
            'JavaScript': [
                {
                    'question': 'What is the default return value of a function?',
                    'options': ['null', 'undefined', '0', 'false'],
                    'correct': 'undefined'
                }
            ]
        }
    
    def generate_skill_test(self, skill: str) -> List[Dict]:
        """Generate MCQ test for skill"""
        return self.mcq_questions.get(skill, [])
    
    def score_test_responses(self, skill: str, responses: List[str]) -> float:
        """Score test responses (0-1)"""
        questions = self.mcq_questions.get(skill, [])
        
        if not questions:
            return 0.5  # Unknown skill
        
        correct = sum(1 for i, resp in enumerate(responses) 
                     if i < len(questions) and resp == questions[i]['correct'])
        
        return correct / len(questions)
    
    def verify(self, claimed_skill: str, test_responses: List[str] = None, **kwargs) -> Dict[str, Any]:
        """Verify skill through assessment"""
        
        result = {
            'source': 'skill_test',
            'claim': claimed_skill,
            'score': 0.5,
            'evidence': {
                'test_available': claimed_skill in self.mcq_questions,
                'questions_count': len(self.mcq_questions.get(claimed_skill, []))
            }
        }
        
        if test_responses:
            result['score'] = self.score_test_responses(claimed_skill, test_responses)
        else:
            # No test taken yet
            test = self.generate_skill_test(claimed_skill)
            result['test'] = test
        
        self.logger.info(f"Skill assessment for {claimed_skill}: {result['score']:.2f}")
        return result

# ===================== MULTI-SOURCE VERIFICATION ORCHESTRATOR =====================

class VerificationOrchestrator:
    """Coordinate multiple verification engines"""
    
    def __init__(self, github_key: str = "", linkedin_key: str = ""):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.engines = {
            'github': GitHubVerificationEngine(github_key),
            'timeline': TimelineValidator(),
            'certificate': CertificateDetector(),
            'linkedin': LinkedInVerificationEngine(linkedin_key),
            'skill': SkillAssessor()
        }
    
    def verify_claim(self, claim_type: str, claim_text: str, context: Dict = None) -> Dict[str, Any]:
        """Verify a single claim using appropriate engines"""
        
        if context is None:
            context = {}
        
        results = []
        
        if claim_type == 'skill':
            # Verify against GitHub
            github_result = self.engines['github'].verify(
                claim_text,
                **context.get('github_context', {})
            )
            results.append(github_result)
            
            # Skill assessment
            skill_result = self.engines['skill'].verify(
                claim_text,
                **context.get('skill_context', {})
            )
            results.append(skill_result)
        
        elif claim_type == 'education':
            linkedin_result = self.engines['linkedin'].verify(
                claim_text,
                **context.get('linkedin_context', {})
            )
            results.append(linkedin_result)
        
        elif claim_type == 'experience':
            linkedin_result = self.engines['linkedin'].verify(
                claim_text,
                **context.get('linkedin_context', {})
            )
            results.append(linkedin_result)
        
        elif claim_type == 'certification':
            cert_result = self.engines['certificate'].verify(
                claim_text,
                **context.get('cert_context', {})
            )
            results.append(cert_result)
        
        # Timeline validation for all types
        timeline_result = self.engines['timeline'].verify(
            claim_text,
            **context.get('timeline_context', {})
        )
        results.append(timeline_result)
        
        # Aggregate results
        aggregated = {
            'claim': claim_text,
            'claim_type': claim_type,
            'verification_results': results,
            'average_score': np.mean([r.get('score', 0) for r in results]) if results else 0,
            'verified_at': datetime.utcnow().isoformat()
        }
        
        return aggregated

import numpy as np
