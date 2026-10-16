from config.database import get_db_config
import re

def show_atlas_connection_info():
    """Show exact Atlas connection details to match with UI"""
    print("🔍 MongoDB Atlas Connection Information")
    print("=" * 50)
    
    config = get_db_config()
    config.connect()
    
    if config.db is not None:
        # Parse connection string to get cluster info
        connection_string = config.connection_string
        print(f"🔗 Full Connection String:")
        print(f"   {connection_string}")
        print()
        
        # Extract cluster name from connection string
        cluster_match = re.search(r'@(cluster\d+)\.([^.]+)\.mongodb\.net', connection_string)
        if cluster_match:
            cluster_name = cluster_match.group(1)
            cluster_id = cluster_match.group(2)
            print(f"🏷️  Cluster Name: {cluster_name}")
            print(f"🆔 Cluster ID: {cluster_id}")
        
        print(f"🗄️  Database Name: {config.database_name}")
        print(f"📍 Current Connection: {config.client.address}")
        print()
        
        # Show all databases on this cluster
        print("📂 All Databases on This Cluster:")
        try:
            databases = config.client.list_database_names()
            for db_name in databases:
                if db_name == config.database_name:
                    print(f"   ➤ {db_name} ⭐ (THIS IS YOUR TARGET DATABASE)")
                else:
                    print(f"   - {db_name}")
        except Exception as e:
            print(f"   Error: {e}")
        print()
        
        # Show collections in target database
        print(f"📁 Collections in '{config.database_name}':")
        collections = config.db.list_collection_names()
        if collections:
            for collection_name in collections:
                count = config.db[collection_name].count_documents({})
                print(f"   ✅ {collection_name} ({count} documents)")
        else:
            print("   ⚠️  No collections found")
        
        print()
        print("🎯 To Find These Collections in Atlas UI:")
        print("   1. Go to https://cloud.mongodb.com/")
        print("   2. Select your project")
        print(f"   3. Click on cluster: {cluster_match.group(1) if cluster_match else 'your cluster'}")
        print("   4. Click 'Browse Collections'")
        print(f"   5. Look for database: '{config.database_name}'")
        print("   6. Collections should be visible there")
        print()
        print("💡 If still not visible:")
        print("   - Try refreshing the page (Ctrl+F5)")
        print("   - Check if you're in the right MongoDB project")
        print("   - Verify you're looking at the correct cluster")
        
    else:
        print("❌ Database connection failed")

if __name__ == "__main__":
    show_atlas_connection_info()
