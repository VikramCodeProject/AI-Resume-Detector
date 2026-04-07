"""
LLM Reasoning Layer Service
Contextual explanation generation for resume verification results

Enterprise Features:
- OpenAI GPT integration
- Open-source LLM fallback (HuggingFace)
- Structured reasoning templates
- Risk assessment narratives
- Actionable recommendations
"""

import logging
from typing import Dict, List, Optional
from datetime import UTC, datetime
import os
import json

from utils.time_utils import utc_now_iso

# OpenAI (primary)
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("openai package not available")

# HuggingFace (fallback)
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False
    logging.warning("transformers not available")

logger = logging.getLogger(__name__)


class LLMReasoningService:
    """
    Generate human-readable explanations for verification results
    
    Capabilities:
    - Contextual analysis
    - Risk narrative generation
    - Timeline anomaly explanation
    - Skill-GitHub mismatch reasoning
    - Certificate authenticity explanation
    """
    
    # LLM configuration
    DEFAULT_MODEL_OPENAI = "gpt-4o-mini"  # Cost-effective for production
    DEFAULT_MODEL_HUGGINGFACE = "mistralai/Mistral-7B-Instruct-v0.2"
    MAX_TOKENS = 500
    TEMPERATURE = 0.7
    
    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        use_openai: bool = True,
        model_name: Optional[str] = None
    ):
        """
        Initialize LLM service
        
        Args:
            openai_api_key: OpenAI API key (optional)
            use_openai: Use OpenAI if available (else HuggingFace)
            model_name: Override default model
        """
        self.api_key = openai_api_key or os.getenv('OPENAI_API_KEY', '')
        self.use_openai = use_openai and OPENAI_AVAILABLE and self.api_key
        
        if self.use_openai:
            openai.api_key = self.api_key
            self.model = model_name or self.DEFAULT_MODEL_OPENAI
            logger.info(f"LLM service initialized with OpenAI: {self.model}")
        elif HUGGINGFACE_AVAILABLE:
            self.model = model_name or self.DEFAULT_MODEL_HUGGINGFACE
            logger.info(f"LLM service initializing HuggingFace model: {self.model}")
            
            # Initialize HuggingFace pipeline (lazy loading)
            self.tokenizer = None
            self.llm_pipeline = None
            logger.info("HuggingFace model will be loaded on first use")
        else:
            logger.warning("No LLM backend available - using template-based reasoning")
            self.use_openai = False
    
    def _ensure_huggingface_loaded(self):
        """Lazy load HuggingFace model"""
        if self.llm_pipeline is None and HUGGINGFACE_AVAILABLE:
            logger.info("Loading HuggingFace model...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model)
            self.llm_pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_new_tokens=self.MAX_TOKENS,
                temperature=self.TEMPERATURE,
                do_sample=True
            )
            logger.info("HuggingFace model loaded successfully")
    
    async def generate_verification_explanation(
        self,
        resume_data: Dict,
        github_analysis: Optional[Dict] = None,
        certificate_analysis: Optional[Dict] = None,
        deepfake_analysis: Optional[Dict] = None,
        ml_prediction: Optional[Dict] = None,
        timeline_anomalies: Optional[List[str]] = None
    ) -> Dict:
        """
        Generate comprehensive explanation for verification results
        
        Args:
            resume_data: Parsed resume information
            github_analysis: GitHub verification results
            certificate_analysis: OCR certificate results
            deepfake_analysis: AI-generated text detection
            ml_prediction: ML model classification
            timeline_anomalies: Detected timeline issues
        
        Returns:
            Structured explanation with risk assessment
        """
        try:
            # Build context summary
            context = self._build_context(
                resume_data,
                github_analysis,
                certificate_analysis,
                deepfake_analysis,
                ml_prediction,
                timeline_anomalies
            )
            
            # Generate explanation using LLM
            if self.use_openai:
                explanation = await self._generate_with_openai(context)
            elif HUGGINGFACE_AVAILABLE:
                self._ensure_huggingface_loaded()
                explanation = self._generate_with_huggingface(context)
            else:
                explanation = self._generate_with_template(context)
            
            # Compute final trust score
            final_score = self._compute_final_trust_score(
                github_analysis,
                certificate_analysis,
                deepfake_analysis,
                ml_prediction
            )
            
            # Determine risk level
            risk_level = self._determine_risk_level(final_score)
            
            # Build response
            result = {
                'final_trust_score': final_score,
                'risk_level': risk_level,
                'explanation': explanation,
                'key_findings': self._extract_key_findings(context),
                'red_flags': self._extract_red_flags(context),
                'green_flags': self._extract_green_flags(context),
                'recommendation': self._generate_recommendation(final_score, risk_level),
                'generated_at': utc_now_iso(),
                'reasoning_engine': 'OpenAI' if self.use_openai else 'HuggingFace' if HUGGINGFACE_AVAILABLE else 'Template'
            }
            
            logger.info(f"LLM explanation generated: trust_score={final_score:.2f}, risk={risk_level}")
            return result
            
        except Exception as e:
            logger.exception(f"LLM reasoning error: {str(e)}")
            return self._error_response(str(e))
    
    def _build_context(
        self,
        resume_data: Dict,
        github_analysis: Optional[Dict],
        certificate_analysis: Optional[Dict],
        deepfake_analysis: Optional[Dict],
        ml_prediction: Optional[Dict],
        timeline_anomalies: Optional[List[str]]
    ) -> Dict:
        """Build structured context for LLM prompt"""
        context = {
            'candidate_name': resume_data.get('name', 'Unknown'),
            'claimed_experience_years': resume_data.get('experience_years', 0),
            'claimed_skills': resume_data.get('skills', []),
            'education': resume_data.get('education', []),
            'employment_history': resume_data.get('employment', []),
        }
        
        # GitHub analysis
        if github_analysis:
            context['github'] = {
                'score': github_analysis.get('github_authenticity_score', 0),
                'repo_count': github_analysis.get('metrics', {}).get('public_repos', 0),
                'languages': github_analysis.get('metrics', {}).get('top_languages', []),
                'activity_days': github_analysis.get('metrics', {}).get('days_since_last_activity'),
                'risk_level': github_analysis.get('risk_level', 'Unknown')
            }
        
        # Certificate analysis
        if certificate_analysis:
            context['certificate'] = {
                'valid': certificate_analysis.get('certificate_valid', False),
                'score': certificate_analysis.get('authenticity_score', 0),
                'issuer': certificate_analysis.get('extracted_data', {}).get('issuer'),
                'duplicate': certificate_analysis.get('duplicate_detected', False),
                'risk_level': certificate_analysis.get('risk_level', 'Unknown')
            }
        
        # Deepfake analysis
        if deepfake_analysis:
            context['deepfake'] = {
                'ai_generated_probability': deepfake_analysis.get('ai_generated_probability', 0),
                'flag': deepfake_analysis.get('deepfake_flag', False),
                'stylometric_risk': deepfake_analysis.get('stylometric_risk', 0)
            }
        
        # ML prediction
        if ml_prediction:
            context['ml_prediction'] = {
                'classification': ml_prediction.get('classification', 'unknown'),
                'confidence': ml_prediction.get('confidence', 0)
            }
        
        # Timeline anomalies
        if timeline_anomalies:
            context['timeline_issues'] = timeline_anomalies
        
        return context
    
    async def _generate_with_openai(self, context: Dict) -> str:
        """Generate explanation using OpenAI GPT"""
        prompt = self._build_prompt(context)
        
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert AI Resume Auditor. Analyze verification data and provide clear, actionable explanations about resume authenticity. Be professional, specific, and highlight both concerns and positive indicators."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.MAX_TOKENS,
                temperature=self.TEMPERATURE
            )
            
            explanation = response.choices[0].message.content.strip()
            return explanation
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._generate_with_template(context)
    
    def _generate_with_huggingface(self, context: Dict) -> str:
        """Generate explanation using HuggingFace model"""
        prompt = self._build_prompt(context)
        
        try:
            # Generate with HuggingFace pipeline
            result = self.llm_pipeline(
                prompt,
                max_new_tokens=self.MAX_TOKENS,
                temperature=self.TEMPERATURE,
                do_sample=True,
                top_p=0.9
            )
            
            explanation = result[0]['generated_text']
            
            # Extract only the generated part (after prompt)
            if prompt in explanation:
                explanation = explanation.split(prompt)[1].strip()
            
            return explanation
            
        except Exception as e:
            logger.error(f"HuggingFace generation error: {e}")
            return self._generate_with_template(context)
    
    def _generate_with_template(self, context: Dict) -> str:
        """Generate explanation using templates (fallback)"""
        sections = []
        
        # Overall assessment
        final_score = self._compute_final_trust_score(
            context.get('github'),
            context.get('certificate'),
            context.get('deepfake'),
            context.get('ml_prediction')
        )
        
        if final_score >= 80:
            sections.append(f"The resume for {context['candidate_name']} shows strong authenticity indicators.")
        elif final_score >= 60:
            sections.append(f"The resume for {context['candidate_name']} has moderate authenticity with some concerns.")
        elif final_score >= 40:
            sections.append(f"The resume for {context['candidate_name']} raises several authenticity concerns.")
        else:
            sections.append(f"⚠️ The resume for {context['candidate_name']} has significant authenticity issues.")
        
        # GitHub analysis
        if 'github' in context:
            gh = context['github']
            if gh['score'] >= 70:
                sections.append(f"GitHub profile shows strong evidence with {gh['repo_count']} public repositories and recent activity in {', '.join(gh['languages'][:3])}.")
            elif gh['score'] >= 40:
                sections.append(f"GitHub profile has limited activity ({gh['repo_count']} repos) and may not fully support claimed skills.")
            else:
                sections.append(f"⚠️ GitHub profile shows minimal activity or does not match claimed technical skills.")
        
        # Certificate analysis
        if 'certificate' in context:
            cert = context['certificate']
            if cert['valid']:
                sections.append(f"Certificate from {cert['issuer']} appears authentic.")
            elif cert['duplicate']:
                sections.append(f"⚠️ Certificate appears in multiple submissions - possible duplication or forgery.")
            else:
                sections.append(f"⚠️ Certificate validation failed - issuer or authenticity concerns.")
        
        # Deepfake detection
        if 'deepfake' in context:
            df = context['deepfake']
            if df['flag']:
                sections.append(f"⚠️ Resume text shows signs of AI generation (probability: {df['ai_generated_probability']:.1%}).")
        
        # Timeline issues
        if 'timeline_issues' in context and context['timeline_issues']:
            sections.append(f"Timeline inconsistencies detected: {'; '.join(context['timeline_issues'][:2])}.")
        
        return ' '.join(sections)
    
    def _build_prompt(self, context: Dict) -> str:
        """Build LLM prompt from context"""
        prompt_parts = [
            f"Analyze this resume verification data and provide a clear explanation:\n",
            f"Candidate: {context['candidate_name']}",
            f"Claimed Experience: {context['claimed_experience_years']} years",
            f"Skills: {', '.join(context['claimed_skills'][:5])}\n"
        ]
        
        if 'github' in context:
            gh = context['github']
            prompt_parts.append(
                f"GitHub Analysis:\n"
                f"- Authenticity Score: {gh['score']:.1f}/100\n"
                f"- Repositories: {gh['repo_count']}\n"
                f"- Languages: {', '.join(gh['languages'])}\n"
                f"- Days Since Activity: {gh['activity_days']}\n"
            )
        
        if 'certificate' in context:
            cert = context['certificate']
            prompt_parts.append(
                f"Certificate Verification:\n"
                f"- Valid: {cert['valid']}\n"
                f"- Issuer: {cert['issuer']}\n"
                f"- Duplicate Detected: {cert['duplicate']}\n"
            )
        
        if 'deepfake' in context:
            df = context['deepfake']
            prompt_parts.append(
                f"AI-Generated Content Detection:\n"
                f"- AI Probability: {df['ai_generated_probability']:.1%}\n"
                f"- Flagged: {df['flag']}\n"
            )
        
        if 'timeline_issues' in context:
            prompt_parts.append(
                f"Timeline Issues:\n{chr(10).join('- ' + issue for issue in context['timeline_issues'])}\n"
            )
        
        prompt_parts.append(
            "\nProvide a professional 3-4 sentence explanation of authenticity concerns and recommendations."
        )
        
        return '\n'.join(prompt_parts)
    
    def _compute_final_trust_score(
        self,
        github_analysis: Optional[Dict],
        certificate_analysis: Optional[Dict],
        deepfake_analysis: Optional[Dict],
        ml_prediction: Optional[Dict]
    ) -> float:
        """Compute weighted final trust score"""
        score_components = []
        
        # GitHub (30% weight)
        if github_analysis:
            github_score = github_analysis.get('github_authenticity_score', 0)
            score_components.append(github_score * 0.30)
        
        # Certificate (25% weight)
        if certificate_analysis:
            cert_score = certificate_analysis.get('authenticity_score', 0)
            score_components.append(cert_score * 0.25)
        
        # Deepfake detection (20% weight)
        if deepfake_analysis:
            ai_prob = deepfake_analysis.get('ai_generated_probability', 0)
            # Invert: higher AI probability = lower score
            deepfake_score = (1.0 - ai_prob) * 100
            score_components.append(deepfake_score * 0.20)
        
        # ML prediction (25% weight)
        if ml_prediction:
            classification = ml_prediction.get('classification', '').lower()
            if classification == 'verified':
                ml_score = 90
            elif classification == 'doubtful':
                ml_score = 50
            elif classification == 'fake':
                ml_score = 10
            else:
                ml_score = 50
            
            score_components.append(ml_score * 0.25)
        
        # Calculate weighted average
        if score_components:
            final_score = sum(score_components)
        else:
            final_score = 50.0  # Neutral if no data
        
        return round(min(100.0, max(0.0, final_score)), 2)
    
    def _determine_risk_level(self, score: float) -> str:
        """Determine risk level from trust score"""
        if score >= 80:
            return "Low"
        elif score >= 60:
            return "Medium"
        elif score >= 40:
            return "High"
        else:
            return "Critical"
    
    def _extract_key_findings(self, context: Dict) -> List[str]:
        """Extract key findings from analysis"""
        findings = []
        
        if 'github' in context:
            gh = context['github']
            findings.append(f"GitHub: {gh['repo_count']} repos, {gh['risk_level']} risk")
        
        if 'certificate' in context:
            cert = context['certificate']
            findings.append(f"Certificate: {'Valid' if cert['valid'] else 'Invalid'}")
        
        if 'ml_prediction' in context:
            ml = context['ml_prediction']
            findings.append(f"ML Classification: {ml['classification'].title()}")
        
        return findings
    
    def _extract_red_flags(self, context: Dict) -> List[str]:
        """Extract red flags (concerns)"""
        red_flags = []
        
        if 'github' in context and context['github']['risk_level'] in ['High', 'Critical']:
            red_flags.append("GitHub activity does not match claimed experience")
        
        if 'certificate' in context:
            if context['certificate'].get('duplicate'):
                red_flags.append("Certificate ID found in multiple submissions")
            if not context['certificate'].get('valid'):
                red_flags.append("Certificate authenticity could not be verified")
        
        if 'deepfake' in context and context['deepfake'].get('flag'):
            red_flags.append("AI-generated content detected in resume text")
        
        if 'timeline_issues' in context and context['timeline_issues']:
            red_flags.extend(context['timeline_issues'][:2])
        
        return red_flags
    
    def _extract_green_flags(self, context: Dict) -> List[str]:
        """Extract green flags (positive indicators)"""
        green_flags = []
        
        if 'github' in context:
            gh = context['github']
            if gh['repo_count'] >= 10:
                green_flags.append(f"Active GitHub presence with {gh['repo_count']} repositories")
            if gh['activity_days'] is not None and gh['activity_days'] < 30:
                green_flags.append("Recent GitHub activity (within 30 days)")
        
        if 'certificate' in context and context['certificate'].get('valid'):
            green_flags.append("Valid certificate from recognized issuer")
        
        if 'ml_prediction' in context:
            if context['ml_prediction'].get('classification') == 'verified':
                green_flags.append("ML model classified as authentic")
        
        return green_flags
    
    def _generate_recommendation(self, final_score: float, risk_level: str) -> str:
        """Generate hiring recommendation"""
        if final_score >= 80:
            return "PROCEED - Strong authenticity indicators. Candidate profile verified."
        elif final_score >= 60:
            return "PROCEED WITH CAUTION - Some concerns identified. Recommend additional reference checks."
        elif final_score >= 40:
            return "REVIEW REQUIRED - Significant concerns detected. Manual verification recommended."
        else:
            return "⚠️ HIGH RISK - Multiple authenticity issues. Recommend detailed background check or rejection."
    
    def _error_response(self, error_message: str) -> Dict:
        """Generate error response"""
        return {
            'final_trust_score': 50.0,
            'risk_level': 'Unknown',
            'explanation': f"Unable to generate complete analysis: {error_message}",
            'key_findings': [],
            'red_flags': ["Analysis incomplete due to error"],
            'green_flags': [],
            'recommendation': "Manual review required due to analysis error",
            'generated_at': utc_now_iso()
        }


# Singleton instance
_llm_service: Optional[LLMReasoningService] = None

def get_llm_service(
    openai_api_key: Optional[str] = None,
    use_openai: bool = True,
    model_name: Optional[str] = None
) -> LLMReasoningService:
    """Get or create LLM reasoning service instance"""
    global _llm_service
    
    if _llm_service is None:
        _llm_service = LLMReasoningService(openai_api_key, use_openai, model_name)
    
    return _llm_service

