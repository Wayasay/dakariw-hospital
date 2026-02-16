#!/usr/bin/env python3
"""
Hospital Meal Planner - Startup Script
Run this file to start the application!
"""

import os
import sys

def main():
    print("=" * 60)
    print("🏥 HOSPITAL MEAL PLANNER - STARTING UP...")
    print("=" * 60)
    print()
    
    # Check if Flask is installed
    try:
        import flask
        print(f"✅ Flask found (version {flask.__version__})")
    except ImportError:
        print("❌ Flask not found! Installing...")
        os.system(f"{sys.executable} -m pip install Flask")
        print("✅ Flask installed successfully!")
    
    print()
    print("🚀 Starting server...")
    print()
    print("=" * 60)
    print("👉 Open your browser and go to:")
    print()
    print("   http://localhost:5000")
    print()
    print("=" * 60)
    print()
    print("Press Ctrl+C to stop the server")
    print()
    
    # Import and run the app
    from app import app
    app.run(debug=True, port=5001, host='0.0.0.0')

if __name__ == '__main__':
    main()
