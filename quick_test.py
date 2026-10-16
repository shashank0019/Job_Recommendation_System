import requests

# Test fullstack developer questions
response = requests.post("http://127.0.0.1:5000/interview/questions", json={
    'skills': ['React', 'Node.js', 'JavaScript'],
    'role_hint': 'fullstack developer',
    'num_questions': 2
})

print("Status:", response.status_code)
if response.status_code == 200:
    data = response.json()
    if data.get('success'):
        questions = data.get('questions', [])
        print(f"Generated {len(questions)} questions:")
        for i, q in enumerate(questions, 1):
            print(f"\nQ{i}: {q.get('text')}")
            print(f"Skills: {q.get('skills_tested')}")
            print(f"Difficulty: {q.get('difficulty')}")
    else:
        print("Error:", data.get('error'))
else:
    print("HTTP Error:", response.text)
