"""
Deepfake Resume Detection Service
Detect AI-generated and manipulated resume content

Enterprise Features:
- AI-generated text detection (GPT-detector style)
- Stylometric analysis
- Perplexity scoring
- N-gram repetition analysis
- Burstiness detection
- Vocabulary richness
"""

import logging
from typing import Dict, List, Optional, Tuple
from collections import Counter
import re
import math
from datetime import UTC, datetime

from utils.time_utils import utc_now_iso

# NLP and language modeling
import numpy as np

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logging.warning("spaCy not available")

try:
    from transformers import GPT2LMHeadModel, GPT2TokenizerFast
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("transformers not available for perplexity scoring")

logger = logging.getLogger(__name__)


class DeepfakeDetector:
    """
    Detect AI-generated or manipulated resume content
    
    Detection Methods:
    1. Perplexity scoring (language model likelihood)
    2. Stylometric analysis (writing patterns)
    3. N-gram repetition detection
    4. Burstiness analysis (sentence variance)
    5. Generic phrase detection
    """
    
    # Detection thresholds
    AI_PROBABILITY_THRESHOLD = 0.65  # 65%+ = likely AI-generated
    STYLOMETRIC_RISK_THRESHOLD = 0.60
    REPETITION_RISK_THRESHOLD = 0.55
    
    # Generic phrases commonly used by AI
    GENERIC_PHRASES = [
        'results-oriented professional',
        'team player',
        'self-motivated',
        'detail-oriented',
        'proven track record',
        'excellent communication skills',
        'fast-paced environment',
        'dynamic team',
        'work independently',
        'deadline-driven',
        'strong analytical skills',
        'problem-solving abilities',
        'customer-focused',
        'goal-oriented',
        'passionate about',
        'innovative solutions',
        'collaborative environment'
    ]
    
    def __init__(self, use_perplexity: bool = True):
        """
        Initialize deepfake detector
        
        Args:
            use_perplexity: Use GPT-2 perplexity scoring (computationally expensive)
        """
        self.use_perplexity = use_perplexity and TRANSFORMERS_AVAILABLE
        
        # Load spaCy for linguistic analysis
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load('en_core_web_sm')
            except OSError:
                logger.warning("spaCy model not loaded")
                self.nlp = None
        else:
            self.nlp = None
        
        # Load GPT-2 for perplexity scoring (lazy loading)
        self.perplexity_model = None
        self.perplexity_tokenizer = None
        
        logger.info(f"Deepfake detector initialized (perplexity: {self.use_perplexity})")
    
    def _ensure_perplexity_loaded(self):
        """Lazy load GPT-2 model for perplexity"""
        if self.use_perplexity and self.perplexity_model is None:
            logger.info("Loading GPT-2 model for perplexity scoring...")
            self.perplexity_tokenizer = GPT2TokenizerFast.from_pretrained('gpt2')
            self.perplexity_model = GPT2LMHeadModel.from_pretrained('gpt2')
            self.perplexity_model.eval()
            logger.info("GPT-2 model loaded")
    
    async def analyze_resume_text(self, resume_text: str) -> Dict:
        """
        Complete deepfake analysis of resume text
        
        Args:
            resume_text: Full resume text
        
        Returns:
            Detection report with AI probability and flags
        """
        if not resume_text or len(resume_text) < 50:
            return self._error_response("Insufficient text for analysis")
        
        try:
            logger.info("Starting deepfake detection analysis")
            
            # 1. Perplexity scoring (AI likelihood)
            if self.use_perplexity:
                self._ensure_perplexity_loaded()
                perplexity_score = self._compute_perplexity(resume_text)
            else:
                perplexity_score = None
            
            # 2. Stylometric analysis
            stylometric_results = self._analyze_stylometry(resume_text)
            
            # 3. N-gram repetition analysis
            repetition_results = self._analyze_repetition(resume_text)
            
            # 4. Burstiness analysis
            burstiness_results = self._analyze_burstiness(resume_text)
            
            # 5. Generic phrase detection
            generic_phrase_results = self._detect_generic_phrases(resume_text)
            
            # 6. Compute AI-generated probability
            ai_probability = self._compute_ai_probability(
                perplexity_score,
                stylometric_results,
                repetition_results,
                burstiness_results,
                generic_phrase_results
            )
            
            # 7. Determine if deepfake
            is_deepfake = ai_probability >= self.AI_PROBABILITY_THRESHOLD
            
            # Build response
            result = {
                'ai_generated_probability': round(ai_probability, 4),
                'deepfake_flag': is_deepfake,
                'risk_level': self._determine_risk_level(ai_probability),
                'analysis_breakdown': {
                    'perplexity_score': perplexity_score,
                    'stylometric_risk': round(stylometric_results['risk_score'], 4),
                    'repetition_score': round(repetition_results['risk_score'], 4),
                    'burstiness_score': round(burstiness_results['risk_score'], 4),
                    'generic_phrase_count': generic_phrase_results['count']
                },
                'detailed_metrics': {
                    'stylometry': stylometric_results,
                    'repetition': repetition_results,
                    'burstiness': burstiness_results,
                    'generic_phrases': generic_phrase_results
                },
                'indicators': self._extract_indicators(
                    stylometric_results,
                    repetition_results,
                    burstiness_results,
                    generic_phrase_results
                ),
                'recommendations': self._generate_recommendations(ai_probability, is_deepfake),
                'analyzed_at': utc_now_iso()
            }
            
            logger.info(f"Deepfake analysis complete: AI probability={ai_probability:.2%}, flag={is_deepfake}")
            return result
            
        except Exception as e:
            logger.exception(f"Deepfake detection error: {str(e)}")
            return self._error_response(f"Analysis failed: {str(e)}")
    
    def _compute_perplexity(self, text: str, max_length: int = 512) -> float:
        """
        Compute perplexity using GPT-2
        Lower perplexity = more likely AI-generated (too predictable)
        """
        try:
            # Truncate text for efficiency
            text = text[:max_length]
            
            # Tokenize
            encodings = self.perplexity_tokenizer(text, return_tensors='pt')
            
            # Compute perplexity
            with torch.no_grad():
                outputs = self.perplexity_model(**encodings, labels=encodings['input_ids'])
                loss = outputs.loss
                perplexity = torch.exp(loss).item()
            
            return perplexity
            
        except Exception as e:
            logger.error(f"Perplexity computation error: {e}")
            return None
    
    def _analyze_stylometry(self, text: str) -> Dict:
        """
        Stylometric analysis - writing pattern analysis
        
        AI-generated text tends to have:
        - Uniform sentence length
        - Predictable vocabulary
        - Low lexical diversity
        """
        if self.nlp:
            doc = self.nlp(text)
            sentences = list(doc.sents)
        else:
            # Fallback: simple sentence split
            sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        
        if not sentences:
            return {'risk_score': 0.5, 'error': 'No sentences found'}
        
        # 1. Sentence length variance
        sentence_lengths = [len(sent.split()) for sent in [str(s) for s in sentences]]
        avg_length = np.mean(sentence_lengths)
        std_length = np.std(sentence_lengths)
        
        # AI tends to have low variance (coefficient of variation)
        cv_length = std_length / avg_length if avg_length > 0 else 0
        
        # Expected CV for human writing: 0.3-0.6
        # AI writing: often < 0.25
        length_uniformity_score = 1.0 - min(cv_length / 0.5, 1.0)
        
        # 2. Lexical diversity (Type-Token Ratio)
        tokens = re.findall(r'\b\w+\b', text.lower())
        unique_tokens = set(tokens)
        ttr = len(unique_tokens) / len(tokens) if tokens else 0
        
        # AI tends to have lower TTR (< 0.5)
        # Human writing: typically 0.5-0.7
        low_diversity_score = 1.0 - min(ttr / 0.6, 1.0)
        
        # 3. Vocabulary richness (average word length)
        avg_word_length = np.mean([len(token) for token in tokens]) if tokens else 0
        
        # AI tends to use simpler vocabulary
        # Expected: 4-6 characters average
        simple_vocab_score = 1.0 if avg_word_length < 4.5 else 0.0
        
        # 4. Punctuation patterns
        punctuation_count = len(re.findall(r'[,;:\-]', text))
        punctuation_density = punctuation_count / len(tokens) if tokens else 0
        
        # AI tends to overuse or underuse punctuation
        # Expected: 0.05-0.15
        punctuation_anomaly = abs(punctuation_density - 0.1) / 0.1
        
        # Combine scores
        risk_score = (
            length_uniformity_score * 0.35 +
            low_diversity_score * 0.35 +
            simple_vocab_score * 0.15 +
            punctuation_anomaly * 0.15
        )
        
        return {
            'risk_score': risk_score,
            'sentence_count': len(sentences),
            'avg_sentence_length': round(avg_length, 2),
            'sentence_length_variance': round(std_length, 2),
            'coefficient_variation': round(cv_length, 3),
            'lexical_diversity_ttr': round(ttr, 3),
            'avg_word_length': round(avg_word_length, 2),
            'punctuation_density': round(punctuation_density, 3)
        }
    
    def _analyze_repetition(self, text: str) -> Dict:
        """
        Analyze N-gram repetition patterns
        AI-generated text often repeats phrases
        """
        # Tokenize
        tokens = re.findall(r'\b\w+\b', text.lower())
        
        if len(tokens) < 10:
            return {'risk_score': 0.0, 'error': 'Insufficient tokens'}
        
        # Analyze bigrams (2-word sequences)
        bigrams = [' '.join(tokens[i:i+2]) for i in range(len(tokens) - 1)]
        bigram_counts = Counter(bigrams)
        
        # Analyze trigrams (3-word sequences)
        trigrams = [' '.join(tokens[i:i+3]) for i in range(len(tokens) - 2)]
        trigram_counts = Counter(trigrams)
        
        # Calculate repetition metrics
        total_bigrams = len(bigrams)
        unique_bigrams = len(bigram_counts)
        bigram_repetition = 1.0 - (unique_bigrams / total_bigrams) if total_bigrams > 0 else 0
        
        total_trigrams = len(trigrams)
        unique_trigrams = len(trigram_counts)
        trigram_repetition = 1.0 - (unique_trigrams / total_trigrams) if total_trigrams > 0 else 0
        
        # Find most repeated phrases
        most_repeated_bigrams = bigram_counts.most_common(5)
        most_repeated_trigrams = trigram_counts.most_common(5)
        
        # Score: higher repetition = higher risk
        # Expected: bigram 0.1-0.3, trigram 0.05-0.15
        bigram_risk = max(0, (bigram_repetition - 0.2) / 0.3)
        trigram_risk = max(0, (trigram_repetition - 0.1) / 0.2)
        
        risk_score = (bigram_risk * 0.5 + trigram_risk * 0.5)
        
        return {
            'risk_score': risk_score,
            'bigram_repetition': round(bigram_repetition, 3),
            'trigram_repetition': round(trigram_repetition, 3),
            'most_repeated_bigrams': [
                {'phrase': phrase, 'count': count}
                for phrase, count in most_repeated_bigrams if count > 1
            ],
            'most_repeated_trigrams': [
                {'phrase': phrase, 'count': count}
                for phrase, count in most_repeated_trigrams if count > 1
            ]
        }
    
    def _analyze_burstiness(self, text: str) -> Dict:
        """
        Analyze burstiness - variation in sentence complexity
        
        AI text tends to have uniform complexity
        Human text has "bursts" of complex and simple sentences
        """
        if self.nlp:
            doc = self.nlp(text)
            sentences = list(doc.sents)
        else:
            sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        
        if len(sentences) < 3:
            return {'risk_score': 0.5, 'error': 'Insufficient sentences'}
        
        # Compute sentence complexities (word count + punctuation)
        complexities = []
        for sent in sentences:
            sent_str = str(sent)
            word_count = len(sent_str.split())
            punctuation_count = len(re.findall(r'[,;:]', sent_str))
            complexity = word_count + punctuation_count * 2
            complexities.append(complexity)
        
        # Calculate burstiness metric
        # Higher variance = more bursty (human-like)
        mean_complexity = np.mean(complexities)
        std_complexity = np.std(complexities)
        
        # Calculate burstiness coefficient
        if mean_complexity > 0:
            burstiness = (std_complexity - mean_complexity) / (std_complexity + mean_complexity)
        else:
            burstiness = 0
        
        # AI typically has burstiness near 0 (uniform)
        # Human writing: -0.5 to 0.5 (more variance)
        # Map to risk score: abs(burstiness) close to 0 = higher risk
        risk_score = 1.0 - min(abs(burstiness), 1.0)
        
        return {
            'risk_score': risk_score,
            'burstiness_coefficient': round(burstiness, 3),
            'avg_sentence_complexity': round(mean_complexity, 2),
            'complexity_variance': round(std_complexity, 2),
            'complexity_range': [min(complexities), max(complexities)]
        }
    
    def _detect_generic_phrases(self, text: str) -> Dict:
        """Detect overuse of generic/cliché phrases"""
        text_lower = text.lower()
        
        found_phrases = []
        for phrase in self.GENERIC_PHRASES:
            if phrase in text_lower:
                found_phrases.append(phrase)
        
        phrase_count = len(found_phrases)
        
        # Risk: too many generic phrases (>3 indicates AI or template)
        risk_score = min(phrase_count / 5.0, 1.0)
        
        return {
            'count': phrase_count,
            'phrases_found': found_phrases,
            'risk_score': risk_score
        }
    
    def _compute_ai_probability(
        self,
        perplexity: Optional[float],
        stylometric: Dict,
        repetition: Dict,
        burstiness: Dict,
        generic_phrases: Dict
    ) -> float:
        """
        Compute overall AI-generated probability
        
        Weights:
        - Perplexity: 25% (if available)
        - Stylometric: 30%
        - Repetition: 25%
        - Burstiness: 15%
        - Generic phrases: 5%
        """
        scores = []
        
        # Perplexity score
        if perplexity is not None:
            # Lower perplexity = higher AI probability
            # Typical GPT-2 perplexity on AI text: 20-50
            # Human text: 50-200+
            if perplexity < 30:
                perplexity_risk = 0.9
            elif perplexity < 60:
                perplexity_risk = 0.6
            elif perplexity < 100:
                perplexity_risk = 0.3
            else:
                perplexity_risk = 0.1
            
            scores.append(perplexity_risk * 0.25)
        
        # Other scores
        scores.append(stylometric['risk_score'] * 0.30)
        scores.append(repetition['risk_score'] * 0.25)
        scores.append(burstiness['risk_score'] * 0.15)
        scores.append(generic_phrases['risk_score'] * 0.05)
        
        probability = sum(scores)
        return min(1.0, max(0.0, probability))
    
    def _determine_risk_level(self, ai_probability: float) -> str:
        """Determine risk level"""
        if ai_probability >= 0.80:
            return "Critical"
        elif ai_probability >= 0.65:
            return "High"
        elif ai_probability >= 0.45:
            return "Medium"
        else:
            return "Low"
    
    def _extract_indicators(
        self,
        stylometric: Dict,
        repetition: Dict,
        burstiness: Dict,
        generic_phrases: Dict
    ) -> List[str]:
        """Extract key indicators"""
        indicators = []
        
        if stylometric['risk_score'] > 0.6:
            indicators.append(f"Uniform writing style (TTR: {stylometric['lexical_diversity_ttr']:.2f})")
        
        if repetition['risk_score'] > 0.6:
            indicators.append(f"High phrase repetition detected")
        
        if burstiness['risk_score'] > 0.7:
            indicators.append(f"Uniform sentence complexity (burstiness: {burstiness['burstiness_coefficient']:.2f})")
        
        if generic_phrases['count'] > 3:
            indicators.append(f"{generic_phrases['count']} generic phrases found")
        
        if not indicators:
            indicators.append("No significant AI indicators detected")
        
        return indicators
    
    def _generate_recommendations(
        self,
        ai_probability: float,
        is_deepfake: bool
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if is_deepfake:
            recommendations.append("⚠️ HIGH RISK: Resume shows strong AI-generation indicators")
            recommendations.append("Conduct thorough interview to verify claimed experience")
            recommendations.append("Request work samples or portfolio evidence")
        elif ai_probability > 0.45:
            recommendations.append("MODERATE RISK: Some AI-generation indicators present")
            recommendations.append("Verify key claims with references")
        else:
            recommendations.append("LOW RISK: Resume appears to be human-written")
        
        return recommendations
    
    def _error_response(self, error_message: str) -> Dict:
        """Generate error response"""
        return {
            'ai_generated_probability': 0.5,
            'deepfake_flag': False,
            'risk_level': 'Unknown',
            'error': error_message,
            'analyzed_at': utc_now_iso()
        }


# Singleton instance
_deepfake_detector: Optional[DeepfakeDetector] = None

def get_deepfake_detector(use_perplexity: bool = True) -> DeepfakeDetector:
    """Get or create deepfake detector instance"""
    global _deepfake_detector
    
    if _deepfake_detector is None:
        _deepfake_detector = DeepfakeDetector(use_perplexity)
    
    return _deepfake_detector

