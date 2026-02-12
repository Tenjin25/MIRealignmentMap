# Michigan Election Realignment Project 🗳️

An interactive data visualization exploring Michigan's dramatic political transformation from 1998-2024, featuring county-level election results across 37 elections.

## 📊 Project Overview

This project analyzes **1998-2024** Michigan election data to reveal how the state evolved from a reliable "blue wall" swing state into one of America's most competitive political battlegrounds. Using interactive maps and data-driven narratives, it tracks the suburban-rural realignment that has reshaped Michigan politics.

### Key Features
- **Interactive County Maps**: Click any of Michigan's 83 counties to explore detailed results
- **26-Year Time Series**: Track political trends from 1998 through 2024
- **Multiple Contest Types**: Presidential, U.S. Senate, Governor, and other statewide races
- **3,071 County-Level Records**: Comprehensive contest results by county
- **Accessible Design**: Color-blind friendly mode and responsive mobile layout

## 🔍 Key Findings

### The Great Suburban-Rural Exchange

Michigan's political landscape underwent a dramatic transformation:

#### Presidential Election Swings (First Year → Most Recent)

- **Kent County**: -10.9% (2000) → +2.7% (2024) = **13.62-point swing toward Democrats**
- **Washtenaw County**: +12.3% (2000) → +22.8% (2024) = **10.47-point swing toward Democrats**
- **Macomb County**: +1.2% (2000) → -7.0% (2024) = **8.21-point swing toward Republicans**
- **Wayne County**: +20.4% (2000) → +15.0% (2024) = **5.37-point swing toward Republicans**
- **Oakland County**: +0.6% (2000) → +5.4% (2024) = **4.78-point swing toward Democrats**


### U.S. Senate Competitiveness

Michigan's 9 most recent U.S. Senate races demonstrate the state's swing-state status:

- **2012**: Debbie Stabenow (D) vs Pete Hoekstra (R) → Democrat by 10.75%
- **2014**: Gary Peters (D) vs Terri Lynn Land (R) → Democrat by 6.92%
- **2018**: Debbie Stabenow (D) vs John James (R) → Democrat by 3.32%
- **2020**: Gary Peters (D) vs John James (R) → Democrat by 0.86%
- **2024**: Elissa Slotkin (D) vs Mike Rogers (R) → Democrat by 0.18%


### Competitiveness Categories

The visualization classifies each county's results into 15 competitiveness categories based on the margin of victory:

- **Safe Democratic** (`D_SAFE`): Kalamazoo County - President 2024 (D by 18.04%)
- **Likely Democratic** (`D_LIKELY`): Leelanau County - President 2024 (D by 7.86%)
- **Lean Democratic** (`D_LEAN`): Genesee County - President 2024 (D by 4.26%)
- **Lean Republican** (`R_LEAN`): Eaton County - President 2024 (R by 3.19%)
- **Likely Republican** (`R_LIKELY`): Benzie County - President 2024 (R by 8.80%)
- **Safe Republican** (`R_SAFE`): Bay County - President 2024 (R by 14.90%)
- **Annihilation Democratic** (`D_ANNIHILATION`): Washtenaw County - President 2024 (D by 45.51%)
- **Annihilation Republican** (`R_ANNIHILATION`): Alcona County - President 2024 (R by 42.14%)
- **Dominant Democratic** (`D_DOMINANT`): Ingham County - President 2024 (D by 30.31%)
- **Dominant Republican** (`R_DOMINANT`): Baraga County - President 2024 (R by 30.26%)
- **Stronghold Democratic** (`D_STRONGHOLD`): Genesee County - Attorney General 1998 (D by 25.69%)
- **Stronghold Republican** (`R_STRONGHOLD`): Alger County - President 2024 (R by 20.05%)
- **Tilt Democratic** (`D_TILT`): Alpena County - Attorney General 1998 (D by 0.71%)
- **Tilt Republican** (`R_TILT`): Oakland County - Attorney General 1998 (R by 0.96%)
- **Tossup** (`TOSSUP`): Eaton County - US Senate 2024 (R by 0.28%)


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
2. **Configure Mapbox token**:
   - Copy `config.example.js` to `config.js`
   - Get a free public token from [Mapbox](https://account.mapbox.com/tokens/)
   - Add your token to `config.js`
   - **Do NOT commit `config.js`** (it's in .gitignore)
3. Open `index.html` in a modern web browser (Chrome, Firefox, Safari, Edge)
4. No build process required - pure HTML/CSS/JavaScript

### Updating Data
To add new election results:
1. Place CSV files in `data/` folder (format: `YYYYMMDD__mi__general__*.csv`)
2. Run the aggregation script:
```bash
python tools/aggregate_election_data.py
```
3. Refresh `index.html` to see updated results

## 📊 Data Statistics

- **Elections Tracked**: 37 contests
- **Years Covered**: 1998-2024 (14 election years)
- **Counties**: All 83 Michigan counties
- **County Records**: 3,071 individual county results
- **Contest Types**: Attorney General, Governor, President, Secretary of State, US Senate


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

### 1. Macomb County - The Bellwether
Once a Democratic stronghold of union autoworkers, Macomb County swung **8.21 points toward Republicans** from 2000 to 2024, epitomizing working-class realignment.

### 2. Oakland County - The Affluent Flip
Historically Republican Oakland County shifted **4.78 points toward Democrats**, reflecting college-educated suburban voters' evolving political attitudes.

### 3. Kent County - Grand Rapids Revolution
West Michigan's GOP stronghold moved **13.62 points toward Democrats**, a stunning reversal driven by educated suburbs and changing social attitudes.

### 4. Wayne County - Democratic Anchor
Despite population decline, Wayne County (including Detroit) maintains **15.0%+ Democratic margins**, providing the statewide foundation.

### 5. Rural Michigan - Red Wave
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

**Last Updated**: February 12, 2026  
**Data Through**: 2024 General Election
