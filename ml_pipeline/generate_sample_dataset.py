"""
Resume Authenticity Detection - Sample Dataset Generator

This script generates a synthetic dataset for testing the ML pipeline.
Creates resumes with three categories: Authentic, Exaggerated, and Fake.

Author: ML Engineering Team
Date: February 28, 2026
"""

import pandas as pd
import random
import os
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResumeGenerator:
    """Generates synthetic resume data for testing."""
    
    def __init__(self):
        """Initialize the generator with templates and data."""
        
        # Skills databases
        self.skills_programming = [
            'Python', 'Java', 'JavaScript', 'C++', 'C#', 'Ruby', 'Go', 'Rust',
            'TypeScript', 'PHP', 'Swift', 'Kotlin', 'Scala', 'R', 'MATLAB'
        ]
        
        self.skills_frameworks = [
            'React', 'Angular', 'Vue.js', 'Django', 'Flask', 'FastAPI',
            'Spring Boot', 'Node.js', 'Express', 'TensorFlow', 'PyTorch',
            'scikit-learn', 'Pandas', 'NumPy'
        ]
        
        self.skills_tools = [
            'Git', 'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP',
            'Jenkins', 'CircleCI', 'Terraform', 'Ansible', 'MongoDB',
            'PostgreSQL', 'MySQL', 'Redis', 'Elasticsearch'
        ]
        
        self.skills_soft = [
            'Team Leadership', 'Project Management', 'Agile Methodologies',
            'Communication', 'Problem Solving', 'Critical Thinking',
            'Time Management', 'Collaboration'
        ]
        
        # Job titles
        self.job_titles = [
            'Software Engineer', 'Senior Developer', 'Data Scientist',
            'Machine Learning Engineer', 'Full Stack Developer',
            'Backend Engineer', 'Frontend Developer', 'DevOps Engineer',
            'Cloud Architect', 'System Administrator', 'QA Engineer',
            'Technical Lead', 'Software Architect'
        ]
        
        # Companies
        self.companies_real = [
            'Google', 'Microsoft', 'Amazon', 'Apple', 'Meta (Facebook)',
            'Netflix', 'Adobe', 'Salesforce', 'Oracle', 'IBM',
            'Intel', 'NVIDIA', 'Tesla', 'SpaceX', 'Uber'
        ]
        
        self.companies_fake = [
            'Gooogle Inc', 'Microsft Corporation', 'Amazn.com',
            'Aple Computer', 'FaceBook Technologies', 'Netflixx',
            'Goggle LLC', 'Mikerosoft', 'Appel Inc'
        ]
        
        # Universities
        self.universities_real = [
            'MIT', 'Stanford University', 'Harvard University',
            'UC Berkeley', 'Carnegie Mellon University', 'Caltech',
            'University of Washington', 'Cornell University',
            'Georgia Tech', 'University of Michigan'
        ]
        
        self.universities_fake = [
            'Stanford Online University', 'MIT Distance Learning',
            'Harvard Extension Online', 'UC Berkeley Correspondence',
            'International Tech University'
        ]
        
        # Degrees
        self.degrees = [
            'Bachelor of Science in Computer Science',
            'Master of Science in Computer Science',
            'Bachelor of Engineering in Software Engineering',
            'Master of Science in Data Science',
            'Bachelor of Technology in Information Technology',
            'MBA in Technology Management'
        ]
    
    def generate_authentic_resume(self) -> str:
        """Generate an authentic resume with realistic claims."""
        
        years_exp = random.randint(2, 15)
        skills = random.sample(self.skills_programming, k=random.randint(2, 4))
        skills += random.sample(self.skills_frameworks, k=random.randint(1, 3))
        skills += random.sample(self.skills_tools, k=random.randint(2, 4))
        
        job_title = random.choice(self.job_titles)
        company1 = random.choice(self.companies_real)
        company2 = random.choice([c for c in self.companies_real if c != company1])
        
        university = random.choice(self.universities_real)
        degree = random.choice(self.degrees)
        
        resume = f"""
{job_title} with {years_exp} years of professional experience in software development.

EDUCATION:
- {degree}, {university}, Graduated {2020 - years_exp}

PROFESSIONAL EXPERIENCE:

{job_title} at {company1}
- Developed and maintained scalable applications using {skills[0]} and {skills[1]}
- Collaborated with cross-functional teams to deliver high-quality software solutions
- Implemented CI/CD pipelines using {random.choice(self.skills_tools)}
- Mentored junior developers and conducted code reviews
Duration: {random.randint(2, 5)} years

Software Developer at {company2}
- Built full-stack applications using {random.choice(self.skills_frameworks)}
- Optimized database queries resulting in 30% performance improvement
- Participated in agile development processes and sprint planning
Duration: {random.randint(1, 3)} years

TECHNICAL SKILLS:
Programming Languages: {', '.join(skills[:4])}
Frameworks: {', '.join(random.sample(self.skills_frameworks, k=2))}
Tools & Technologies: {', '.join(random.sample(self.skills_tools, k=3))}

PROJECTS:
- E-commerce Platform: Developed using {random.choice(self.skills_frameworks)} and {random.choice(self.skills_programming)}
- Data Analytics Dashboard: Built with {random.choice(['Python', 'JavaScript'])} and visualization libraries

CERTIFICATIONS:
- AWS Certified Solutions Architect
- Professional Scrum Master (PSM I)
"""
        return resume.strip()
    
    def generate_exaggerated_resume(self) -> str:
        """Generate an exaggerated resume with inflated claims."""
        
        years_exp = random.randint(8, 25)  # Inflated experience
        
        # Too many skills to be realistic
        skills = random.sample(self.skills_programming, k=random.randint(8, 12))
        skills += random.sample(self.skills_frameworks, k=random.randint(6, 10))
        skills += random.sample(self.skills_tools, k=random.randint(8, 12))
        
        job_title = random.choice(['Senior Architect', 'Principal Engineer', 
                                   'Chief Technology Officer', 'VP of Engineering'])
        company1 = random.choice(self.companies_real)
        company2 = random.choice(self.companies_real)
        
        university = random.choice(self.universities_real)
        
        resume = f"""
{job_title} with {years_exp}+ years of extensive experience leading large-scale enterprise projects.

EDUCATION:
- PhD in Computer Science, {university} (Thesis on Advanced AI)
- Master of Science in Software Engineering, {random.choice(self.universities_real)}
- {random.choice(self.degrees)}, {random.choice(self.universities_real)}

PROFESSIONAL EXPERIENCE:

{job_title} at {company1}
- Led a team of 50+ engineers across multiple continents
- Architected and deployed mission-critical systems serving 100M+ users
- Achieved 99.999% uptime for critical infrastructure
- Reduced costs by 80% through innovative optimization strategies
- Single-handedly rewrote entire legacy codebase in 3 months
- Expert in ALL programming languages and frameworks
Duration: {random.randint(8, 12)} years

Technology Leader at {company2}
- Managed $50M+ technology budget
- Drove digital transformation initiatives across the organization
- Invented proprietary algorithms that increased efficiency by 300%
- Received multiple innovation awards and patents
Duration: {random.randint(5, 10)} years

TECHNICAL SKILLS:
Programming Languages (EXPERT in ALL): {', '.join(skills[:12])}
Frameworks (MASTERED): {', '.join(self.skills_frameworks)}
Tools & Technologies (ALL): {', '.join(self.skills_tools)}
Soft Skills: World-class leadership, Exceptional communication, Genius-level problem solving

ACHIEVEMENTS:
- Led projects worth over $100M
- Managed teams of 100+ people
- Delivered 50+ enterprise applications
- 99.99% project success rate
- Recognized as top 10 technologist globally by Forbes

CERTIFICATIONS (20+ certifications):
- AWS Certified Solutions Architect Professional
- Google Cloud Professional Architect
- Azure Solutions Architect Expert
- CISSP, PMP, Six Sigma Black Belt
- Multiple Ivy League executive programs
"""
        return resume.strip()
    
    def generate_fake_resume(self) -> str:
        """Generate a fake resume with false information."""
        
        years_exp = random.randint(15, 30)  # Unrealistic experience
        
        job_title = random.choice(['Founder and CEO', 'Chief Innovation Officer',
                                   'Global Technology Director', 'Senior Principal Consultant'])
        
        # Mix of real and fake companies
        company1 = random.choice(self.companies_fake)
        company2 = random.choice(self.companies_real) if random.random() > 0.5 else random.choice(self.companies_fake)
        
        university = random.choice(self.universities_fake)
        
        # Impossible or fake claims
        resume = f"""
{job_title} with {years_exp} years revolutionizing the technology industry worldwide.

EDUCATION:
- PhD in Artificial Intelligence and Quantum Computing, {university}
- Multiple honorary doctorates from prestigious institutions
- Studied under {random.choice(['Bill Gates', 'Steve Jobs', 'Elon Musk'])}

PROFESSIONAL EXPERIENCE:

{job_title}, {company1}
- Founded and scaled the company from 0 to $1B valuation in 6 months
- Invented the blockchain technology (before Bitcoin existed)
- Created the world's first AGI (Artificial General Intelligence)
- Developed revolutionary algorithms that broke all encryption standards
- Worked directly with {random.choice(['Mark Zuckerberg', 'Jeff Bezos', 'Sundar Pichai'])}
Duration: {random.randint(10, 15)} years

Co-Founder, {company2}
- Built the entire {random.choice(['Google', 'Amazon', 'Microsoft'])} infrastructure single-handedly
- Wrote 10 million+ lines of bug-free code
- Achieved impossible performance metrics (0ms latency globally)
- Patented time-travel algorithm for distributed systems
Duration: {random.randint(8, 12)} years

TECHNICAL SKILLS:
- Expert in over 100 programming languages (including ones I invented)
- Created several widely-used frameworks (React, Angular, TensorFlow - all me)
- Quantum computing pioneer
- AI/ML Guru with supernatural abilities

IMPOSSIBLE ACHIEVEMENTS:
- Hacked the Pentagon at age 12
- Declined multiple offers from CIA and NSA
- Featured on cover of Time Magazine as "Person of the Year"
- Nobel Prize nominee for technology innovation
- Youngest person to be inducted into Tech Hall of Fame
- Personal friend of every tech billionaire
- IQ of 210 (certified genius)

CERTIFICATIONS:
- Certified by organizations that don't exist
- Over 100 professional certifications
- Licensed by International Technology Council (non-existent)

SPEAKING ENGAGEMENTS:
- Keynote speaker at EVERY major tech conference
- TED Talk viewed 1 billion times
- Regular guest on major TV networks

PUBLICATIONS:
- Authored 50+ books on technology (all bestsellers)
- Published 200+ research papers in top journals
- Created technologies used by everyone on Earth
"""
        return resume.strip()
    
    def generate_dataset(self, n_samples: int = 1000, output_file: str = None) -> pd.DataFrame:
        """
        Generate a complete dataset with balanced classes.
        
        Args:
            n_samples: Total number of samples to generate
            output_file: Path to save the CSV file
            
        Returns:
            DataFrame with resume_text and label columns
        """
        logger.info(f"Generating dataset with {n_samples} samples...")
        
        # Calculate samples per class (balanced)
        samples_per_class = n_samples // 3
        remaining = n_samples % 3
        
        resumes = []
        labels = []
        
        # Generate Authentic resumes
        logger.info(f"Generating {samples_per_class + (1 if remaining > 0 else 0)} Authentic resumes...")
        for _ in range(samples_per_class + (1 if remaining > 0 else 0)):
            resumes.append(self.generate_authentic_resume())
            labels.append('Authentic')
        
        # Generate Exaggerated resumes
        logger.info(f"Generating {samples_per_class + (1 if remaining > 1 else 0)} Exaggerated resumes...")
        for _ in range(samples_per_class + (1 if remaining > 1 else 0)):
            resumes.append(self.generate_exaggerated_resume())
            labels.append('Exaggerated')
        
        # Generate Fake resumes
        logger.info(f"Generating {samples_per_class} Fake resumes...")
        for _ in range(samples_per_class):
            resumes.append(self.generate_fake_resume())
            labels.append('Fake')
        
        # Create DataFrame
        df = pd.DataFrame({
            'resume_text': resumes,
            'label': labels
        })
        
        # Shuffle the dataset
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)
        
        # Save to file
        if output_file:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            df.to_csv(output_file, index=False)
            logger.info(f"Dataset saved to: {output_file}")
        
        # Print statistics
        logger.info("\nDataset Statistics:")
        logger.info(f"Total Samples: {len(df)}")
        logger.info("\nClass Distribution:")
        for label, count in df['label'].value_counts().items():
            percentage = (count / len(df)) * 100
            logger.info(f"  {label}: {count} ({percentage:.2f}%)")
        
        logger.info("\nSample Resume (Authentic):")
        logger.info(df[df['label'] == 'Authentic'].iloc[0]['resume_text'][:300] + "...")
        
        return df


def main():
    """Main function to generate sample dataset."""
    
    logger.info("="*80)
    logger.info("RESUME AUTHENTICITY DETECTION - SAMPLE DATASET GENERATOR")
    logger.info("="*80)
    
    # Configuration
    n_samples = 1000
    output_file = './data/resume_dataset.csv'
    
    # Generate dataset
    generator = ResumeGenerator()
    df = generator.generate_dataset(n_samples=n_samples, output_file=output_file)
    
    logger.info("\n" + "="*80)
    logger.info("DATASET GENERATION COMPLETED SUCCESSFULLY")
    logger.info("="*80)
    logger.info(f"File: {output_file}")
    logger.info(f"Total Samples: {len(df)}")
    logger.info("\nYou can now run the ML pipeline:")
    logger.info(f"  python main.py --dataset {output_file}")
    logger.info("="*80)


if __name__ == "__main__":
    main()
