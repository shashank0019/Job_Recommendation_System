"""Debug password hashing and verification"""
from auth.models import User
from auth.utils import AuthUtils
from config.database import get_db_config

def test_password_verification():
    """Test if password verification is working"""
    print("\n=== Testing Password Verification ===")
    
    # Initialize database
    db_config = get_db_config()
    db_config.connect()
    
    # Get the user
    user = User.find_by_email("shashikingmaker495@gmail.com")
    
    if not user:
        print("❌ User not found!")
        return
    
    print(f"User found: {user.name}")
    print(f"Email: {user.email}")
    print(f"Password hash: {user.password_hash[:50]}...")
    
    # Test password
    test_password = "Test@123"
    print(f"\nTesting password: {test_password}")
    
    # Method 1: Using user.verify_password()
    print("\n--- Method 1: user.verify_password() ---")
    is_valid = user.verify_password(test_password)
    print(f"Result: {is_valid}")
    
    # Method 2: Using AuthUtils.verify_password()
    print("\n--- Method 2: AuthUtils.verify_password() ---")
    is_valid2 = AuthUtils.verify_password(test_password, user.password_hash)
    print(f"Result: {is_valid2}")
    
    # Method 3: Hash the test password and compare
    print("\n--- Method 3: Test hashing ---")
    hashed = AuthUtils.hash_password(test_password)
    print(f"New hash: {hashed[:50]}...")
    
    # Verify with the new hash
    verify_new = AuthUtils.verify_password(test_password, hashed)
    print(f"Verify new hash: {verify_new}")

if __name__ == "__main__":
    test_password_verification()
