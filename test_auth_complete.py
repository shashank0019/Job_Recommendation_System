#!/usr/bin/env python3

import requests
import json
import sys

def test_signup():
    print('🧪 Testing signup endpoint...')
    
    signup_data = {
        'name': 'Shashank C A',
        'email': 'shashikingmaker495@gmail.com', 
        'password': 'SecurePass123'
    }

    try:
        response = requests.post('http://localhost:5000/auth/signup', 
                               json=signup_data, 
                               headers={'Content-Type': 'application/json'},
                               timeout=10)
        
        print(f'Status Code: {response.status_code}')
        print(f'Response Headers: {dict(response.headers)}')
        print(f'Response Body: {response.text}')
        
        if response.status_code == 201:
            print('✅ Signup successful!')
            return True
        else:
            print('❌ Signup failed')
            return False
            
    except requests.exceptions.ConnectionError:
        print('❌ Connection refused - server not running?')
        return False
    except requests.exceptions.RequestException as e:
        print(f'❌ Request error: {e}')
        return False
    except Exception as e:
        print(f'❌ Other error: {e}')
        return False

def test_signin():
    print('\n🧪 Testing signin endpoint...')
    
    signin_data = {
        'email': 'shashikingmaker495@gmail.com', 
        'password': 'SecurePass123'
    }

    try:
        response = requests.post('http://localhost:5000/auth/signin', 
                               json=signin_data, 
                               headers={'Content-Type': 'application/json'},
                               timeout=10)
        
        print(f'Status Code: {response.status_code}')
        print(f'Response Body: {response.text}')
        
        if response.status_code == 200:
            print('✅ Signin successful!')
            return True
        else:
            print('❌ Signin failed')
            return False
            
    except requests.exceptions.ConnectionError:
        print('❌ Connection refused - server not running?')
        return False
    except Exception as e:
        print(f'❌ Error: {e}')
        return False

if __name__ == '__main__':
    print('🚀 Starting authentication tests...\n')
    
    # Test signup
    signup_success = test_signup()
    
    # Test signin (if signup was successful or user already exists)
    signin_success = test_signin()
    
    print('\n📊 Test Results:')
    print(f'Signup: {"✅ PASS" if signup_success else "❌ FAIL"}')
    print(f'Signin: {"✅ PASS" if signin_success else "❌ FAIL"}')