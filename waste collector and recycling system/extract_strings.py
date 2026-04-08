import os
from babel.messages.extract import extract_from_dir
from babel.messages.pofile import write_po
from babel.messages.catalog import Catalog
from datetime import datetime

# Extract strings from the application directory
def_options = {
    'encoding': 'utf-8',
}

# Extract from templates and Python files
extracted = extract_from_dir(
    dirname='application/',
    method_map=[
        ('**.py', 'python'),
        ('**/templates/**.html', 'jinja2'),
    ],
    options_map={
        '**': def_options,
    },
)

# Create new catalog with extracted strings
catalog = Catalog()
for extracted_data in extracted:
    message = extracted_data[0]
    locations = extracted_data[1] if len(extracted_data) > 1 else []
    if message:
        catalog.add(message, locations=locations)

# Write to POT file
with open('messages.pot', 'wb') as pot_file:
    write_po(pot_file, catalog, sort_output=True)

print("Translation strings extracted successfully!")
print(f"Total strings extracted: {len(catalog)}")
