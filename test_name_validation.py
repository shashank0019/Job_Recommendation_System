#!/usr/bin/env python3

from auth.utils import AuthUtils

test_name = 'Test User 2'
print(f'Testing name: "{test_name}"')

name_valid, name_error = AuthUtils.validate_name(test_name)
print(f'Valid: {name_valid}')
print(f'Error: {name_error}')

# Try without the number
test_name2 = 'Test User'
name_valid2, name_error2 = AuthUtils.validate_name(test_name2)
print(f'\nTesting name: "{test_name2}"')
print(f'Valid: {name_valid2}')
print(f'Error: {name_error2}')