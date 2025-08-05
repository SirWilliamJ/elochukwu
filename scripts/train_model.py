#!/usr/bin/env python3
"""
Standalone Model Training Script

This script trains the deep learning model for app security risk prediction.
It can be run independently with various configuration options.

Usage:
    python scripts/train_model.py [options]
"""

import sys
import os
import argparse
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import warnings
warnings.filterwarnings('ignore')

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.neural_network import SecurityRiskNetwork
from data.collector import DataCollector


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Train app security risk prediction model'
    )
    
    parser.add_argument(
        '--data', '-d',
        type=str,
        default='app_security_dataset.csv',
        help='Path to dataset CSV file'
    )
    
    parser.add_argument(
        '--epochs', '-e',
        type=int,
        default=50,
        help='Number of training epochs (default: 50)'
    )
    
    parser.add_argument(
        '--batch-size', '-b',
        type=int,
        default=32,
        help='Training batch size (default: 32)'
    )
    
    parser.add_argument(
        '--test-size', '-t',
        type=float,
        default=0.2,
        help='Test set size ratio (default: 0.2)'
    )
    
    parser.add_argument(
        '--validation-split', '-v',
        type=float,
        default=0.2,
        help='Validation split ratio (default: 0.2)'
    )
    
    parser.add_argument(
        '--learning-rate', '-lr',
        type=float,
        default=0.001,
        help='Learning rate (default: 0.001)'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        type=str,
        default='models',
        help='Output directory for saved models (default: models)'
    )
    
    parser.add_argument(
        '--generate-data',
        action='store_true',
        help='Generate synthetic data if dataset file not found'
    )
    
    parser.add_argument(
        '--seed', '-s',
        type=int,
        default=42,
        help='Random seed for reproducibility (default: 42)'
    )
    
    return parser.parse_args()


def preprocess_data(df, is_training=True, scaler=None, label_encoders=None):
    """
    Preprocess the dataset for training.
    
    Args:
        df: Input dataframe
        is_training: Whether this is training data
        scaler: Pre-fitted scaler (for inference)
        label_encoders: Pre-fitted label encoders (for inference)
        
    Returns:
        Processed features, target, scaler, label_encoders
    """
    df_processed = df.copy()
    
    # Initialize encoders if training
    if is_training:
        scaler = StandardScaler()
        label_encoders = {}
    
    # Categorical columns to encode
    categorical_columns = ['category', 'os_type', 'app_store', 'developer_type']
    
    # Encode categorical variables
    for col in categorical_columns:
        if is_training:
            le = LabelEncoder()
            df_processed[col] = le.fit_transform(df_processed[col])
            label_encoders[col] = le
        else:
            if col in label_encoders:
                # Handle unseen categories
                unique_values = set(df_processed[col].unique())
                known_values = set(label_encoders[col].classes_)
                unseen_values = unique_values - known_values
                
                if unseen_values:
                    most_common = label_encoders[col].classes_[0]
                    df_processed[col] = df_processed[col].replace(
                        list(unseen_values), most_common
                    )
                
                df_processed[col] = label_encoders[col].transform(df_processed[col])
    
    # Feature engineering
    df_processed['app_age_years'] = df_processed['days_since_release'] / 365.25
    df_processed['days_since_update_normalized'] = np.log1p(
        df_processed['days_since_last_update']
    )
    df_processed['permission_intensity'] = (
        df_processed['sensitive_permissions'] / 
        np.log1p(df_processed['permissions_requested'])
    )
    df_processed['popularity_score'] = (
        np.log1p(df_processed['install_count']) * df_processed['rating']
    )
    df_processed['security_composite'] = (
        df_processed['static_analysis_score'] + 
        df_processed['dynamic_analysis_score'] + 
        df_processed['malware_scan_score']
    ) / 3
    
    # Define feature columns (excluding target and ID columns)
    feature_columns = [
        col for col in df_processed.columns 
        if col not in ['app_id', 'risk_score', 'risk_category']
    ]
    
    # Prepare features
    X = df_processed[feature_columns]
    
    # Scale features
    if is_training:
        X_scaled = scaler.fit_transform(X)
    else:
        X_scaled = scaler.transform(X)
    
    # Prepare target if available
    y = None
    if 'risk_category' in df.columns:
        risk_mapping = {'Low': 0, 'Medium': 1, 'High': 2}
        y = df['risk_category'].map(risk_mapping)
    
    return X_scaled, y, scaler, label_encoders, feature_columns


def main():
    """Main training function."""
    args = parse_arguments()
    
    print("🔒 App Security Risk Predictor - Model Training")
    print("=" * 55)
    
    # Set random seeds
    np.random.seed(args.seed)
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load or generate dataset
    data_path = Path(args.data)
    if not data_path.exists():
        if args.generate_data:
            print(f"📊 Dataset not found. Generating synthetic data...")
            collector = DataCollector(random_seed=args.seed)
            df = collector.generate_synthetic_dataset(
                n_samples=5000,
                save_path=str(data_path)
            )
        else:
            print(f"❌ Dataset file not found: {args.data}")
            print("Use --generate-data flag to create synthetic dataset")
            sys.exit(1)
    else:
        print(f"📁 Loading dataset from: {args.data}")
        df = pd.read_csv(data_path)
    
    print(f"📈 Dataset shape: {df.shape}")
    
    # Preprocess data
    print("🔄 Preprocessing data...")
    X, y, scaler, label_encoders, feature_columns = preprocess_data(df)
    
    print(f"📋 Features: {X.shape[1]}")
    print(f"🎯 Target distribution:")
    risk_dist = df['risk_category'].value_counts()
    for category, count in risk_dist.items():
        percentage = (count / len(df)) * 100
        print(f"  {category:>6}: {count:>5,} ({percentage:>5.1f}%)")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=args.seed, stratify=y
    )
    
    print(f"\n🔀 Data split:")
    print(f"  Training: {X_train.shape[0]:,} samples")
    print(f"  Testing:  {X_test.shape[0]:,} samples")
    
    # Build model
    print(f"\n🧠 Building neural network...")
    network = SecurityRiskNetwork(
        input_dim=X.shape[1],
        learning_rate=args.learning_rate
    )
    model = network.build_model()
    
    print("Model Architecture:")
    print(network.get_model_summary())
    
    # Get callbacks
    callbacks = network.get_callbacks()
    
    # Train model
    print(f"🚀 Starting training...")
    print(f"  Epochs: {args.epochs}")
    print(f"  Batch size: {args.batch_size}")
    print(f"  Validation split: {args.validation_split}")
    print(f"  Learning rate: {args.learning_rate}")
    print()
    
    try:
        history = model.fit(
            X_train, y_train,
            validation_split=args.validation_split,
            epochs=args.epochs,
            batch_size=args.batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        # Evaluate model
        print(f"\n📊 Evaluating model...")
        y_pred = model.predict(X_test)
        y_pred_classes = np.argmax(y_pred, axis=1)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred_classes)
        print(f"✅ Test Accuracy: {accuracy:.4f}")
        
        # Classification report
        risk_labels = ['Low', 'Medium', 'High']
        print(f"\n📋 Classification Report:")
        print(classification_report(y_test, y_pred_classes, target_names=risk_labels))
        
        # Confusion matrix
        print(f"🔍 Confusion Matrix:")
        cm = confusion_matrix(y_test, y_pred_classes)
        print(cm)
        
        # Save model and artifacts
        model_path = output_dir / 'app_security_model.h5'
        scaler_path = output_dir / 'scaler.pkl'
        encoders_path = output_dir / 'label_encoders.pkl'
        
        print(f"\n💾 Saving model artifacts...")
        
        # Save model
        model.save(str(model_path))
        print(f"  Model: {model_path}")
        
        # Save scaler
        joblib.dump(scaler, str(scaler_path))
        print(f"  Scaler: {scaler_path}")
        
        # Save encoders and metadata
        metadata = {
            'label_encoders': label_encoders,
            'feature_columns': feature_columns,
            'model_config': {
                'input_dim': X.shape[1],
                'hidden_layers': network.hidden_layers,
                'dropout_rates': network.dropout_rates,
                'learning_rate': args.learning_rate
            },
            'training_config': {
                'epochs': args.epochs,
                'batch_size': args.batch_size,
                'test_size': args.test_size,
                'validation_split': args.validation_split,
                'seed': args.seed
            },
            'performance': {
                'test_accuracy': float(accuracy),
                'final_epoch': len(history.history['loss'])
            }
        }
        
        joblib.dump(metadata, str(encoders_path))
        print(f"  Metadata: {encoders_path}")
        
        print(f"\n✅ Training completed successfully!")
        print(f"🎯 Final test accuracy: {accuracy:.4f}")
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Training interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Training failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()