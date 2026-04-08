"""Add the missing translations"""

from babel.messages.pofile import read_po, write_po
from babel.messages.catalog import Catalog

# Translation mappings for Malay
malay_translations = {
    "Point History": "Sejarah Mata",
    "Pending Complaints": "Aduan Tertangguh",
    "Rewards Hub": "Hub Ganjaran",
    "Spend Points": "Belanjakan Mata",
    "Community News": "Berita Komuniti",
    "Waste Reporting Center": "Pusat Pelaporan Sampah",
    "Make a New Report": "Buat Laporan Baru",
    "Check Complaint Status": "Semak Status Aduan",
    "Give Us Feedback": "Berikan Kami Maklum Balas",
    "Support Center": "Pusat Sokongan",
    "Hotline": "Talian Panas",
    "FAQ": "Soalan Lazim",
    "Common questions.": "Soalan umum.",
    "Start Chat": "Mulai Sembang",
}

# Translation mappings for Chinese
chinese_translations = {
    "Point History": "积分历史",
    "Pending Complaints": "待处理投诉",
    "Rewards Hub": "奖励中心",
    "Spend Points": "消费积分",
    "Community News": "社区新闻",
    "Waste Reporting Center": "废物举报中心",
    "Make a New Report": "提交新举报",
    "Check Complaint Status": "检查投诉状态",
    "Give Us Feedback": "给我们反馈",
    "Support Center": "支持中心",
    "Hotline": "热线",
    "FAQ": "常见问题",
    "Common questions.": "常见问题。",
    "Start Chat": "开始聊天",
}

def update_po_file(filepath, translations):
    """Update translations in a .po file"""
    with open(filepath, 'rb') as f:
        catalog = read_po(f)
    
    updated_count = 0
    for message_id, translation in translations.items():
        # Find the message and update it
        for message in catalog:
            if message.id == message_id:
                message.string = translation
                updated_count += 1
                break
    
    with open(filepath, 'wb') as f:
        write_po(f, catalog, sort_output=True)
    
    return updated_count

# Update Malay file
ms_count = update_po_file(
    'application/translations/ms/LC_MESSAGES/messages.po',
    malay_translations
)
print(f"Updated {ms_count} Malay translations")

# Update Chinese file
zh_count = update_po_file(
    'application/translations/zh/LC_MESSAGES/messages.po',
    chinese_translations
)
print(f"Updated {zh_count} Chinese translations")

print("\n✓ Translation updates complete!")
