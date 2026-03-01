"""
Resume Authenticity Detection - MLflow Experiment Tracking Module

This module handles integration with MLflow for experiment tracking:
- Parameter logging
- Metric logging
- Artifact logging (models, plots, reports)
- Model registry

Author: ML Engineering Team
Date: February 28, 2026
"""

import logging
import mlflow
import mlflow.sklearn
import mlflow.xgboost
from typing import Dict, Any, Optional, List
import numpy as np
import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MLflowLogger:
    """
    Handles all MLflow experiment tracking and logging operations.
    
    Attributes:
        experiment_name: Name of the MLflow experiment
        tracking_uri: URI of the MLflow tracking server
        run_id: Current run ID
    """
    
    def __init__(
        self,
        experiment_name: str = "Resume_Authenticity_Experiment",
        tracking_uri: Optional[str] = None
    ):
        """
        Initialize MLflow logger with experiment configuration.
        
        Args:
            experiment_name: Name of the experiment
            tracking_uri: MLflow tracking server URI (None for local)
        """
        self.experiment_name = experiment_name
        self.tracking_uri = tracking_uri or "file:./mlruns"
        self.run_id = None
        
        # Set tracking URI
        mlflow.set_tracking_uri(self.tracking_uri)
        
        # Create or get experiment
        try:
            experiment = mlflow.get_experiment_by_name(experiment_name)
            if experiment is None:
                self.experiment_id = mlflow.create_experiment(experiment_name)
                logger.info(f"Created new experiment: {experiment_name}")
            else:
                self.experiment_id = experiment.experiment_id
                logger.info(f"Using existing experiment: {experiment_name}")
            
            mlflow.set_experiment(experiment_name)
            
        except Exception as e:
            logger.error(f"Error setting up MLflow experiment: {str(e)}")
            raise
        
        logger.info(f"MLflow Logger initialized")
        logger.info(f"  Experiment: {experiment_name}")
        logger.info(f"  Tracking URI: {self.tracking_uri}")
    
    def start_run(
        self,
        run_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Start a new MLflow run.
        
        Args:
            run_name: Name for the run
            tags: Dictionary of tags to add to the run
            
        Returns:
            Run ID
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            run_name = run_name or f"run_{timestamp}"
            
            mlflow.start_run(run_name=run_name)
            self.run_id = mlflow.active_run().info.run_id
            
            # Add default tags
            default_tags = {
                "project": "Resume_Authenticity_Detection",
                "framework": "scikit-learn",
                "timestamp": timestamp
            }
            
            if tags:
                default_tags.update(tags)
            
            mlflow.set_tags(default_tags)
            
            logger.info(f"Started MLflow run: {run_name} (ID: {self.run_id})")
            return self.run_id
            
        except Exception as e:
            logger.error(f"Error starting MLflow run: {str(e)}")
            raise
    
    def end_run(self):
        """End the current MLflow run."""
        try:
            if mlflow.active_run():
                mlflow.end_run()
                logger.info(f"Ended MLflow run: {self.run_id}")
                self.run_id = None
        except Exception as e:
            logger.error(f"Error ending MLflow run: {str(e)}")
    
    def log_parameters(self, params: Dict[str, Any]):
        """
        Log parameters to MLflow.
        
        Args:
            params: Dictionary of parameters
        """
        try:
            # Filter out complex objects
            simple_params = {}
            for key, value in params.items():
                if isinstance(value, (int, float, str, bool)) or value is None:
                    simple_params[key] = value
                elif isinstance(value, (list, tuple)) and len(value) < 10:
                    simple_params[key] = str(value)
            
            mlflow.log_params(simple_params)
            logger.info(f"Logged {len(simple_params)} parameters to MLflow")
            
        except Exception as e:
            logger.error(f"Error logging parameters: {str(e)}")
    
    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None):
        """
        Log metrics to MLflow.
        
        Args:
            metrics: Dictionary of metrics
            step: Optional step number
        """
        try:
            # Filter out non-numeric values
            numeric_metrics = {
                k: float(v) for k, v in metrics.items()
                if isinstance(v, (int, float, np.number)) and not np.isnan(v)
            }
            
            if step is not None:
                for key, value in numeric_metrics.items():
                    mlflow.log_metric(key, value, step=step)
            else:
                mlflow.log_metrics(numeric_metrics)
            
            logger.info(f"Logged {len(numeric_metrics)} metrics to MLflow")
            
        except Exception as e:
            logger.error(f"Error logging metrics: {str(e)}")
    
    def log_artifact(self, artifact_path: str, artifact_type: str = "general"):
        """
        Log an artifact (file) to MLflow.
        
        Args:
            artifact_path: Path to the artifact file
            artifact_type: Type of artifact for organization
        """
        try:
            if os.path.exists(artifact_path):
                mlflow.log_artifact(artifact_path, artifact_path=artifact_type)
                logger.info(f"Logged artifact: {artifact_path}")
            else:
                logger.warning(f"Artifact not found: {artifact_path}")
        except Exception as e:
            logger.error(f"Error logging artifact {artifact_path}: {str(e)}")
    
    def log_model(
        self,
        model: Any,
        model_name: str,
        signature: Optional[Any] = None,
        input_example: Optional[Any] = None
    ):
        """
        Log a trained model to MLflow.
        
        Args:
            model: Trained model object
            model_name: Name for the model
            signature: Model signature (optional)
            input_example: Example input (optional)
        """
        try:
            # Determine the appropriate logging function based on model type
            model_type = type(model).__name__
            
            if 'XGB' in model_type:
                mlflow.xgboost.log_model(
                    model,
                    artifact_path=model_name,
                    signature=signature,
                    input_example=input_example
                )
            else:
                mlflow.sklearn.log_model(
                    model,
                    artifact_path=model_name,
                    signature=signature,
                    input_example=input_example
                )
            
            logger.info(f"Logged model: {model_name} ({model_type})")
            
        except Exception as e:
            logger.error(f"Error logging model {model_name}: {str(e)}")
    
    def log_confusion_matrix(
        self,
        confusion_matrix: np.ndarray,
        model_name: str,
        label_names: List[str]
    ):
        """
        Log confusion matrix as an artifact.
        
        Args:
            confusion_matrix: Confusion matrix array
            model_name: Name of the model
            label_names: List of class labels
        """
        try:
            # Create confusion matrix plot
            import seaborn as sns
            plt.figure(figsize=(10, 8))
            sns.heatmap(
                confusion_matrix,
                annot=True,
                fmt='d',
                cmap='Blues',
                xticklabels=label_names,
                yticklabels=label_names
            )
            plt.title(f'Confusion Matrix - {model_name}')
            plt.ylabel('True Label')
            plt.xlabel('Predicted Label')
            
            # Save to temporary file
            temp_path = f"temp_cm_{model_name}.png"
            plt.savefig(temp_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            # Log as artifact
            self.log_artifact(temp_path, "confusion_matrices")
            
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            logger.info(f"Logged confusion matrix for {model_name}")
            
        except Exception as e:
            logger.error(f"Error logging confusion matrix: {str(e)}")
    
    def log_classification_report(
        self,
        report: Dict[str, Any],
        model_name: str
    ):
        """
        Log classification report as text artifact.
        
        Args:
            report: Classification report dictionary
            model_name: Name of the model
        """
        try:
            # Convert report to formatted text
            report_text = f"Classification Report - {model_name}\n"
            report_text += "=" * 60 + "\n\n"
            
            for label, metrics in report.items():
                if isinstance(metrics, dict):
                    report_text += f"{label}:\n"
                    for metric_name, value in metrics.items():
                        if metric_name != 'support':
                            report_text += f"  {metric_name}: {value:.4f}\n"
                        else:
                            report_text += f"  {metric_name}: {int(value)}\n"
                    report_text += "\n"
            
            # Save to temporary file
            temp_path = f"temp_report_{model_name}.txt"
            with open(temp_path, 'w') as f:
                f.write(report_text)
            
            # Log as artifact
            self.log_artifact(temp_path, "classification_reports")
            
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            logger.info(f"Logged classification report for {model_name}")
            
        except Exception as e:
            logger.error(f"Error logging classification report: {str(e)}")
    
    def log_model_experiment(
        self,
        model: Any,
        model_name: str,
        params: Dict[str, Any],
        metrics: Dict[str, float],
        confusion_matrix: Optional[np.ndarray] = None,
        classification_report: Optional[Dict[str, Any]] = None,
        label_names: Optional[List[str]] = None,
        artifacts: Optional[List[str]] = None
    ):
        """
        Log complete model experiment with all associated data.
        
        Args:
            model: Trained model
            model_name: Name of the model
            params: Model parameters
            metrics: Evaluation metrics
            confusion_matrix: Confusion matrix array
            classification_report: Classification report
            label_names: Class label names
            artifacts: List of artifact file paths
        """
        try:
            # Start a new run for this model
            run_name = f"{model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.start_run(run_name=run_name, tags={'model_type': model_name})
            
            # Log parameters
            self.log_parameters(params)
            
            # Log metrics
            self.log_metrics(metrics)
            
            # Log model
            self.log_model(model, model_name)
            
            # Log confusion matrix if provided
            if confusion_matrix is not None and label_names is not None:
                self.log_confusion_matrix(confusion_matrix, model_name, label_names)
            
            # Log classification report if provided
            if classification_report is not None:
                self.log_classification_report(classification_report, model_name)
            
            # Log additional artifacts
            if artifacts:
                for artifact_path in artifacts:
                    self.log_artifact(artifact_path)
            
            # End run
            self.end_run()
            
            logger.info(f"Completed logging experiment for {model_name}")
            
        except Exception as e:
            logger.error(f"Error logging model experiment: {str(e)}")
            self.end_run()  # Ensure run is ended even on error
    
    def log_dataset_info(self, dataset_info: Dict[str, Any]):
        """
        Log dataset information and statistics.
        
        Args:
            dataset_info: Dictionary containing dataset information
        """
        try:
            # Convert to parameters (MLflow doesn't directly support dicts)
            for key, value in dataset_info.items():
                if isinstance(value, (int, float, str, bool)):
                    mlflow.log_param(f"dataset_{key}", value)
            
            logger.info("Logged dataset information")
            
        except Exception as e:
            logger.error(f"Error logging dataset info: {str(e)}")
    
    def compare_runs(self, metric_name: str = "f1_macro") -> pd.DataFrame:
        """
        Compare all runs in the experiment based on a metric.
        
        Args:
            metric_name: Metric to use for comparison
            
        Returns:
            DataFrame with run comparison
        """
        try:
            # Search for all runs in the experiment
            runs = mlflow.search_runs(
                experiment_ids=[self.experiment_id],
                order_by=[f"metrics.{metric_name} DESC"]
            )
            
            logger.info(f"\nExperiment Run Comparison (sorted by {metric_name}):")
            logger.info("\n" + runs.to_string())
            
            return runs
            
        except Exception as e:
            logger.error(f"Error comparing runs: {str(e)}")
            return pd.DataFrame()
    
    def get_best_run(self, metric_name: str = "f1_macro") -> Optional[Dict[str, Any]]:
        """
        Get the best run based on a specific metric.
        
        Args:
            metric_name: Metric to use for ranking
            
        Returns:
            Dictionary with best run information
        """
        try:
            runs = mlflow.search_runs(
                experiment_ids=[self.experiment_id],
                order_by=[f"metrics.{metric_name} DESC"],
                max_results=1
            )
            
            if len(runs) > 0:
                best_run = runs.iloc[0].to_dict()
                logger.info(f"\nBest Run (by {metric_name}):")
                logger.info(f"  Run ID: {best_run.get('run_id', 'N/A')}")
                logger.info(f"  {metric_name}: {best_run.get(f'metrics.{metric_name}', 'N/A')}")
                return best_run
            else:
                logger.warning("No runs found in experiment")
                return None
                
        except Exception as e:
            logger.error(f"Error getting best run: {str(e)}")
            return None
    
    def load_model_from_run(self, run_id: str, model_name: str) -> Any:
        """
        Load a model from a specific run.
        
        Args:
            run_id: MLflow run ID
            model_name: Name of the model artifact
            
        Returns:
            Loaded model object
        """
        try:
            model_uri = f"runs:/{run_id}/{model_name}"
            
            # Try sklearn first, then xgboost
            try:
                model = mlflow.sklearn.load_model(model_uri)
            except:
                model = mlflow.xgboost.load_model(model_uri)
            
            logger.info(f"Loaded model from run {run_id}")
            return model
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise


def setup_mlflow_experiment(
    experiment_name: str = "Resume_Authenticity_Experiment",
    tracking_uri: Optional[str] = None
) -> MLflowLogger:
    """
    Helper function to set up MLflow experiment.
    
    Args:
        experiment_name: Name of the experiment
        tracking_uri: Tracking server URI
        
    Returns:
        Configured MLflowLogger instance
    """
    logger.info("Setting up MLflow experiment tracking...")
    mlflow_logger = MLflowLogger(experiment_name, tracking_uri)
    logger.info("MLflow experiment tracking ready")
    return mlflow_logger


if __name__ == "__main__":
    logger.info("This module should be imported, not run directly.")
    logger.info("Example usage:")
    logger.info("  from mlflow_logger import MLflowLogger")
    logger.info("  ml_logger = MLflowLogger('Resume_Authenticity_Experiment')")
    logger.info("  ml_logger.start_run('model_experiment')")
    logger.info("  ml_logger.log_parameters(params)")
    logger.info("  ml_logger.log_metrics(metrics)")
