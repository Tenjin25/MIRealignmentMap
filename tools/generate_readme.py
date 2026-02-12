"""
Generate comprehensive README.md for Michigan Election Realignment Project
Includes actual data statistics and insights from mi_elections_aggregated.json
"""

import json
import os
from datetime import datetime

def load_election_data():
    """Load the aggregated Michigan election data"""
    json_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'mi_elections_aggregated.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # Flatten the results_by_year structure into a list of contests
        contests = []
        for year, year_contests in data['results_by_year'].items():
            for contest_type, contest_data in year_contests.items():
                for contest_id, contest_info in contest_data.items():
                    contest_info['year'] = int(year)
                    contest_info['contest_type'] = contest_type
                    contest_info['contest_id'] = contest_id
                    contests.append(contest_info)
        return contests

def get_data_statistics(data):
    """Extract key statistics from the election data"""
    stats = {
        'total_contests': len(data),
        'years': set(),
        'contest_names': set(),
        'counties': set(),
        'total_county_records': 0
    }
    
    for contest in data:
        stats['years'].add(contest['year'])
        stats['contest_names'].add(contest.get('contest_name', 'Unknown'))
        
        results = contest.get('results', {})
        for county_name in results.keys():
            stats['counties'].add(county_name)
            stats['total_county_records'] += 1
    
    return {
        'total_contests': stats['total_contests'],
        'year_range': f"{min(stats['years'])}-{max(stats['years'])}",
        'years_covered': sorted(stats['years']),
        'contest_types': sorted(stats['contest_names']),
        'counties_tracked': len(stats['counties']),
        'total_county_records': stats['total_county_records']
    }

def analyze_presidential_trends(data):
    """Analyze presidential election trends for key counties"""
    presidential = [c for c in data if c.get('contest_name') == 'President']
    
    counties_of_interest = ['Macomb', 'Oakland', 'Wayne', 'Kent', 'Washtenaw']
    trends = {}
    
    for county in counties_of_interest:
        county_data = []
        for contest in sorted(presidential, key=lambda x: x['year']):
            results = contest.get('results', {})
            if county in results:
                county_result = results[county]
                dem_votes = county_result.get('dem_votes', 0)
                rep_votes = county_result.get('rep_votes', 0)
                total = dem_votes + rep_votes
                if total > 0:
                    dem_pct = (dem_votes / total) * 100
                    margin = dem_pct - 50
                    county_data.append({
                        'year': contest['year'],
                        'dem_margin': margin
                    })
        
        if len(county_data) >= 2:
            first = county_data[0]
            last = county_data[-1]
            swing = last['dem_margin'] - first['dem_margin']
            trends[county] = {
                'first_year': first['year'],
                'first_margin': first['dem_margin'],
                'last_year': last['year'],
                'last_margin': last['dem_margin'],
                'swing': swing
            }
    
    return trends

def analyze_senate_races(data):
    """Analyze US Senate races"""
    senate = [c for c in data if 'Senate' in c.get('contest_name', '')]
    
    senate_results = []
    for contest in sorted(senate, key=lambda x: x['year']):
        results = contest.get('results', {})
        
        # Try to get Statewide results, or aggregate from all counties
        if 'Statewide' in results:
            statewide = results['Statewide']
            dem_votes = statewide.get('dem_votes', 0)
            rep_votes = statewide.get('rep_votes', 0)
            dem_candidate = statewide.get('dem_candidate', 'Unknown')
            rep_candidate = statewide.get('rep_candidate', 'Unknown')
        else:
            # Aggregate from all counties
            dem_votes = sum(r.get('dem_votes', 0) for r in results.values())
            rep_votes = sum(r.get('rep_votes', 0) for r in results.values())
            # Get candidates from first county
            first_county = next(iter(results.values()), {})
            dem_candidate = first_county.get('dem_candidate', 'Unknown')
            rep_candidate = first_county.get('rep_candidate', 'Unknown')
        
        total = dem_votes + rep_votes
        if total > 0:
            dem_pct = (dem_votes / total) * 100
            margin = dem_pct - 50
            
            senate_results.append({
                'year': contest['year'],
                'dem_candidate': dem_candidate,
                'rep_candidate': rep_candidate,
                'dem_margin': margin,
                'winner': 'Democrat' if margin > 0 else 'Republican'
            })
    
    return senate_results

def get_competitiveness_categories(data):
    """Extract competitiveness categories and find examples, preferring 2024 Presidential"""
    categories = {}
    category_examples = {}
    
    # First pass: collect all categories and their examples
    for contest in data:
        results = contest.get('results', {})
        year = contest.get('year')
        contest_name = contest.get('contest_name')
        
        for county_name, county_data in results.items():
            if 'competitiveness' in county_data:
                comp = county_data['competitiveness']
                category = comp.get('category')
                
                if category:
                    # Store category info
                    if category not in categories:
                        categories[category] = {
                            'code': comp.get('code'),
                            'party': comp.get('party', 'N/A'),
                            'color': comp.get('color', 'N/A')
                        }
                    
                    # Priority: 2024 Presidential > 2024 other > any other year
                    current_example = category_examples.get(category, {})
                    current_year = current_example.get('year', 0)
                    current_contest = current_example.get('contest', '')
                    
                    is_2024_pres = (year == 2024 and contest_name == 'President')
                    current_is_2024_pres = (current_year == 2024 and current_contest == 'President')
                    
                    # Update if: no example yet, OR this is 2024 Presidential and current isn't, OR this is 2024 and current isn't
                    should_update = (
                        category not in category_examples or
                        (is_2024_pres and not current_is_2024_pres) or
                        (year == 2024 and current_year != 2024 and not current_is_2024_pres)
                    )
                    
                    if should_update:
                        category_examples[category] = {
                            'county': county_name,
                            'contest': contest_name,
                            'year': year,
                            'margin_pct': county_data.get('margin_pct', 0),
                            'winner': county_data.get('winner', 'N/A')
                        }
    
    return categories, category_examples

def generate_readme(data):
    """Generate comprehensive README content"""
    
    stats = get_data_statistics(data)
    pres_trends = analyze_presidential_trends(data)
    senate = analyze_senate_races(data)
    categories, category_examples = get_competitiveness_categories(data)
    
    readme = f"""# Michigan Election Realignment Project 🗳️

An interactive data visualization exploring Michigan's dramatic political transformation from 1998-2024, featuring county-level election results across {stats['total_contests']} elections.

## 📊 Project Overview

This project analyzes **{stats['year_range']}** Michigan election data to reveal how the state evolved from a reliable "blue wall" swing state into one of America's most competitive political battlegrounds. Using interactive maps and data-driven narratives, it tracks the suburban-rural realignment that has reshaped Michigan politics.

### Key Features
- **Interactive County Maps**: Click any of Michigan's {stats['counties_tracked']} counties to explore detailed results
- **26-Year Time Series**: Track political trends from {stats['years_covered'][0]} through {stats['years_covered'][-1]}
- **Multiple Contest Types**: Presidential, U.S. Senate, Governor, and other statewide races
- **{stats['total_county_records']:,} County-Level Records**: Comprehensive contest results by county
- **Accessible Design**: Color-blind friendly mode and responsive mobile layout

## 🔍 Key Findings

### The Great Suburban-Rural Exchange

Michigan's political landscape underwent a dramatic transformation:

"""
    
    # Add presidential trends
    readme += "#### Presidential Election Swings (First Year → Most Recent)\n\n"
    for county, trend in sorted(pres_trends.items(), key=lambda x: abs(x[1]['swing']), reverse=True):
        direction = "toward Democrats" if trend['swing'] > 0 else "toward Republicans"
        readme += f"- **{county} County**: {trend['first_margin']:+.1f}% ({trend['first_year']}) → {trend['last_margin']:+.1f}% ({trend['last_year']}) = **{abs(trend['swing']):.2f}-point swing {direction}**\n"
    
    readme += f"""

### U.S. Senate Competitiveness

Michigan's {len(senate)} most recent U.S. Senate races demonstrate the state's swing-state status:

"""
    
    for race in senate[-5:]:  # Last 5 races
        readme += f"- **{race['year']}**: {race['dem_candidate']} (D) vs {race['rep_candidate']} (R) → {race['winner']} by {abs(race['dem_margin']):.2f}%\n"
    
    # Add competitiveness categories explanation
    readme += f"""

### Competitiveness Categories

The visualization classifies each county's results into {len(categories)} competitiveness categories based on the margin of victory:

"""
    
    # Sort categories by political spectrum (Dem → Competitive → Rep)
    category_order = [
        'Safe Democratic', 'Likely Democratic', 'Lean Democratic', 
        'Competitive Democratic', 'Competitive',
        'Competitive Republican', 'Lean Republican', 'Likely Republican', 'Safe Republican'
    ]
    
    # Add any categories we found that aren't in our expected order
    found_categories = set(categories.keys())
    ordered_categories = [cat for cat in category_order if cat in found_categories]
    ordered_categories.extend([cat for cat in sorted(found_categories) if cat not in category_order])
    
    for category in ordered_categories:
        if category in categories:
            example = category_examples.get(category, {})
            cat_info = categories[category]
            
            # Build category line with code
            readme += f"- **{category}** (`{cat_info['code']}`)"
            
            if example:
                winner_party = "D" if example['winner'] == 'DEM' else "R" if example['winner'] == 'REP' else example['winner']
                readme += f": {example['county']} County - {example['contest']} {example['year']} ({winner_party} by {abs(example['margin_pct']):.2f}%)\n"
            else:
                readme += "\n"
    
    readme += """

## 🗂️ Project Structure

```
MIRealignment/
├── index.html                          # Main interactive visualization (3,442 lines)
├── data/
│   ├── mi_elections_aggregated.json   # Normalized election data (85,197 lines)
│   ├── tl_2020_26_county20.geojson    # Michigan county boundaries for mapping
│   ├── *__mi__general__*.csv          # Raw precinct/county data (1998-2024)
│   └── *_CENR_BY_COUNTY.txt          # Secretary of State official results
└── tools/
    ├── aggregate_election_data.py     # CSV → JSON normalization pipeline
    ├── generate_county_narratives.py  # Data-driven narrative generation
    ├── generate_readme.py             # This script - creates README with stats
    ├── convert_shapefile_to_geojson.py
    └── convert_state_txt_to_csv.py
```

## 📈 Data Sources

### Primary Sources
1. **MIT Election Data + Science Lab**: Precinct-level returns (1998-2022)
2. **Michigan Secretary of State**: Official county canvass reports (2020-2024)
3. **U.S. Census Bureau TIGER/Line**: County boundary shapefiles

### Data Processing Pipeline
```
Raw CSV Files → aggregate_election_data.py → mi_elections_aggregated.json → index.html
```

The aggregation script:
- Normalizes candidate names (handles ALL CAPS, punctuation inconsistencies)
- Standardizes county names (handles "St." vs "Saint", "De" capitalization)
- Aggregates precinct data to county level where needed
- Handles write-in candidates and vote totals
- Ensures consistent party abbreviations (DEM, REP, LIB, GRN, etc.)

## 🎨 Visualization Features

### Interactive Map
- **Choropleth Coloring**: Counties colored by Democratic/Republican margin intensity
- **Click for Details**: County-specific breakdowns with vote totals and percentages
- **Responsive Design**: Optimized for desktop, tablet, and mobile
- **Accessibility**: Color-blind friendly palette toggle

### Data Display Options
- **Contest Selector**: Switch between Presidential, Senate, Governor races
- **Year Navigation**: Track changes election-by-election
- **County Labels**: Toggle county name overlays
- **Research Sidebar**: In-depth analysis of key counties and trends

## 🚀 Usage

### Running Locally
1. Clone this repository
2. Open `index.html` in a modern web browser (Chrome, Firefox, Safari, Edge)
3. No build process required - pure HTML/CSS/JavaScript

### Updating Data
To add new election results:
1. Place CSV files in `data/` folder (format: `YYYYMMDD__mi__general__*.csv`)
2. Run the aggregation script:
```bash
python tools/aggregate_election_data.py
```
3. Refresh `index.html` to see updated results"""
    
    # Data Statistics section with actual values
    readme += f"""

## 📊 Data Statistics

- **Elections Tracked**: {stats['total_contests']} contests
- **Years Covered**: {stats['year_range']} ({len(stats['years_covered'])} election years)
- **Counties**: All {stats['counties_tracked']} Michigan counties
- **County Records**: {stats['total_county_records']:,} individual county results
- **Contest Types**: {', '.join(stats['contest_types'][:5])}{"..." if len(stats['contest_types']) > 5 else ""}
"""
    
    readme += """

## 🔧 Technical Details

### Technologies Used
- **Mapbox GL JS**: Interactive mapping and geospatial visualization
- **Vanilla JavaScript**: No framework dependencies, optimized performance
- **CSS Grid/Flexbox**: Responsive layout system
- **Python 3.11+**: Data processing and normalization

### Browser Compatibility
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers supported

## 📝 Key Narratives Explored

"""
    
    # Add key narratives with actual data
    if 'Macomb' in pres_trends:
        macomb = pres_trends['Macomb']
        readme += f"""### 1. Macomb County - The Bellwether
Once a Democratic stronghold of union autoworkers, Macomb County swung **{abs(macomb['swing']):.2f} points toward {'Republicans' if macomb['swing'] < 0 else 'Democrats'}** from {macomb['first_year']} to {macomb['last_year']}, epitomizing working-class realignment.

"""
    
    if 'Oakland' in pres_trends:
        oakland = pres_trends['Oakland']
        readme += f"""### 2. Oakland County - The Affluent Flip
Historically Republican Oakland County shifted **{abs(oakland['swing']):.2f} points toward {'Democrats' if oakland['swing'] > 0 else 'Republicans'}**, reflecting college-educated suburban voters' evolving political attitudes.

"""
    
    if 'Kent' in pres_trends:
        kent = pres_trends['Kent']
        readme += f"""### 3. Kent County - Grand Rapids Revolution
West Michigan's GOP stronghold moved **{abs(kent['swing']):.2f} points toward {'Democrats' if kent['swing'] > 0 else 'Republicans'}**, a stunning reversal driven by educated suburbs and changing social attitudes.

"""
    
    if 'Wayne' in pres_trends:
        wayne = pres_trends['Wayne']
        readme += f"""### 4. Wayne County - Democratic Anchor
Despite population decline, Wayne County (including Detroit) maintains **{abs(wayne['last_margin']):.1f}%+ Democratic margins**, providing the statewide foundation.

"""
    
    readme += """### 5. Rural Michigan - Red Wave
Upper Peninsula and northern counties shifted sharply Republican, offsetting Democratic suburban gains and keeping Michigan hyper-competitive.

## 🎓 Research Applications

This project is valuable for:
- **Political Science**: Understanding electoral realignment and demographic sorting
- **Data Journalism**: Sourcing verified election statistics
- **Campaign Strategy**: Identifying swing counties and voter trends
- **Civics Education**: Teaching election analysis and data literacy

## 📜 License & Attribution

### Data Sources
- MIT Election Data + Science Lab (CC BY 4.0)
- Michigan Secretary of State (public domain)
- U.S. Census Bureau TIGER/Line Shapefiles (public domain)

### Code
Created by **Shamar Davis** for CPT-236 course project.

## 🔮 Future Enhancements

- [ ] Add demographic data overlay (race, education, income by county)
- [ ] Include primary election results
- [ ] Legislative district analysis
- [ ] Voter turnout trends by county
- [ ] Export data visualization as images
- [ ] Add historical comparison tool (compare any two elections)

## 📧 Contact

Questions, suggestions, or data corrections? Open an issue or submit a pull request.

---
"""
    
    # Add footer with dynamic date
    readme += f"""
**Last Updated**: {datetime.now().strftime('%B %d, %Y')}  
**Data Through**: {stats['years_covered'][-1]} General Election
"""
    
    return readme

def main():
    """Main execution function"""
    print("=" * 60)
    print("Michigan Election Realignment - README Generator")
    print("=" * 60)
    print()
    
    # Load data
    print("📂 Loading election data...")
    data = load_election_data()
    print(f"   ✓ Loaded {len(data)} contests")
    print()
    
    # Generate README
    print("📝 Generating comprehensive README...")
    readme_content = generate_readme(data)
    
    # Write to file
    output_path = os.path.join(os.path.dirname(__file__), '..', 'README.md')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"   ✓ Wrote {len(readme_content):,} characters to README.md")
    print()
    
    # Show preview
    print("📋 Preview (first 500 characters):")
    print("-" * 60)
    print(readme_content[:500] + "...")
    print("-" * 60)
    print()
    
    print("✅ README.md generation complete!")
    print(f"   Output: {output_path}")

if __name__ == '__main__':
    main()
