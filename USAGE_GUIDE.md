# 📖 Usage Guide - App Security Risk Predictor

## Quick Start Guide

This guide explains how to use the modular app security risk prediction system for different scenarios.

## 🚀 Installation & Setup

### 1. Basic Setup (Development)
```bash
# Clone repository
git clone <repository-url>
cd app-security-predictor

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements/development.txt
```

### 2. Production Setup
```bash
# Install only production dependencies
pip install -r requirements/production.txt
```

### 3. Minimal Setup (Core only)
```bash
# Install only core ML dependencies
pip install -r requirements/base.txt
```

## 📊 Data Collection & Generation

### Generate Synthetic Dataset
```bash
# Basic generation (5,000 samples)
python scripts/generate_data.py

# Custom generation
python scripts/generate_data.py --samples 10000 --output data/custom_dataset.csv --seed 123

# With verbose output
python scripts/generate_data.py --samples 1000 --verbose
```

### Programmatic Data Generation
```python
from src.data.collector import DataCollector

# Initialize collector
collector = DataCollector(random_seed=42)

# Generate dataset
df = collector.generate_synthetic_dataset(
    n_samples=5000,
    save_path='my_dataset.csv'
)

# Get statistics
stats = collector.get_data_statistics(df)
print(stats)
```

## 🧠 Model Training

### Command Line Training
```bash
# Basic training
python scripts/train_model.py

# Custom training with parameters
python scripts/train_model.py \
    --data my_dataset.csv \
    --epochs 100 \
    --batch-size 64 \
    --learning-rate 0.0005 \
    --output-dir models/experiment_1

# Training with data generation
python scripts/train_model.py --generate-data --samples 10000
```

### Programmatic Training
```python
import pandas as pd
from src.models.neural_network import SecurityRiskNetwork
from scripts.train_model import preprocess_data

# Load data
df = pd.read_csv('app_security_dataset.csv')

# Preprocess
X, y, scaler, encoders, features = preprocess_data(df)

# Create and train model
network = SecurityRiskNetwork(input_dim=X.shape[1])
model = network.build_model()

# Train
history = model.fit(X, y, epochs=50, validation_split=0.2)
```

## 🖥️ Web Interface

### Launch Streamlit App
```bash
# Using main entry point
streamlit run app.py

# Using modular entry point
streamlit run app_streamlit.py

# Custom port and configuration
streamlit run app.py --server.port 8080 --server.address 0.0.0.0
```

### Interface Features

#### 🏠 Home Dashboard
- Overview of dataset statistics
- Model status and performance metrics
- Risk distribution visualization
- Recent activity simulation

#### 📊 Dataset Analysis
- Interactive data exploration
- Feature correlation analysis
- Distribution visualizations
- Data quality assessment

#### 🔮 Risk Prediction
**Manual Input Mode:**
```
1. Select app category, OS, store, developer type
2. Enter app metrics (size, rating, installs)
3. Configure security features
4. Get instant risk prediction with confidence
```

**Batch Prediction Mode:**
```
1. Upload CSV file with app data
2. Preview data structure
3. Run batch predictions
4. Download results with risk scores
```

**Random Sample Mode:**
```
1. Click "Predict Random Sample"
2. View sample app details
3. See prediction results
4. Analyze risk factors
```

#### 📈 Model Training Interface
```
1. Configure training parameters
2. Start training process
3. Monitor real-time progress
4. View training history plots
5. Download trained model
```

## 🔧 Configuration

### Model Configuration
Create `config/model_config.yaml`:
```yaml
model:
  architecture:
    layers: [256, 128, 64, 32]
    dropout_rates: [0.3, 0.3, 0.2, 0.2]
    activation: 'relu'
  training:
    epochs: 50
    batch_size: 32
    learning_rate: 0.001
    early_stopping_patience: 15
```

### Data Configuration
Create `config/data_config.yaml`:
```yaml
data:
  generation:
    default_samples: 5000
    random_seed: 42
  features:
    categorical: ['category', 'os_type', 'app_store', 'developer_type']
    numerical: ['app_size_mb', 'rating', 'install_count']
  preprocessing:
    scaling_method: 'standard'
    encoding_method: 'label'
```

## 🐳 Docker Deployment

### Build Docker Image
```bash
# Create Dockerfile
cat > Dockerfile << EOF
FROM python:3.10-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements/production.txt

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
EOF

# Build image
docker build -t app-security-predictor .

# Run container
docker run -p 8501:8501 app-security-predictor
```

### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./models:/app/models
    environment:
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

## 📚 API Usage Examples

### Data Collection API
```python
from src.data.collector import DataCollector

collector = DataCollector()

# Generate specific dataset
df = collector.generate_synthetic_dataset(
    n_samples=1000,
    save_path='small_dataset.csv'
)

# Get dataset statistics
stats = collector.get_data_statistics(df)
```

### Model API
```python
from src.models.neural_network import SecurityRiskNetwork
import numpy as np

# Create model
network = SecurityRiskNetwork(input_dim=36)
model = network.build_model()

# Make predictions
X = np.random.random((10, 36))  # 10 samples, 36 features
predictions = network.predict(X)
```

### Prediction API
```python
import pandas as pd
from model import AppSecurityRiskPredictor

# Load trained model
predictor = AppSecurityRiskPredictor()
predictor.load_model()

# Prepare data
app_data = pd.DataFrame({
    'category': ['Games'],
    'os_type': ['Android'],
    # ... other features
})

# Predict
categories, confidence, probabilities = predictor.predict(app_data)
print(f"Risk: {categories[0]} (Confidence: {confidence[0]:.2%})")
```

## 🔍 Advanced Usage

### Custom Model Architecture
```python
from src.models.neural_network import SecurityRiskNetwork

# Custom architecture
network = SecurityRiskNetwork(
    input_dim=36,
    hidden_layers=[512, 256, 128, 64, 32],
    dropout_rates=[0.4, 0.3, 0.3, 0.2, 0.2],
    learning_rate=0.0001
)

model = network.build_model()
```

### Hyperparameter Tuning
```python
import itertools
from sklearn.model_selection import ParameterGrid

# Define parameter grid
param_grid = {
    'learning_rate': [0.001, 0.0005, 0.0001],
    'batch_size': [16, 32, 64],
    'hidden_layers': [
        [256, 128, 64, 32],
        [512, 256, 128, 64],
        [128, 64, 32]
    ]
}

# Grid search
best_accuracy = 0
best_params = None

for params in ParameterGrid(param_grid):
    # Train model with params
    network = SecurityRiskNetwork(
        input_dim=36,
        hidden_layers=params['hidden_layers'],
        learning_rate=params['learning_rate']
    )
    # ... training code
    
    if accuracy > best_accuracy:
        best_accuracy = accuracy
        best_params = params
```

### Batch Processing
```python
import pandas as pd
from pathlib import Path

# Process multiple files
data_dir = Path('data/batch')
results = []

for csv_file in data_dir.glob('*.csv'):
    df = pd.read_csv(csv_file)
    predictions, confidence, _ = predictor.predict(df)
    
    results.append({
        'file': csv_file.name,
        'high_risk_count': sum(1 for p in predictions if p == 'High'),
        'avg_confidence': np.mean(confidence)
    })

results_df = pd.DataFrame(results)
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Ensure src is in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Or use the provided scripts
python scripts/train_model.py  # Already handles path
```

#### 2. Memory Issues
```python
# Reduce batch size for large datasets
python scripts/train_model.py --batch-size 16

# Use data generators for very large datasets
# (Implementation in future versions)
```

#### 3. Model Loading Issues
```python
# Check model file exists
import os
if not os.path.exists('app_security_model.h5'):
    print("Model file not found. Run training first.")

# Verify TensorFlow version compatibility
import tensorflow as tf
print(f"TensorFlow version: {tf.__version__}")
```

#### 4. Streamlit Issues
```bash
# Clear Streamlit cache
streamlit cache clear

# Run with specific Python version
python3.10 -m streamlit run app.py

# Check port availability
netstat -an | grep 8501
```

## 📈 Performance Optimization

### Training Optimization
```python
# Use mixed precision training
import tensorflow as tf
tf.keras.mixed_precision.set_global_policy('mixed_float16')

# Enable GPU if available
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    tf.config.experimental.set_memory_growth(gpus[0], True)
```

### Inference Optimization
```python
# Batch predictions for efficiency
batch_size = 1000
predictions = []

for i in range(0, len(data), batch_size):
    batch = data[i:i+batch_size]
    batch_pred = predictor.predict(batch)
    predictions.extend(batch_pred)
```

## 🔐 Security Considerations

### Data Privacy
```python
# Anonymize sensitive data
df['app_id'] = df['app_id'].apply(lambda x: hash(x))

# Remove personally identifiable information
df = df.drop(['developer_name', 'app_name'], axis=1, errors='ignore')
```

### Model Security
```bash
# Verify model integrity
sha256sum app_security_model.h5

# Use secure model storage
chmod 600 app_security_model.h5
```

## 📞 Support & Resources

### Getting Help
- **Documentation**: Check README.md and STACK_BREAKDOWN.md
- **Issues**: Open GitHub issues for bugs
- **Discussions**: Use GitHub Discussions for questions

### Monitoring & Logging
```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app_security.log'),
        logging.StreamHandler()
    ]
)
```

---

**Happy Predicting! 🔒🚀**