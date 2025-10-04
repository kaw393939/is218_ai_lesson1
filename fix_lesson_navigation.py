#!/usr/bin/env python3
"""Fix navigation in all lesson files to point to README instead of INDEX.md"""

import re
from pathlib import Path

lessons_dir = Path("/Users/kwilliams/Desktop/218-test-complete/lessons")

# Update all lesson files
for lesson_file in lessons_dir.rglob("lesson_*.md"):
    print(f"Fixing {lesson_file.name}...")
    
    content = lesson_file.read_text()
    
    # Replace "Course Index" with "All Lessons"
    content = re.sub(
        r'🏠 \[Course Index\]',
        '🏠 [All Lessons]',
        content
    )
    
    # Ensure README links are correct
    content = re.sub(
        r'\[README\]\(\.\.\/INDEX\.md\)',
        '[README](../../README.md)',
        content
    )
    
    lesson_file.write_text(content)
    print(f"  ✅ Fixed {lesson_file.name}")

print("\n✅ All lesson navigation fixed!")
