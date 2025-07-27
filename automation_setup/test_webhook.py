#!/usr/bin/env python3
"""
Test script for Make.com webhook integration
Tests the complete data flow from WBSC scraper to Make.com webhook
"""

import json
import requests
import sys
from datetime import datetime

def create_test_payload():
    """Create sample JSON payload matching our scraper output format"""
    return {
        "tournament": {
            "tournament_name": "2025 U-18 Women's Softball European Championship",
            "tournament_slug": "u18-womens-softball-european-2025",
            "year": "2025",
            "location": "Prague, Czech Republic",
            "start_date": "2025-07-25",
            "end_date": "2025-08-01"
        },
        "posts": [
            {
                "type": "enhanced_game_result",
                "template_data": {
                    "winner_team": "Spain",
                    "winner_score": 7,
                    "loser_team": "Germany",
                    "loser_score": 4,
                    "winner_hits": 9,
                    "loser_hits": 6,
                    "winner_errors": 1,
                    "loser_errors": 2,
                    "venue": "Softball Stadium Prague",
                    "date": "2025-07-25",
                    "round_info": "Opening Round - Game 12"
                },
                "caption": "🏆 GAME RESULT\n\nSpain defeats Germany 7-4 in an exciting Opening Round match!\n\n📊 Final Score: ESP 7 - GER 4\n⚾ Hits: ESP 9 - GER 6\n❌ Errors: ESP 1 - GER 2\n🏟️ Venue: Softball Stadium Prague\n📅 Date: July 25, 2025\n\n#U18WomensSoftball #EuropeanChampionship #WBSC #Prague2025"
            },
            {
                "type": "round_standings",
                "template_data": {
                    "round_name": "Opening Round - Group A",
                    "tournament_name": "2025 U-18 Women's Softball European Championship",
                    "standings_text": "1. Spain (3-0, .000 GB)\n2. Italy (2-1, 1.0 GB)\n3. Germany (1-2, 2.0 GB)\n4. France (0-3, 3.0 GB)"
                },
                "caption": "📊 STANDINGS UPDATE\n\nOpening Round - Group A after today's games:\n\n🥇 Spain (3-0)\n🥈 Italy (2-1)\n🥉 Germany (1-2)\n4️⃣ France (0-3)\n\n#U18WomensSoftball #Standings #Prague2025"
            },
            {
                "type": "tournament_progression", 
                "template_data": {
                    "tournament_name": "2025 U-18 Women's Softball European Championship",
                    "current_round": "Second Round",
                    "teams_advancing": "Top 2 from each group advance to Second Round",
                    "next_games": "Second Round starts July 28"
                },
                "caption": "🚀 TOURNAMENT UPDATE\n\nOpening Round completed! \n\n✅ Top 2 teams from each group advance\n📅 Second Round starts July 28\n🏆 Road to the championship continues\n\n#TournamentProgression #Prague2025 #WBSC"
            }
        ],
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "scraper_version": "2.0",
            "total_posts": 3,
            "post_types": ["enhanced_game_result", "round_standings", "tournament_progression"]
        }
    }

def test_webhook(webhook_url, payload=None):
    """Send test payload to Make.com webhook"""
    if payload is None:
        payload = create_test_payload()
    
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'WBSC-Scraper/2.0'
    }
    
    try:
        print(f"Sending test payload to: {webhook_url}")
        print(f"Payload size: {len(json.dumps(payload))} characters")
        print(f"Number of posts: {len(payload['posts'])}")
        
        response = requests.post(
            webhook_url,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.text:
            print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook test successful!")
            return True
        else:
            print(f"❌ Webhook test failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending webhook: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python test_webhook.py <WEBHOOK_URL>")
        print("\nExample:")
        print("python test_webhook.py https://hook.eu1.make.com/xxxxxxxxxxxxx")
        sys.exit(1)
    
    webhook_url = sys.argv[1]
    
    # Validate URL format
    if not webhook_url.startswith('https://hook.') or 'make.com' not in webhook_url:
        print("❌ Invalid webhook URL format. Should be: https://hook.eu1.make.com/xxxxx")
        sys.exit(1)
    
    print("🔧 WBSC Instagram Automation - Webhook Test")
    print("=" * 50)
    
    # Create and send test payload
    test_payload = create_test_payload()
    success = test_webhook(webhook_url, test_payload)
    
    if success:
        print("\n✅ Test completed successfully!")
        print("Next steps:")
        print("1. Check Make.com scenario execution log")
        print("2. Verify Bannerbear image generation")
        print("3. Check download folder for generated images")
    else:
        print("\n❌ Test failed. Check:")
        print("1. Webhook URL is correct")
        print("2. Make.com scenario is active")
        print("3. Network connectivity")

if __name__ == "__main__":
    main()