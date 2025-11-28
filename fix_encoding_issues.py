#!/usr/bin/env python3
"""
Script to fix character encoding issues by replacing emojis with ASCII-safe alternatives
"""

import os
import re
from pathlib import Path

# Emoji replacements
emoji_replacements = {
    '[OK]': '[OK]',
    '[FAIL]': '[FAIL]',
    '[EDU]': '[EDU]',
    '[BOOK]': '[BOOK]',
    '[NOTE]': '[NOTE]',
    '[USERS]': '[USERS]',
    '[USER]': '[USER]',
    '[UPDATE]': '[UPDATE]',
    '[STATS]': '[STATS]',
    '[GROWTH]': '[GROWTH]',
    '[TARGET]': '[TARGET]',
    '[START]': '[START]',
    '[TIP]': '[TIP]',
    '[WARNING]': '[WARNING]',
    '[SEARCH]': '[SEARCH]',
    '[LIST]': '[LIST]',
    '[TOOLS]': '[TOOLS]',
    '[DOC]': '[DOC]',
    '[POWER]': '[POWER]',
    '[WORK]': '[WORK]',
    '[SUCCESS]': '[SUCCESS]',
    '[STAR]': '[STAR]',
    '[SETTINGS]': '[SETTINGS]',
    '[MOBILE]': '[MOBILE]',
    '[TAG]': '[TAG]',
    '[TIME]': '[TIME]',
    '[DATE]': '[DATE]',
    '[FILES]': '[FILES]',
    '[LINK]': '[LINK]',
    '[CALL]': '[CALL]',
    '[CHAT]': '[CHAT]',
    '[EMAIL]': '[EMAIL]',
    '[WEB]': '[WEB]',
    '[COMPUTER]': '[COMPUTER]',
    '[DESKTOP]': '[DESKTOP]',
    '[SECURE]': '[SECURE]',
    '[OPEN]': '[OPEN]',
    '[GROWTH]': '[UP]',
    '[DOWN]': '[DOWN]',
    '[ADD]': '[ADD]',
    '[SUBTRACT]': '[SUBTRACT]',
    '[MULTIPLY]': '[MULTIPLY]',
    '[DIVIDE]': '[DIVIDE]',
    '[ART]': '[ART]',
    '[MUSIC]': '[MUSIC]',
    '[VIDEO]': '[VIDEO]',
    '[TV]': '[TV]',
    '[GAME]': '[GAME]',
    '[WIN]': '[WIN]',
    '[RATING]': '[RATING]',
    '[HOT]': '[HOT]',
    '[COLD]': '[COLD]',
    '[RAIN]': '[RAIN]',
    '[SUN]': '[SUN]',
    '[MOON]': '[MOON]',
    '[PARTY]': '[PARTY]',
    '[BALLOON]': '[BALLOON]',
    '[GIFT]': '[GIFT]'
}

def replace_emojis_in_file(file_path):
    """Replace emojis in a single file"""
    try:
        # Read the file with proper encoding
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = []
        
        # Replace each emoji
        for emoji, replacement in emoji_replacements.items():
            if emoji in content:
                content = content.replace(emoji, replacement)
                changes_made.append(f"{emoji} -> {replacement}")
        
        # Only write if changes were made
        if changes_made:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return changes_made
        return []
    
    except UnicodeDecodeError:
        print(f"Could not decode file: {file_path}")
        return []
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return []

def main():
    """Main function to process all Python files"""
    current_dir = Path('.')
    python_files = list(current_dir.rglob('*.py'))
    
    total_files = 0
    total_changes = 0
    changed_files = []
    
    print("Fixing character encoding issues...")
    print(f"Found {len(python_files)} Python files to process")
    
    for file_path in python_files:
        changes = replace_emojis_in_file(file_path)
        if changes:
            total_files += 1
            total_changes += len(changes)
            changed_files.append(str(file_path))
            print(f"Fixed {file_path}: {len(changes)} changes")
            for change in changes:
                print(f"  - {change}")
    
    print(f"\nSummary:")
    print(f"Files processed: {len(python_files)}")
    print(f"Files changed: {total_files}")
    print(f"Total emoji replacements: {total_changes}")
    
    if changed_files:
        print(f"\nFiles modified:")
        for file_path in changed_files:
            print(f"  - {file_path}")
    else:
        print("\nNo emoji issues found!")
    
    print("\nCharacter encoding fix complete!")

if __name__ == "__main__":
    main()