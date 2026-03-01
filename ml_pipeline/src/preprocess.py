"""
Resume Authenticity Detection - Data Preprocessing Module

This module handles all data preprocessing tasks including:
- Data loading and validation
- Text cleaning and normalization
- Feature extraction using TF-IDF
- Train-test splitting with stratification

Author: ML Engineering Team
Date: February 28, 2026
"""

import logging
import re
import pandas as pd
import numpy as np
from typing import Tuple, Optional
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ResumePreprocessor:
    """
    Handles all preprocessing operations for resume text data.
    
    Attributes:
        tfidf_vectorizer: TF-IDF vectorizer for feature extraction
        label_encoder: Encoder for converting labels to numeric format
        lemmatizer: WordNet lemmatizer for text normalization
        stop_words: Set of English stopwords
    """
    
    def __init__(self, max_features: int = 5000):
        """
        Initialize the preprocessor with necessary components.
        
        Args:
            max_features: Maximum number of features for TF-IDF vectorization
        """
        self.max_features = max_features
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95
        )
        self.label_encoder = LabelEncoder()
        self.lemmatizer = None
        self.stop_words = None
        
        # Download required NLTK data
        self._download_nltk_resources()
        
        # Initialize NLTK components
        try:
            self.lemmatizer = WordNetLemmatizer()
            self.stop_words = set(stopwords.words('english'))
            logger.info("NLTK components initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing NLTK components: {str(e)}")
            raise
    
    def _download_nltk_resources(self):
        """Download required NLTK resources if not already present."""
        resources = ['stopwords', 'wordnet', 'punkt', 'omw-1.4', 'averaged_perceptron_tagger']
        for resource in resources:
            try:
                nltk.download(resource, quiet=True)
            except Exception as e:
                logger.warning(f"Could not download NLTK resource '{resource}': {str(e)}")
    
    def load_dataset(self, file_path: str) -> pd.DataFrame:
        """
        Load dataset from CSV file with validation.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Loaded DataFrame
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If required columns are missing
        """
        try:
            logger.info(f"Loading dataset from: {file_path}")
            df = pd.read_csv(file_path)
            
            # Validate required columns
            required_columns = ['resume_text', 'label']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            logger.info(f"Dataset loaded successfully. Shape: {df.shape}")
            logger.info(f"Columns: {list(df.columns)}")
            
            return df
            
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading dataset: {str(e)}")
            raise
    
    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing values in the dataset.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with handled missing values
        """
        logger.info("Handling missing values...")
        
        initial_shape = df.shape[0]
        
        # Check for missing values
        missing_counts = df.isnull().sum()
        if missing_counts.any():
            logger.warning(f"Missing values detected:\n{missing_counts[missing_counts > 0]}")
        
        # Remove rows with missing resume_text or label
        df = df.dropna(subset=['resume_text', 'label'])
        
        # Fill other missing values if any
        df = df.fillna('')
        
        final_shape = df.shape[0]
        removed_rows = initial_shape - final_shape
        
        if removed_rows > 0:
            logger.info(f"Removed {removed_rows} rows with missing critical values")
        
        return df
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text data.
        
        Performs:
        - Lowercasing
        - Special character removal
        - Stopword removal
        - Lemmatization
        
        Args:
            text: Input text string
            
        Returns:
            Cleaned text string
        """
        if not isinstance(text, str):
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Tokenization
        try:
            tokens = word_tokenize(text)
        except Exception:
            # Fallback to simple split if tokenization fails
            tokens = text.split()
        
        # Remove stopwords and lemmatize
        if self.lemmatizer and self.stop_words:
            tokens = [
                self.lemmatizer.lemmatize(word)
                for word in tokens
                if word not in self.stop_words and len(word) > 2
            ]
        
        return ' '.join(tokens)
    
    def preprocess_texts(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess all resume texts in the DataFrame.
        
        Args:
            df: Input DataFrame with resume_text column
            
        Returns:
            DataFrame with cleaned texts
        """
        logger.info("Preprocessing resume texts...")
        
        # Create a copy to avoid modifying the original
        df = df.copy()
        
        # Apply text cleaning
        total_resumes = len(df)
        logger.info(f"Cleaning {total_resumes} resume texts...")
        
        df['cleaned_text'] = df['resume_text'].apply(self.clean_text)
        
        # Remove empty texts after cleaning
        initial_count = len(df)
        df = df[df['cleaned_text'].str.strip() != '']
        final_count = len(df)
        
        if initial_count > final_count:
            logger.warning(f"Removed {initial_count - final_count} resumes with empty text after cleaning")
        
        logger.info(f"Text preprocessing completed for {final_count} resumes")
        
        return df
    
    def encode_labels(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Encode categorical labels to numeric format.
        
        Args:
            df: Input DataFrame with label column
            
        Returns:
            DataFrame with encoded labels
        """
        logger.info("Encoding labels...")
        
        df = df.copy()
        
        # Log unique labels
        unique_labels = df['label'].unique()
        logger.info(f"Unique labels found: {unique_labels}")
        
        # Encode labels
        df['label_encoded'] = self.label_encoder.fit_transform(df['label'])
        
        # Log encoding mapping
        label_mapping = {
            label: encoded
            for label, encoded in zip(
                self.label_encoder.classes_,
                range(len(self.label_encoder.classes_))
            )
        }
        logger.info(f"Label encoding mapping: {label_mapping}")
        
        return df
    
    def vectorize_text(
        self,
        train_texts: pd.Series,
        test_texts: Optional[pd.Series] = None
    ) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        Convert text to TF-IDF features.
        
        Args:
            train_texts: Training text data
            test_texts: Testing text data (optional)
            
        Returns:
            Tuple of (train_features, test_features)
        """
        logger.info(f"Vectorizing texts using TF-IDF (max_features={self.max_features})...")
        
        try:
            # Fit and transform training data
            X_train = self.tfidf_vectorizer.fit_transform(train_texts)
            logger.info(f"Training features shape: {X_train.shape}")
            
            # Transform test data if provided
            X_test = None
            if test_texts is not None:
                X_test = self.tfidf_vectorizer.transform(test_texts)
                logger.info(f"Testing features shape: {X_test.shape}")
            
            return X_train, X_test
            
        except Exception as e:
            logger.error(f"Error during vectorization: {str(e)}")
            raise
    
    def split_dataset(
        self,
        df: pd.DataFrame,
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """
        Split dataset into training and testing sets with stratification.
        
        Args:
            df: Input DataFrame
            test_size: Proportion of dataset for testing
            random_state: Random state for reproducibility
            
        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        logger.info(f"Splitting dataset (test_size={test_size}, stratified)...")
        
        X = df['cleaned_text']
        y = df['label_encoded']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_size,
            random_state=random_state,
            stratify=y
        )
        
        logger.info(f"Training samples: {len(X_train)}")
        logger.info(f"Testing samples: {len(X_test)}")
        
        # Log class distribution
        train_dist = y_train.value_counts().sort_index()
        test_dist = y_test.value_counts().sort_index()
        
        logger.info("Training set distribution:")
        for idx, count in train_dist.items():
            label_name = self.label_encoder.classes_[idx]
            logger.info(f"  {label_name}: {count} ({count/len(y_train)*100:.2f}%)")
        
        logger.info("Testing set distribution:")
        for idx, count in test_dist.items():
            label_name = self.label_encoder.classes_[idx]
            logger.info(f"  {label_name}: {count} ({count/len(y_test)*100:.2f}%)")
        
        return X_train, X_test, y_train, y_test
    
    def get_label_names(self) -> list:
        """
        Get the list of label names.
        
        Returns:
            List of label names
        """
        return list(self.label_encoder.classes_)
    
    def print_dataset_summary(self, df: pd.DataFrame):
        """
        Print comprehensive dataset summary.
        
        Args:
            df: Input DataFrame
        """
        logger.info("\n" + "="*50)
        logger.info("DATASET SUMMARY")
        logger.info("="*50)
        
        logger.info(f"\nTotal Records: {len(df)}")
        logger.info(f"Total Features after preprocessing: {len(df.columns)}")
        
        logger.info("\nLabel Distribution:")
        label_counts = df['label'].value_counts()
        for label, count in label_counts.items():
            percentage = (count / len(df)) * 100
            logger.info(f"  {label}: {count} ({percentage:.2f}%)")
        
        logger.info("\nText Statistics:")
        df['text_length'] = df['cleaned_text'].str.split().str.len()
        logger.info(f"  Average words per resume: {df['text_length'].mean():.2f}")
        logger.info(f"  Min words: {df['text_length'].min()}")
        logger.info(f"  Max words: {df['text_length'].max()}")
        logger.info(f"  Median words: {df['text_length'].median():.2f}")
        
        logger.info("\n" + "="*50)


def preprocess_pipeline(
    file_path: str,
    test_size: float = 0.2,
    max_features: int = 5000,
    random_state: int = 42
) -> dict:
    """
    Execute complete preprocessing pipeline.
    
    Args:
        file_path: Path to the dataset CSV file
        test_size: Proportion for test split
        max_features: Maximum TF-IDF features
        random_state: Random state for reproducibility
        
    Returns:
        Dictionary containing processed data and preprocessor
    """
    logger.info("Starting preprocessing pipeline...")
    
    try:
        # Initialize preprocessor
        preprocessor = ResumePreprocessor(max_features=max_features)
        
        # Load dataset
        df = preprocessor.load_dataset(file_path)
        
        # Handle missing values
        df = preprocessor.handle_missing_values(df)
        
        # Preprocess texts
        df = preprocessor.preprocess_texts(df)
        
        # Encode labels
        df = preprocessor.encode_labels(df)
        
        # Print summary
        preprocessor.print_dataset_summary(df)
        
        # Split dataset
        X_train, X_test, y_train, y_test = preprocessor.split_dataset(
            df, test_size=test_size, random_state=random_state
        )
        
        # Vectorize texts
        X_train_vec, X_test_vec = preprocessor.vectorize_text(X_train, X_test)
        
        logger.info("Preprocessing pipeline completed successfully!")
        
        return {
            'X_train': X_train_vec,
            'X_test': X_test_vec,
            'y_train': y_train,
            'y_test': y_test,
            'preprocessor': preprocessor,
            'label_names': preprocessor.get_label_names(),
            'raw_df': df
        }
        
    except Exception as e:
        logger.error(f"Error in preprocessing pipeline: {str(e)}")
        raise


if __name__ == "__main__":
    # Example usage
    logger.info("This module should be imported, not run directly.")
    logger.info("Example usage:")
    logger.info("  from preprocess import preprocess_pipeline")
    logger.info("  data = preprocess_pipeline('path/to/dataset.csv')")
