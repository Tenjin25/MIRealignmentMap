"""
Update index.html with generated narratives
Replaces sections 7-10 with Michigan-specific content
"""
from pathlib import Path

script_dir = Path(__file__).parent
project_dir = script_dir.parent
narratives_file = project_dir / 'county_narratives.html'
index_file = project_dir / 'index.html'

print("Reading generated narratives...")
with open(narratives_file, 'r', encoding='utf-8') as f:
    narratives = f.read()

print("Reading index.html...")
with open(index_file, 'r', encoding='utf-8') as f:
    index_content = f.read()

# Extract sections 7-10 from narratives
# Find section 7 start (after section 6)
s7_start_marker = '<h5>7️⃣ Metro Detroit'
s7_start = narratives.find(s7_start_marker)

if s7_start == -1:
    print("ERROR: Could not find section 7 in narratives")
    exit(1)

# Back up to the opening <div class="finding-card">
s7_start = narratives.rfind('<div class="finding-card">', 0, s7_start)

# Find the end of section 10 (last section)
# Look for the closing </div> after section 10
last_section_marker = '<h5>🔟 Future Trajectory'
last_section_start = narratives.find(last_section_marker)

if last_section_start == -1:
    print("ERROR: Could not find section 10 in narratives")
    exit(1)

# Find the closing </div> for section 10
s10_end = narratives.find('\n\n', last_section_start)  # End of last section
if s10_end == -1:
    s10_end = len(narratives)

# Extract sections 7-10
new_sections_7_10 = narratives[s7_start:s10_end].strip()

print(f"Extracted {len(new_sections_7_10)} characters from narratives")

# Now find and replace in index.html
# Find section 7 heading
idx_s7_marker = '<h5>7️⃣'
idx_s7_start = index_content.find(idx_s7_marker)

if idx_s7_start == -1:
    print("ERROR: Could not find section 7 in index.html")
    exit(1)

# Back up to the opening <div class="finding-card">
idx_s7_start = index_content.rfind('<div class="finding-card">', 0, idx_s7_start)

# Find section 10 end
idx_s10_marker = '<h5>🔟'
idx_s10_start = index_content.find(idx_s10_marker)

if idx_s10_start == -1:
    print("ERROR: Could not find section 10 in index.html")
    exit(1)

# Find the closing </div> after section 10
# Look for the pattern: </div>\n        </div>\n      </div>
# This marks the end of findings section
idx_s10_end = index_content.find('        </div>\n      </div>\n      <div class="sidebar-footer"', idx_s10_start)

if idx_s10_end == -1:
    print("ERROR: Could not find end of section 10")
    exit(1)

# Back up to just include the closing </div> of section 10
idx_s10_end = index_content.rfind('</div>', idx_s7_start, idx_s10_end) + len('</div>')

print(f"Found sections 7-10 in index.html: positions {idx_s7_start} to {idx_s10_end}")

# Replace
new_index = index_content[:idx_s7_start] + new_sections_7_10 + '\n' + index_content[idx_s10_end:]

# Write output
print("Writing updated index.html...")
with open(index_file, 'w', encoding='utf-8') as f:
    f.write(new_index)

print("✓ Successfully updated index.html with Michigan-specific narratives!")
print(f"  - Replaced {idx_s10_end - idx_s7_start} characters")
print(f"  - With {len(new_sections_7_10)} characters of new content")
print("\nSections updated:")
print("  7️⃣ Metro Detroit: The Democratic Firewall Under Siege")
print("  8️⃣ Rural Michigan & the Upper Peninsula: The Great Realignment")
print("  9️⃣ Demographic and Sociological Factors: The New Dividing Lines")
print("  🔟 Future Trajectory: Michigan's Razor's Edge Politics")
