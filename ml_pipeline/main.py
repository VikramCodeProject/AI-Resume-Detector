"""
Resume Authenticity Detection - Main Pipeline Orchestrator

This is the main entry point for the ML pipeline that orchestrates:
1. Data Preprocessing
2. Model Training
3. Model Evaluation
4. Cross-Validation
5. MLflow Experiment Tracking

Author: ML Engineering Team
Date: February 28, 2026
"""

import logging
import os
import sys
import argparse
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.preprocess import preprocess_pipeline
from src.train import ModelTrainer, create_model_comparison_table, identify_best_model
from src.evaluate import ModelEvaluator
from src.mlflow_logger import MLflowLogger

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'pipeline_run_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ResumePipeline:
    """
    Main pipeline orchestrator for Resume Authenticity Detection.
    
    This class coordinates all components of the ML pipeline including
    preprocessing, training, evaluation, and experiment tracking.
    """
    
    def __init__(
        self,
        dataset_path: str,
        experiment_name: str = "Resume_Authenticity_Experiment",
        random_state: int = 42
    ):
        """
        Initialize the pipeline with configuration.
        
        Args:
            dataset_path: Path to the dataset CSV file
            experiment_name: Name for MLflow experiment
            random_state: Random state for reproducibility
        """
        self.dataset_path = dataset_path
        self.experiment_name = experiment_name
        self.random_state = random_state
        
        # Initialize components
        self.preprocessed_data = None
        self.trainer = None
        self.evaluator = None
        self.mlflow_logger = None
        
        logger.info("="*80)
        logger.info("RESUME AUTHENTICITY DETECTION - ML PIPELINE")
        logger.info("="*80)
        logger.info(f"Dataset: {dataset_path}")
        logger.info(f"Experiment: {experiment_name}")
        logger.info(f"Random State: {random_state}")
        logger.info(f"Timestamp: {datetime.now()}")
        logger.info("="*80)
    
    def run_preprocessing(self, test_size: float = 0.2, max_features: int = 5000):
        """
        Execute the preprocessing pipeline.
        
        Args:
            test_size: Proportion of data for testing
            max_features: Maximum TF-IDF features
        """
        logger.info("\n" + "="*80)
        logger.info("STEP 1: DATA PREPROCESSING")
        logger.info("="*80)
        
        try:
            self.preprocessed_data = preprocess_pipeline(
                file_path=self.dataset_path,
                test_size=test_size,
                max_features=max_features,
                random_state=self.random_state
            )
            
            logger.info("✓ Preprocessing completed successfully")
            return self.preprocessed_data
            
        except Exception as e:
            logger.error(f"✗ Preprocessing failed: {str(e)}")
            raise
    
    def run_training(self):
        """
        Execute model training for all algorithms.
        """
        logger.info("\n" + "="*80)
        logger.info("STEP 2: MODEL TRAINING")
        logger.info("="*80)
        
        if self.preprocessed_data is None:
            raise ValueError("Data must be preprocessed before training")
        
        try:
            # Initialize trainer
            self.trainer = ModelTrainer(random_state=self.random_state)
            
            # Train all models
            trained_models = self.trainer.train_all_models(
                X_train=self.preprocessed_data['X_train'],
                y_train=self.preprocessed_data['y_train']
            )
            
            logger.info("✓ Model training completed successfully")
            return trained_models
            
        except Exception as e:
            logger.error(f"✗ Model training failed: {str(e)}")
            raise
    
    def run_evaluation(self):
        """
        Execute model evaluation on test set.
        
        Returns:
            Dictionary of evaluation results
        """
        logger.info("\n" + "="*80)
        logger.info("STEP 3: MODEL EVALUATION")
        logger.info("="*80)
        
        if self.trainer is None or not self.trainer.trained_models:
            raise ValueError("Models must be trained before evaluation")
        
        try:
            # Initialize evaluator
            self.evaluator = ModelEvaluator(
                label_names=self.preprocessed_data['label_names']
            )
            
            # Evaluate all models
            evaluation_results = self.evaluator.evaluate_all_models(
                models=self.trainer.trained_models,
                X_test=self.preprocessed_data['X_test'],
                y_test=self.preprocessed_data['y_test']
            )
            
            # Create comparison table
            comparison_df = self.evaluator.create_comparison_table()
            
            # Print classification reports
            for model_name in self.trainer.trained_models.keys():
                self.evaluator.print_classification_report(model_name)
            
            # Generate visualizations
            logger.info("\nGenerating visualizations...")
            os.makedirs('artifacts', exist_ok=True)
            self.evaluator.plot_all_confusion_matrices('./artifacts')
            self.evaluator.plot_model_comparison('./artifacts/model_comparison.png')
            
            # Identify best model
            best_model_name, best_metrics = self.evaluator.get_best_model()
            
            logger.info("✓ Model evaluation completed successfully")
            return evaluation_results
            
        except Exception as e:
            logger.error(f"✗ Model evaluation failed: {str(e)}")
            raise
    
    def run_cross_validation(self, cv_folds: int = 5):
        """
        Execute K-Fold cross-validation for all models.
        
        Args:
            cv_folds: Number of folds for cross-validation
        """
        logger.info("\n" + "="*80)
        logger.info("STEP 4: K-FOLD CROSS-VALIDATION")
        logger.info("="*80)
        
        if self.trainer is None:
            raise ValueError("Trainer must be initialized before cross-validation")
        
        try:
            # Combine train and test data for cross-validation
            from scipy.sparse import vstack
            X_full = vstack([
                self.preprocessed_data['X_train'],
                self.preprocessed_data['X_test']
            ])
            
            import pandas as pd
            y_full = pd.concat([
                self.preprocessed_data['y_train'],
                self.preprocessed_data['y_test']
            ])
            
            # Perform cross-validation for all models
            cv_results = self.trainer.cross_validate_all_models(
                X=X_full,
                y=y_full,
                cv_folds=cv_folds
            )
            
            logger.info("✓ Cross-validation completed successfully")
            return cv_results
            
        except Exception as e:
            logger.error(f"✗ Cross-validation failed: {str(e)}")
            raise
    
    def run_mlflow_tracking(self):
        """
        Log all experiments to MLflow.
        """
        logger.info("\n" + "="*80)
        logger.info("STEP 5: MLFLOW EXPERIMENT TRACKING")
        logger.info("="*80)
        
        if self.evaluator is None or not self.evaluator.evaluation_results:
            raise ValueError("Evaluation must be completed before MLflow tracking")
        
        try:
            # Initialize MLflow logger
            self.mlflow_logger = MLflowLogger(experiment_name=self.experiment_name)
            
            # Log experiments for each model
            for model_name, model in self.trainer.trained_models.items():
                logger.info(f"\nLogging experiment for {model_name}...")
                
                # Get model parameters
                params = self.trainer.get_model_parameters(model_name)
                
                # Get evaluation metrics
                metrics = self.evaluator.evaluation_results[model_name]
                
                # Extract scalar metrics for MLflow
                mlflow_metrics = {
                    'accuracy': metrics['accuracy'],
                    'precision_macro': metrics['precision_macro'],
                    'recall_macro': metrics['recall_macro'],
                    'f1_macro': metrics['f1_macro'],
                    'precision_weighted': metrics['precision_weighted'],
                    'recall_weighted': metrics['recall_weighted'],
                    'f1_weighted': metrics['f1_weighted']
                }
                
                # Log complete experiment
                self.mlflow_logger.log_model_experiment(
                    model=model,
                    model_name=model_name,
                    params=params,
                    metrics=mlflow_metrics,
                    confusion_matrix=metrics['confusion_matrix'],
                    classification_report=metrics['classification_report'],
                    label_names=self.preprocessed_data['label_names']
                )
            
            # Compare all runs
            logger.info("\n" + "-"*80)
            self.mlflow_logger.compare_runs(metric_name='f1_macro')
            
            # Get best run
            best_run = self.mlflow_logger.get_best_run(metric_name='f1_macro')
            
            logger.info("✓ MLflow tracking completed successfully")
            logger.info(f"\nMLflow UI: Run 'mlflow ui' and open http://localhost:5000")
            
        except Exception as e:
            logger.error(f"✗ MLflow tracking failed: {str(e)}")
            # Don't raise - MLflow tracking failure shouldn't stop the pipeline
            logger.warning("Continuing without MLflow tracking...")
    
    def save_models(self, save_dir: str = "./models"):
        """
        Save all trained models to disk.
        
        Args:
            save_dir: Directory to save models
        """
        logger.info(f"\nSaving models to {save_dir}...")
        
        try:
            saved_paths = self.trainer.save_all_models(save_dir=save_dir)
            logger.info(f"✓ Saved {len(saved_paths)} models successfully")
            return saved_paths
        except Exception as e:
            logger.error(f"✗ Failed to save models: {str(e)}")
    
    def export_results(self, output_dir: str = "./results"):
        """
        Export all results and artifacts.
        
        Args:
            output_dir: Directory to save results
        """
        logger.info(f"\nExporting results to {output_dir}...")
        
        try:
            self.evaluator.export_results(output_dir=output_dir)
            logger.info(f"✓ Results exported successfully")
        except Exception as e:
            logger.error(f"✗ Failed to export results: {str(e)}")
    
    def run_full_pipeline(
        self,
        test_size: float = 0.2,
        max_features: int = 5000,
        cv_folds: int = 5,
        save_models: bool = True,
        export_results: bool = True
    ):
        """
        Execute the complete ML pipeline end-to-end.
        
        Args:
            test_size: Proportion for test split
            max_features: Maximum TF-IDF features
            cv_folds: Number of cross-validation folds
            save_models: Whether to save trained models
            export_results: Whether to export results
        """
        start_time = datetime.now()
        
        try:
            # Step 1: Preprocessing
            self.run_preprocessing(test_size=test_size, max_features=max_features)
            
            # Step 2: Training
            self.run_training()
            
            # Step 3: Evaluation
            self.run_evaluation()
            
            # Step 4: Cross-Validation
            self.run_cross_validation(cv_folds=cv_folds)
            
            # Step 5: MLflow Tracking
            self.run_mlflow_tracking()
            
            # Optional: Save models
            if save_models:
                self.save_models()
            
            # Optional: Export results
            if export_results:
                self.export_results()
            
            # Pipeline completion
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info("\n" + "="*80)
            logger.info("PIPELINE EXECUTION COMPLETED SUCCESSFULLY")
            logger.info("="*80)
            logger.info(f"Total Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
            logger.info(f"Models Trained: {len(self.trainer.trained_models)}")
            logger.info(f"Best Model: {self.evaluator.get_best_model()[0]}")
            logger.info(f"Results saved in: ./results, ./models, ./artifacts")
            logger.info(f"MLflow UI: Run 'mlflow ui' and open http://localhost:5000")
            logger.info("="*80)
            
            return True
            
        except Exception as e:
            logger.error(f"\n{'='*80}")
            logger.error("PIPELINE EXECUTION FAILED")
            logger.error(f"{'='*80}")
            logger.error(f"Error: {str(e)}")
            logger.error(f"{'='*80}")
            return False


def main():
    """
    Main function to run the pipeline with command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description='Resume Authenticity Detection ML Pipeline'
    )
    parser.add_argument(
        '--dataset',
        type=str,
        default='./data/resume_dataset.csv',
        help='Path to the dataset CSV file'
    )
    parser.add_argument(
        '--experiment-name',
        type=str,
        default='Resume_Authenticity_Experiment',
        help='Name for MLflow experiment'
    )
    parser.add_argument(
        '--test-size',
        type=float,
        default=0.2,
        help='Proportion of data for testing (default: 0.2)'
    )
    parser.add_argument(
        '--max-features',
        type=int,
        default=5000,
        help='Maximum TF-IDF features (default: 5000)'
    )
    parser.add_argument(
        '--cv-folds',
        type=int,
        default=5,
        help='Number of cross-validation folds (default: 5)'
    )
    parser.add_argument(
        '--random-state',
        type=int,
        default=42,
        help='Random state for reproducibility (default: 42)'
    )
    parser.add_argument(
        '--no-save-models',
        action='store_true',
        help='Skip saving models to disk'
    )
    parser.add_argument(
        '--no-export-results',
        action='store_true',
        help='Skip exporting results'
    )
    
    args = parser.parse_args()
    
    # Initialize and run pipeline
    pipeline = ResumePipeline(
        dataset_path=args.dataset,
        experiment_name=args.experiment_name,
        random_state=args.random_state
    )
    
    success = pipeline.run_full_pipeline(
        test_size=args.test_size,
        max_features=args.max_features,
        cv_folds=args.cv_folds,
        save_models=not args.no_save_models,
        export_results=not args.no_export_results
    )
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
