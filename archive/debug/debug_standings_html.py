import requests
from bs4 import BeautifulSoup

def debug_standings_html():
    """Debug function to analyze the HTML structure of standings page"""
    url = "https://www.wbsceurope.org/en/events/2025-u-18-womens-softball-european-championship/standings"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("=== LOOKING FOR DATA CONTAINERS ===")
        
        # Look for different data container patterns
        selectors = [
            'div[data-page]',
            'div[data-standings]',
            'div[data-tournament]',
            'script[type="application/json"]',
            'script[data-json]',
            '.standings-container',
            '.tournament-standings',
            'table',
            '.react-root',
            '#app',
            '[data-react]'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                print(f"\nFound {len(elements)} elements with selector: {selector}")
                for i, elem in enumerate(elements[:2]):  # Show first 2
                    print(f"Element {i+1}: {str(elem)[:300]}...")
        
        print("\n=== LOOKING FOR SCRIPTS WITH DATA ===")
        scripts = soup.find_all('script')
        for i, script in enumerate(scripts):
            if script.string:
                script_content = script.string.strip()
                if any(keyword in script_content.lower() for keyword in ['standing', 'tournament', 'team', 'round']):
                    print(f"\nRelevant script {i+1}:")
                    print(script_content[:500] + "..." if len(script_content) > 500 else script_content)
        
        # Save full HTML for manual inspection
        with open('standings_page.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        
        print(f"\n=== Full HTML saved to standings_page.html ===")
        
        # Check if this is a redirect or different page structure
        print(f"\n=== PAGE INFO ===")
        print(f"Status Code: {response.status_code}")
        print(f"Final URL: {response.url}")
        print(f"Content Length: {len(response.content)}")
        
        return soup
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    debug_standings_html()