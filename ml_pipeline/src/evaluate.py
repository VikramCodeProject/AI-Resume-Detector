"""
Resume Authenticity Detection - Model Evaluation Module

This module handles comprehensive model evaluation including:
- Accuracy, Precision, Recall, F1-Score calculation
- Confusion Matrix generation
- Classification Report
- Performance visualization

Author: ML Engineering Team
Date: February 28, 2026
"""

import logging
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Any, Optional
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set style for visualizations
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (10, 8)


class ModelEvaluator:
    """
    Comprehensive model evaluation framework for classification tasks.
    
    Attributes:
        label_names: List of class label names
        evaluation_results: Dictionary storing all evaluation metrics
    """
    
    def __init__(self, label_names: List[str]):
        """
        Initialize the evaluator with label information.
        
        Args:
            label_names: List of class label names
        """
        self.label_names = label_names
        self.evaluation_results = {}
        
        logger.info(f"ModelEvaluator initialized with {len(label_names)} classes")
        logger.info(f"Classes: {label_names}")
    
    def evaluate_model(
        self,
        model: Any,
        X_test: np.ndarray,
        y_test: np.ndarray,
        model_name: str
    ) -> Dict[str, Any]:
        """
        Comprehensive evaluation of a single model.
        
        Args:
            model: Trained model object
            X_test: Test features
            y_test: True labels
            model_name: Name of the model
            
        Returns:
            Dictionary containing all evaluation metrics
        """
        logger.info(f"\nEvaluating {model_name}...")
        
        try:
            # Make predictions
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            metrics = {
                'model_name': model_name,
                'accuracy': accuracy_score(y_test, y_pred),
                'precision_macro': precision_score(y_test, y_pred, average='macro', zero_division=0),
                'recall_macro': recall_score(y_test, y_pred, average='macro', zero_division=0),
                'f1_macro': f1_score(y_test, y_pred, average='macro', zero_division=0),
                'precision_weighted': precision_score(y_test, y_pred, average='weighted', zero_division=0),
                'recall_weighted': recall_score(y_test, y_pred, average='weighted', zero_division=0),
                'f1_weighted': f1_score(y_test, y_pred, average='weighted', zero_division=0),
            }
            
            # Calculate per-class metrics
            precision_per_class = precision_score(y_test, y_pred, average=None, zero_division=0)
            recall_per_class = recall_score(y_test, y_pred, average=None, zero_division=0)
            f1_per_class = f1_score(y_test, y_pred, average=None, zero_division=0)
            
            metrics['precision_per_class'] = precision_per_class
            metrics['recall_per_class'] = recall_per_class
            metrics['f1_per_class'] = f1_per_class
            
            # Confusion matrix
            cm = confusion_matrix(y_test, y_pred)
            metrics['confusion_matrix'] = cm
            
            # Classification report
            report = classification_report(
                y_test, y_pred,
                target_names=self.label_names,
                output_dict=True,
                zero_division=0
            )
            metrics['classification_report'] = report
            
            # Store results
            self.evaluation_results[model_name] = metrics
            
            # Log results
            self._log_metrics(model_name, metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error evaluating {model_name}: {str(e)}")
            raise
    
    def _log_metrics(self, model_name: str, metrics: Dict[str, Any]):
        """
        Log evaluation metrics to console.
        
        Args:
            model_name: Name of the model
            metrics: Dictionary of metrics
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Results for {model_name}")
        logger.info(f"{'='*60}")
        logger.info(f"Accuracy:           {metrics['accuracy']:.4f}")
        logger.info(f"Precision (macro):  {metrics['precision_macro']:.4f}")
        logger.info(f"Recall (macro):     {metrics['recall_macro']:.4f}")
        logger.info(f"F1-Score (macro):   {metrics['f1_macro']:.4f}")
        logger.info(f"{'='*60}")
        
        logger.info("\nPer-Class Metrics:")
        for i, label in enumerate(self.label_names):
            logger.info(f"  {label}:")
            logger.info(f"    Precision: {metrics['precision_per_class'][i]:.4f}")
            logger.info(f"    Recall:    {metrics['recall_per_class'][i]:.4f}")
            logger.info(f"    F1-Score:  {metrics['f1_per_class'][i]:.4f}")
    
    def evaluate_all_models(
        self,
        models: Dict[str, Any],
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> Dict[str, Dict[str, Any]]:
        """
        Evaluate all models and compile results.
        
        Args:
            models: Dictionary of trained models
            X_test: Test features
            y_test: True labels
            
        Returns:
            Dictionary of evaluation results for all models
        """
        logger.info("\n" + "="*60)
        logger.info("EVALUATING ALL MODELS")
        logger.info("="*60)
        
        for model_name, model in models.items():
            try:
                self.evaluate_model(model, X_test, y_test, model_name)
            except Exception as e:
                logger.error(f"Failed to evaluate {model_name}: {str(e)}")
                continue
        
        logger.info(f"\nEvaluated {len(self.evaluation_results)} models successfully")
        return self.evaluation_results
    
    def create_comparison_table(self) -> pd.DataFrame:
        """
        Create a comparison table of all evaluated models.
        
        Returns:
            DataFrame with model comparison
        """
        if not self.evaluation_results:
            logger.warning("No evaluation results available")
            return pd.DataFrame()
        
        # Extract key metrics for comparison
        comparison_data = []
        for model_name, metrics in self.evaluation_results.items():
            comparison_data.append({
                'Model': model_name,
                'Accuracy': metrics['accuracy'],
                'Precision (Macro)': metrics['precision_macro'],
                'Recall (Macro)': metrics['recall_macro'],
                'F1-Score (Macro)': metrics['f1_macro'],
                'Precision (Weighted)': metrics['precision_weighted'],
                'Recall (Weighted)': metrics['recall_weighted'],
                'F1-Score (Weighted)': metrics['f1_weighted']
            })
        
        df = pd.DataFrame(comparison_data)
        df = df.sort_values('F1-Score (Macro)', ascending=False)
        df = df.round(4)
        
        logger.info("\n" + "="*80)
        logger.info("MODEL COMPARISON TABLE")
        logger.info("="*80)
        logger.info("\n" + df.to_string(index=False))
        logger.info("="*80)
        
        return df
    
    def print_classification_report(self, model_name: str):
        """
        Print detailed classification report for a model.
        
        Args:
            model_name: Name of the model
        """
        if model_name not in self.evaluation_results:
            logger.error(f"No results found for model: {model_name}")
            return
        
        report = self.evaluation_results[model_name]['classification_report']
        
        logger.info(f"\n{'='*60}")
        logger.info(f"CLASSIFICATION REPORT - {model_name}")
        logger.info(f"{'='*60}\n")
        
        # Print per-class metrics
        for label in self.label_names:
            metrics = report[label]
            logger.info(f"{label}:")
            logger.info(f"  Precision: {metrics['precision']:.4f}")
            logger.info(f"  Recall:    {metrics['recall']:.4f}")
            logger.info(f"  F1-Score:  {metrics['f1-score']:.4f}")
            logger.info(f"  Support:   {int(metrics['support'])}")
            logger.info("")
        
        # Print overall metrics
        logger.info("Overall Metrics:")
        logger.info(f"  Accuracy:                    {report['accuracy']:.4f}")
        logger.info(f"  Macro Avg Precision:         {report['macro avg']['precision']:.4f}")
        logger.info(f"  Macro Avg Recall:            {report['macro avg']['recall']:.4f}")
        logger.info(f"  Macro Avg F1-Score:          {report['macro avg']['f1-score']:.4f}")
        logger.info(f"  Weighted Avg Precision:      {report['weighted avg']['precision']:.4f}")
        logger.info(f"  Weighted Avg Recall:         {report['weighted avg']['recall']:.4f}")
        logger.info(f"  Weighted Avg F1-Score:       {report['weighted avg']['f1-score']:.4f}")
        logger.info("="*60)
    
    def plot_confusion_matrix(
        self,
        model_name: str,
        save_path: Optional[str] = None,
        normalize: bool = False
    ) -> str:
        """
        Plot confusion matrix for a model.
        
        Args:
            model_name: Name of the model
            save_path: Path to save the plot (optional)
            normalize: Whether to normalize the confusion matrix
            
        Returns:
            Path to saved plot
        """
        if model_name not in self.evaluation_results:
            logger.error(f"No results found for model: {model_name}")
            return ""
        
        cm = self.evaluation_results[model_name]['confusion_matrix']
        
        if normalize:
            cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
            title = f'Normalized Confusion Matrix - {model_name}'
            fmt = '.2f'
        else:
            title = f'Confusion Matrix - {model_name}'
            fmt = 'd'
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(
            cm,
            annot=True,
            fmt=fmt,
            cmap='Blues',
            xticklabels=self.label_names,
            yticklabels=self.label_names,
            cbar_kws={'label': 'Count' if not normalize else 'Proportion'}
        )
        plt.title(title, fontsize=16, fontweight='bold')
        plt.ylabel('True Label', fontsize=12)
        plt.xlabel('Predicted Label', fontsize=12)
        plt.tight_layout()
        
        # Save plot
        if save_path is None:
            os.makedirs('artifacts', exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = f"artifacts/confusion_matrix_{model_name}_{timestamp}.png"
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Confusion matrix saved: {save_path}")
        return save_path
    
    def plot_all_confusion_matrices(
        self,
        save_dir: str = "./artifacts"
    ) -> Dict[str, str]:
        """
        Plot confusion matrices for all evaluated models.
        
        Args:
            save_dir: Directory to save plots
            
        Returns:
            Dictionary mapping model names to plot paths
        """
        os.makedirs(save_dir, exist_ok=True)
        
        logger.info(f"\nGenerating confusion matrices for all models...")
        plot_paths = {}
        
        for model_name in self.evaluation_results.keys():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = os.path.join(
                save_dir,
                f"confusion_matrix_{model_name}_{timestamp}.png"
            )
            try:
                path = self.plot_confusion_matrix(model_name, save_path)
                plot_paths[model_name] = path
            except Exception as e:
                logger.error(f"Failed to plot confusion matrix for {model_name}: {str(e)}")
                continue
        
        logger.info(f"Generated {len(plot_paths)} confusion matrix plots")
        return plot_paths
    
    def plot_model_comparison(
        self,
        save_path: Optional[str] = None
    ) -> str:
        """
        Create a visual comparison of all models.
        
        Args:
            save_path: Path to save the plot
            
        Returns:
            Path to saved plot
        """
        if not self.evaluation_results:
            logger.warning("No evaluation results available for comparison")
            return ""
        
        # Extract metrics for plotting
        models = []
        accuracies = []
        precisions = []
        recalls = []
        f1_scores = []
        
        for model_name, metrics in self.evaluation_results.items():
            models.append(model_name)
            accuracies.append(metrics['accuracy'])
            precisions.append(metrics['precision_macro'])
            recalls.append(metrics['recall_macro'])
            f1_scores.append(metrics['f1_macro'])
        
        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Model Performance Comparison', fontsize=18, fontweight='bold')
        
        metrics_data = [
            ('Accuracy', accuracies, axes[0, 0]),
            ('Precision (Macro)', precisions, axes[0, 1]),
            ('Recall (Macro)', recalls, axes[1, 0]),
            ('F1-Score (Macro)', f1_scores, axes[1, 1])
        ]
        
        for metric_name, values, ax in metrics_data:
            bars = ax.bar(models, values, color='skyblue', edgecolor='navy', alpha=0.7)
            ax.set_title(metric_name, fontsize=14, fontweight='bold')
            ax.set_ylabel('Score', fontsize=12)
            ax.set_ylim([0, 1])
            ax.grid(axis='y', alpha=0.3)
            
            # Rotate x-axis labels
            ax.set_xticklabels(models, rotation=45, ha='right')
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width()/2., height,
                    f'{height:.3f}',
                    ha='center', va='bottom', fontsize=10
                )
        
        plt.tight_layout()
        
        # Save plot
        if save_path is None:
            os.makedirs('artifacts', exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = f"artifacts/model_comparison_{timestamp}.png"
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Model comparison plot saved: {save_path}")
        return save_path
    
    def get_best_model(self) -> Tuple[str, Dict[str, Any]]:
        """
        Identify the best performing model based on F1-score.
        
        Returns:
            Tuple of (best_model_name, best_model_metrics)
        """
        if not self.evaluation_results:
            logger.warning("No evaluation results available")
            return "", {}
        
        best_model = max(
            self.evaluation_results.items(),
            key=lambda x: x[1]['f1_macro']
        )
        
        logger.info("\n" + "="*60)
        logger.info("BEST MODEL IDENTIFICATION")
        logger.info("="*60)
        logger.info(f"Best Model: {best_model[0]}")
        logger.info(f"F1-Score (Macro): {best_model[1]['f1_macro']:.4f}")
        logger.info(f"Accuracy: {best_model[1]['accuracy']:.4f}")
        logger.info("="*60)
        
        return best_model
    
    def export_results(self, output_dir: str = "./results"):
        """
        Export all evaluation results to files.
        
        Args:
            output_dir: Directory to save results
        """
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export comparison table
        comparison_df = self.create_comparison_table()
        comparison_path = os.path.join(output_dir, f"model_comparison_{timestamp}.csv")
        comparison_df.to_csv(comparison_path, index=False)
        logger.info(f"Comparison table saved: {comparison_path}")
        
        # Export detailed reports for each model
        for model_name in self.evaluation_results.keys():
            report_path = os.path.join(output_dir, f"report_{model_name}_{timestamp}.txt")
            with open(report_path, 'w') as f:
                f.write(f"{'='*60}\n")
                f.write(f"Classification Report - {model_name}\n")
                f.write(f"{'='*60}\n\n")
                
                report = self.evaluation_results[model_name]['classification_report']
                for label in self.label_names:
                    metrics = report[label]
                    f.write(f"{label}:\n")
                    f.write(f"  Precision: {metrics['precision']:.4f}\n")
                    f.write(f"  Recall:    {metrics['recall']:.4f}\n")
                    f.write(f"  F1-Score:  {metrics['f1-score']:.4f}\n")
                    f.write(f"  Support:   {int(metrics['support'])}\n\n")
            
            logger.info(f"Report saved: {report_path}")
        
        logger.info(f"All results exported to {output_dir}")


if __name__ == "__main__":
    logger.info("This module should be imported, not run directly.")
    logger.info("Example usage:")
    logger.info("  from evaluate import ModelEvaluator")
    logger.info("  evaluator = ModelEvaluator(label_names)")
    logger.info("  evaluator.evaluate_all_models(models, X_test, y_test)")
