from config.database import get_db_config
import re

def find_correct_cluster():
    """Show the exact cluster details to find in Atlas UI"""
    print("🎯 Find Your Correct Cluster in Atlas")
    print("=" * 50)
    
    config = get_db_config()
    connection_string = config.connection_string
    
    # Parse connection string
    cluster_match = re.search(r'@(cluster\d+)\.([^.]+)\.mongodb\.net', connection_string)
    
    if cluster_match:
        cluster_name = cluster_match.group(1)
        cluster_id = cluster_match.group(2)
        
        print(f"🔍 LOOK FOR THIS EXACT CLUSTER IN ATLAS:")
        print(f"   Cluster Name: {cluster_name}")
        print(f"   Cluster ID: {cluster_id}")
        print(f"   Full Hostname: {cluster_name}.{cluster_id}.mongodb.net")
        print()
        
        print("🌐 In Atlas UI, you should see:")
        print(f"   - A cluster named '{cluster_name}'")
        print(f"   - With hostname containing '{cluster_id}'")
        print(f"   - In database '{config.database_name}'")
        print(f"   - With 4 collections (not 3)")
        print()
        
        print("📋 Expected Collections in Correct Cluster:")
        print("   ✅ users (8 documents)")
        print("   ✅ sessions (20 documents)")
        print("   ✅ job_postings (2 documents) ← MISSING IN YOUR UI")
        print("   ✅ interview_experiences (2 documents) ← MISSING IN YOUR UI")
        print()
        
        print("❌ What You're Currently Seeing (Wrong Cluster):")
        print("   - users")
        print("   - sessions") 
        print("   - connection_test")
        print("   (Missing job_postings & interview_experiences)")
        print()
        
        print("🔧 ACTION STEPS:")
        print("1. In MongoDB Atlas, look for MULTIPLE clusters")
        print("2. Find the one with hostname containing 'xseglna'")
        print("3. That cluster should have 4 collections, not 3")
        print("4. If you can't find it, you might be in the wrong project/organization")
    
    else:
        print("❌ Could not parse connection string")

if __name__ == "__main__":
    find_correct_cluster()
