"""
Resume Authenticity Detection - Model Training Module

This module handles training of multiple ML models:
- Logistic Regression
- Random Forest
- XGBoost
- Neural Network (MLP)

Includes K-Fold cross-validation and model comparison.

Author: ML Engineering Team
Date: February 28, 2026
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import StratifiedKFold, cross_validate
import xgboost as xgb
import joblib
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ModelTrainer:
    """
    Handles training of multiple ML models for resume authenticity detection.
    
    Attributes:
        models: Dictionary of model instances
        trained_models: Dictionary of trained model objects
        model_results: Dictionary storing performance metrics
    """
    
    def __init__(self, random_state: int = 42):
        """
        Initialize the model trainer with all classifiers.
        
        Args:
            random_state: Random state for reproducibility
        """
        self.random_state = random_state
        self.models = self._initialize_models()
        self.trained_models = {}
        self.model_results = {}
        
        logger.info(f"ModelTrainer initialized with {len(self.models)} models")
    
    def _initialize_models(self) -> Dict[str, Any]:
        """
        Initialize all machine learning models with optimized parameters.
        
        Returns:
            Dictionary of model instances
        """
        models = {
            'Logistic_Regression': LogisticRegression(
                max_iter=1000,
                random_state=self.random_state,
                n_jobs=-1,
                C=1.0,
                solver='lbfgs',
                multi_class='multinomial',
                class_weight='balanced'
            ),
            
            'Random_Forest': RandomForestClassifier(
                n_estimators=200,
                max_depth=20,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=self.random_state,
                n_jobs=-1,
                class_weight='balanced',
                max_features='sqrt'
            ),
            
            'XGBoost': xgb.XGBClassifier(
                n_estimators=200,
                max_depth=8,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=self.random_state,
                n_jobs=-1,
                eval_metric='mlogloss',
                use_label_encoder=False
            ),
            
            'Neural_Network': MLPClassifier(
                hidden_layer_sizes=(128, 64, 32),
                activation='relu',
                solver='adam',
                alpha=0.0001,
                batch_size=64,
                learning_rate='adaptive',
                learning_rate_init=0.001,
                max_iter=500,
                random_state=self.random_state,
                early_stopping=True,
                validation_fraction=0.1,
                n_iter_no_change=20
            )
        }
        
        logger.info("Models initialized:")
        for model_name in models.keys():
            logger.info(f"  - {model_name}")
        
        return models
    
    def train_model(
        self,
        model_name: str,
        X_train: np.ndarray,
        y_train: np.ndarray
    ) -> Any:
        """
        Train a single model.
        
        Args:
            model_name: Name of the model to train
            X_train: Training features
            y_train: Training labels
            
        Returns:
            Trained model object
            
        Raises:
            ValueError: If model_name is not recognized
        """
        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' not found. Available: {list(self.models.keys())}")
        
        logger.info(f"\nTraining {model_name}...")
        start_time = datetime.now()
        
        try:
            model = self.models[model_name]
            
            # Special handling for sparse matrices
            if hasattr(X_train, 'toarray'):
                logger.info(f"  Training data shape: {X_train.shape} (sparse)")
            else:
                logger.info(f"  Training data shape: {X_train.shape}")
            
            # Train the model
            model.fit(X_train, y_train)
            
            training_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"  Training completed in {training_time:.2f} seconds")
            
            # Store trained model
            self.trained_models[model_name] = model
            
            return model
            
        except Exception as e:
            logger.error(f"Error training {model_name}: {str(e)}")
            raise
    
    def train_all_models(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray
    ) -> Dict[str, Any]:
        """
        Train all models in the pipeline.
        
        Args:
            X_train: Training features
            y_train: Training labels
            
        Returns:
            Dictionary of trained models
        """
        logger.info("="*60)
        logger.info("TRAINING ALL MODELS")
        logger.info("="*60)
        
        for model_name in self.models.keys():
            try:
                self.train_model(model_name, X_train, y_train)
            except Exception as e:
                logger.error(f"Failed to train {model_name}: {str(e)}")
                continue
        
        logger.info(f"\nSuccessfully trained {len(self.trained_models)} models")
        return self.trained_models
    
    def cross_validate_model(
        self,
        model_name: str,
        X: np.ndarray,
        y: np.ndarray,
        cv_folds: int = 5
    ) -> Dict[str, Any]:
        """
        Perform stratified K-fold cross-validation on a model.
        
        Args:
            model_name: Name of the model
            X: Feature matrix
            y: Labels
            cv_folds: Number of folds for cross-validation
            
        Returns:
            Dictionary containing cross-validation results
        """
        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' not found")
        
        logger.info(f"\nPerforming {cv_folds}-fold cross-validation on {model_name}...")
        
        try:
            model = self.models[model_name]
            
            # Configure cross-validation
            cv = StratifiedKFold(
                n_splits=cv_folds,
                shuffle=True,
                random_state=self.random_state
            )
            
            # Perform cross-validation
            scoring = ['accuracy', 'precision_macro', 'recall_macro', 'f1_macro']
            cv_results = cross_validate(
                model, X, y,
                cv=cv,
                scoring=scoring,
                n_jobs=-1,
                return_train_score=False
            )
            
            # Calculate mean and std for each metric
            results = {
                'accuracy_mean': cv_results['test_accuracy'].mean(),
                'accuracy_std': cv_results['test_accuracy'].std(),
                'precision_mean': cv_results['test_precision_macro'].mean(),
                'precision_std': cv_results['test_precision_macro'].std(),
                'recall_mean': cv_results['test_recall_macro'].mean(),
                'recall_std': cv_results['test_recall_macro'].std(),
                'f1_mean': cv_results['test_f1_macro'].mean(),
                'f1_std': cv_results['test_f1_macro'].std(),
            }
            
            logger.info(f"  Accuracy: {results['accuracy_mean']:.4f} (+/- {results['accuracy_std']:.4f})")
            logger.info(f"  F1-Score: {results['f1_mean']:.4f} (+/- {results['f1_std']:.4f})")
            logger.info(f"  Precision: {results['precision_mean']:.4f} (+/- {results['precision_std']:.4f})")
            logger.info(f"  Recall: {results['recall_mean']:.4f} (+/- {results['recall_std']:.4f})")
            
            return results
            
        except Exception as e:
            logger.error(f"Error during cross-validation of {model_name}: {str(e)}")
            raise
    
    def cross_validate_all_models(
        self,
        X: np.ndarray,
        y: np.ndarray,
        cv_folds: int = 5
    ) -> pd.DataFrame:
        """
        Perform cross-validation on all models.
        
        Args:
            X: Feature matrix
            y: Labels
            cv_folds: Number of folds
            
        Returns:
            DataFrame with cross-validation results
        """
        logger.info("\n" + "="*60)
        logger.info(f"K-FOLD CROSS-VALIDATION (k={cv_folds})")
        logger.info("="*60)
        
        cv_results = {}
        
        for model_name in self.models.keys():
            try:
                results = self.cross_validate_model(model_name, X, y, cv_folds)
                cv_results[model_name] = results
            except Exception as e:
                logger.error(f"Failed cross-validation for {model_name}: {str(e)}")
                continue
        
        # Create DataFrame for easy comparison
        df_results = pd.DataFrame(cv_results).T
        df_results = df_results.round(4)
        
        logger.info("\n" + "="*60)
        logger.info("CROSS-VALIDATION SUMMARY")
        logger.info("="*60)
        logger.info("\n" + df_results.to_string())
        
        # Identify best model
        best_model = df_results['f1_mean'].idxmax()
        logger.info(f"\nBest Model (by F1-score): {best_model}")
        logger.info(f"  F1-Score: {df_results.loc[best_model, 'f1_mean']:.4f}")
        
        return df_results
    
    def save_model(
        self,
        model_name: str,
        save_dir: str = "./models"
    ) -> str:
        """
        Save a trained model to disk.
        
        Args:
            model_name: Name of the model to save
            save_dir: Directory to save the model
            
        Returns:
            Path to saved model
        """
        if model_name not in self.trained_models:
            raise ValueError(f"Model '{model_name}' has not been trained yet")
        
        try:
            os.makedirs(save_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{model_name}_{timestamp}.joblib"
            filepath = os.path.join(save_dir, filename)
            
            joblib.dump(self.trained_models[model_name], filepath)
            logger.info(f"Model saved: {filepath}")
            
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving model {model_name}: {str(e)}")
            raise
    
    def save_all_models(self, save_dir: str = "./models") -> Dict[str, str]:
        """
        Save all trained models to disk.
        
        Args:
            save_dir: Directory to save models
            
        Returns:
            Dictionary mapping model names to file paths
        """
        logger.info(f"\nSaving all trained models to {save_dir}...")
        
        saved_paths = {}
        for model_name in self.trained_models.keys():
            try:
                filepath = self.save_model(model_name, save_dir)
                saved_paths[model_name] = filepath
            except Exception as e:
                logger.error(f"Failed to save {model_name}: {str(e)}")
                continue
        
        logger.info(f"Saved {len(saved_paths)} models successfully")
        return saved_paths
    
    def load_model(self, filepath: str) -> Any:
        """
        Load a trained model from disk.
        
        Args:
            filepath: Path to the model file
            
        Returns:
            Loaded model object
        """
        try:
            model = joblib.load(filepath)
            logger.info(f"Model loaded from: {filepath}")
            return model
        except Exception as e:
            logger.error(f"Error loading model from {filepath}: {str(e)}")
            raise
    
    def get_model_parameters(self, model_name: str) -> Dict[str, Any]:
        """
        Get parameters of a model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Dictionary of model parameters
        """
        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' not found")
        
        model = self.models[model_name]
        return model.get_params()
    
    def get_all_model_parameters(self) -> Dict[str, Dict[str, Any]]:
        """
        Get parameters of all models.
        
        Returns:
            Dictionary mapping model names to their parameters
        """
        all_params = {}
        for model_name in self.models.keys():
            all_params[model_name] = self.get_model_parameters(model_name)
        
        return all_params


def create_model_comparison_table(results: Dict[str, Dict[str, float]]) -> pd.DataFrame:
    """
    Create a formatted comparison table for model results.
    
    Args:
        results: Dictionary containing model evaluation results
        
    Returns:
        Formatted pandas DataFrame
    """
    df = pd.DataFrame(results).T
    df = df.round(4)
    
    # Sort by F1-score
    if 'f1_macro' in df.columns:
        df = df.sort_values('f1_macro', ascending=False)
    
    return df


def identify_best_model(results: Dict[str, Dict[str, float]]) -> Tuple[str, Dict[str, float]]:
    """
    Identify the best performing model based on F1-score.
    
    Args:
        results: Dictionary containing model evaluation results
        
    Returns:
        Tuple of (best_model_name, best_model_metrics)
    """
    best_model_name = None
    best_f1_score = -1
    
    for model_name, metrics in results.items():
        f1_score = metrics.get('f1_macro', 0)
        if f1_score > best_f1_score:
            best_f1_score = f1_score
            best_model_name = model_name
    
    logger.info("\n" + "="*60)
    logger.info("BEST MODEL IDENTIFICATION")
    logger.info("="*60)
    logger.info(f"Best Model: {best_model_name}")
    logger.info(f"F1-Score: {best_f1_score:.4f}")
    logger.info("="*60)
    
    return best_model_name, results[best_model_name]


if __name__ == "__main__":
    logger.info("This module should be imported, not run directly.")
    logger.info("Example usage:")
    logger.info("  from train import ModelTrainer")
    logger.info("  trainer = ModelTrainer()")
    logger.info("  trainer.train_all_models(X_train, y_train)")
