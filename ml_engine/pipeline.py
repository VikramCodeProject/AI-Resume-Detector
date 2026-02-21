"""
Resume Truth Verification System - ML/NLP Pipeline
Advanced NLP processing for resume analysis, claim extraction, and truth verification
"""

import logging
from typing import List, Dict, Tuple, Any
import numpy as np
import json
from datetime import datetime
import re
from dataclasses import dataclass, asdict

import spacy
from spacy.tokens import Doc
import pytextrank
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import PyPDF2
import docx
from pathlib import Path

logger = logging.getLogger(__name__)

# ===================== DATA CLASSES =====================

@dataclass
class ExtractedClaim:
    """Represents an extracted claim from resume"""
    claim_type: str  # skill, education, experience, certification, project, achievement
    claim_text: str
    confidence: float
    start_pos: int
    end_pos: int
    section: str  # education, experience, skills, etc.
    entities: Dict[str, Any] = None

@dataclass
class FeatureVector:
    """Feature vector for ML model"""
    claim_id: str
    github_activity_score: float = 0.0
    github_recency_score: float = 0.0
    linkedin_match_score: float = 0.0
    certificate_authenticity_score: float = 0.0
    timeline_violation_penalty: float = 0.0
    skill_test_score: float = 0.0
    source_document_quality: float = 0.0
    claim_specificity: float = 0.0
    language_confidence: float = 0.0
    entity_recognition_score: float = 0.0
    temporal_consistency: float = 0.0
    duplicate_claim_count: int = 0

# ===================== RESUME PARSER =====================

class ResumeParser:
    """Parse PDF/DOCX resumes and extract raw text"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def parse_pdf(self, file_path: str) -> str:
        """Extract text from PDF resume"""
        try:
            text = ""
            with open(file_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                num_pages = len(pdf_reader.pages)
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text()
            
            self.logger.info(f"PDF parsed successfully: {len(text)} characters extracted")
            return text
        except Exception as e:
            self.logger.error(f"Error parsing PDF: {str(e)}")
            raise
    
    def parse_docx(self, file_path: str) -> str:
        """Extract text from DOCX resume"""
        try:
            doc = docx.Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            
            self.logger.info(f"DOCX parsed successfully: {len(text)} characters extracted")
            return text
        except Exception as e:
            self.logger.error(f"Error parsing DOCX: {str(e)}")
            raise
    
    def parse(self, file_path: str) -> str:
        """Parse resume file (auto-detect format)"""
        path = Path(file_path)
        
        if path.suffix.lower() == '.pdf':
            return self.parse_pdf(file_path)
        elif path.suffix.lower() == '.docx':
            return self.parse_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize resume text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\-.,():/]', '', text)
        return text.strip()

# ===================== CLAIM EXTRACTOR =====================

class ClaimExtractor:
    """Extract claims from resume using NLP"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Load SpaCy model with custom components
        try:
            self.nlp = spacy.load("en_core_web_sm")
            # Add textrank for keyword extraction
            self.nlp.add_pipe("textrank", last=True)
        except OSError:
            self.logger.warning("SpaCy model not found. Download with: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Load transformer model for semantic understanding
        try:
            self.semantic_model = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli"
            )
        except Exception as e:
            self.logger.warning(f"Could not load semantic model: {str(e)}")
            self.semantic_model = None
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities using NER"""
        if not self.nlp:
            return {}
        
        doc = self.nlp(text)
        entities = {}
        
        for ent in doc.ents:
            label = ent.label_
            if label not in entities:
                entities[label] = []
            entities[label].append(ent.text)
        
        return entities
    
    def extract_skills(self, text: str) -> List[ExtractedClaim]:
        """Extract skill claims using patterns and NER"""
        skills = []
        
        # Define programming languages, frameworks, tools
        skill_patterns = {
            'programming_languages': [
                'Python', 'JavaScript', 'Java', 'C++', 'C#', 'Go', 'Rust',
                'PHP', 'Ruby', 'Swift', 'Kotlin', 'TypeScript', 'SQL'
            ],
            'frameworks': [
                'React', 'Angular', 'Vue', 'Django', 'Flask', 'FastAPI',
                'Spring', '.NET', 'Node.js', 'Express', 'TensorFlow', 'PyTorch'
            ],
            'tools': [
                'Docker', 'Kubernetes', 'Git', 'Jenkins', 'AWS', 'GCP',
                'Azure', 'Linux', 'Windows', 'macOS', 'Terraform', 'PostgreSQL'
            ]
        }
        
        # Search for skill patterns in text
        for category, skill_list in skill_patterns.items():
            for skill in skill_list:
                pattern = rf'\b{re.escape(skill)}\b'
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    skills.append(ExtractedClaim(
                        claim_type='skill',
                        claim_text=match.group(),
                        confidence=0.9,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        section=category,
                        entities={'category': category}
                    ))
        
        self.logger.info(f"Extracted {len(skills)} skill claims")
        return skills
    
    def extract_education(self, text: str) -> List[ExtractedClaim]:
        """Extract education claims"""
        education_claims = []
        
        # Pattern for degree + university
        degree_pattern = r'(Bachelor|Master|PhD|Associate|B\.S\.|M\.S\.|B\.A\.|M\.A\.).*?(?:from|at|in)?\s+([A-Z][A-Za-z\s]+(?:University|College|Institute|School))'
        
        for match in re.finditer(degree_pattern, text, re.IGNORECASE):
            degree = match.group(1)
            university = match.group(2)
            education_claims.append(ExtractedClaim(
                claim_type='education',
                claim_text=f"{degree} from {university}",
                confidence=0.85,
                start_pos=match.start(),
                end_pos=match.end(),
                section='education',
                entities={'degree': degree, 'university': university}
            ))
        
        self.logger.info(f"Extracted {len(education_claims)} education claims")
        return education_claims
    
    def extract_experience(self, text: str) -> List[ExtractedClaim]:
        """Extract work experience claims"""
        experience_claims = []
        
        # Pattern for job title + company
        experience_pattern = r'(Senior|Lead|Principal|Junior)?.*?(Software Engineer|Developer|Manager|Data Scientist|Product Manager).*?(?:at|for)?\s+([A-Z][A-Za-z\s&]+?)(?:\s+-|\s+\||experience|worked)'
        
        for match in re.finditer(experience_pattern, text, re.IGNORECASE):
            job_title = match.group(2)
            company = match.group(3)
            experience_claims.append(ExtractedClaim(
                claim_type='experience',
                claim_text=f"{job_title} at {company}",
                confidence=0.80,
                start_pos=match.start(),
                end_pos=match.end(),
                section='experience',
                entities={'title': job_title, 'company': company}
            ))
        
        self.logger.info(f"Extracted {len(experience_claims)} experience claims")
        return experience_claims
    
    def extract_certifications(self, text: str) -> List[ExtractedClaim]:
        """Extract certification claims"""
        certifications = []
        
        # Pattern for certifications
        cert_pattern = r'(AWS|GCP|Azure|Certified|Certification).*?(?:Certification|Certified|Certificate)(?:\s+-|\s+\()?([A-Z][A-Za-z\s&]+?)(?:\)|$)'
        
        for match in re.finditer(cert_pattern, text, re.IGNORECASE):
            cert_name = match.group(0)
            certifications.append(ExtractedClaim(
                claim_type='certification',
                claim_text=cert_name,
                confidence=0.88,
                start_pos=match.start(),
                end_pos=match.end(),
                section='certifications',
                entities={'name': cert_name}
            ))
        
        self.logger.info(f"Extracted {len(certifications)} certification claims")
        return certifications
    
    def extract_all_claims(self, resume_text: str) -> List[ExtractedClaim]:
        """Extract all claim types from resume"""
        all_claims = []
        
        all_claims.extend(self.extract_skills(resume_text))
        all_claims.extend(self.extract_education(resume_text))
        all_claims.extend(self.extract_experience(resume_text))
        all_claims.extend(self.extract_certifications(resume_text))
        
        self.logger.info(f"Total claims extracted: {len(all_claims)}")
        return all_claims

# ===================== FEATURE ENGINEER =====================

class FeatureEngineer:
    """Engineer features from verification results for ML model"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def calculate_source_quality(self, text: str) -> float:
        """Calculate resume document quality score (0-1)"""
        score = 0.0
        
        # Check spelling and grammar
        word_count = len(text.split())
        if 200 <= word_count <= 2000:
            score += 0.2
        
        # Check for structured sections
        sections = ['experience', 'education', 'skills', 'projects', 'certification']
        found_sections = sum(1 for s in sections if s.lower() in text.lower())
        score += (found_sections / len(sections)) * 0.3
        
        # Check for contact info
        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
            score += 0.2
        
        # Check for dates
        if re.search(r'\b(20\d{2}|19\d{2})\b', text):
            score += 0.15
        
        # Check for valid URLs
        if re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text):
            score += 0.15
        
        return min(score, 1.0)
    
    def calculate_claim_specificity(self, claim: ExtractedClaim) -> float:
        """Calculate specificity of claim (0-1)"""
        text = claim.claim_text
        
        # Length-based specificity
        length_score = min(len(text) / 100, 0.5)
        
        # Contains numbers/dates
        numbers_score = 0.25 if re.search(r'\d+', text) else 0
        
        # Contains company/institution names
        proper_nouns_score = 0.25 if any(word[0].isupper() for word in text.split()) else 0
        
        return length_score + numbers_score + proper_nouns_score
    
    def create_feature_vector(
        self,
        claim: ExtractedClaim,
        verification_results: Dict[str, float],
        resume_context: Dict[str, Any]
    ) -> FeatureVector:
        """Create feature vector for ML model input"""
        
        feature_vector = FeatureVector(
            claim_id=resume_context.get('claim_id', 'unknown'),
            github_activity_score=verification_results.get('github_score', 0.0),
            github_recency_score=verification_results.get('github_recency', 0.0),
            linkedin_match_score=verification_results.get('linkedin_score', 0.0),
            certificate_authenticity_score=verification_results.get('certificate_score', 0.0),
            timeline_violation_penalty=verification_results.get('timeline_penalty', 0.0),
            skill_test_score=verification_results.get('skill_test_score', 0.0),
            source_document_quality=self.calculate_source_quality(resume_context.get('full_text', '')),
            claim_specificity=self.calculate_claim_specificity(claim),
            language_confidence=verification_results.get('language_confidence', 0.0),
            entity_recognition_score=verification_results.get('ner_confidence', 0.0),
            temporal_consistency=verification_results.get('temporal_consistency', 0.0),
            duplicate_claim_count=resume_context.get('duplicate_count', 0)
        )
        
        return feature_vector
    
    def normalize_features(self, feature_vector: FeatureVector) -> np.ndarray:
        """Normalize feature vector to [0, 1] range"""
        features = asdict(feature_vector)
        claim_id = features.pop('claim_id')
        
        # Normalize each feature
        normalized = {}
        for key, value in features.items():
            if isinstance(value, (int, float)):
                if key == 'duplicate_claim_count':
                    # Special handling for count
                    normalized[key] = min(value / 5, 1.0)  # Normalize assuming max 5 duplicates
                else:
                    # Already in [0, 1] range
                    normalized[key] = min(max(value, 0), 1)
        
        # Convert to numpy array (ordered by feature names)
        feature_array = np.array([v for k, v in sorted(normalized.items())])
        
        return feature_array

# ===================== TRUTH CLASSIFIER =====================

class TruthClassifier:
    """ML classifier for claim truth classification"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model = None
        self.feature_names = self._get_feature_names()
    
    def _get_feature_names(self) -> List[str]:
        """Get ordered list of feature names"""
        return [
            'certificate_authenticity_score',
            'claim_specificity',
            'duplicate_claim_count',
            'entity_recognition_score',
            'github_activity_score',
            'github_recency_score',
            'language_confidence',
            'linkedin_match_score',
            'skill_test_score',
            'source_document_quality',
            'temporal_consistency',
            'timeline_violation_penalty'
        ]
    
    def load_model(self, model_path: str):
        """Load pre-trained XGBoost model"""
        try:
            import xgboost as xgb
            self.model = xgb.Booster()
            self.model.load_model(model_path)
            self.logger.info("Model loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading model: {str(e)}")
            raise
    
    def predict(self, feature_array: np.ndarray) -> Tuple[str, float]:
        """Predict claim truth: (verified, doubtful, fake) with confidence"""
        if self.model is None:
            # Return random prediction if model not loaded
            self.logger.warning("Model not loaded, returning placeholder prediction")
            predictions = [0.6, 0.25, 0.15]  # verified, doubtful, fake
        else:
            import xgboost as xgb
            dmatrix = xgb.DMatrix(feature_array.reshape(1, -1))
            predictions = self.model.predict(dmatrix)[0]
        
        # Map predictions to class
        class_map = {0: 'verified', 1: 'doubtful', 2: 'fake'}
        predicted_class_idx = np.argmax(predictions)
        predicted_class = class_map[predicted_class_idx]
        confidence = float(predictions[predicted_class_idx])
        
        return predicted_class, confidence
    
    def predict_batch(self, feature_array: np.ndarray) -> List[Tuple[str, float]]:
        """Predict for multiple claims"""
        results = []
        for i in range(len(feature_array)):
            pred, conf = self.predict(feature_array[i])
            results.append((pred, conf))
        return results

# ===================== EXPLAINABILITY =====================

class ExplainabilityEngine:
    """Generate human-readable explanations for predictions"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def generate_shap_explanation(
        self,
        claim: ExtractedClaim,
        feature_vector: FeatureVector,
        prediction: str,
        confidence: float
    ) -> Dict[str, Any]:
        """Generate SHAP-style explanation for prediction"""
        
        explanation = {
            "claim": claim.claim_text,
            "prediction": prediction,
            "confidence": confidence,
            "reasoning": [],
            "contributing_factors": []
        }
        
        # Analyze each feature
        features_analysis = [
            ("GitHub Activity Score", feature_vector.github_activity_score, 0.7, "positive"),
            ("GitHub Recency", feature_vector.github_recency_score, 0.5, "positive"),
            ("LinkedIn Match", feature_vector.linkedin_match_score, 0.6, "positive"),
            ("Certificate Authenticity", feature_vector.certificate_authenticity_score, 0.8, "positive"),
            ("Timeline Consistency", feature_vector.temporal_consistency, 0.7, "positive"),
            ("Document Quality", feature_vector.source_document_quality, 0.6, "positive"),
            ("Claim Specificity", feature_vector.claim_specificity, 0.5, "neutral"),
        ]
        
        # Generate reasoning
        for feature_name, value, threshold, impact_type in features_analysis:
            if value < threshold * 0.5:
                factor = f"{feature_name}: {value:.2f} (LOW - signals inconsistency)"
                explanation["contributing_factors"].append(factor)
        
        # Create natural language explanation
        if prediction == "fake":
            explanation["reasoning"].append(
                f"Claim '{claim.claim_text}' is flagged as FAKE because:"
            )
            if feature_vector.github_activity_score < 0.3:
                explanation["reasoning"].append(
                    f"  - GitHub shows minimal activity in related repositories"
                )
            if feature_vector.linkedin_match_score < 0.4:
                explanation["reasoning"].append(
                    f"  - LinkedIn profile doesn't match claimed experience"
                )
        elif prediction == "doubtful":
            explanation["reasoning"].append(
                f"Claim '{claim.claim_text}' is DOUBTFUL because:"
            )
            explanation["reasoning"].append(
                f"  - Incomplete verification evidence"
            )
        else:
            explanation["reasoning"].append(
                f"Claim '{claim.claim_text}' appears VERIFIED based on:"
            )
            explanation["reasoning"].append(
                f"  - Strong supporting evidence across sources"
            )
        
        return explanation

# ===================== PIPELINE ORCHESTRATOR =====================

class ResumeTruthPipeline:
    """Orchestrate the complete resume verification pipeline"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.parser = ResumeParser()
        self.extractor = ClaimExtractor()
        self.feature_engineer = FeatureEngineer()
        self.classifier = TruthClassifier()
        self.explainer = ExplainabilityEngine()
    
    def process_resume(self, file_path: str, verification_results: Dict = None) -> Dict[str, Any]:
        """Process resume end-to-end"""
        
        if verification_results is None:
            verification_results = {}
        
        try:
            # Stage 1: Parse resume
            self.logger.info(f"Stage 1: Parsing resume from {file_path}")
            resume_text = self.parser.parse(file_path)
            clean_text = self.parser.clean_text(resume_text)
            
            # Stage 2: Extract claims
            self.logger.info("Stage 2: Extracting claims")
            claims = self.extractor.extract_all_claims(clean_text)
            
            # Stage 3: Engineer features and predict
            self.logger.info("Stage 3: Engineering features and predicting")
            predictions = []
            explanations = []
            
            for claim in claims:
                # Create feature vector
                feature_vector = self.feature_engineer.create_feature_vector(
                    claim,
                    verification_results.get('claim_verification', {}),
                    {'full_text': clean_text, 'claim_id': claim.claim_text}
                )
                
                # Normalize and predict
                normalized_features = self.feature_engineer.normalize_features(feature_vector)
                prediction, confidence = self.classifier.predict(normalized_features)
                
                # Generate explanation
                explanation = self.explainer.generate_shap_explanation(
                    claim, feature_vector, prediction, confidence
                )
                
                predictions.append({
                    'claim': claim.claim_text,
                    'type': claim.claim_type,
                    'prediction': prediction,
                    'confidence': confidence
                })
                
                explanations.append(explanation)
            
            # Calculate overall trust score
            verified_count = sum(1 for p in predictions if p['prediction'] == 'verified')
            doubtful_count = sum(1 for p in predictions if p['prediction'] == 'doubtful')
            fake_count = sum(1 for p in predictions if p['prediction'] == 'fake')
            
            total_claims = len(predictions)
            overall_score = ((verified_count * 100) + (doubtful_count * 50)) / max(total_claims, 1)
            
            result = {
                'resume_file': file_path,
                'total_claims': total_claims,
                'verified_count': verified_count,
                'doubtful_count': doubtful_count,
                'fake_count': fake_count,
                'overall_trust_score': overall_score,
                'predictions': predictions,
                'explanations': explanations,
                'processed_at': datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"Pipeline completed: {overall_score:.1f} trust score")
            return result
            
        except Exception as e:
            self.logger.error(f"Pipeline error: {str(e)}", exc_info=True)
            raise

# ===================== USAGE EXAMPLE =====================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize pipeline
    pipeline = ResumeTruthPipeline()
    
    # Process sample resume (would need actual file)
    # results = pipeline.process_resume("sample_resume.pdf")
    # print(json.dumps(results, indent=2))
