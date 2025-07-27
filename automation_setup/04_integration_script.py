#!/usr/bin/env python3
"""
Integration script that connects WBSC scrapers to Make.com webhook
Runs scrapers and automatically sends results to automation pipeline
"""

import json
import sys
import os
import subprocess
import requests
from datetime import datetime
from pathlib import Path

# Add clean_scrapers to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'clean_scrapers'))

def run_scrapers(tournament_url, max_posts=10):
    """Run all WBSC scrapers and collect outputs"""
    print(f"🔄 Running scrapers for: {tournament_url}")
    
    # Change to clean_scrapers directory
    scrapers_dir = Path(__file__).parent.parent / 'clean_scrapers'
    os.chdir(scrapers_dir)
    
    try:
        # Run Instagram generator script (includes all scrapers)
        cmd = [
            sys.executable, 
            'wbsc_instagram_generator.py', 
            tournament_url,
            '--max-posts', str(max_posts)
        ]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        print("✅ Scrapers completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout}")
            
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Scraper error: {e}")
        if e.stdout:
            print(f"Stdout: {e.stdout}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        return False

def find_latest_output():
    """Find the most recent JSON output from scrapers"""
    outputs_dir = Path(__file__).parent.parent / 'outputs'
    
    # Find latest dated directory
    dated_dirs = [d for d in outputs_dir.iterdir() if d.is_dir() and d.name != '.gitkeep']
    if not dated_dirs:
        print("❌ No output directories found")
        return None
    
    latest_dir = max(dated_dirs, key=lambda x: x.stat().st_mtime)
    print(f"📁 Latest output directory: {latest_dir.name}")
    
    # Find JSON files in latest directory
    json_files = list(latest_dir.glob('*instagram*.json'))
    if not json_files:
        print(f"❌ No Instagram JSON files found in {latest_dir}")
        return None
    
    latest_json = max(json_files, key=lambda x: x.stat().st_mtime)
    print(f"📄 Latest JSON file: {latest_json.name}")
    
    return latest_json

def send_to_webhook(webhook_url, json_file_path):
    """Send JSON data to Make.com webhook"""
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            payload = json.load(f)
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'WBSC-Integration/1.0'
        }
        
        print(f"📤 Sending to webhook: {webhook_url}")
        print(f"📊 Payload contains {len(payload.get('posts', []))} posts")
        
        response = requests.post(
            webhook_url,
            json=payload,
            headers=headers,
            timeout=60
        )
        
        if response.status_code == 200:
            print("✅ Successfully sent to Make.com webhook")
            return True
        else:
            print(f"❌ Webhook failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending to webhook: {e}")
        return False

def main():
    if len(sys.argv) < 3:
        print("Usage: python 04_integration_script.py <TOURNAMENT_URL> <WEBHOOK_URL> [MAX_POSTS]")
        print("\nExample:")
        print("python 04_integration_script.py \\")
        print("  'https://www.wbsceurope.org/en/events/2025-u-18-womens-softball-european-championship/' \\")
        print("  'https://hook.eu1.make.com/xxxxxxxxxxxxx' \\")
        print("  10")
        sys.exit(1)
    
    tournament_url = sys.argv[1]
    webhook_url = sys.argv[2] 
    max_posts = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    
    print("🚀 WBSC to Instagram Automation Pipeline")
    print("=" * 50)
    print(f"Tournament: {tournament_url}")
    print(f"Webhook: {webhook_url}")
    print(f"Max posts: {max_posts}")
    print("")
    
    # Step 1: Run scrapers
    if not run_scrapers(tournament_url, max_posts):
        print("❌ Pipeline failed at scraper stage")
        sys.exit(1)
    
    # Step 2: Find latest output
    json_file = find_latest_output()
    if not json_file:
        print("❌ Pipeline failed - no output JSON found")
        sys.exit(1)
    
    # Step 3: Send to webhook
    if not send_to_webhook(webhook_url, json_file):
        print("❌ Pipeline failed at webhook stage")
        sys.exit(1)
    
    print("\n🎉 Pipeline completed successfully!")
    print("Next: Check Make.com for image generation and downloads")

if __name__ == "__main__":
    main()