"""Remove fuzzy flag from Pending Complaints translation"""

from babel.messages.pofile import read_po, write_po

def fix_pending_complaints(filepath, lang):
    """Remove fuzzy flag from Pending Complaints"""
    with open(filepath, 'rb') as f:
        catalog = read_po(f)
    
    for message in catalog:
        if message.id == "Pending Complaints":
            if 'fuzzy' in message.flags:
                message.flags.remove('fuzzy')
                print(f"{lang}: Removed fuzzy flag from 'Pending Complaints'")
            break
    
    with open(filepath, 'wb') as f:
        write_po(f, catalog)

# Fix Malay
fix_pending_complaints(
    'application/translations/ms/LC_MESSAGES/messages.po',
    'Malay'
)

# Fix Chinese
fix_pending_complaints(
    'application/translations/zh/LC_MESSAGES/messages.po',
    'Chinese'
)

print("\n✓ Fuzzy flag removed, ready to compile!")
