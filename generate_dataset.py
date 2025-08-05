import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_app_security_dataset(n_samples=5000):
    """
    Generate a synthetic dataset for app security risk prediction.
    Features include app characteristics, permissions, network behavior, etc.
    """
    
    # App categories
    categories = ['Social', 'Games', 'Finance', 'Shopping', 'Productivity', 
                 'Education', 'Health', 'Travel', 'Entertainment', 'Business']
    
    # Operating systems
    os_types = ['Android', 'iOS', 'Windows', 'macOS', 'Linux']
    
    # App stores
    app_stores = ['Google Play', 'App Store', 'Microsoft Store', 'Third Party', 'Enterprise']
    
    # Developer types
    dev_types = ['Individual', 'Small Company', 'Large Corporation', 'Open Source', 'Unknown']
    
    data = []
    
    for i in range(n_samples):
        # Basic app info
        app_id = f"app_{i:05d}"
        category = random.choice(categories)
        os_type = random.choice(os_types)
        app_store = random.choice(app_stores)
        developer_type = random.choice(dev_types)
        
        # App metrics
        app_size_mb = np.random.lognormal(3, 1)  # Log-normal distribution for app size
        install_count = np.random.randint(100, 1000000)
        rating = np.random.uniform(1.0, 5.0)
        review_count = np.random.randint(10, 50000)
        
        # Time-based features
        days_since_release = np.random.randint(1, 3650)  # Up to 10 years
        days_since_last_update = np.random.randint(0, 730)  # Up to 2 years
        update_frequency = np.random.poisson(12)  # Updates per year
        
        # Permission features (0-1 scale)
        permissions_requested = np.random.randint(5, 50)
        sensitive_permissions = np.random.randint(0, min(15, permissions_requested))
        permission_ratio = sensitive_permissions / permissions_requested if permissions_requested > 0 else 0
        
        # Network behavior
        network_requests_per_day = np.random.lognormal(5, 2)
        external_domains_contacted = np.random.randint(1, 20)
        encrypted_traffic_ratio = np.random.uniform(0.3, 1.0)
        
        # Code analysis features
        code_obfuscation_detected = np.random.choice([0, 1], p=[0.8, 0.2])
        anti_debugging_techniques = np.random.choice([0, 1], p=[0.9, 0.1])
        suspicious_api_calls = np.random.randint(0, 10)
        
        # Behavioral features
        background_activity_score = np.random.uniform(0, 1)
        data_collection_intensity = np.random.uniform(0, 1)
        user_interaction_anomalies = np.random.uniform(0, 1)
        
        # Developer reputation
        developer_history_score = np.random.uniform(0, 1)
        previous_violations = np.random.choice([0, 1], p=[0.85, 0.15])
        
        # Security scan results
        static_analysis_score = np.random.uniform(0, 1)
        dynamic_analysis_score = np.random.uniform(0, 1)
        malware_scan_score = np.random.uniform(0, 1)
        
        # Calculate risk score based on features (for supervised learning)
        risk_factors = []
        
        # Higher risk factors
        if app_store == 'Third Party':
            risk_factors.append(0.3)
        if developer_type == 'Unknown':
            risk_factors.append(0.25)
        if days_since_last_update > 365:
            risk_factors.append(0.2)
        if permission_ratio > 0.7:
            risk_factors.append(0.3)
        if code_obfuscation_detected:
            risk_factors.append(0.4)
        if anti_debugging_techniques:
            risk_factors.append(0.5)
        if suspicious_api_calls > 5:
            risk_factors.append(0.3)
        if encrypted_traffic_ratio < 0.5:
            risk_factors.append(0.2)
        if previous_violations:
            risk_factors.append(0.4)
        if static_analysis_score < 0.3:
            risk_factors.append(0.3)
        if dynamic_analysis_score < 0.3:
            risk_factors.append(0.3)
        if malware_scan_score < 0.3:
            risk_factors.append(0.4)
        
        # Lower risk factors
        if rating > 4.0 and review_count > 1000:
            risk_factors.append(-0.2)
        if developer_type == 'Large Corporation':
            risk_factors.append(-0.1)
        if app_store in ['Google Play', 'App Store']:
            risk_factors.append(-0.1)
        if developer_history_score > 0.8:
            risk_factors.append(-0.2)
        
        # Calculate final risk score
        base_risk = 0.3  # Base risk level
        risk_score = base_risk + sum(risk_factors) + np.random.normal(0, 0.1)
        risk_score = max(0, min(1, risk_score))  # Clamp between 0 and 1
        
        # Determine risk category
        if risk_score < 0.3:
            risk_category = 'Low'
        elif risk_score < 0.6:
            risk_category = 'Medium'
        else:
            risk_category = 'High'
        
        # Create data row
        row = {
            'app_id': app_id,
            'category': category,
            'os_type': os_type,
            'app_store': app_store,
            'developer_type': developer_type,
            'app_size_mb': round(app_size_mb, 2),
            'install_count': install_count,
            'rating': round(rating, 2),
            'review_count': review_count,
            'days_since_release': days_since_release,
            'days_since_last_update': days_since_last_update,
            'update_frequency': update_frequency,
            'permissions_requested': permissions_requested,
            'sensitive_permissions': sensitive_permissions,
            'permission_ratio': round(permission_ratio, 3),
            'network_requests_per_day': round(network_requests_per_day, 2),
            'external_domains_contacted': external_domains_contacted,
            'encrypted_traffic_ratio': round(encrypted_traffic_ratio, 3),
            'code_obfuscation_detected': code_obfuscation_detected,
            'anti_debugging_techniques': anti_debugging_techniques,
            'suspicious_api_calls': suspicious_api_calls,
            'background_activity_score': round(background_activity_score, 3),
            'data_collection_intensity': round(data_collection_intensity, 3),
            'user_interaction_anomalies': round(user_interaction_anomalies, 3),
            'developer_history_score': round(developer_history_score, 3),
            'previous_violations': previous_violations,
            'static_analysis_score': round(static_analysis_score, 3),
            'dynamic_analysis_score': round(dynamic_analysis_score, 3),
            'malware_scan_score': round(malware_scan_score, 3),
            'risk_score': round(risk_score, 3),
            'risk_category': risk_category
        }
        
        data.append(row)
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    print("Generating app security dataset...")
    df = generate_app_security_dataset(5000)
    
    # Save to CSV
    df.to_csv('/workspace/app_security_dataset.csv', index=False)
    print(f"Dataset generated with {len(df)} samples")
    print(f"Saved to: app_security_dataset.csv")
    
    # Display basic statistics
    print("\nDataset Overview:")
    print(f"Shape: {df.shape}")
    print(f"\nRisk Category Distribution:")
    print(df['risk_category'].value_counts())
    print(f"\nFirst few rows:")
    print(df.head())