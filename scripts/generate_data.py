#!/usr/bin/env python3
"""
Standalone Data Generation Script

This script generates synthetic app security datasets for training and testing.
It can be run independently of the main application.

Usage:
    python scripts/generate_data.py [options]
"""

import sys
import os
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data.collector import DataCollector


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Generate synthetic app security dataset'
    )
    
    parser.add_argument(
        '--samples', '-n',
        type=int,
        default=5000,
        help='Number of samples to generate (default: 5000)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='app_security_dataset.csv',
        help='Output file path (default: app_security_dataset.csv)'
    )
    
    parser.add_argument(
        '--seed', '-s',
        type=int,
        default=42,
        help='Random seed for reproducibility (default: 42)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    return parser.parse_args()


def main():
    """Main execution function."""
    args = parse_arguments()
    
    print("🔒 App Security Risk Predictor - Data Generation")
    print("=" * 50)
    
    # Create output directory if it doesn't exist
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Initialize data collector
    collector = DataCollector(random_seed=args.seed)
    
    print(f"📊 Generating {args.samples:,} samples...")
    print(f"📁 Output file: {args.output}")
    print(f"🎲 Random seed: {args.seed}")
    print()
    
    try:
        # Generate dataset
        df = collector.generate_synthetic_dataset(
            n_samples=args.samples,
            save_path=args.output
        )
        
        # Display statistics
        stats = collector.get_data_statistics(df)
        
        print("\n✅ Dataset Generation Complete!")
        print("=" * 50)
        print(f"📈 Total Samples: {stats['total_samples']:,}")
        print(f"📋 Features: {stats['features']}")
        print(f"💾 File Size: {stats['memory_usage_mb']:.2f} MB")
        print(f"❌ Missing Values: {stats['missing_values']}")
        
        print(f"\n📊 Risk Distribution:")
        for category, count in stats['risk_distribution'].items():
            percentage = (count / stats['total_samples']) * 100
            print(f"  {category:>6}: {count:>5,} ({percentage:>5.1f}%)")
        
        print(f"\n💾 Dataset saved to: {args.output}")
        
    except Exception as e:
        print(f"❌ Error generating dataset: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()