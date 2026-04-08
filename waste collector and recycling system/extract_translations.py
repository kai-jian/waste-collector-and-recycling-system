from babel.messages import frontend as babel

# Extract all translatable strings from the application
babel_main = babel.main

import sys
sys.argv = ['pybabel', 'extract', '-F', 'babel.cfg', '-k', 'lazy_gettext', '-o', 'messages.pot', 'application/']
babel_main(['extract'])

print("Translation strings extracted successfully!")
