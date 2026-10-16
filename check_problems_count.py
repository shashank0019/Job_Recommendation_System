import json

with open('data/Problems/problems.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f'Total problems in database file: {len(data)}')
print(f'Easy: {sum(1 for p in data if p["difficulty"] == "Easy")}')
print(f'Medium: {sum(1 for p in data if p["difficulty"] == "Medium")}')
print(f'Hard: {sum(1 for p in data if p["difficulty"] == "Hard")}')
print(f'\n✅ Backend has {len(data)} problems ready to serve!')
