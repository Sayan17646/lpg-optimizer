"""
Main entry point for LPG Optimization System
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from backend.app import app
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == '__main__':
    # Development server
    port = int(os.getenv('API_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', True)
    
    print("""
    ================================================
     LPG Live Optimization System - India Scale
    ================================================
     Backend Server Starting...
     Optimization Engine: VAM + DP + Network Flow
     Frontend : http://localhost:3000
     API      : http://localhost:{}
     Real-time monitoring & live optimization
    ================================================
    """.format(port))
    
    app.run(host='0.0.0.0', port=port, debug=debug)
