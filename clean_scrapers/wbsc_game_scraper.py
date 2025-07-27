import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time
import json
import html
import sys
import argparse
import os
from typing import List, Dict, Optional
import logging

class WBSCTournamentScraper:
    def __init__(self, base_url: str, delay: float = 1.0):
        """
        Initialize scraper for WBSC tournament results
        
        Args:
            base_url: Base URL of tournament (e.g., tournament/schedule-and-results)
            delay: Delay between requests in seconds
        """
        self.base_url = base_url
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def extract_react_data(self) -> Optional[Dict]:
        """Extract the React data from the WBSC page"""
        try:
            response = self.session.get(self.base_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the div with data-page attribute
            data_div = soup.find('div', {'data-page': True})
            
            if data_div:
                # Get the JSON data
                data_page = data_div.get('data-page')
                
                # Decode HTML entities
                decoded_data = html.unescape(data_page)
                
                # Parse JSON
                page_data = json.loads(decoded_data)
                
                return page_data
            else:
                self.logger.error("No data-page div found")
                return None
                
        except Exception as e:
            self.logger.error(f"Error extracting React data: {e}")
            return None
    
    def scrape_all_games(self) -> List[Dict]:
        """Scrape all games from the tournament"""
        try:
            page_data = self.extract_react_data()
            if not page_data:
                return []
            
            props = page_data.get('props', {})
            games_data = props.get('games', [])
            tournament_data = props.get('tournament', {})
            
            self.logger.info(f"Found {len(games_data)} games in tournament")
            
            processed_games = []
            
            for game in games_data:
                processed_game = self._process_game_data(game, tournament_data)
                if processed_game:
                    processed_games.append(processed_game)
            
            self.logger.info(f"Successfully processed {len(processed_games)} games")
            return processed_games
            
        except Exception as e:
            self.logger.error(f"Error scraping games: {e}")
            return []
    
    def _process_game_data(self, game: Dict, tournament: Dict) -> Optional[Dict]:
        """Process a single game from the raw data"""
        try:
            # Extract basic game info
            game_id = game.get('id')
            game_number = game.get('gamenumber')
            game_code = game.get('gamecode')
            
            # Extract teams
            home_team = game.get('homelabel', 'Unknown')
            away_team = game.get('awaylabel', 'Unknown')
            home_ioc = game.get('homeioc', '')
            away_ioc = game.get('awayioc', '')
            
            # Extract scores - total runs
            home_runs = game.get('homeruns', 0) or 0
            away_runs = game.get('awayruns', 0) or 0
            
            # Extract inning-by-inning scores
            innings_data = self._extract_innings_data(game)
            
            # Extract game status and timing
            game_status = game.get('gamestatustext', 'Unknown')
            start_time = game.get('start', '')
            start_date = game.get('start_date', '')
            
            # Extract venue information
            venue = game.get('stadium', '') or game.get('location', '')
            
            # Extract round and group info
            round_info = game.get('round', '')
            group_info = game.get('grouplabel', '') or game.get('group', '')
            
            # Extract statistics
            home_hits = game.get('homehits', 0) or 0
            away_hits = game.get('awayhits', 0) or 0
            home_errors = game.get('homeerrors', 0) or 0
            away_errors = game.get('awayerrors', 0) or 0
            
            # Extract officials
            umpires = self._extract_officials(game)
            
            return {
                'game_id': game_id,
                'game_number': game_number,
                'game_code': game_code,
                'date': start_date,
                'start_time': start_time,
                'venue': venue,
                'home_team': home_team,
                'away_team': away_team,
                'home_ioc': home_ioc,
                'away_ioc': away_ioc,
                'home_runs': home_runs,
                'away_runs': away_runs,
                'home_hits': home_hits,
                'away_hits': away_hits,
                'home_errors': home_errors,
                'away_errors': away_errors,
                'innings': innings_data,
                'status': game_status,
                'round': round_info,
                'group': group_info,
                'umpires': umpires,
                'tournament': tournament.get('name', ''),
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error processing game data: {e}")
            return None
    
    def _extract_innings_data(self, game: Dict) -> Dict:
        """Extract inning-by-inning scores"""
        innings = {'home': [], 'away': []}
        
        # Extract up to 20 innings (WBSC format supports extra innings)
        for i in range(1, 21):
            home_key = f'runshome{i}'
            away_key = f'runsaway{i}'
            
            home_runs = game.get(home_key)
            away_runs = game.get(away_key)
            
            # Stop when we hit empty innings
            if home_runs is None and away_runs is None:
                break
                
            innings['home'].append(home_runs if home_runs is not None else '')
            innings['away'].append(away_runs if away_runs is not None else '')
        
        return innings
    
    def _extract_officials(self, game: Dict) -> Dict:
        """Extract umpires and officials information"""
        officials = {
            'umpires': [],
            'scorers': [],
            'technical_commissioners': []
        }
        
        # Extract umpires (up to 7 possible positions)
        for i in range(7):
            umpire_key = f'umpire{i}name'
            umpire_name = game.get(umpire_key)
            if umpire_name:
                officials['umpires'].append(umpire_name)
        
        # Extract scorers
        for i in range(1, 5):
            scorer_key = f'scorer{i}name'
            scorer_name = game.get(scorer_key)
            if scorer_name:
                officials['scorers'].append(scorer_name)
        
        # Extract technical commissioners
        for i in range(1, 4):
            tc_key = f'tc{i}name'
            tc_name = game.get(tc_key)
            if tc_name:
                officials['technical_commissioners'].append(tc_name)
        
        return officials
    
    def get_games_by_status(self, games: List[Dict], status: str) -> List[Dict]:
        """Filter games by status (e.g., 'Final', 'Live', 'Preview')"""
        return [game for game in games if game.get('status', '').lower() == status.lower()]
    
    def get_games_by_team(self, games: List[Dict], team_name: str) -> List[Dict]:
        """Filter games by team name"""
        return [
            game for game in games 
            if team_name.lower() in game.get('home_team', '').lower() or 
               team_name.lower() in game.get('away_team', '').lower()
        ]
    
    def get_games_by_date(self, games: List[Dict], date: str) -> List[Dict]:
        """Filter games by date (YYYY-MM-DD format)"""
        return [game for game in games if game.get('date', '').startswith(date)]
    
    def save_results(self, games: List[Dict], output_path: str = None, tournament_name: str = None):
        """Save results to JSON and CSV files in structured folders"""
        
        # Create structured folder name
        if not output_path:
            current_date = datetime.now().strftime('%Y-%m-%d')
            timestamp = datetime.now().strftime('%H%M%S')
            
            # Extract tournament name from URL or use provided name
            if not tournament_name:
                tournament_name = 'tournament'
            
            # Clean tournament name for folder
            clean_tournament_name = tournament_name.replace('-', '_').replace(' ', '_')
            folder_name = f"{current_date}_{clean_tournament_name}"
            output_path = f"../outputs/{folder_name}/games_{timestamp}"
        
        # Create output directory
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
        # Save as JSON
        json_path = f"{output_path}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(games, f, indent=2, ensure_ascii=False)
            
        # Save as CSV (flatten some nested data)
        if games:
            # Prepare data for CSV (flatten nested structures)
            csv_games = []
            for game in games:
                csv_game = game.copy()
                
                # Flatten innings data
                csv_game['home_innings'] = ','.join(str(x) for x in game.get('innings', {}).get('home', []))
                csv_game['away_innings'] = ','.join(str(x) for x in game.get('innings', {}).get('away', []))
                
                # Flatten officials data
                officials = game.get('umpires', {})
                csv_game['umpires'] = ','.join(officials.get('umpires', []))
                csv_game['scorers'] = ','.join(officials.get('scorers', []))
                csv_game['technical_commissioners'] = ','.join(officials.get('technical_commissioners', []))
                
                # Remove nested structures
                del csv_game['innings']
                del csv_game['umpires']
                
                csv_games.append(csv_game)
            
            csv_path = f"{output_path}.csv"
            df = pd.DataFrame(csv_games)
            df.to_csv(csv_path, index=False, encoding='utf-8')
            
        self.logger.info(f"Results saved to {json_path} and {csv_path}")
    
    def print_summary(self, games: List[Dict]):
        """Print a summary of the scraped games"""
        if not games:
            print("No games found.")
            return
        
        print(f"\n=== TOURNAMENT SUMMARY ===")
        print(f"Total games: {len(games)}")
        
        # Group by status
        status_counts = {}
        for game in games:
            status = game.get('status', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"\nGames by status:")
        for status, count in status_counts.items():
            print(f"  {status}: {count}")
        
        # Show recent completed games
        completed_games = [g for g in games if g.get('status', '').lower() == 'final']
        if completed_games:
            print(f"\n=== RECENT COMPLETED GAMES ===")
            for game in completed_games[-5:]:  # Last 5 completed games
                print(f"{game['away_team']} {game['away_runs']}-{game['home_runs']} {game['home_team']} ({game.get('date', 'Unknown date')})")


# Usage example
if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='WBSC Tournament Scraper')
    parser.add_argument('url', help='Base URL of the tournament (e.g., https://www.wbsceurope.org/en/events/tournament-name/)')
    parser.add_argument('--delay', type=float, default=1.5, help='Delay between requests in seconds (default: 1.5)')
    parser.add_argument('--output', type=str, help='Output filename prefix (without extension)')
    
    args = parser.parse_args()
    
    # Ensure URL has trailing slash and add schedule-and-results if needed
    base_url = args.url.rstrip('/')
    if not base_url.endswith('/schedule-and-results'):
        base_url += '/schedule-and-results'
    
    print(f"Scraping tournament data from: {base_url}")
    
    # Initialize scraper
    scraper = WBSCTournamentScraper(
        base_url=base_url,
        delay=args.delay
    )
    
    # Scrape all games
    all_games = scraper.scrape_all_games()
    
    # Print summary
    scraper.print_summary(all_games)
    
    # Extract tournament name from URL
    url_parts = args.url.rstrip('/').split('/')
    tournament_name = url_parts[-1] if url_parts else 'tournament'
    
    # Save results with structured output
    if args.output:
        # Custom output path provided
        scraper.save_results(all_games, output_path=args.output, tournament_name=tournament_name)
    else:
        # Use structured output with date and tournament name
        scraper.save_results(all_games, tournament_name=tournament_name)
    
    # Examples of filtering
    if all_games:
        print(f"\n=== FILTERING EXAMPLES ===")
        
        # Get completed games
        completed = scraper.get_games_by_status(all_games, 'Final')
        print(f"Completed games: {len(completed)}")
        
        # Get games for a specific team (example)
        example_team = all_games[0]['home_team']
        team_games = scraper.get_games_by_team(all_games, example_team)
        print(f"Games for {example_team}: {len(team_games)}")
    
    print(f"\nScraping completed! Results saved to structured output folder.")