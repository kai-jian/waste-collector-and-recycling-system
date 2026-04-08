"""Remove fuzzy flags from complaint page translations"""

from babel.messages.pofile import read_po, write_po

strings_to_fix = [
    "Waste Reporting Center",
    "Make a New Report",
    "Check Complaint Status",
]

def remove_fuzzy_flags(filepath, lang):
    """Remove fuzzy flags from specified strings"""
    with open(filepath, 'rb') as f:
        catalog = read_po(f)
    
    fixed_count = 0
    for message in catalog:
        if message.id in strings_to_fix:
            if 'fuzzy' in message.flags:
                message.flags.remove('fuzzy')
                fixed_count += 1
                print(f"{lang}: Removed fuzzy from '{message.id}'")
    
    with open(filepath, 'wb') as f:
        write_po(f, catalog)
    
    return fixed_count

# Fix Malay
ms_fixed = remove_fuzzy_flags(
    'application/translations/ms/LC_MESSAGES/messages.po',
    'Malay'
)
print(f"Malay: Fixed {ms_fixed} entries\n")

# Fix Chinese
zh_fixed = remove_fuzzy_flags(
    'application/translations/zh/LC_MESSAGES/messages.po',
    'Chinese'
)
print(f"Chinese: Fixed {zh_fixed} entries")
print("\n✓ Ready to compile!")
