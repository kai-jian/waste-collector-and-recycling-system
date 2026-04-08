import os
from babel.messages import pofile, mofile

# Find all .po files and compile them to .mo
translations_dir = "application/translations"
for root, dirs, files in os.walk(translations_dir):
    for file in files:
        if file.endswith(".po"):
            po_path = os.path.join(root, file)
            mo_path = os.path.join(root, file.replace(".po", ".mo"))
            
            # Read the .po file
            with open(po_path, "rb") as f:
                catalog = pofile.read_po(f)
            
            # Write the .mo file
            with open(mo_path, "wb") as f:
                mofile.write_mo(f, catalog)
            
            print(f"Compiled: {po_path} -> {mo_path}")

print("Translation compilation complete!")
