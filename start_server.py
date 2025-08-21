#!/usr/bin/env python3
"""
Start the Secure File Transfer Flask Server
This script runs the Flask app locally for mobile QR code scanning.
"""

import os
import sys
from app import app

if __name__ == '__main__':
    print("🔒 Secure File Transfer - Local Server")
    print("=" * 50)
    print("📱 QR Code functionality is ready!")
    print("🌐 Server will be available at: http://localhost:5000")
    print("📋 Make sure your .env file has the required AWS credentials")
    print("📱 Mobile devices can scan QR codes to download files")
    print("=" * 50)
    
    # Set debug mode for local development
    app.debug = True
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
