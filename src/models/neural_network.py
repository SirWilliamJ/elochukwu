"""
Neural Network Architecture Module

Defines the deep learning architecture for app security risk prediction.
"""

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from typing import List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class SecurityRiskNetwork:
    """
    Deep neural network for app security risk prediction.
    
    This class encapsulates the model architecture, compilation,
    and training configuration for the security risk prediction task.
    """
    
    def __init__(
        self,
        input_dim: int,
        hidden_layers: List[int] = [256, 128, 64, 32],
        dropout_rates: List[float] = [0.3, 0.3, 0.2, 0.2],
        activation: str = 'relu',
        output_classes: int = 3,
        learning_rate: float = 0.001
    ):
        """
        Initialize the neural network architecture.
        
        Args:
            input_dim: Number of input features
            hidden_layers: List of hidden layer sizes
            dropout_rates: Dropout rates for each hidden layer
            activation: Activation function for hidden layers
            output_classes: Number of output classes (Low/Medium/High)
            learning_rate: Learning rate for optimizer
        """
        self.input_dim = input_dim
        self.hidden_layers = hidden_layers
        self.dropout_rates = dropout_rates
        self.activation = activation
        self.output_classes = output_classes
        self.learning_rate = learning_rate
        
        self.model = None
        
        logger.info(
            "SecurityRiskNetwork initialized: input_dim=%d, layers=%s",
            input_dim, hidden_layers
        )
    
    def build_model(self) -> tf.keras.Model:
        """
        Build the neural network model.
        
        Returns:
            Compiled Keras model
        """
        model = Sequential()
        
        # Input layer with first hidden layer
        model.add(Dense(
            self.hidden_layers[0],
            input_dim=self.input_dim,
            activation=self.activation,
            name='input_layer'
        ))
        model.add(BatchNormalization(name='bn_input'))
        model.add(Dropout(self.dropout_rates[0], name='dropout_input'))
        
        # Hidden layers
        for i, (units, dropout_rate) in enumerate(
            zip(self.hidden_layers[1:], self.dropout_rates[1:]), 1
        ):
            model.add(Dense(
                units,
                activation=self.activation,
                name=f'hidden_{i}'
            ))
            model.add(BatchNormalization(name=f'bn_hidden_{i}'))
            model.add(Dropout(dropout_rate, name=f'dropout_hidden_{i}'))
        
        # Output layer
        model.add(Dense(
            self.output_classes,
            activation='softmax',
            name='output_layer'
        ))
        
        # Compile model
        model.compile(
            optimizer=Adam(learning_rate=self.learning_rate),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        self.model = model
        logger.info("Model built and compiled successfully")
        
        return model
    
    def get_model_summary(self) -> str:
        """
        Get model architecture summary.
        
        Returns:
            String representation of model summary
        """
        if self.model is None:
            return "Model not built yet"
        
        # Capture summary in string
        import io
        summary_buffer = io.StringIO()
        self.model.summary(print_fn=lambda x: summary_buffer.write(x + '\n'))
        return summary_buffer.getvalue()
    
    def get_callbacks(
        self,
        patience_early_stop: int = 15,
        patience_lr_reduce: int = 10,
        min_lr: float = 0.0001,
        monitor: str = 'val_loss'
    ) -> List[tf.keras.callbacks.Callback]:
        """
        Get training callbacks for model optimization.
        
        Args:
            patience_early_stop: Patience for early stopping
            patience_lr_reduce: Patience for learning rate reduction
            min_lr: Minimum learning rate
            monitor: Metric to monitor
            
        Returns:
            List of Keras callbacks
        """
        callbacks = [
            EarlyStopping(
                monitor=monitor,
                patience=patience_early_stop,
                restore_best_weights=True,
                verbose=1,
                mode='min'
            ),
            ReduceLROnPlateau(
                monitor=monitor,
                factor=0.5,
                patience=patience_lr_reduce,
                min_lr=min_lr,
                verbose=1,
                mode='min'
            )
        ]
        
        logger.info("Training callbacks configured")
        return callbacks
    
    def save_model(self, filepath: str) -> None:
        """
        Save the trained model.
        
        Args:
            filepath: Path to save the model
        """
        if self.model is None:
            raise ValueError("Model not built yet")
        
        self.model.save(filepath)
        logger.info("Model saved to: %s", filepath)
    
    def load_model(self, filepath: str) -> tf.keras.Model:
        """
        Load a pre-trained model.
        
        Args:
            filepath: Path to the saved model
            
        Returns:
            Loaded Keras model
        """
        self.model = tf.keras.models.load_model(filepath)
        logger.info("Model loaded from: %s", filepath)
        return self.model
    
    def predict(self, X: tf.Tensor) -> tf.Tensor:
        """
        Make predictions using the model.
        
        Args:
            X: Input features
            
        Returns:
            Prediction probabilities
        """
        if self.model is None:
            raise ValueError("Model not built or loaded")
        
        return self.model.predict(X)
    
    def evaluate(self, X: tf.Tensor, y: tf.Tensor) -> Tuple[float, float]:
        """
        Evaluate model performance.
        
        Args:
            X: Input features
            y: True labels
            
        Returns:
            Tuple of (loss, accuracy)
        """
        if self.model is None:
            raise ValueError("Model not built or loaded")
        
        loss, accuracy = self.model.evaluate(X, y, verbose=0)
        return loss, accuracy


def create_default_network(input_dim: int) -> SecurityRiskNetwork:
    """
    Create a default network configuration.
    
    Args:
        input_dim: Number of input features
        
    Returns:
        Configured SecurityRiskNetwork instance
    """
    return SecurityRiskNetwork(
        input_dim=input_dim,
        hidden_layers=[256, 128, 64, 32],
        dropout_rates=[0.3, 0.3, 0.2, 0.2],
        activation='relu',
        output_classes=3,
        learning_rate=0.001
    )