"""
Final Instagram automation with round-based standings
Creates sophisticated social media content differentiating between tournament rounds
"""

from wbsc_standings_scraper import WBSCCompleteRoundScraper
import json
import sys
import argparse
import os
from datetime import datetime, timedelta
from typing import List, Dict

def create_round_specific_standings_post(round_name: str, round_standings: List[Dict], max_groups=3):
    """Create Instagram post for specific round standings"""
    
    if not round_standings:
        return None
    
    # Group standings by groups
    groups = {}
    for standing in round_standings:
        group = standing.get('group', 'Unknown')
        if group not in groups:
            groups[group] = []
        groups[group].append(standing)
    
    # Sort groups and limit to most interesting ones
    sorted_groups = list(groups.items())[:max_groups]
    
    # Create standings text for each group
    standings_texts = []
    
    for group_name, group_standings in sorted_groups:
        # Sort by position
        group_standings.sort(key=lambda x: int(x.get('position', 999)))
        
        group_text = f"📊 {group_name}:\n"
        
        for standing in group_standings[:4]:  # Top 4 teams
            pos = standing.get('position', '?')
            team = standing.get('team_name', 'Unknown')
            ioc = standing.get('team_ioc', '')
            stats = standing.get('statistics', {})
            wins = stats.get('wins', 0)
            losses = stats.get('losses', 0)
            pct = stats.get('pct', 0.0)
            
            # Add medal emoji for top 3
            medal = ""
            if pos == "1":
                medal = "🥇"
            elif pos == "2":
                medal = "🥈" 
            elif pos == "3":
                medal = "🥉"
            
            group_text += f"{medal} {pos}. {ioc} {team} ({wins}-{losses})\n"
        
        standings_texts.append(group_text)
    
    all_standings_text = "\n".join(standings_texts)
    
    # Determine round emoji and description
    round_emoji = "🚀" if "Opening" in round_name else "⚡"
    round_description = "Opening Round - Pool Play" if "Opening" in round_name else "Second Round - Playoff Phase"
    
    return {
        'type': 'round_standings',
        'round_name': round_name,
        'round_description': round_description,
        'groups_count': len(sorted_groups),
        'total_teams': len(round_standings),
        'post_caption': f"""{round_emoji} {round_name.upper()} STANDINGS {round_emoji}

{round_description}

{all_standings_text}

🏆 U-18 Women's Softball European Championship 2025

#SoftballEurope #U18Womens #WBSC #{round_name.replace(' ', '')}Standings #EuropeanChampionship #Softball2025""",
        'template_data': {
            'round_name': round_name,
            'round_description': round_description,
            'standings_text': all_standings_text,
            'groups_data': sorted_groups,
            'tournament_name': 'U-18 Women\'s Softball European Championship 2025'
        }
    }

def create_round_progression_post(all_round_standings: Dict[str, List[Dict]]):
    """Create a post showing team progression between rounds"""
    
    if len(all_round_standings) < 2:
        return None
    
    # Get teams that appear in multiple rounds
    opening_teams = {}
    second_teams = {}
    
    if 'Opening Round' in all_round_standings:
        for standing in all_round_standings['Opening Round']:
            team_ioc = standing.get('team_ioc', '')
            if team_ioc:
                opening_teams[team_ioc] = standing
    
    if 'Second Round' in all_round_standings:
        for standing in all_round_standings['Second Round']:
            team_ioc = standing.get('team_ioc', '')
            if team_ioc:
                second_teams[team_ioc] = standing
    
    # Find teams that progressed
    progressed_teams = []
    for team_ioc in second_teams.keys():
        if team_ioc in opening_teams:
            opening_standing = opening_teams[team_ioc]
            second_standing = second_teams[team_ioc]
            
            progressed_teams.append({
                'team_ioc': team_ioc,
                'team_name': second_standing.get('team_name', ''),
                'opening_group': opening_standing.get('group', ''),
                'opening_record': f"{opening_standing.get('statistics', {}).get('wins', 0)}-{opening_standing.get('statistics', {}).get('losses', 0)}",
                'second_group': second_standing.get('group', ''),
                'second_record': f"{second_standing.get('statistics', {}).get('wins', 0)}-{second_standing.get('statistics', {}).get('losses', 0)}"
            })
    
    if not progressed_teams:
        return None
    
    # Create progression text
    progression_text = ""
    for team in progressed_teams[:6]:  # Top 6 teams
        progression_text += f"🎯 {team['team_ioc']} {team['team_name']}\n"
        progression_text += f"   Opening: {team['opening_group']} ({team['opening_record']})\n"
        progression_text += f"   Second: {team['second_group']} ({team['second_record']})\n\n"
    
    return {
        'type': 'round_progression',
        'progressed_teams_count': len(progressed_teams),
        'post_caption': f"""⚡ TOURNAMENT PROGRESSION ⚡

Teams advancing from Opening Round to Second Round:

{progression_text}

🚀 From pool play to playoffs!

🏆 U-18 Women's Softball European Championship 2025

#SoftballEurope #U18Womens #WBSC #TournamentProgression #Playoffs #EuropeanChampionship""",
        'template_data': {
            'progressed_teams': progressed_teams,
            'tournament_name': 'U-18 Women\'s Softball European Championship 2025'
        }
    }

def create_comprehensive_tournament_posts(complete_data: Dict, max_posts=12):
    """Create comprehensive Instagram content with round-based data"""
    posts = []
    
    games = complete_data.get('games', [])
    round_standings = complete_data.get('round_standings', {})
    
    # 1. Recent game results (40% of content)
    recent_games = get_recent_completed_games(games, days_back=2)
    game_posts_count = int(max_posts * 0.4)
    
    for game in recent_games[:game_posts_count]:
        game_post = create_enhanced_game_post(game)
        if game_post:
            posts.append(game_post)
    
    # 2. Round-specific standings (40% of content)
    standings_posts_count = int(max_posts * 0.4)
    
    for round_name, standings in round_standings.items():
        if len(posts) < game_posts_count + standings_posts_count:
            round_post = create_round_specific_standings_post(round_name, standings)
            if round_post:
                posts.append(round_post)
    
    # 3. Special content (20% of content)
    # Round progression post
    progression_post = create_round_progression_post(round_standings)
    if progression_post and len(posts) < max_posts:
        posts.append(progression_post)
    
    # Tournament summary
    if len(posts) < max_posts:
        summary_post = create_advanced_tournament_summary(complete_data)
        if summary_post:
            posts.append(summary_post)
    
    return posts

def get_recent_completed_games(games: List[Dict], days_back=2):
    """Get recent completed games"""
    cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    
    recent_games = []
    for game in games:
        game_date = game.get('date', '')
        if game_date >= cutoff_date and game.get('status') in ['F', 'F/7']:
            recent_games.append(game)
    
    # Sort by date, most recent first
    recent_games.sort(key=lambda x: x.get('date', ''), reverse=True)
    return recent_games

def create_enhanced_game_post(game):
    """Create enhanced game result post with round context"""
    home_team = game.get('home_team', '')
    away_team = game.get('away_team', '')
    home_runs = game.get('home_runs', 0)
    away_runs = game.get('away_runs', 0)
    venue = game.get('venue', '')
    round_info = game.get('round', '') or game.get('group', '')
    
    # Determine winner
    if home_runs > away_runs:
        winner = home_team
        winner_score = home_runs
        loser = away_team
        loser_score = away_runs
        winner_flag = game.get('home_ioc', '')
    else:
        winner = away_team
        winner_score = away_runs
        loser = home_team
        loser_score = home_runs
        winner_flag = game.get('away_ioc', '')
    
    # Add context about score margin
    margin = abs(home_runs - away_runs)
    margin_text = ""
    if margin == 1:
        margin_text = "⚡ Close game!"
    elif margin >= 10:
        margin_text = "💥 Dominant performance!"
    elif margin >= 5:
        margin_text = "🔥 Strong victory!"
    
    return {
        'type': 'enhanced_game_result',
        'game_data': game,
        'margin': margin,
        'post_caption': f"""🥎 FINAL RESULT 🥎

{away_team} {away_runs} - {home_runs} {home_team}

🏆 {winner} wins! {winner_flag}
{margin_text}

📍 {venue}
📅 {game.get('date', '')}
{f"🎯 {round_info}" if round_info else ""}

#SoftballEurope #U18Womens #WBSC #SoftballResults #EuropeanChampionship #Softball2025""",
        'template_data': {
            'winner_team': winner,
            'winner_score': winner_score,
            'winner_flag': winner_flag,
            'loser_team': loser,
            'loser_score': loser_score,
            'margin': margin,
            'margin_text': margin_text,
            'venue': venue,
            'date': game.get('date', ''),
            'round_info': round_info
        }
    }

def create_advanced_tournament_summary(complete_data: Dict):
    """Create advanced tournament summary with round insights"""
    summary = complete_data.get('summary', {})
    round_standings = complete_data.get('round_standings', {})
    
    # Get top performers from each round
    round_leaders = {}
    for round_name, standings in round_standings.items():
        # Find undefeated teams
        undefeated = []
        top_performers = []
        
        for standing in standings:
            stats = standing.get('statistics', {})
            losses = stats.get('losses', 0)
            wins = stats.get('wins', 0)
            
            if losses == 0 and wins > 0:
                undefeated.append(f"{standing.get('team_ioc', '')} {standing.get('team_name', '')}")
            elif wins >= 3:
                top_performers.append(f"{standing.get('team_ioc', '')} {standing.get('team_name', '')}")
        
        round_leaders[round_name] = {
            'undefeated': undefeated[:3],
            'top_performers': top_performers[:3]
        }
    
    # Create summary text
    summary_parts = []
    
    for round_name, leaders in round_leaders.items():
        if leaders['undefeated']:
            summary_parts.append(f"🔥 {round_name} - Undefeated: {', '.join(leaders['undefeated'])}")
        elif leaders['top_performers']:
            summary_parts.append(f"⭐ {round_name} - Top teams: {', '.join(leaders['top_performers'])}")
    
    leaders_text = "\n".join(summary_parts)
    
    return {
        'type': 'advanced_tournament_summary',
        'post_caption': f"""🎯 TOURNAMENT SPOTLIGHT 🎯

{leaders_text}

📊 Tournament Overview:
⚾ Total Games: {summary.get('total_games', 0)}
✅ Completed: {summary.get('completed_games', 0)}
🏆 Teams: {summary.get('unique_teams', 0)}
🚀 Rounds: {len(round_standings)}

🏆 U-18 Women's Softball European Championship 2025

#SoftballEurope #U18Womens #WBSC #TournamentUpdate #EuropeanChampionship #Softball2025""",
        'template_data': {
            'round_leaders': round_leaders,
            'tournament_stats': summary,
            'tournament_name': 'U-18 Women\'s Softball European Championship 2025'
        }
    }

def save_comprehensive_instagram_data(posts: List[Dict], filename="comprehensive_round_based_instagram.json"):
    """Save comprehensive Instagram automation data"""
    
    content_breakdown = {
        'enhanced_game_results': len([p for p in posts if p.get('type') == 'enhanced_game_result']),
        'round_standings': len([p for p in posts if p.get('type') == 'round_standings']),
        'round_progression': len([p for p in posts if p.get('type') == 'round_progression']),
        'advanced_summary': len([p for p in posts if p.get('type') == 'advanced_tournament_summary'])
    }
    
    output = {
        'generated_at': datetime.now().isoformat(),
        'total_posts': len(posts),
        'content_breakdown': content_breakdown,
        'automation_features': [
            'Round-based standings differentiation',
            'Tournament progression tracking',
            'Enhanced game result analysis',
            'Advanced performance insights',
            'Comprehensive tournament overview'
        ],
        'posts': posts
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"Comprehensive Instagram data saved to {filename}")
    return filename

def print_comprehensive_preview(posts: List[Dict]):
    """Print comprehensive preview of Instagram content"""
    print("\n🎯 COMPREHENSIVE ROUND-BASED INSTAGRAM PREVIEW")
    print("=" * 70)
    
    for i, post in enumerate(posts, 1):
        post_type = post.get('type', 'unknown').replace('_', ' ').title()
        print(f"\n--- POST {i}: {post_type} ---")
        
        if post.get('type') == 'enhanced_game_result':
            game = post.get('game_data', {})
            margin = post.get('margin', 0)
            print(f"Match: {game.get('away_team', '')} vs {game.get('home_team', '')}")
            print(f"Score: {game.get('away_runs', 0)}-{game.get('home_runs', 0)} (Margin: {margin})")
        elif post.get('type') == 'round_standings':
            print(f"Round: {post.get('round_name', '')}")
            print(f"Groups: {post.get('groups_count', 0)}, Teams: {post.get('total_teams', 0)}")
        elif post.get('type') == 'round_progression':
            print(f"Teams progressed: {post.get('progressed_teams_count', 0)}")
        elif post.get('type') == 'advanced_tournament_summary':
            print("Advanced tournament insights and statistics")
        
        # Show caption preview
        caption = post.get('post_caption', '')
        lines = caption.split('\n')[:4]
        print("Caption preview:")
        for line in lines:
            print(f"  {line}")
        print("  ...")
        print("-" * 50)

# Main execution
if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='WBSC Instagram Content Generator with Round Support')
    parser.add_argument('url', help='Base URL of the tournament (e.g., https://www.wbsceurope.org/en/events/tournament-name/)')
    parser.add_argument('--delay', type=float, default=1.5, help='Delay between requests in seconds (default: 1.5)')
    parser.add_argument('--output', type=str, help='Output filename prefix (without extension)')
    parser.add_argument('--max-posts', type=int, default=10, help='Maximum number of posts to generate (default: 10)')
    
    args = parser.parse_args()
    
    print("🏆 COMPREHENSIVE ROUND-BASED WBSC INSTAGRAM AUTOMATION")
    print("=" * 80)
    print(f"🎯 Tournament URL: {args.url}")
    
    # Initialize round-based scraper
    scraper = WBSCCompleteRoundScraper(
        tournament_base_url=args.url.rstrip('/'),
        delay=args.delay
    )
    
    # Get complete tournament data with rounds
    print("📥 Fetching complete tournament data with round differentiation...")
    complete_data = scraper.scrape_complete_tournament_with_rounds()
    
    # Create comprehensive posts
    print("📱 Creating comprehensive round-based Instagram content...")
    comprehensive_posts = create_comprehensive_tournament_posts(complete_data, max_posts=args.max_posts)
    
    # Extract tournament name from URL
    url_parts = args.url.rstrip('/').split('/')
    tournament_name = url_parts[-1] if url_parts else 'tournament'
    
    # Save with structured output
    if args.output:
        # Custom output path provided
        output_path = args.output
    else:
        # Use structured output with date and tournament name
        current_date = datetime.now().strftime('%Y-%m-%d')
        timestamp = datetime.now().strftime('%H%M%S')
        clean_tournament_name = tournament_name.replace('-', '_').replace(' ', '_')
        folder_name = f"{current_date}_{clean_tournament_name}"
        output_path = f"outputs/{folder_name}/instagram_{timestamp}"
    
    # Create output directory
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save data
    json_path = f"{output_path}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        # Structure the output data
        output_data = {
            'tournament': complete_data.get('tournament', {}),
            'generated_at': datetime.now().isoformat(),
            'total_posts': len(comprehensive_posts),
            'posts': comprehensive_posts
        }
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    # Print preview
    print_comprehensive_preview(comprehensive_posts)
    
    print(f"\n✅ COMPREHENSIVE AUTOMATION SUCCESS!")
    print(f"📄 Data saved to: {json_path}")
    print(f"📊 Generated {len(comprehensive_posts)} sophisticated Instagram posts")
    
    # Print content breakdown
    content_breakdown = {}
    for post in comprehensive_posts:
        post_type = post.get('type', 'unknown')
        content_breakdown[post_type] = content_breakdown.get(post_type, 0) + 1
    
    print(f"\n🎯 Content breakdown:")
    for content_type, count in content_breakdown.items():
        print(f"   - {content_type.replace('_', ' ').title()}: {count}")
    
    print(f"\n🚀 Features implemented:")
    print(f"   ✅ Round-based standings differentiation (Opening Round vs Second Round)")
    print(f"   ✅ Tournament progression tracking")
    print(f"   ✅ Enhanced game analysis with performance insights")
    print(f"   ✅ Comprehensive tournament overview")
    print(f"   ✅ Ready for Canva template automation")
    print(f"   ✅ Structured data for Instagram scheduling")