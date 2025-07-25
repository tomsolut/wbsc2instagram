import requests
from bs4 import BeautifulSoup
import json
import html

def debug_standings_page():
    """Debug function to analyze the WBSC standings page structure"""
    url = "https://www.wbsceurope.org/en/events/2025-u-18-womens-softball-european-championship/standings"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("=== PAGE TITLE ===")
        print(soup.title.text if soup.title else "No title found")
        
        # Find the div with data-page attribute
        data_div = soup.find('div', {'data-page': True})
        
        if data_div:
            # Get the JSON data
            data_page = data_div.get('data-page')
            
            # Decode HTML entities
            decoded_data = html.unescape(data_page)
            
            # Parse JSON
            page_data = json.loads(decoded_data)
            
            print("\n=== COMPONENT INFO ===")
            print(f"Component: {page_data.get('component')}")
            
            props = page_data.get('props', {})
            
            print(f"\n=== PROPS KEYS ===")
            for key in props.keys():
                print(f"{key}: {type(props[key])}")
                if isinstance(props[key], list):
                    print(f"  - Contains {len(props[key])} items")
                elif isinstance(props[key], dict):
                    print(f"  - Contains keys: {list(props[key].keys())[:10]}")
            
            # Look for standings-specific data
            print(f"\n=== LOOKING FOR STANDINGS DATA ===")
            possible_keys = ['standings', 'teams', 'rounds', 'groups', 'table', 'ranking']
            for key in possible_keys:
                if key in props:
                    data = props[key]
                    print(f"Found {key}: {type(data)}")
                    if isinstance(data, list) and data:
                        print(f"  First item keys: {list(data[0].keys()) if isinstance(data[0], dict) else data[0]}")
                    elif isinstance(data, dict):
                        print(f"  Dict keys: {list(data.keys())}")
            
            # Save full data for inspection
            with open('standings_debug.json', 'w', encoding='utf-8') as f:
                json.dump(page_data, f, indent=2, ensure_ascii=False)
            
            print(f"\n=== Full data saved to standings_debug.json ===")
            
            return page_data
        else:
            print("No data-page div found")
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    debug_standings_page()