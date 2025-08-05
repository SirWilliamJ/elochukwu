#!/usr/bin/env python3
"""
Main Streamlit Application Entry Point

This is the main entry point for the Streamlit web interface.
It uses the modular architecture for better maintainability.

Usage:
    streamlit run app_streamlit.py
"""

import sys
import os
from pathlib import Path

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Import the original app functionality
from app import main

if __name__ == "__main__":
    main()