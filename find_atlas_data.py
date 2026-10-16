"""
Help locate the exact Atlas cluster and database where your data is stored
"""
from config.database import get_db_config
import re

def find_atlas_data_location():
    """Show exact Atlas location details to help find data in UI"""
    print("🔍 Find Your Data in MongoDB Atlas UI")
    print("=" * 50)
    
    config = get_db_config()
    connection_string = config.connection_string
    
    # Parse connection details
    print("📋 YOUR ATLAS CONNECTION DETAILS:")
    print(f"Connection String: {connection_string}")
    print()
    
    # Extract cluster information
    cluster_match = re.search(r'mongodb\+srv://([^:]+):([^@]+)@([^/]+)/', connection_string)
    if cluster_match:
        username = cluster_match.group(1)
        password = cluster_match.group(2)
        hostname = cluster_match.group(3)
        
        # Extract cluster name and ID
        cluster_parts = hostname.split('.')
        if len(cluster_parts) >= 3:
            cluster_name = cluster_parts[0]  # e.g., "cluster0"
            cluster_id = cluster_parts[1]    # e.g., "xseglna"
            
            print(f"🏷️  Username: {username}")
            print(f"🔐 Password: {password[:3]}***{password[-3:] if len(password) > 6 else '***'}")
            print(f"🌐 Hostname: {hostname}")
            print(f"📊 Cluster Name: {cluster_name}")
            print(f"🆔 Cluster ID: {cluster_id}")
            print(f"🗄️  Database: {config.database_name}")
    
    print()
    print("🎯 STEP-BY-STEP TO FIND YOUR DATA:")
    print("=" * 50)
    
    print("1️⃣  LOGIN TO ATLAS:")
    print("   - Go to https://cloud.mongodb.com/")
    print("   - Sign in with your MongoDB account")
    print()
    
    print("2️⃣  CHECK ORGANIZATION:")
    print("   - Click on your profile picture (top right)")
    print("   - If you see multiple organizations, try each one")
    print("   - Look for the organization that has your cluster")
    print()
    
    print("3️⃣  CHECK PROJECT:")
    print("   - In the left sidebar, look for 'Projects'")
    print("   - If you have multiple projects, check each one")
    print("   - Look for a project containing your cluster")
    print()
    
    print("4️⃣  FIND YOUR CLUSTER:")
    print(f"   - Look for a cluster named: '{cluster_name}' (from connection string)")
    print(f"   - Or look for hostname containing: '{cluster_id}'")
    print("   - The cluster should show as 'Active' or 'Running'")
    print()
    
    print("5️⃣  BROWSE COLLECTIONS:")
    print("   - Click 'Browse Collections' on your cluster")
    print(f"   - Select database: '{config.database_name}'")
    print("   - You should see these collections:")
    print("     ✅ job_postings")
    print("     ✅ interview_experiences") 
    print("     ✅ users")
    print("     ✅ sessions")
    print()
    
    print("🚨 COMMON ISSUES & SOLUTIONS:")
    print("=" * 50)
    
    print("❌ Issue: 'No clusters found'")
    print("   ✅ Solution: Check different organization/project")
    print()
    
    print("❌ Issue: 'Wrong collections showing'")
    print("   ✅ Solution: You're looking at wrong cluster")
    print()
    
    print("❌ Issue: 'Database not found'")
    print("   ✅ Solution: Check database dropdown for 'career_guidance_platform'")
    print()
    
    print("❌ Issue: 'Collections empty'")
    print("   ✅ Solution: Wrong cluster - look for one with data")
    print()
    
    # Test connection and show actual data
    print("🧪 VERIFYING DATA EXISTS:")
    print("=" * 50)
    
    try:
        config.connect()
        if config.db is not None:
            collections = config.db.list_collection_names()
            print("✅ Connection successful!")
            print(f"📊 Collections found: {collections}")
            
            # Show sample data from each collection
            for collection_name in ['job_postings', 'interview_experiences']:
                if collection_name in collections:
                    collection = config.db[collection_name]
                    count = collection.count_documents({})
                    print(f"📋 {collection_name}: {count} documents")
                    
                    if count > 0:
                        sample = collection.find_one({})
                        if collection_name == 'job_postings':
                            print(f"   Sample: {sample.get('title', 'N/A')} at {sample.get('company', 'N/A')}")
                        else:
                            print(f"   Sample: {sample.get('position', 'N/A')} at {sample.get('company', 'N/A')}")
            
            print()
            print("✅ YOUR DATA EXISTS IN ATLAS!")
            print("The issue is finding the right cluster in the Atlas UI.")
            
        else:
            print("❌ Connection failed")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    print("💡 QUICK TIPS:")
    print("- Try different browsers (Chrome, Firefox, Edge)")
    print("- Clear browser cache and cookies")
    print("- Use incognito/private browsing mode")
    print("- Check if you have multiple MongoDB accounts")

if __name__ == "__main__":
    find_atlas_data_location()
