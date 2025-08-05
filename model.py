import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
import joblib
import warnings
warnings.filterwarnings('ignore')

class AppSecurityRiskPredictor:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = None
        self.is_trained = False
        
    def preprocess_data(self, df, is_training=True):
        """
        Preprocess the data for training/prediction
        """
        df_processed = df.copy()
        
        # Categorical columns to encode
        categorical_columns = ['category', 'os_type', 'app_store', 'developer_type']
        
        # Encode categorical variables
        for col in categorical_columns:
            if is_training:
                # Create and fit label encoder during training
                le = LabelEncoder()
                df_processed[col] = le.fit_transform(df_processed[col])
                self.label_encoders[col] = le
            else:
                # Use existing label encoder during prediction
                if col in self.label_encoders:
                    # Handle unseen categories
                    unique_values = set(df_processed[col].unique())
                    known_values = set(self.label_encoders[col].classes_)
                    unseen_values = unique_values - known_values
                    
                    if unseen_values:
                        # Map unseen values to the most common class
                        most_common = self.label_encoders[col].classes_[0]
                        df_processed[col] = df_processed[col].replace(list(unseen_values), most_common)
                    
                    df_processed[col] = self.label_encoders[col].transform(df_processed[col])
        
        # Feature engineering
        df_processed['app_age_years'] = df_processed['days_since_release'] / 365.25
        df_processed['days_since_update_normalized'] = np.log1p(df_processed['days_since_last_update'])
        df_processed['permission_intensity'] = df_processed['sensitive_permissions'] / np.log1p(df_processed['permissions_requested'])
        df_processed['popularity_score'] = np.log1p(df_processed['install_count']) * df_processed['rating']
        df_processed['security_composite'] = (df_processed['static_analysis_score'] + 
                                            df_processed['dynamic_analysis_score'] + 
                                            df_processed['malware_scan_score']) / 3
        
        # Define feature columns (excluding target and ID columns)
        if is_training:
            self.feature_columns = [col for col in df_processed.columns 
                                  if col not in ['app_id', 'risk_score', 'risk_category']]
        
        return df_processed
    
    def build_model(self, input_dim):
        """
        Build the deep learning model architecture
        """
        model = Sequential([
            # Input layer with batch normalization
            Dense(256, input_dim=input_dim, activation='relu'),
            BatchNormalization(),
            Dropout(0.3),
            
            # Hidden layers with decreasing size
            Dense(128, activation='relu'),
            BatchNormalization(),
            Dropout(0.3),
            
            Dense(64, activation='relu'),
            BatchNormalization(),
            Dropout(0.2),
            
            Dense(32, activation='relu'),
            BatchNormalization(),
            Dropout(0.2),
            
            # Output layer for 3-class classification (Low, Medium, High)
            Dense(3, activation='softmax')
        ])
        
        # Compile model
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def train(self, df, test_size=0.2, validation_split=0.2, epochs=100, batch_size=32):
        """
        Train the deep learning model
        """
        print("Preprocessing data...")
        df_processed = self.preprocess_data(df, is_training=True)
        
        # Prepare features and target
        X = df_processed[self.feature_columns]
        
        # Convert risk categories to numerical labels
        risk_mapping = {'Low': 0, 'Medium': 1, 'High': 2}
        y = df['risk_category'].map(risk_mapping)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Build model
        print("Building model...")
        self.model = self.build_model(X_train_scaled.shape[1])
        
        # Define callbacks
        callbacks = [
            EarlyStopping(
                monitor='val_loss',
                patience=15,
                restore_best_weights=True,
                verbose=1
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=10,
                min_lr=0.0001,
                verbose=1
            )
        ]
        
        # Train model
        print("Training model...")
        history = self.model.fit(
            X_train_scaled, y_train,
            validation_split=validation_split,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        # Evaluate model
        print("\nEvaluating model...")
        y_pred = self.model.predict(X_test_scaled)
        y_pred_classes = np.argmax(y_pred, axis=1)
        
        # Print evaluation metrics
        accuracy = accuracy_score(y_test, y_pred_classes)
        print(f"Test Accuracy: {accuracy:.4f}")
        
        # Classification report
        risk_labels = ['Low', 'Medium', 'High']
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred_classes, target_names=risk_labels))
        
        # Confusion matrix
        print("\nConfusion Matrix:")
        cm = confusion_matrix(y_test, y_pred_classes)
        print(cm)
        
        self.is_trained = True
        return history
    
    def predict(self, df):
        """
        Make predictions on new data
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Preprocess data
        df_processed = self.preprocess_data(df, is_training=False)
        X = df_processed[self.feature_columns]
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Make predictions
        predictions = self.model.predict(X_scaled)
        predicted_classes = np.argmax(predictions, axis=1)
        
        # Convert back to risk categories
        risk_mapping = {0: 'Low', 1: 'Medium', 2: 'High'}
        predicted_categories = [risk_mapping[cls] for cls in predicted_classes]
        
        # Get confidence scores
        confidence_scores = np.max(predictions, axis=1)
        
        return predicted_categories, confidence_scores, predictions
    
    def save_model(self, model_path='app_security_model.h5', scaler_path='scaler.pkl', 
                   encoders_path='label_encoders.pkl'):
        """
        Save the trained model and preprocessors
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")
        
        # Save model
        self.model.save(model_path)
        
        # Save scaler
        joblib.dump(self.scaler, scaler_path)
        
        # Save label encoders and feature columns
        model_metadata = {
            'label_encoders': self.label_encoders,
            'feature_columns': self.feature_columns
        }
        joblib.dump(model_metadata, encoders_path)
        
        print(f"Model saved to {model_path}")
        print(f"Scaler saved to {scaler_path}")
        print(f"Metadata saved to {encoders_path}")
    
    def load_model(self, model_path='app_security_model.h5', scaler_path='scaler.pkl',
                   encoders_path='label_encoders.pkl'):
        """
        Load a trained model and preprocessors
        """
        # Load model
        self.model = tf.keras.models.load_model(model_path)
        
        # Load scaler
        self.scaler = joblib.load(scaler_path)
        
        # Load label encoders and feature columns
        model_metadata = joblib.load(encoders_path)
        self.label_encoders = model_metadata['label_encoders']
        self.feature_columns = model_metadata['feature_columns']
        
        self.is_trained = True
        print("Model loaded successfully!")

def main():
    """
    Main function to train the model
    """
    # Load dataset
    print("Loading dataset...")
    df = pd.read_csv('app_security_dataset.csv')
    print(f"Dataset shape: {df.shape}")
    
    # Initialize and train model
    predictor = AppSecurityRiskPredictor()
    history = predictor.train(df, epochs=50)
    
    # Save model
    predictor.save_model()
    
    print("\nModel training completed and saved!")

if __name__ == "__main__":
    main()