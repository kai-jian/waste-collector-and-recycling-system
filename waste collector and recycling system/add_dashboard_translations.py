"""Add missing translations for dashboard strings"""

from babel.messages.pofile import read_po, write_po

# Translations for Malay
malay_translations = {
    "Hello,": "Hai,",
    "My Recent Activity": "Aktiviti Terkini Saya",
    "Together, we can keep our neighborhood clean and sustainable. Have you spotted any waste issues today?": "Bersama-sama, kita boleh menjaga kawasan kita tetap bersih dan lestari. Adakah anda menemui sebarang isu sampah hari ini?",
    "Resolved": "Diselesaikan",
}

# Translations for Chinese
chinese_translations = {
    "Hello,": "你好，",
    "My Recent Activity": "我的最近活动",
    "Together, we can keep our neighborhood clean and sustainable. Have you spotted any waste issues today?": "一起来，我们可以保持我们的社区干净和可持续。你今天发现了什么垃圾问题吗?",
    "Resolved": "已解决",
}

def update_po_translations(filepath, translations):
    """Update translations in a .po file"""
    with open(filepath, 'rb') as f:
        catalog = read_po(f)
    
    updated_count = 0
    for message in catalog:
        if message.id in translations:
            message.string = translations[message.id]
            updated_count += 1
            # Remove fuzzy flag if it was set
            if 'fuzzy' in message.flags:
                message.flags.remove('fuzzy')
    
    with open(filepath, 'wb') as f:
        write_po(f, catalog)
    
    return updated_count

# Update Malay file
ms_count = update_po_translations(
    'application/translations/ms/LC_MESSAGES/messages.po',
    malay_translations
)
print(f"Updated {ms_count} Malay translations")

# Update Chinese file  
zh_count = update_po_translations(
    'application/translations/zh/LC_MESSAGES/messages.po',
    chinese_translations
)
print(f"Updated {zh_count} Chinese translations")

print("\n✓ Dashboard translation updates complete!")
