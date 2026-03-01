"""
Resume Authenticity Detection - ML Pipeline Package

This package provides a complete production-ready ML pipeline for
resume authenticity classification.

Modules:
    - preprocess: Data preprocessing and feature engineering
    - train: Model training and cross-validation
    - evaluate: Model evaluation and visualization
    - mlflow_logger: MLflow experiment tracking integration

Author: ML Engineering Team
Date: February 28, 2026
Version: 1.0.0
"""

__version__ = '1.0.0'
__author__ = 'ML Engineering Team'
__email__ = 'ml-team@university.edu'

# Import main classes for easy access
from .preprocess import ResumePreprocessor, preprocess_pipeline
from .train import ModelTrainer, create_model_comparison_table, identify_best_model
from .evaluate import ModelEvaluator
from .mlflow_logger import MLflowLogger, setup_mlflow_experiment

__all__ = [
    'ResumePreprocessor',
    'preprocess_pipeline',
    'ModelTrainer',
    'create_model_comparison_table',
    'identify_best_model',
    'ModelEvaluator',
    'MLflowLogger',
    'setup_mlflow_experiment'
]
