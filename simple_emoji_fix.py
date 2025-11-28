#!/usr/bin/env python3

import os
from pathlib import Path

# Simple file processing without any emojis in output
def fix_file_emoji_encoding(file_path):
    """Fix emoji encoding in a file"""
    try:
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace emojis
        content = content.replace('[OK]', '[OK]')
        content = content.replace('[FAIL]', '[FAIL]')
        content = content.replace('[EDU]', '[EDU]')
        content = content.replace('[BOOK]', '[BOOK]')
        content = content.replace('[NOTE]', '[NOTE]')
        content = content.replace('[USERS]', '[USERS]')
        content = content.replace('[USER]', '[USER]')
        content = content.replace('[UPDATE]', '[UPDATE]')
        content = content.replace('[STATS]', '[STATS]')
        content = content.replace('[GROWTH]', '[GROWTH]')
        content = content.replace('[TARGET]', '[TARGET]')
        content = content.replace('[START]', '[START]')
        content = content.replace('[TIP]', '[TIP]')
        content = content.replace('[WARNING]', '[WARNING]')
        content = content.replace('[SEARCH]', '[SEARCH]')
        content = content.replace('[LIST]', '[LIST]')
        content = content.replace('[TOOLS]', '[TOOLS]')
        content = content.replace('[DOC]', '[DOC]')
        content = content.replace('[POWER]', '[POWER]')
        content = content.replace('[WORK]', '[WORK]')
        content = content.replace('[SUCCESS]', '[SUCCESS]')
        content = content.replace('[STAR]', '[STAR]')
        content = content.replace('[SETTINGS]', '[SETTINGS]')
        content = content.replace('[MOBILE]', '[MOBILE]')
        content = content.replace('[TAG]', '[TAG]')
        content = content.replace('[TIME]', '[TIME]')
        content = content.replace('[DATE]', '[DATE]')
        content = content.replace('[FILES]', '[FILES]')
        content = content.replace('[LINK]', '[LINK]')
        content = content.replace('[CALL]', '[CALL]')
        content = content.replace('[CHAT]', '[CHAT]')
        content = content.replace('[EMAIL]', '[EMAIL]')
        content = content.replace('[WEB]', '[WEB]')
        content = content.replace('[COMPUTER]', '[COMPUTER]')
        content = content.replace('[DESKTOP]', '[DESKTOP]')
        content = content.replace('[SECURE]', '[SECURE]')
        content = content.replace('[OPEN]', '[OPEN]')
        content = content.replace('[DOWN]', '[DOWN]')
        content = content.replace('[ADD]', '[ADD]')
        content = content.replace('[SUBTRACT]', '[SUBTRACT]')
        content = content.replace('[MULTIPLY]', '[MULTIPLY]')
        content = content.replace('[DIVIDE]', '[DIVIDE]')
        content = content.replace('[ART]', '[ART]')
        content = content.replace('[MUSIC]', '[MUSIC]')
        content = content.replace('[VIDEO]', '[VIDEO]')
        content = content.replace('[TV]', '[TV]')
        content = content.replace('[GAME]', '[GAME]')
        content = content.replace('[WIN]', '[WIN]')
        content = content.replace('[RATING]', '[RATING]')
        content = content.replace('[HOT]', '[HOT]')
        content = content.replace('[COLD]', '[COLD]')
        content = content.replace('[RAIN]', '[RAIN]')
        content = content.replace('[SUN]', '[SUN]')
        content = content.replace('[MOON]', '[MOON]')
        content = content.replace('[PARTY]', '[PARTY]')
        content = content.replace('[BALLOON]', '[BALLOON]')
        content = content.replace('[GIFT]', '[GIFT]')
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
        
    except Exception as e:
        return False

# Process all Python files
current_dir = Path('.')
python_files = list(current_dir.rglob('*.py'))

fixed_count = 0
for file_path in python_files:
    if fix_file_emoji_encoding(file_path):
        fixed_count += 1

print(f"Fixed {fixed_count} files")
print("Done")