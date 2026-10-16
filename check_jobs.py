import pandas as pd

# Load first 200 jobs
df = pd.read_csv('data/unified_job_dataset.csv', nrows=200)

print(f"Total jobs loaded: {len(df)}")
print(f"\nColumns: {list(df.columns)}\n")

# Find tech jobs with Python, JavaScript, React, Node.js
tech_keywords = ['Python', 'JavaScript', 'React', 'Node', 'Java ', 'Developer', 'Engineer', 'Software']
tech_jobs = df[df['skills'].str.contains('|'.join(tech_keywords), case=False, na=False) | 
               df['title'].str.contains('|'.join(tech_keywords), case=False, na=False)]

print(f"Found {len(tech_jobs)} tech-related jobs\n")
print("Sample tech jobs:")
print("="*80)

for i, row in tech_jobs.head(10).iterrows():
    print(f"\n{i+1}. {row['title']}")
    print(f"   Company: {row['company']}")
    skills_str = str(row['skills']) if pd.notna(row['skills']) else 'N/A'
    print(f"   Skills: {skills_str[:100]}...")
    print(f"   Location: {row['location']}")

print("\n" + "="*80)
print("\nAll unique skills in first 200 jobs:")
all_skills = set()
for skills in df['skills'].dropna():
    all_skills.update([s.strip() for s in str(skills).split(',')])

tech_skills = [s for s in sorted(all_skills) if any(kw.lower() in s.lower() for kw in ['python', 'javascript', 'react', 'node', 'java', 'sql', 'database', 'web', 'api'])]
print(", ".join(tech_skills[:30]))
