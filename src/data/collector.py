"""
Data Collection Module

Handles synthetic data generation and external data source integration
for app security risk prediction.
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataCollector:
    """
    Data collection and generation class for app security datasets.
    
    This class handles:
    - Synthetic data generation based on realistic patterns
    - External API integration (future implementation)
    - Data source management and configuration
    """
    
    def __init__(self, random_seed: int = 42):
        """
        Initialize the DataCollector.
        
        Args:
            random_seed: Random seed for reproducible data generation
        """
        self.random_seed = random_seed
        self.setup_random_state()
        
        # App categories and types
        self.categories = [
            'Social', 'Games', 'Finance', 'Shopping', 'Productivity', 
            'Education', 'Health', 'Travel', 'Entertainment', 'Business'
        ]
        
        self.os_types = ['Android', 'iOS', 'Windows', 'macOS', 'Linux']
        self.app_stores = [
            'Google Play', 'App Store', 'Microsoft Store', 
            'Third Party', 'Enterprise'
        ]
        self.developer_types = [
            'Individual', 'Small Company', 'Large Corporation', 
            'Open Source', 'Unknown'
        ]
        
        logger.info("DataCollector initialized with random seed: %d", random_seed)
    
    def setup_random_state(self) -> None:
        """Set up random state for reproducible generation."""
        np.random.seed(self.random_seed)
        random.seed(self.random_seed)
    
    def generate_synthetic_dataset(
        self, 
        n_samples: int = 5000,
        save_path: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Generate a synthetic dataset for app security risk prediction.
        
        Args:
            n_samples: Number of samples to generate
            save_path: Optional path to save the generated dataset
            
        Returns:
            Generated dataset as pandas DataFrame
        """
        logger.info("Generating synthetic dataset with %d samples", n_samples)
        
        data = []
        for i in range(n_samples):
            sample = self._generate_single_app_record(i)
            data.append(sample)
            
            # Progress logging
            if (i + 1) % 1000 == 0:
                logger.info("Generated %d/%d samples", i + 1, n_samples)
        
        df = pd.DataFrame(data)
        
        # Save if path provided
        if save_path:
            df.to_csv(save_path, index=False)
            logger.info("Dataset saved to: %s", save_path)
        
        logger.info("Dataset generation completed. Shape: %s", df.shape)
        return df
    
    def _generate_single_app_record(self, app_index: int) -> Dict:
        """
        Generate a single app record with realistic characteristics.
        
        Args:
            app_index: Index of the app being generated
            
        Returns:
            Dictionary containing app features
        """
        # Basic app information
        app_id = f"app_{app_index:05d}"
        category = random.choice(self.categories)
        os_type = random.choice(self.os_types)
        app_store = random.choice(self.app_stores)
        developer_type = random.choice(self.developer_types)
        
        # App metrics with realistic distributions
        app_size_mb = np.random.lognormal(3, 1)  # Log-normal for app size
        install_count = np.random.randint(100, 1000000)
        rating = np.random.uniform(1.0, 5.0)
        review_count = np.random.randint(10, 50000)
        
        # Temporal features
        days_since_release = np.random.randint(1, 3650)  # Up to 10 years
        days_since_last_update = np.random.randint(0, 730)  # Up to 2 years
        update_frequency = np.random.poisson(12)  # Updates per year
        
        # Permission analysis
        permissions_requested = np.random.randint(5, 50)
        sensitive_permissions = np.random.randint(0, min(15, permissions_requested))
        permission_ratio = (
            sensitive_permissions / permissions_requested 
            if permissions_requested > 0 else 0
        )
        
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
        
        # Calculate risk score based on security indicators
        risk_score = self._calculate_risk_score(
            app_store, developer_type, days_since_last_update,
            permission_ratio, code_obfuscation_detected,
            anti_debugging_techniques, suspicious_api_calls,
            encrypted_traffic_ratio, previous_violations,
            static_analysis_score, dynamic_analysis_score,
            malware_scan_score, rating, review_count,
            developer_history_score
        )
        
        # Determine risk category
        risk_category = self._categorize_risk(risk_score)
        
        return {
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
    
    def _calculate_risk_score(
        self, app_store: str, developer_type: str, days_since_last_update: int,
        permission_ratio: float, code_obfuscation_detected: int,
        anti_debugging_techniques: int, suspicious_api_calls: int,
        encrypted_traffic_ratio: float, previous_violations: int,
        static_analysis_score: float, dynamic_analysis_score: float,
        malware_scan_score: float, rating: float, review_count: int,
        developer_history_score: float
    ) -> float:
        """
        Calculate risk score based on security indicators.
        
        Args:
            Various app security features
            
        Returns:
            Risk score between 0 and 1
        """
        risk_factors = []
        
        # High-risk indicators (increase risk)
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
        
        # Low-risk indicators (decrease risk)
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
        
        # Clamp between 0 and 1
        return max(0, min(1, risk_score))
    
    def _categorize_risk(self, risk_score: float) -> str:
        """
        Categorize risk score into Low/Medium/High categories.
        
        Args:
            risk_score: Numerical risk score (0-1)
            
        Returns:
            Risk category string
        """
        if risk_score < 0.3:
            return 'Low'
        elif risk_score < 0.6:
            return 'Medium'
        else:
            return 'High'
    
    def load_external_data(self, source: str, **kwargs) -> pd.DataFrame:
        """
        Load data from external sources (future implementation).
        
        Args:
            source: Data source identifier
            **kwargs: Additional parameters for data loading
            
        Returns:
            Loaded dataset
            
        Raises:
            NotImplementedError: This feature is not yet implemented
        """
        logger.warning("External data loading not yet implemented")
        raise NotImplementedError("External data sources not yet supported")
    
    def get_data_statistics(self, df: pd.DataFrame) -> Dict:
        """
        Get basic statistics about the generated dataset.
        
        Args:
            df: Dataset to analyze
            
        Returns:
            Dictionary containing dataset statistics
        """
        stats = {
            'total_samples': len(df),
            'features': df.shape[1],
            'risk_distribution': df['risk_category'].value_counts().to_dict(),
            'missing_values': df.isnull().sum().sum(),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2
        }
        
        logger.info("Dataset statistics: %s", stats)
        return stats


def main():
    """Main function for standalone execution."""
    collector = DataCollector(random_seed=42)
    
    # Generate dataset
    df = collector.generate_synthetic_dataset(
        n_samples=5000,
        save_path='data/raw/app_security_dataset.csv'
    )
    
    # Display statistics
    stats = collector.get_data_statistics(df)
    print("\nDataset Statistics:")
    for key, value in stats.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()