#!/usr/bin/env python
"""Extract and update translations for the application."""

import os
import sys
from pathlib import Path
from babel.messages.extract import extract_from_dir
from babel.messages.pofile import read_po, write_po
from babel.messages.catalog import Catalog

# Change to project directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("Extracting translatable strings...")

# Extract all translatable strings
def_options = {
    'encoding': 'utf-8',
}

extracted = extract_from_dir(
    dirname='application/',
    method_map=[
        ('**.py', 'python'),
        ('**/templates/**.html', 'jinja2'),
    ],
)

# Create a new catalog from extracted data
catalog = Catalog()
for filename, lineno, message, comments, context in extracted:
    if message:
        catalog.add(
            message,
            locations=[(filename, lineno)] if lineno else [],
            auto_comments=comments if isinstance(comments, list) else ([comments] if comments else []),
            context=context,
        )

print(f"Extracted {len(catalog)} translatable strings")

# Write to POT file
print("Writing messages.pot...")
with open('messages.pot', 'wb') as pot_file:
    write_po(pot_file, catalog, sort_output=True)

print("✓ Translation extraction complete!")
