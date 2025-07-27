import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import json
import sys
import argparse
import os
from typing import List, Dict, Optional
import logging

class WBSCRoundBasedStandingsScraper:
    def __init__(self, base_url: str, delay: float = 1.0):
        """
        Initialize scraper for WBSC tournament standings with round differentiation
        
        Args:
            base_url: Base URL of tournament standings page
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
    
    def scrape_all_rounds_standings(self) -> Dict[str, List[Dict]]:
        """Scrape standings for all tournament rounds including final standings"""
        try:
            response = self.session.get(self.base_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            all_rounds_standings = {}
            
            # Check for final standings first (for completed tournaments)
            final_standings = self._extract_final_standings(soup)
            if final_standings:
                all_rounds_standings['Final Standings'] = final_standings
                self.logger.info(f"Found Final Standings with {len(final_standings)} teams")
            
            # Find round tabs
            round_tabs = self._extract_round_tabs(soup)
            self.logger.info(f"Found {len(round_tabs)} tournament rounds")
            
            for round_name, tab_id in round_tabs.items():
                self.logger.info(f"Processing {round_name} (ID: {tab_id})")
                round_standings = self._extract_round_standings(soup, round_name, tab_id)
                all_rounds_standings[round_name] = round_standings
                
                time.sleep(self.delay)
            
            return all_rounds_standings
            
        except Exception as e:
            self.logger.error(f"Error scraping rounds standings: {e}")
            return {}
    
    def _extract_round_tabs(self, soup) -> Dict[str, str]:
        """Extract round names and their corresponding tab IDs"""
        round_tabs = {}
        
        try:
            # Find the nav-tabs container
            nav_tabs = soup.find('ul', class_='nav nav-tabs')
            
            if nav_tabs:
                # Find all tab links
                tab_links = nav_tabs.find_all('a', attrs={'data-toggle': 'tab'})
                
                for link in tab_links:
                    round_name = link.get_text(strip=True)
                    tab_href = link.get('href', '')
                    
                    if tab_href.startswith('#'):
                        tab_id = tab_href[1:]  # Remove the '#'
                        round_tabs[round_name] = tab_id
                        self.logger.info(f"Found round: {round_name} -> {tab_id}")
            
        except Exception as e:
            self.logger.error(f"Error extracting round tabs: {e}")
        
        return round_tabs
    
    def _extract_final_standings(self, soup) -> List[Dict]:
        """Extract final standings table (for completed tournaments)"""
        try:
            # Look for "Final Standings" header
            final_header = soup.find('h1', string=lambda text: text and 'final standings' in text.lower())
            
            if final_header:
                self.logger.info("Found Final Standings header")
                
                # Look for table after the header
                current = final_header
                for _ in range(5):  # Search up to 5 elements after header
                    current = current.find_next_sibling()
                    if not current:
                        break
                    
                    # Check if this element contains a table
                    table = None
                    if current.name == 'table':
                        table = current
                    else:
                        table = current.find('table', class_='table table-hover')
                    
                    if table:
                        self.logger.info("Found Final Standings table")
                        return self._extract_final_standings_from_table(table)
                
                # Alternative: look for table in the same container as header
                container = final_header.find_parent(['div', 'section'])
                if container:
                    table = container.find('table', class_='table table-hover')
                    if table:
                        self.logger.info("Found Final Standings table in container")
                        return self._extract_final_standings_from_table(table)
            
            # Alternative approach: look for tables before nav-tabs
            nav_tabs = soup.find('ul', class_='nav nav-tabs')
            if nav_tabs:
                # Check elements before the tabs
                current = nav_tabs
                for _ in range(10):
                    current = current.find_previous_sibling()
                    if not current:
                        break
                    
                    if current.name == 'table' or (current.name in ['div', 'section'] and current.find('table')):
                        table = current if current.name == 'table' else current.find('table')
                        
                        # Check if this might be final standings by looking for text content
                        table_text = table.get_text().lower()
                        if any(keyword in table_text for keyword in ['final', 'overall', 'tournament']):
                            self.logger.info("Found potential Final Standings table before tabs")
                            return self._extract_final_standings_from_table(table)
            
            self.logger.info("No Final Standings found - tournament likely ongoing")
            return []
            
        except Exception as e:
            self.logger.error(f"Error extracting final standings: {e}")
            return []
    
    def _extract_final_standings_from_table(self, table) -> List[Dict]:
        """Extract final standings data from table"""
        try:
            # Find all data rows (skip header rows)
            rows = table.find_all('tr')
            
            # Skip header rows (usually first 1-2 rows)
            data_rows = []
            for row in rows:
                cells = row.find_all(['td', 'th'])
                # Skip if row contains only th elements (header row)
                if any(cell.name == 'td' for cell in cells):
                    data_rows.append(row)
            
            final_standings = []
            
            for i, row in enumerate(data_rows):
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 6:  # Minimum: position, flag, team, W, L, T
                    team_data = self._extract_final_standings_team_data(cells, i + 1)
                    if team_data:
                        final_standings.append(team_data)
            
            return final_standings
            
        except Exception as e:
            self.logger.error(f"Error extracting final standings from table: {e}")
            return []
    
    def _extract_final_standings_team_data(self, cells, table_position: int) -> Optional[Dict]:
        """Extract team data from final standings table row"""
        try:
            # Final standings structure: Position, Flag, Team, W, L, T
            position = cells[0].get_text(strip=True)
            
            # Flag cell (cells[1]) - usually empty or contains flag image
            flag_cell = cells[1] if len(cells) > 1 else None
            team_ioc = ''
            if flag_cell:
                flag_img = flag_cell.find('img')
                if flag_img:
                    alt_text = flag_img.get('alt', '')
                    if 'flag' in alt_text.lower():
                        team_ioc = alt_text.replace(' flag', '').strip()
            
            # Team cell - contains team name and possibly IOC
            team_cell = cells[2] if len(cells) > 2 else None
            team_name = ''
            if team_cell:
                team_text = team_cell.get_text(strip=True)
                
                # Extract team name from link or text
                team_link = team_cell.find('a')
                if team_link:
                    team_name = team_link.get_text(strip=True)
                else:
                    team_name = team_text
                
                # If no IOC from flag, try to extract from team cell
                if not team_ioc and len(team_name) > 3:
                    # Look for IOC pattern (3 uppercase letters)
                    parts = team_name.split()
                    for part in parts:
                        if len(part) == 3 and part.isupper():
                            team_ioc = part
                            team_name = team_name.replace(part, '').strip()
                            break
            
            # Extract wins, losses, ties
            wins = self._parse_stat_value(cells[3].get_text(strip=True)) if len(cells) > 3 else 0
            losses = self._parse_stat_value(cells[4].get_text(strip=True)) if len(cells) > 4 else 0
            ties = self._parse_stat_value(cells[5].get_text(strip=True)) if len(cells) > 5 else 0
            
            # Calculate percentage
            total_games = wins + losses + ties
            pct = wins / total_games if total_games > 0 else 0.0
            
            return {
                'position': position,
                'team_name': team_name,
                'team_ioc': team_ioc,
                'table_number': 1,  # Final standings is always table 1
                'round': 'Final Standings',
                'group': 'Final',
                'group_full_name': 'Final Tournament Standings',
                'statistics': {
                    'wins': wins,
                    'losses': losses,
                    'ties': ties,
                    'pct': round(pct, 3),
                    'total_games': total_games
                },
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting final standings team data: {e}")
            return None
    
    def _extract_round_standings(self, soup, round_name: str, tab_id: str) -> List[Dict]:
        """Extract standings for a specific round"""
        try:
            # Find the tab pane for this round
            tab_pane = soup.find('div', {'id': tab_id, 'class': 'tab-pane'})
            
            if not tab_pane:
                self.logger.warning(f"Could not find tab pane for {round_name} (ID: {tab_id})")
                return []
            
            # Find all standings tables within this tab pane
            standings_tables = tab_pane.find_all('table', class_='table table-hover standings-print')
            
            self.logger.info(f"Found {len(standings_tables)} tables in {round_name}")
            
            round_standings = []
            
            for i, table in enumerate(standings_tables):
                table_data = self._extract_table_data(table, i + 1, round_name, tab_pane)
                if table_data:
                    round_standings.extend(table_data)
            
            self.logger.info(f"Extracted {len(round_standings)} team standings from {round_name}")
            return round_standings
            
        except Exception as e:
            self.logger.error(f"Error extracting standings for {round_name}: {e}")
            return []
    
    def _extract_table_data(self, table, table_number: int, round_name: str, tab_pane) -> List[Dict]:
        """Extract data from a single standings table"""
        try:
            # Find the group header for this table
            group_info = self._find_group_info(table, tab_pane)
            
            # Find all data rows (skip header row)
            rows = table.find_all('tr')[1:]  # Skip header
            
            table_standings = []
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 7:  # Minimum required cells
                    team_data = self._extract_team_data(cells, table_number, round_name, group_info)
                    if team_data:
                        table_standings.append(team_data)
            
            return table_standings
            
        except Exception as e:
            self.logger.error(f"Error extracting table {table_number} in {round_name}: {e}")
            return []
    
    def _find_group_info(self, table, tab_pane) -> Dict:
        """Find group information for the table"""
        group_info = {
            'group': '',
            'group_full_name': ''
        }
        
        try:
            # Look for h3 header before the table
            current = table
            for _ in range(5):  # Search up to 5 elements above
                current = current.find_previous_sibling()
                if not current:
                    break
                
                if current.name == 'h3':
                    group_text = current.get_text(strip=True)
                    group_info['group'] = group_text
                    group_info['group_full_name'] = group_text
                    break
            
            # Alternative: look for the box-container parent
            box_container = table.find_parent('div', class_='box-container')
            if box_container and not group_info['group']:
                h3 = box_container.find('h3')
                if h3:
                    group_text = h3.get_text(strip=True)
                    group_info['group'] = group_text
                    group_info['group_full_name'] = group_text
                    
        except Exception as e:
            self.logger.warning(f"Could not extract group info: {e}")
        
        return group_info
    
    def _extract_team_data(self, cells, table_number: int, round_name: str, group_info: Dict) -> Optional[Dict]:
        """Extract team data from table row cells"""
        try:
            if len(cells) < 7:
                return None
            
            # Structure: Position, Flag (empty), Team (IOC+Name), W, L, T, PCT, GB
            position = cells[0].get_text(strip=True)
            
            # Flag cell (cells[1]) - extract IOC code from image alt
            flag_cell = cells[1]
            team_ioc = ''
            flag_img = flag_cell.find('img')
            if flag_img:
                alt_text = flag_img.get('alt', '')
                if 'flag' in alt_text:
                    team_ioc = alt_text.replace(' flag', '').strip()
            
            # Team cell (cells[2]) - contains team name
            team_cell = cells[2]
            team_text = team_cell.get_text(strip=True)
            
            # Extract team name from the <small> tag
            team_name = ''
            small_tag = team_cell.find('small')
            if small_tag:
                team_name = small_tag.get_text(strip=True)
            else:
                # Fallback: parse from combined text
                if team_ioc and team_text.startswith(team_ioc):
                    team_name = team_text[len(team_ioc):].strip()
                else:
                    team_name = team_text
            
            # Extract statistics
            stats = {
                'wins': self._parse_stat_value(cells[3].get_text(strip=True)),
                'losses': self._parse_stat_value(cells[4].get_text(strip=True)),
                'ties': self._parse_stat_value(cells[5].get_text(strip=True)),
                'pct': self._parse_stat_value(cells[6].get_text(strip=True))
            }
            
            # Games behind (if available)
            if len(cells) > 7:
                stats['gb'] = self._parse_stat_value(cells[7].get_text(strip=True))
            
            return {
                'position': position,
                'team_name': team_name,
                'team_ioc': team_ioc,
                'table_number': table_number,
                'round': round_name,
                'group': group_info.get('group', ''),
                'group_full_name': group_info.get('group_full_name', ''),
                'statistics': stats,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting team data: {e}")
            return None
    
    def _parse_stat_value(self, value: str):
        """Parse a statistic value to appropriate type"""
        if not value or value == '-':
            return 0
        
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            return value
    
    def get_standings_by_round(self, all_standings: Dict[str, List[Dict]], round_name: str) -> List[Dict]:
        """Get standings for a specific round"""
        return all_standings.get(round_name, [])
    
    def get_standings_by_group(self, all_standings: Dict[str, List[Dict]], group_name: str) -> List[Dict]:
        """Get standings for a specific group across all rounds"""
        result = []
        for round_name, standings in all_standings.items():
            for standing in standings:
                if group_name.lower() in standing.get('group', '').lower():
                    result.append(standing)
        return result
    
    def save_round_based_standings(self, all_standings: Dict[str, List[Dict]], output_path: str = None, tournament_name: str = None):
        """Save round-based standings to JSON and CSV files in structured folders"""
        
        # Create structured folder name
        if not output_path:
            current_date = datetime.now().strftime('%Y-%m-%d')
            timestamp = datetime.now().strftime('%H%M%S')
            
            # Extract tournament name or use provided name
            if not tournament_name:
                tournament_name = 'tournament'
            
            # Clean tournament name for folder
            clean_tournament_name = tournament_name.replace('-', '_').replace(' ', '_')
            folder_name = f"{current_date}_{clean_tournament_name}"
            output_path = f"../outputs/{folder_name}/standings_{timestamp}"
        
        # Create output directory
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save complete structure as JSON
        json_path = f"{output_path}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(all_standings, f, indent=2, ensure_ascii=False)
        
        # Create flattened CSV with all rounds
        all_teams = []
        for round_name, standings in all_standings.items():
            for standing in standings:
                # Flatten statistics
                flat_standing = standing.copy()
                stats = standing.get('statistics', {})
                for key, value in stats.items():
                    flat_standing[f'stat_{key}'] = value
                del flat_standing['statistics']
                all_teams.append(flat_standing)
        
        # Save master CSV with all rounds
        if all_teams:
            csv_path = f"{output_path}.csv"
            df = pd.DataFrame(all_teams)
            df.to_csv(csv_path, index=False, encoding='utf-8')
        
        # Save separate files for each round
        for round_name, standings in all_standings.items():
            round_clean_name = round_name.lower().replace(' ', '_')
            round_output_path = f"{output_path}_{round_clean_name}"
            
            # Save individual JSON files
            round_json_path = f"{round_output_path}.json"
            with open(round_json_path, 'w', encoding='utf-8') as f:
                json.dump(standings, f, indent=2, ensure_ascii=False)
            
            # Save individual CSV files
            if standings:
                flat_standings = []
                for standing in standings:
                    flat_standing = standing.copy()
                    stats = standing.get('statistics', {})
                    for key, value in stats.items():
                        flat_standing[f'stat_{key}'] = value
                    del flat_standing['statistics']
                    flat_standings.append(flat_standing)
                
                round_csv_path = f"{round_output_path}.csv"
                df = pd.DataFrame(flat_standings)
                df.to_csv(round_csv_path, index=False, encoding='utf-8')
        
        self.logger.info(f"Round-based standings saved to {json_path} and related files")
    
    def print_round_summary(self, all_standings: Dict[str, List[Dict]]):
        """Print a summary of all rounds"""
        print(f"\n🏆 TOURNAMENT ROUNDS SUMMARY")
        print("=" * 60)
        
        total_teams = 0
        for round_name, standings in all_standings.items():
            print(f"\n📊 {round_name}")
            print("-" * 40)
            
            if not standings:
                print("  No data found")
                continue
            
            # Group by groups
            groups = {}
            for standing in standings:
                group = standing.get('group', 'Unknown')
                if group not in groups:
                    groups[group] = []
                groups[group].append(standing)
            
            print(f"  Groups: {len(groups)}")
            print(f"  Teams: {len(standings)}")
            total_teams += len(standings)
            
            # Show groups and their leaders
            for group_name, group_standings in groups.items():
                if group_standings:
                    # Sort by position
                    group_standings.sort(key=lambda x: int(x.get('position', 999)))
                    leader = group_standings[0]
                    stats = leader.get('statistics', {})
                    print(f"    {group_name}: {leader.get('team_ioc', '')} {leader.get('team_name', '')} ({stats.get('wins', 0)}-{stats.get('losses', 0)})")
        
        print(f"\n📈 Total teams across all rounds: {total_teams}")


# Combined scraper with round support
class WBSCCompleteRoundScraper(WBSCRoundBasedStandingsScraper):
    """Complete scraper with round-based standings and games"""
    
    def __init__(self, tournament_base_url: str, delay: float = 1.0):
        self.tournament_base_url = tournament_base_url.rstrip('/')
        standings_url = f"{self.tournament_base_url}/standings"
        
        super().__init__(standings_url, delay)
        
        # Import games scraper
        from wbsc_game_scraper import WBSCTournamentScraper
        self.games_scraper = WBSCTournamentScraper(f"{self.tournament_base_url}/schedule-and-results", delay)
    
    def scrape_complete_tournament_with_rounds(self) -> Dict:
        """Scrape complete tournament data with round-based standings"""
        print("🏆 Scraping complete tournament data with rounds...")
        
        # Scrape games
        print("📊 Scraping games and results...")
        games = self.games_scraper.scrape_all_games()
        
        # Scrape round-based standings
        print("📈 Scraping round-based standings...")
        round_standings = self.scrape_all_rounds_standings()
        
        complete_data = {
            'tournament_info': {
                'name': 'U-18 Women\'s Softball European Championship 2025',
                'base_url': self.tournament_base_url,
                'scraped_at': datetime.now().isoformat()
            },
            'games': games,
            'round_standings': round_standings,
            'summary': {
                'total_games': len(games),
                'completed_games': len([g for g in games if g.get('status') in ['F', 'F/7']]),
                'rounds': list(round_standings.keys()),
                'total_standings_entries': sum(len(standings) for standings in round_standings.values()),
                'unique_teams': len(set(
                    s.get('team_name', '') 
                    for standings in round_standings.values() 
                    for s in standings
                ))
            }
        }
        
        return complete_data


# Usage example
if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='WBSC Tournament Standings Scraper with Round Support')
    parser.add_argument('url', help='Base URL of the tournament (e.g., https://www.wbsceurope.org/en/events/tournament-name/)')
    parser.add_argument('--delay', type=float, default=1.5, help='Delay between requests in seconds (default: 1.5)')
    parser.add_argument('--output', type=str, help='Output filename prefix (without extension)')
    parser.add_argument('--mode', choices=['standings', 'complete'], default='complete', 
                       help='Scraping mode: standings only or complete tournament data (default: complete)')
    
    args = parser.parse_args()
    
    # Extract tournament name from URL for filename
    url_parts = args.url.rstrip('/').split('/')
    tournament_name = url_parts[-1] if url_parts else 'tournament'
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if args.mode == 'standings':
        # Standings only mode
        standings_url = args.url.rstrip('/') + '/standings'
        print(f"Scraping standings data from: {standings_url}")
        
        scraper = WBSCRoundBasedStandingsScraper(
            base_url=standings_url,
            delay=args.delay
        )
        
        all_rounds = scraper.scrape_all_rounds_standings()
        scraper.print_round_summary(all_rounds)
        
        # Save with structured output
        if args.output:
            # Custom output path provided
            scraper.save_round_based_standings(all_rounds, output_path=args.output, tournament_name=tournament_name)
            print(f"\n✅ Standings data saved to {args.output} folder")
        else:
            # Use structured output with date and tournament name
            scraper.save_round_based_standings(all_rounds, tournament_name=tournament_name)
            print(f"\n✅ Standings data saved to structured folders")
        
    else:
        # Complete tournament mode
        print(f"Scraping complete tournament data from: {args.url}")
        
        complete_scraper = WBSCCompleteRoundScraper(
            tournament_base_url=args.url.rstrip('/'),
            delay=args.delay
        )
        
        complete_data = complete_scraper.scrape_complete_tournament_with_rounds()
        
        print(f"\n🎯 COMPLETE TOURNAMENT WITH ROUNDS SUMMARY:")
        print(f"Games: {complete_data['summary']['total_games']}")
        print(f"Completed games: {complete_data['summary']['completed_games']}")
        print(f"Rounds: {', '.join(complete_data['summary']['rounds'])}")
        print(f"Total standings entries: {complete_data['summary']['total_standings_entries']}")
        print(f"Unique teams: {complete_data['summary']['unique_teams']}")
        
        # Save with structured output  
        if args.output:
            # Custom output path provided
            output_path = args.output
        else:
            # Use structured output with date and tournament name
            current_date = datetime.now().strftime('%Y-%m-%d')
            timestamp_now = datetime.now().strftime('%H%M%S')
            clean_tournament_name = tournament_name.replace('-', '_').replace(' ', '_')
            folder_name = f"{current_date}_{clean_tournament_name}"
            output_path = f"../outputs/{folder_name}/complete_{timestamp_now}"
        
        # Create output directory
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save complete data
        json_path = f'{output_path}.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(complete_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Complete tournament data saved to {json_path}")