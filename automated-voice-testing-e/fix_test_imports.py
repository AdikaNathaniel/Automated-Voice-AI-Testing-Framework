#!/usr/bin/env python3
"""
Fix test imports that incorrectly use 'from backend.XXX' instead of 'from XXX'.

The conftest.py adds 'backend/' to sys.path, so imports should not include 'backend.'
"""

import re
from pathlib import Path

def fix_imports_in_file(filepath):
    """Fix imports in a single test file"""
    with open(filepath, 'r') as f:
        content = f.read()

    original_content = content

    # Replace 'from backend.XXX import' with 'from XXX import'
    content = re.sub(r'from backend\.([a-zA-Z_][a-zA-Z0-9_.]*)', r'from \1', content)

    # Replace 'import backend.XXX' with 'import XXX'
    content = re.sub(r'import backend\.([a-zA-Z_][a-zA-Z0-9_.]*)', r'import \1', content)

    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        return True
    return False

def main():
    """Fix imports in all test files"""
    tests_dir = Path(__file__).parent / 'tests'

    fixed_files = []

    for test_file in tests_dir.glob('test_*.py'):
        if fix_imports_in_file(test_file):
            fixed_files.append(test_file.name)

    if fixed_files:
        print(f"Fixed imports in {len(fixed_files)} files:")
        for filename in sorted(fixed_files):
            print(f"  - {filename}")
    else:
        print("No files needed fixing")

if __name__ == '__main__':
    main()
