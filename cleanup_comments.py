#!/usr/bin/env python3

import os
import re
import sys
from pathlib import Path

def clean_docstrings(content):
    lines = content.split('\n')
    cleaned_lines = []
    i = 0
    in_docstring = False
    docstring_quote = None
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Check for start of docstring
        if not in_docstring:
            # Look for triple quotes