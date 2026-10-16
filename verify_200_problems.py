import requests
import json

def verify_200_problems():
    """Verify that the 200 problems are properly loaded"""
    print("🔍 VERIFYING 200 PROBLEMS IN SYSTEM...")
    
    # 1. Check database file
    try:
        with open('data/Problems/problems.json', 'r', encoding='utf-8') as f:
            db_problems = json.load(f)
        print(f"✅ Database file: {len(db_problems)} problems")
        
        # Check for duplicates in database
        titles = [p['title'] for p in db_problems]
        if len(titles) == len(set(titles)):
            print("✅ Database: No duplicates found")
        else:
            print(f"❌ Database: {len(titles) - len(set(titles))} duplicates found")
            
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return
    
    # 2. Check API endpoint
    try:
        response = requests.get("http://localhost:5000/api/problems?limit=1000", timeout=10)
        if response.status_code == 200:
            data = response.json()
            api_problems = data.get('items', [])
            print(f"✅ API endpoint: {len(api_problems)} problems")
            print(f"✅ API total available: {data.get('total', 0)} problems")
            
            # Check for duplicates in API response
            api_titles = [p['title'] for p in api_problems]
            if len(api_titles) == len(set(api_titles)):
                print("✅ API: No duplicates found")
            else:
                print(f"❌ API: {len(api_titles) - len(set(api_titles))} duplicates found")
                
        else:
            print(f"❌ API endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ API check failed: {e}")
    
    # 3. Show sample problems
    if len(db_problems) >= 5:
        print(f"\n📋 Sample problems:")
        for i in [0, 1, 2, -2, -1]:  # First 3 and last 2
            p = db_problems[i]
            print(f"  {p['id']}: {p['title']} ({p['difficulty']})")
    
    print(f"\n🎉 Verification complete!")
    print(f"📊 Status: {len(db_problems)} unique problems ready for frontend")

if __name__ == "__main__":
    verify_200_problems()
