#!/usr/bin/env python3
"""Script to remove excessive comments from CSS files."""

import os
import re
from pathlib import Path

def clean_css_comments(content):
    """Remove excessive CSS comments while keeping essential ones."""
    # Remove comment blocks that are just section headers
    patterns_to_remove = [
        r'/\* [A-Z][^*]*\*/',  # Section headers like /* Header */
        r'/\* [A-Z][^*]*Component[^*]*\*/',  # Component headers
        r'/\* [A-Z][^*]*Styles[^*]*\*/',  # Style headers  
        r'/\* [A-Z][^*]*Design[^*]*\*/',  # Design headers
        r'/\* [A-Z][^*]*Bar[^*]*\*/',  # Bar headers
        r'/\* [A-Z][^*]*Timeline[^*]*\*/',  # Timeline headers
        r'/\* [A-Z][^*]*Details[^*]*\*/',  # Details headers
        r'/\* [A-Z][^*]*Item[^*]*\*/',  # Item headers
        r'/\* [A-Z][^*]*Content[^*]*\*/',  # Content headers
        r'/\* [A-Z][^*]*Connector[^*]*\*/',  # Connector headers
        r'/\* [A-Z][^*]*Progress[^*]*\*/',  # Progress headers
        r'/\* [A-Z][^*]*Animations[^*]*\*/',  # Animation headers
        r'/\* [A-Z][^*]*Styling[^*]*\*/',  # Styling headers
    ]
    
    cleaned_content = content
    for pattern in patterns_to_remove:
        cleaned_content = re.sub(pattern, '', cleaned_content, flags=re.IGNORECASE)
    
    # Remove empty lines that result from comment removal
    lines = cleaned_content.split('\n')
    cleaned_lines = []
    prev_empty = False
    
    for line in lines:
        if line.strip() == '':
            if not prev_empty:
                cleaned_lines.append(line)
            prev_empty = True
        else:
            cleaned_lines.append(line)
            prev_empty = False
    
    return '\n'.join(cleaned_lines)

def clean_file(filepath):
    """Clean a single CSS file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        cleaned_content = clean_css_comments(content)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        
        print(f"Cleaned: {filepath}")
        
    except Exception as e:
        print(f"Error cleaning {filepath}: {e}")

def main():
    """Main function to clean all CSS files."""
    root_dir = Path('.')
    
    # Find all CSS files
    css_files = list(root_dir.rglob('*.css'))
    
    # Filter out node_modules
    css_files = [f for f in css_files if 'node_modules' not in str(f)]
    
    print(f"Found {len(css_files)} CSS files to clean")
    
    for css_file in css_files:
        clean_file(css_file)
    
    print("CSS cleanup complete!")

if __name__ == "__main__":
    main()
