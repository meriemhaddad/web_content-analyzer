"""
Fix unicode emoji characters in test files for Windows compatibility
"""
import os
import re
from pathlib import Path

# Mapping of common emoji to ASCII alternatives
EMOJI_REPLACEMENTS = {
    '[TEST]': '[TEST]',
    '[SUCCESS]': '[SUCCESS]',
    '[ERROR]': '[ERROR]',
    '[STATS]': '[STATS]',
    '[TIME]': '[TIME]',
    '[INFO]': '[INFO]',
    '[TARGET]': '[TARGET]',
    '[RESULTS]': '[RESULTS]',
    '[EXCEPTION]': '[EXCEPTION]',
    '[CONNECTING]': '[CONNECTING]',
    '[COMPLETE]': '[COMPLETE]',
    '[WARNING]': '[WARNING]',
    '[RUNNING]': '[RUNNING]',
    '[FILE]': '[FILE]',
    '[SUMMARY]': '[SUMMARY]',
}

def fix_file_encoding(file_path):
    """Fix emoji characters in a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace emoji characters with known mappings
        for emoji, replacement in EMOJI_REPLACEMENTS.items():
            content = content.replace(emoji, replacement)
        
        # Replace any remaining high unicode characters
        import re
        # Match any character outside the basic ASCII range that might cause encoding issues
        content = re.sub(r'[\U0001F600-\U0001F64F]', '[EMOJI]', content)  # Emoticons
        content = re.sub(r'[\U0001F300-\U0001F5FF]', '[SYMBOL]', content)  # Misc Symbols
        content = re.sub(r'[\U0001F680-\U0001F6FF]', '[TRANSPORT]', content)  # Transport
        content = re.sub(r'[\U0001F1E0-\U0001F1FF]', '[FLAG]', content)  # Flags
        content = re.sub(r'[\u2600-\u26FF]', '[MISC]', content)  # Miscellaneous symbols
        content = re.sub(r'[\u2700-\u27BF]', '[DINGBAT]', content)  # Dingbats
        
        # Write back with utf-8 encoding
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Fixed: {file_path}")
        return True
        
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    """Fix all test files in the testing directory."""
    testing_dir = Path(__file__).parent
    
    # Find all Python files in testing directory
    py_files = list(testing_dir.rglob('*.py'))
    
    print(f"Fixing emoji characters in {len(py_files)} Python files...")
    
    fixed_count = 0
    for py_file in py_files:
        if fix_file_encoding(py_file):
            fixed_count += 1
    
    print(f"\nFixed {fixed_count}/{len(py_files)} files")

if __name__ == "__main__":
    main()