#!/usr/bin/env python3
"""
Setup script for ngrok to make your Flask server publicly accessible
This allows mobile devices to scan QR codes and download files from anywhere.
"""

import os
import subprocess
import sys
import time
import requests
from urllib.parse import urlparse

def check_ngrok_installed():
    """Check if ngrok is installed"""
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ ngrok is installed")
            return True
        else:
            print("❌ ngrok is not installed or not in PATH")
            return False
    except FileNotFoundError:
        print("❌ ngrok is not installed")
        return False

def install_ngrok():
    """Install ngrok if not present"""
    print("📥 Installing ngrok...")
    
    # For Windows
    if sys.platform.startswith('win'):
        print("Please download ngrok from: https://ngrok.com/download")
        print("Extract it to a folder and add that folder to your PATH")
        return False
    
    # For macOS/Linux
    try:
        subprocess.run(['curl', '-s', 'https://ngrok-agent.s3.amazonaws.com/ngrok.asc'], check=True)
        subprocess.run(['sudo', 'apt-get', 'install', 'ngrok'], check=True)
        print("✅ ngrok installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install ngrok automatically")
        print("Please install manually from: https://ngrok.com/download")
        return False

def start_ngrok(port=5000):
    """Start ngrok tunnel"""
    print(f"🚀 Starting ngrok tunnel on port {port}...")
    
    try:
        # Start ngrok in background
        process = subprocess.Popen(
            ['ngrok', 'http', str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment for ngrok to start
        time.sleep(3)
        
        # Get the public URL
        try:
            response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
            if response.status_code == 200:
                tunnels = response.json()['tunnels']
                if tunnels:
                    public_url = tunnels[0]['public_url']
                    print(f"✅ ngrok tunnel started successfully!")
                    print(f"🌐 Public URL: {public_url}")
                    print(f"📱 Mobile devices can now access: {public_url}")
                    
                    # Update .env file with the public URL
                    update_env_file(public_url)
                    
                    return public_url, process
                else:
                    print("❌ No tunnels found")
                    process.terminate()
                    return None, None
            else:
                print("❌ Failed to get ngrok tunnel info")
                process.terminate()
                return None, None
                
        except requests.RequestException:
            print("❌ Failed to connect to ngrok API")
            process.terminate()
            return None, None
            
    except Exception as e:
        print(f"❌ Failed to start ngrok: {e}")
        return None, None

def update_env_file(public_url):
    """Update .env file with the public URL"""
    env_file = '.env'
    
    # Read existing .env file
    env_lines = []
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            env_lines = f.readlines()
    
    # Update or add PUBLIC_URL
    public_url_line = f"PUBLIC_URL={public_url}\n"
    updated = False
    
    for i, line in enumerate(env_lines):
        if line.startswith('PUBLIC_URL='):
            env_lines[i] = public_url_line
            updated = True
            break
    
    if not updated:
        env_lines.append(public_url_line)
    
    # Write back to .env file
    with open(env_file, 'w') as f:
        f.writelines(env_lines)
    
    print(f"✅ Updated .env file with PUBLIC_URL={public_url}")

def main():
    """Main setup function"""
    print("🔒 Secure File Transfer - ngrok Setup")
    print("=" * 40)
    print("This script will help you set up ngrok to make your Flask server")
    print("publicly accessible for mobile QR code scanning.")
    print()
    
    # Check if ngrok is installed
    if not check_ngrok_installed():
        print("\n📥 ngrok is required for public access.")
        install_choice = input("Would you like to install ngrok? (y/n): ").lower()
        if install_choice == 'y':
            if not install_ngrok():
                print("\n❌ Please install ngrok manually and try again.")
                return
        else:
            print("\n❌ ngrok is required for mobile access.")
            return
    
    # Start ngrok
    print("\n🚀 Starting ngrok tunnel...")
    public_url, process = start_ngrok(5000)
    
    if public_url and process:
        print("\n🎉 Setup complete!")
        print(f"📱 Mobile devices can now scan QR codes and download files from: {public_url}")
        print("\n📋 Next steps:")
        print("1. Start your Flask server: python start_server.py")
        print("2. Upload files and generate QR codes")
        print("3. Mobile devices can scan QR codes from anywhere!")
        print("\n⚠️  Note: Keep this terminal open to maintain the ngrok tunnel")
        print("   Press Ctrl+C to stop ngrok when done")
        
        try:
            # Keep the process running
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping ngrok...")
            process.terminate()
            print("✅ ngrok stopped")
    else:
        print("\n❌ Failed to start ngrok tunnel")
        print("Please check your ngrok installation and try again")

if __name__ == "__main__":
    main()
