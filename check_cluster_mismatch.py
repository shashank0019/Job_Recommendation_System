from config.database import get_db_config
import re

def check_cluster_mismatch():
    """Check if we're connecting to the right cluster that matches the Atlas UI"""
    print("🔍 Cluster Mismatch Investigation")
    print("=" * 50)
    
    config = get_db_config()
    
    # Show current connection string
    print("🔗 Current Connection String in Code:")
    print(f"   {config.connection_string}")
    print()
    
    # Parse the connection details
    cluster_match = re.search(r'@(cluster\d+)\.([^.]+)\.mongodb\.net', config.connection_string)
    if cluster_match:
        code_cluster_name = cluster_match.group(1)
        code_cluster_id = cluster_match.group(2)
        print(f"📋 Code Configuration:")
        print(f"   Cluster Name: {code_cluster_name}")
        print(f"   Cluster ID: {code_cluster_id}")
        print(f"   Database: {config.database_name}")
    
    print()
    print("🖥️  What Your Atlas UI Shows:")
    print("   Collections: users, sessions, connection_test")
    print("   Database: career_guidance_platform")
    print()
    
    # Try connecting and see what we actually get
    try:
        config.connect()
        if config.db is not None:
            print("✅ Connection Successful")
            print(f"📍 Connected to: {config.client.address}")
            
            # List all databases
            databases = config.client.list_database_names()
            print(f"🗂️  All Databases: {databases}")
            
            # Check our target database
            collections = config.db.list_collection_names()
            print(f"📁 Collections in '{config.database_name}': {collections}")
            
            # Count documents in each collection
            for collection_name in collections:
                count = config.db[collection_name].count_documents({})
                print(f"   📊 {collection_name}: {count} documents")
            
            print()
            print("🤔 POSSIBLE ISSUES:")
            
            if 'job_postings' in collections and 'interview_experiences' in collections:
                print("   ✅ Collections exist in code connection")
                print("   ❌ But not visible in Atlas UI")
                print("   🔍 This suggests:")
                print("      - You might be looking at a different cluster in Atlas UI")
                print("      - Or there's a browser cache issue")
                print("      - Or you're in a different MongoDB project")
            else:
                print("   ❌ Collections don't exist in code connection either")
                print("   🔍 This suggests a database connection issue")
            
            print()
            print("🛠️  SOLUTIONS TO TRY:")
            print("   1. Check if you have multiple MongoDB clusters")
            print("   2. Verify you're in the correct MongoDB project")
            print("   3. Look for a cluster with ID 'xseglna'")
            print("   4. Try accessing Atlas from a different browser")
            print("   5. Check if your Atlas account has multiple organizations")
            
        else:
            print("❌ Connection Failed")
    
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    check_cluster_mismatch()
