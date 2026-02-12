"""
Convert Michigan state-provided txt files to OpenElections CSV format
"""
import csv
import os

def convert_txt_to_openelections_csv(txt_file, csv_file):
    """
    Convert Michigan state txt format to OpenElections CSV format
    
    Input format (tab-separated):
    ElectionDate, OfficeCode(text), DistrictCode(Text), StatusCode, CountyCode, 
    CountyName, OfficeDescription, PartyOrder, PartyDescription, CandidateID, 
    CandidateLastName, CandidateFirstName, CandidateMiddleName, CandidateFormerName, 
    CandidateVotes, WriteIn(W)/Uncommitted(Z), Recount(*), Nominated(N)/Elected(E)
    
    Output format (CSV):
    county,office,district,party,candidate,votes
    """
    
    with open(txt_file, 'r', encoding='utf-8') as infile:
        # Read tab-separated values
        reader = csv.DictReader(infile, delimiter='\t')
        
        rows = []
        for row in reader:
            # Skip rows with missing critical data
            if not row.get('CountyName') or not row.get('OfficeDescription'):
                continue
                
            county = row['CountyName'].strip()
            office = row['OfficeDescription'].strip()
            # Handle column name format (may include "(Text)" suffix)
            district_key = 'DistrictCode(Text)' if 'DistrictCode(Text)' in row else 'DistrictCode'
            district = (row.get(district_key) or '').strip()
            
            # Clean up district - convert "00000" to empty string
            if district == "00000":
                district = ""
            
            # Map party descriptions to abbreviations
            party_map = {
                'Democratic': 'DEM',
                'Republican': 'REP',
                'Libertarian': 'LIB',
                'Green': 'GRN',
                'US Taxpayers': 'UST',
                'Natural Law': 'NLP',
                'Working Class Party': 'WCP',
                'No  Affiliation': 'NPA',
                'No Affiliation': 'NPA'
            }
            
            party = party_map.get((row.get('PartyDescription') or '').strip(), (row.get('PartyDescription') or '').strip())
            
            # Build candidate name
            first = (row.get('CandidateFirstName') or '').strip()
            last = (row.get('CandidateLastName') or '').strip()
            middle = (row.get('CandidateMiddleName') or '').strip()
            
            # Full name format
            name_parts = [first, middle, last] if middle else [first, last]
            candidate = ' '.join(filter(None, name_parts))
            
            votes = (row.get('CandidateVotes') or '0').strip()
            
            # Skip write-in candidates with 0 votes
            write_in = row.get('WriteIn(W)/Uncommitted(Z)', '').strip()
            if write_in == 'W' and votes == '0':
                continue
            
            rows.append({
                'county': county,
                'office': office,
                'district': district,
                'party': party,
                'candidate': candidate,
                'votes': votes
            })
    
    # Write to CSV
    with open(csv_file, 'w', newline='', encoding='utf-8') as outfile:
        fieldnames = ['county', 'office', 'district', 'party', 'candidate', 'votes']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"Converted {txt_file} to {csv_file}")
    print(f"Total records: {len(rows)}")


if __name__ == '__main__':
    # Get the script directory and find data directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(script_dir), 'data')
    
    # Convert 2020 file
    txt_2020 = os.path.join(data_dir, '2020STATE_GENERAL_MI_CENR_BY_COUNTY.txt')
    csv_2020 = os.path.join(data_dir, '20201103__mi__general__county.csv')
    
    # Convert 2022 file
    txt_2022 = os.path.join(data_dir, '2022STATE_GENERAL_MI_CENR_BY_COUNTY.txt')
    csv_2022 = os.path.join(data_dir, '20221108__mi__general__county.csv')
    
    # Convert 2024 file
    txt_2024 = os.path.join(data_dir, '2024STATE_GENERAL_MI_CENR_BY_COUNTY.txt')
    csv_2024 = os.path.join(data_dir, '20241105__mi__general__county.csv')
    
    if os.path.exists(txt_2020):
        convert_txt_to_openelections_csv(txt_2020, csv_2020)
    else:
        print(f"File not found: {txt_2020}")
    
    print()
    
    if os.path.exists(txt_2022):
        convert_txt_to_openelections_csv(txt_2022, csv_2022)
    else:
        print(f"File not found: {txt_2022}")
    
    print()
    
    if os.path.exists(txt_2024):
        convert_txt_to_openelections_csv(txt_2024, csv_2024)
    else:
        print(f"File not found: {txt_2024}")
