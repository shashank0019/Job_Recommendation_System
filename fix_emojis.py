#!/usr/bin/env python3
"""Fix emoji characters in app_minimal.py for Windows compatibility"""

replacements = {
    '✅': '[OK]',
    '⚠️': '[WARNING]',
    'ℹ️': '[INFO]',
    '❌': '[ERROR]',
    '🌐': '[WEB]',
    '🚀': '[START]',
    '🔍': '[SEARCH]'
}

with open('app_minimal.py', 'r', encoding='utf-8') as f:
    content = f.read()

for emoji, text in replacements.items():
    content = content.replace(emoji, text)

with open('app_minimal.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✔ Fixed all emojis in app_minimal.py")
