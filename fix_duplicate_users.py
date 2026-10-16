react-dom-client.development.js:24871 Download the React DevTools for a better development experience: https://react.dev/link/react-devtools
AuthContext.jsx:85   POST http://localhost:5000/auth/signin net::ERR_CONNECTION_REFUSED
dispatchXhrRequest @ xhr.js:195
xhr @ xhr.js:15
dispatchRequest @ dispatchRequest.js:51
_request @ Axios.js:187
request @ Axios.js:40
httpMethod @ Axios.js:226
wrap @ bind.js:5
login @ AuthContext.jsx:85
handleSubmit @ LoginForm.jsx:57
executeDispatch @ react-dom-client.development.js:16368
runWithFiberInDEV @ react-dom-client.development.js:1519
processDispatchQueue @ react-dom-client.development.js:16418
(anonymous) @ react-dom-client.development.js:17016
batchedUpdates$1 @ react-dom-client.development.js:3262
dispatchEventForPluginEventSystem @ react-dom-client.development.js:16572
dispatchEvent @ react-dom-client.development.js:20658
dispatchDiscreteEvent @ react-dom-client.development.js:20626
<form>
exports.jsxDEV @ react-jsx-dev-runtime.development.js:346
LoginForm @ LoginForm.jsx:74
react_stack_bottom_frame @ react-dom-client.development.js:23863
renderWithHooksAgain @ react-dom-client.development.js:5629
renderWithHooks @ react-dom-client.development.js:5541
updateFunctionComponent @ react-dom-client.development.js:8897
beginWork @ react-dom-client.development.js:10522
runWithFiberInDEV @ react-dom-client.development.js:1519
performUnitOfWork @ react-dom-client.development.js:15132
workLoopSync @ react-dom-client.development.js:14956
renderRootSync @ react-dom-client.development.js:14936
performWorkOnRoot @ react-dom-client.development.js:14419
performSyncWorkOnRoot @ react-dom-client.development.js:16231
flushSyncWorkAcrossRoots_impl @ react-dom-client.development.js:16079
processRootScheduleInMicrotask @ react-dom-client.development.js:16116
(anonymous) @ react-dom-client.development.js:16250
<LoginForm>
exports.jsxDEV @ react-jsx-dev-runtime.development.js:346
AuthModal @ AuthModal.jsx:56
react_stack_bottom_frame @ react-dom-client.development.js:23863
renderWithHooksAgain @ react-dom-client.development.js:5629
renderWithHooks @ react-dom-client.development.js:5541
updateFunctionComponent @ react-dom-client.development.js:8897
beginWork @ react-dom-client.development.js:10522
runWithFiberInDEV @ react-dom-client.development.js:1519
performUnitOfWork @ react-dom-client.development.js:15132
workLoopSync @ react-dom-client.development.js:14956
renderRootSync @ react-dom-client.development.js:14936
performWorkOnRoot @ react-dom-client.development.js:14419
performSyncWorkOnRoot @ react-dom-client.development.js:16231
flushSyncWorkAcrossRoots_impl @ react-dom-client.development.js:16079
processRootScheduleInMicrotask @ react-dom-client.development.js:16116
(anonymous) @ react-dom-client.development.js:16250
<AuthModal>
exports.jsxDEV @ react-jsx-dev-runtime.development.js:346
AuthGate @ AuthGate.jsx:88
react_stack_bottom_frame @ react-dom-client.development.js:23863
renderWithHooksAgain @ react-dom-client.development.js:5629
renderWithHooks @ react-dom-client.development.js:5541
updateFunctionComponent @ react-dom-client.development.js:8897
beginWork @ react-dom-client.development.js:10522
runWithFiberInDEV @ react-dom-client.development.js:1519
performUnitOfWork @ react-dom-client.development.js:15132
workLoopSync @ react-dom-client.development.js:14956
renderRootSync @ react-dom-client.development.js:14936
performWorkOnRoot @ react-dom-client.development.js:14419
performWorkOnRootViaSchedulerTask @ react-dom-client.development.js:16216
performWorkUntilDeadline @ scheduler.development.js:45
<AuthGate>
exports.jsxDEV @ react-jsx-dev-runtime.development.js:346
(anonymous) @ main.jsx:24
[NEW] Explain Console errors by using Copilot in Edge: click
         
         to explain an error. 
        Learn more
        Don't show again
"""Find and fix duplicate users"""
from config.database import get_db_config
from datetime import datetime

def find_and_fix_duplicates():
    """Find all users with the same email and keep only the most recent"""
    
    # Connect to database
    db_config = get_db_config()
    db_config.connect()
    
    if db_config.db is None:
        print("❌ Database connection failed")
        return
    
    users_collection = db_config.db.users
    
    # Find all users with the email
    email = "shashikingmaker495@gmail.com"
    
    print(f"\n=== Finding all users with email: {email} ===\n")
    
    users = list(users_collection.find({'email': email}))
    
    if not users:
        print("❌ No users found!")
        return
    
    print(f"Found {len(users)} user(s) with this email:\n")
    
    for i, user in enumerate(users, 1):
        print(f"User {i}:")
        print(f"  ID: {user['_id']}")
        print(f"  Name: {user.get('name')}")
        print(f"  Email: {user.get('email')}")
        print(f"  Password Hash: {user.get('password_hash', '')[:50]}...")
        print(f"  Created: {user.get('created_at')}")
        print(f"  Last Login: {user.get('last_login')}")
        print()
    
    if len(users) > 1:
        print(f"⚠️ Found {len(users)} duplicate users!")
        print("\n=== Keeping the OLDEST user (your original signup) ===")
        
        # Sort by created_at to find the oldest
        users_sorted = sorted(users, key=lambda u: u.get('created_at', datetime.min))
        
        keep_user = users_sorted[0]
        delete_users = users_sorted[1:]
        
        print(f"\n✅ Keeping: {keep_user.get('name')} (ID: {keep_user['_id']})")
        print(f"   Created: {keep_user.get('created_at')}")
        
        for user in delete_users:
            print(f"\n❌ Deleting: {user.get('name')} (ID: {user['_id']})")
            print(f"   Created: {user.get('created_at')}")
            
            result = users_collection.delete_one({'_id': user['_id']})
            if result.deleted_count > 0:
                print(f"   ✅ Deleted successfully")
            else:
                print(f"   ❌ Failed to delete")
        
        print(f"\n✅ Cleanup complete! Only the original user remains.")
        print(f"\nYour signin should now work with the password you used during your FIRST signup.")
        print(f"User: {keep_user.get('name')} ({keep_user.get('email')})")
    else:
        print(f"✅ No duplicates found. You have only one user.")
        user = users[0]
        print(f"\nYour user:")
        print(f"  Name: {user.get('name')}")
        print(f"  Email: {user.get('email')}")
        print(f"  Created: {user.get('created_at')}")
        print(f"  Last Login: {user.get('last_login')}")
        print(f"\nMake sure you're using the correct password from your original signup.")

if __name__ == "__main__":
    find_and_fix_duplicates()
