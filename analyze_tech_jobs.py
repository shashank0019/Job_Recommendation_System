import pandas as pd

df = pd.read_csv('data/unified_job_dataset.csv')

# Filter for Software Developer / Software Engineer jobs
sw_jobs = df[df['title'].str.contains('Software Developer|Software Engineer', case=False, na=False)]

print(f"Total Software Developer/Engineer jobs: {len(sw_jobs):,}\n")
print("="*80)
print("Sample of Software jobs with their skills:")
print("="*80)

for i, row in sw_jobs.head(15).iterrows():
    print(f"\n{i+1}. {row['title']}")
    print(f"   Company: {row['company']}")
    print(f"   Location: {row['location']}")
    print(f"   Skills: {row['skills']}")
    print(f"   Experience: {row['experience_level']}")

# Check for Python/JavaScript specific jobs
print("\n" + "="*80)
print("Python-related jobs:")
print("="*80)
python_jobs = df[df['skills'].str.contains('Python', case=False, na=False) | 
                 df['title'].str.contains('Python', case=False, na=False)]
print(f"Total Python jobs: {len(python_jobs):,}")

for i, row in python_jobs.head(5).iterrows():
    print(f"\n{row['title']} - {row['company']}")
    print(f"   Skills: {row['skills'][:100]}...")

print("\n" + "="*80)
print("JavaScript/React jobs:")
print("="*80)
js_jobs = df[df['skills'].str.contains('JavaScript|React|Node', case=False, na=False) | 
             df['title'].str.contains('JavaScript|React|Frontend|Full Stack', case=False, na=False)]
print(f"Total JavaScript/React jobs: {len(js_jobs):,}")

for i, row in js_jobs.head(5).iterrows():
    print(f"\n{row['title']} - {row['company']}")
    print(f"   Skills: {row['skills'][:100]}...")
