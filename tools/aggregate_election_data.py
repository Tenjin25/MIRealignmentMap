"""
Aggregate Michigan election CSV files into JSON format
Includes Presidential, US Senate, Governor, and other statewide races
Outputs in nested year/contest/county format with competitiveness categories
"""
import pandas as pd
import json
from pathlib import Path
from collections import defaultdict
import re

# Paths
script_dir = Path(__file__).parent
data_dir = script_dir.parent / 'data'
output_file = data_dir / 'mi_elections_aggregated.json'

# Color mapping for competitiveness categories
COMPETITIVENESS_MAP = {
    'Annihilation Republican': {'party': 'Republican', 'code': 'R_ANNIHILATION', 'color': '#67000d'},
    'Dominant Republican': {'party': 'Republican', 'code': 'R_DOMINANT', 'color': '#a50f15'},
    'Stronghold Republican': {'party': 'Republican', 'code': 'R_STRONGHOLD', 'color': '#cb181d'},
    'Safe Republican': {'party': 'Republican', 'code': 'R_SAFE', 'color': '#ef3b2c'},
    'Likely Republican': {'party': 'Republican', 'code': 'R_LIKELY', 'color': '#fb6a4a'},
    'Lean Republican': {'party': 'Republican', 'code': 'R_LEAN', 'color': '#fcae91'},
    'Tilt Republican': {'party': 'Republican', 'code': 'R_TILT', 'color': '#fee8c8'},
    'Tossup': {'party': 'Tossup', 'code': 'TOSSUP', 'color': '#f7f7f7'},
    'Tilt Democratic': {'party': 'Democratic', 'code': 'D_TILT', 'color': '#e1f5fe'},
    'Lean Democratic': {'party': 'Democratic', 'code': 'D_LEAN', 'color': '#c6dbef'},
    'Likely Democratic': {'party': 'Democratic', 'code': 'D_LIKELY', 'color': '#9ecae1'},
    'Safe Democratic': {'party': 'Democratic', 'code': 'D_SAFE', 'color': '#6baed6'},
    'Stronghold Democratic': {'party': 'Democratic', 'code': 'D_STRONGHOLD', 'color': '#3182bd'},
    'Dominant Democratic': {'party': 'Democratic', 'code': 'D_DOMINANT', 'color': '#08519c'},
    'Annihilation Democratic': {'party': 'Democratic', 'code': 'D_ANNIHILATION', 'color': '#08306b'},
}

# Get all CSV files
all_csv_files = sorted(data_dir.glob('*__mi__general__*.csv'))
print(f"Found {len(all_csv_files)} CSV files")

# Initialize data structure
results_by_year = {}

def normalize_county_name(name):
    """Normalize county names for consistency"""
    if pd.isna(name):
        return None
    name = str(name).strip().title()
    
    # Specific abbreviation mappings
    if 'Gd.' in name and 'Traverse' in name:
        name = 'Grand Traverse'
    
    # Ensure "St" has a period (St Joseph -> St. Joseph, St. Joseph -> St. Joseph)
    name = re.sub(r'\bSt\s+', 'St. ', name)
    
    # Remove possessive apostrophe-s (e.g., "St. Joseph's" -> "St. Joseph")
    name = re.sub(r"'S$", '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+County$', '', name, flags=re.IGNORECASE)
    return name

def normalize_candidate_name(name):
    """Normalize candidate names for consistency across different data formats"""
    if pd.isna(name):
        return ''
    
    name = str(name).strip()
    
    # Remove party prefixes like "DEM ", "REP ", etc.
    name = re.sub(r'^(DEM|REP|LIB|GRN|UST|NLP|WCP|NPA)\s+', '', name, flags=re.IGNORECASE)
    
    # Remove running mate info (e.g., "/J. D. Vance", "w/ Tim Walz")
    name = re.sub(r'\s*/.*$', '', name)  # Remove everything after "/"
    name = re.sub(r'\s+w/.*$', '', name, flags=re.IGNORECASE)  # Remove "w/ Something"
    name = re.sub(r'\s+with.*$', '', name, flags=re.IGNORECASE)  # Remove "with Something"
    
    # Remove trailing whitespace and slashes
    name = name.strip().rstrip('/')
    
    # Standardize common variations
    # Harris variations
    if 'kamala' in name.lower() and 'harris' in name.lower():
        return 'Kamala D. Harris'
    
    # Trump variations  
    if 'donald' in name.lower() and 'trump' in name.lower():
        return 'Donald J. Trump'
    
    # Biden variations
    if ('joseph' in name.lower() or 'joe' in name.lower()) and 'biden' in name.lower():
        return 'Joseph R. Biden'
    
    # Convert all-caps names to title case (e.g., "ELISSA SLOTKIN" -> "Elissa Slotkin")
    if name.isupper() and len(name) > 2:
        # Title case the name
        name = name.title()
    
    return name.strip()

def normalize_party(party):
    """Normalize party abbreviations"""
    if pd.isna(party):
        return 'Other'
    party = str(party).strip().upper()
    
    party_map = {
        'DEM': 'DEM', 'DEMOCRAT': 'DEM', 'DEMOCRATIC': 'DEM', 'D': 'DEM',
        'REP': 'REP', 'REPUBLICAN': 'REP', 'R': 'REP',
        'DFL': 'DEM',
        'LIB': 'LIB', 'LIBERTARIAN': 'LIB',
        'GRN': 'GRN', 'GREEN': 'GRN', 'GRP': 'GRN', 'GRE': 'GRN',
        'UST': 'UST', 'US TAXPAYERS': 'UST', 'U.S. TAXPAYERS': 'UST',
        'NLP': 'NLP', 'NATURAL LAW': 'NLP', 'NL': 'NLP',
        'NPA': 'NPA', 'NO PARTY AFFILIATION': 'NPA', 'NON': 'NPA', 'NONPARTISAN': 'NPA',
        'WRITE-IN': 'WRITE-IN', 'WRITEIN': 'WRITE-IN',
        'CON': 'CON', 'CONSTITUTION': 'CON',
    }
    
    return party_map.get(party, 'Other')

def infer_party_from_candidate(candidate_name, year):
    """Infer party affiliation from candidate name for records missing party data"""
    if pd.isna(candidate_name):
        return 'Other'
    
    name = str(candidate_name).strip().lower()
    
    # Michigan candidate party lookup (1998-2024)
    party_lookup = {
        # Presidential candidates
        'george w. bush': 'REP', 'george w bush': 'REP', 'george bush': 'REP',
        'al gore': 'DEM', 'albert gore': 'DEM',
        'john kerry': 'DEM', 'john f. kerry': 'DEM', 'john f kerry': 'DEM',
        'barack obama': 'DEM',
        'mitt romney': 'REP',
        'hillary clinton': 'DEM', 'hillary': 'DEM',
        'donald trump': 'REP', 'donald j. trump': 'REP', 'donald j trump': 'REP',
        'joe biden': 'DEM', 'joseph biden': 'DEM', 'joseph r. biden': 'DEM',
        'kamala harris': 'DEM',
        'ralph nader': 'GRN',
        'jill stein': 'GRN',
        'gary johnson': 'LIB',
        'david cobb': 'GRN',
        'michael badnarik': 'LIB',
        'michael anthony peroutka': 'CON',
        'walter brown': 'Other',
        
        # Michigan Governors
        'john engler': 'REP',
        'geoffrey fieger': 'DEM',
        'jennifer granholm': 'DEM', 'jennifer m. granholm': 'DEM',
        'dick posthumus': 'REP',
        'dick devos': 'REP',
        'rick snyder': 'REP',
        'mark schauer': 'DEM',
        'gretchen whitmer': 'DEM',
        'bill schuette': 'REP',
        'tudor dixon': 'REP',
        
        # US Senate
        'debbie stabenow': 'DEM', 'deborah stabenow': 'DEM',
        'spence abraham': 'REP', 'spencer abraham': 'REP',
        'carl levin': 'DEM',
        'andrew raczkowski': 'REP',
        'john james': 'REP',
        'gary peters': 'DEM',
        'terri lynn land': 'REP',
        'elissa slotkin': 'DEM',
        'mike rogers': 'REP',
        
        # Secretary of State
        'candice miller': 'REP', 'candice s. miller': 'REP',
        'terri lynn land': 'REP',
        'ruth johnson': 'REP',
        'jocelyn benson': 'DEM',
        'mary lou parks': 'DEM',
        
        # Attorney General
        'jennifer granholm': 'DEM',
        'john a. smietanka': 'REP',
        'tom leonard': 'REP',
        'dana nessel': 'DEM',
        'mike cox': 'REP',
        'bill schuette': 'REP',
        'mark totten': 'DEM',
    }
    
    return party_lookup.get(name, 'Other')

def extract_year_from_filename(filename):
    """Extract year from filename like '20161108__mi__general__precinct.csv'"""
    match = re.match(r'(\d{4})', filename)
    if match:
        return match.group(1)
    return None

def get_contest_info(office):
    """Get contest type and normalized name"""
    office_lower = office.strip().lower()
    
    if 'president' in office_lower:
        return 'president', 'President'
    elif ('u.s. senate' in office_lower or 'united states senator' in office_lower or 
          ('senate' in office_lower and 'state senate' not in office_lower and 'state' not in office_lower)):
        return 'us_senate', 'US Senate'
    elif 'governor' in office_lower and 'university' not in office_lower and 'board' not in office_lower:
        return 'governor', 'Governor'
    elif 'secretary of state' in office_lower or 'secretary state' in office_lower:
        return 'secretary_of_state', 'Secretary of State'
    elif 'attorney general' in office_lower:
        return 'attorney_general', 'Attorney General'
    elif 'treasurer' in office_lower and 'county' not in office_lower:
        return 'state_treasurer', 'State Treasurer'
    
    return None, None

def categorize_margin(margin_pct, winner_party):
    """Categorize margin into competitiveness category with color"""
    abs_margin = abs(margin_pct)
    
    is_dem = winner_party in ['DEM', 'Democratic', 'D', 'DFL']
    is_rep = winner_party in ['REP', 'Republican', 'R']
    
    if abs_margin >= 40:
        base = 'Annihilation'
    elif abs_margin >= 30:
        base = 'Dominant'
    elif abs_margin >= 20:
        base = 'Stronghold'
    elif abs_margin >= 10:
        base = 'Safe'
    elif abs_margin >= 5.5:
        base = 'Likely'
    elif abs_margin >= 1.0:
        base = 'Lean'
    elif abs_margin >= 0.5:
        base = 'Tilt'
    else:
        return {
            'category': 'Tossup',
            **COMPETITIVENESS_MAP['Tossup']
        }
    
    if is_dem:
        category = f"{base} Democratic"
    elif is_rep:
        category = f"{base} Republican"
    else:
        return {
            'category': 'Tossup',
            **COMPETITIVENESS_MAP['Tossup']
        }
    
    return {
        'category': category,
        **COMPETITIVENESS_MAP[category]
    }

# Prioritize county files over precinct files when both exist for same year
csv_files = []
years_with_county = set()

# First pass: identify years with county files
for f in all_csv_files:
    if '__county.csv' in f.name:
        year = extract_year_from_filename(f.name)
        if year:
            years_with_county.add(year)

# Second pass: add files, skipping precinct files if county file exists
for f in all_csv_files:
    filename = f.name
    year = extract_year_from_filename(filename)
    
    # If this is a precinct file and a county file exists for same year, skip it
    if '__precinct.csv' in filename and year in years_with_county:
        print(f"Skipping {filename} (county file available)")
        continue
    
    csv_files.append(f)

print(f"\nProcessing {len(csv_files)} CSV files (after filtering duplicates)\n")

# Process each CSV file
for csv_file in csv_files:
    filename = csv_file.name
    print(f"\nProcessing: {filename}")
    
    year = extract_year_from_filename(filename)
    if not year:
        print(f"  Skipping - couldn't extract year")
        continue
    
    print(f"  Year: {year}")
    
    try:
        df = pd.read_csv(csv_file, low_memory=False)
    except Exception as e:
        print(f"  Error reading file: {e}")
        continue
    
    if 'votes' in df.columns:
        df['votes'] = df['votes'].apply(lambda x: str(x).replace(' ', '').replace(',', '') if pd.notna(x) else '0')
        df['votes'] = pd.to_numeric(df['votes'], errors='coerce').fillna(0).astype(int)
    
    print(f"  Rows: {len(df)}, Columns: {list(df.columns)}")
    
    if 'office' not in df.columns:
        print(f"  Skipping - no 'office' column")
        continue
    
    df['office_lower'] = df['office'].str.lower()
    relevant_df = df[
        (df['office_lower'].str.contains('president', na=False)) |
        ((df['office_lower'].str.contains('senate', na=False) | df['office_lower'].str.contains('senator', na=False)) & 
         ~df['office_lower'].str.contains('state senate', na=False)) |
        (df['office_lower'].str.contains('governor', na=False) & 
         ~df['office_lower'].str.contains('university', na=False) & 
         ~df['office_lower'].str.contains('board', na=False)) |
        (df['office_lower'].str.contains('secretary', na=False)) |
        (df['office_lower'].str.contains('attorney general', na=False)) |
        (df['office_lower'].str.contains('treasurer', na=False) & ~df['office_lower'].str.contains('county', na=False))
    ].copy()
    
    print(f"  Relevant races: {len(relevant_df)}")
    
    if len(relevant_df) == 0:
        print(f"  No statewide races found")
        continue
    
    relevant_df['county'] = relevant_df['county'].apply(normalize_county_name)
    
    if 'candidate' in relevant_df.columns:
        # Normalize candidate names to handle formatting inconsistencies
        relevant_df['candidate'] = relevant_df['candidate'].apply(normalize_candidate_name)
        
        if 'party' in relevant_df.columns:
            relevant_df['party'] = relevant_df['party'].apply(normalize_party)
            relevant_df['party'] = relevant_df.apply(
                lambda row: infer_party_from_candidate(row['candidate'], year) 
                if pd.isna(row['party']) or row['party'] == 'Other' or row['party'] == '' 
                else row['party'],
                axis=1
            )
        else:
            relevant_df['party'] = relevant_df['candidate'].apply(lambda x: infer_party_from_candidate(x, year))
        
        county_totals = relevant_df.groupby(['county', 'office', 'party', 'candidate'])['votes'].sum().reset_index()
    else:
        def build_candidate_name(row):
            """Build candidate name from first/middle/last, handling NaN values"""
            first = row.get('first', '')
            middle = row.get('middle', '')
            last = row.get('last', '')
            
            # Convert NaN to empty string
            first = '' if pd.isna(first) else str(first)
            middle = '' if pd.isna(middle) else str(middle)
            last = '' if pd.isna(last) else str(last)
            
            # Build full name, handling multiple spaces
            parts = [p.strip() for p in [first, middle, last] if p.strip()]
            return ' '.join(parts)
        
        relevant_df['candidate'] = relevant_df.apply(build_candidate_name, axis=1)
        # Normalize candidate names here too
        relevant_df['candidate'] = relevant_df['candidate'].apply(normalize_candidate_name)
        
        if 'party' in relevant_df.columns:
            relevant_df['party'] = relevant_df['party'].apply(normalize_party)
            relevant_df['party'] = relevant_df.apply(
                lambda row: infer_party_from_candidate(row['candidate'], year) 
                if pd.isna(row['party']) or row['party'] == 'Other' or row['party'] == '' 
                else row['party'],
                axis=1
            )
        else:
            relevant_df['party'] = relevant_df['candidate'].apply(lambda x: infer_party_from_candidate(x, year))
        
        county_totals = relevant_df.groupby(['county', 'office', 'party', 'candidate'])['votes'].sum().reset_index()
    
    if year not in results_by_year:
        results_by_year[year] = {}
    
    for office in county_totals['office'].unique():
        contest_type, contest_name = get_contest_info(office)
        if not contest_type:
            continue
        
        print(f"  Contest: {contest_name} ({year})")
        
        if contest_type not in results_by_year[year]:
            results_by_year[year][contest_type] = {}
        
        contest_key = f"{contest_type}_{year}"
        if contest_key not in results_by_year[year][contest_type]:
            results_by_year[year][contest_type][contest_key] = {
                'contest_name': contest_name,
                'results': {}
            }
        
        office_data = county_totals[county_totals['office'] == office]
        
        for county in office_data['county'].unique():
            if not county:
                continue
            
            county_data = office_data[office_data['county'] == county]
            
            all_parties = {}
            for _, row in county_data.iterrows():
                party = row['party'] if pd.notna(row['party']) else 'Other'
                votes = int(row['votes']) if pd.notna(row['votes']) else 0
                if party in all_parties:
                    all_parties[party] += votes
                else:
                    all_parties[party] = votes
            
            total_votes = sum(all_parties.values())
            dem_votes = all_parties.get('DEM', 0)
            rep_votes = all_parties.get('REP', 0)
            other_votes = total_votes - dem_votes - rep_votes
            two_party_total = dem_votes + rep_votes
            
            dem_candidates = county_data[county_data['party'] == 'DEM']['candidate'].tolist()
            rep_candidates = county_data[county_data['party'] == 'REP']['candidate'].tolist()
            
            dem_candidate = dem_candidates[0] if dem_candidates else ''
            rep_candidate = rep_candidates[0] if rep_candidates else ''
            
            if dem_votes > rep_votes:
                winner = 'DEM'
                margin = dem_votes - rep_votes
            elif rep_votes > dem_votes:
                winner = 'REP'
                margin = rep_votes - dem_votes
            else:
                winner = 'TIE'
                margin = 0
            
            margin_pct = (margin / two_party_total * 100) if two_party_total > 0 else 0
            competitiveness = categorize_margin(margin_pct, winner)
            
            results_by_year[year][contest_type][contest_key]['results'][county] = {
                'county': county,
                'contest': contest_name,
                'year': year,
                'dem_candidate': dem_candidate,
                'rep_candidate': rep_candidate,
                'dem_votes': dem_votes,
                'rep_votes': rep_votes,
                'other_votes': other_votes,
                'total_votes': total_votes,
                'two_party_total': two_party_total,
                'margin': margin,
                'margin_pct': round(margin_pct, 2),
                'winner': winner,
                'competitiveness': competitiveness,
                'all_parties': all_parties
            }

print(f"\n{'='*60}")
print(f"Summary:")
print(f"  Years processed: {len(results_by_year)}")
for year in sorted(results_by_year.keys()):
    print(f"    {year}:")
    for contest_type in results_by_year[year]:
        for contest_key in results_by_year[year][contest_type]:
            county_count = len(results_by_year[year][contest_type][contest_key]['results'])
            print(f"      {contest_key}: {county_count} counties")

output_data = {'results_by_year': results_by_year}

print(f"\nSaving to: {output_file}")
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

file_size = output_file.stat().st_size / (1024 * 1024)
print(f"JSON created: {file_size:.2f} MB")
print("Done!")
