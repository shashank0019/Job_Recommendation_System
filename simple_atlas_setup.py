"""
Simple Atlas Setup - Create New Cluster Configuration
"""

def show_simple_instructions():
    print("Create New MongoDB Atlas Cluster")
    print("=" * 40)
    print()
    print("QUICK SOLUTION:")
    print("Since your collections aren't showing in Atlas UI,")
    print("let's create a NEW cluster that will be visible.")
    print()
    print("STEP 1: Create New Cluster")
    print("- Go to https://cloud.mongodb.com/")
    print("- Click 'Build a Database'")
    print("- Choose FREE (M0)")
    print("- Name: career-platform")
    print("- Click 'Create Cluster'")
    print()
    print("STEP 2: Get Connection String")
    print("- Click 'Connect' on new cluster")
    print("- Choose 'Connect your application'")
    print("- Copy the connection string")
    print()
    print("STEP 3: Create Database User")
    print("- Go to 'Database Access'")
    print("- Add New Database User")
    print("- Username: career_user")
    print("- Password: (your choice)")
    print("- Role: Read and write to any database")
    print()
    print("STEP 4: Update Your Code")
    print("- Replace connection string in config/database.py")
    print("- Run the recreate script")
    print()
    print("The new cluster will definitely show collections!")

if __name__ == "__main__":
    show_simple_instructions()
