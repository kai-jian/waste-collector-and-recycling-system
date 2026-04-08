#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Populate translations for the waste collector system.
Adds Malaysian and Chinese translations to the .po files.
"""

import os
import polib

# Comprehensive translations for the application
TRANSLATIONS = {
    'ms': {  # Malaysian (Bahasa Melayu)
        # ==== From templates extracted by pybabel ====
        # Navigation & Layout
        'Home': 'Halaman Utama',
        'News': 'Berita',
        'Complaints': 'Aduan',
        'Rewards': 'Ganjaran',
        'Feedback': 'Maklum Balas',
        'Helpline': 'Talian Bantuan',
        'Update Status': 'Kemas Kini Status',
        'Dashboard': 'Papan Pemuka',
        'Assign Hub': 'Tetapkan Hab',
        'Verify Points': 'Sahkan Poin',
        'Manage Helpline': 'Urus Talian Bantuan',
        'News Hub': 'Hab Berita',
        'My Profile': 'Profil Saya',
        'Admin Profile': 'Profil Admin',
        'Language Hub': 'Hub Bahasa',
        'Logout': 'Daftar Keluar',
        'Login': 'Daftar Masuk',
        'Register': 'Daftar',
        
        # Login Page
        'Welcome Back': 'Selamat Kembali',
        'Access your waste management dashboard': 'Akses papan pemuka pengurusan sampah anda',
        'New here?': 'Baru di sini?',
        'Sign Up Now': 'Daftar Sekarang',
        
        # Sign Up Page
        'Join EcoClean': 'Sertai EcoClean',
        'Help keep our city clean and sustainable.': 'Bantu menjaga kota kita tetap bersih dan berkelanjutan.',
        'Select your primary role in the system.': 'Pilih peranan utama anda dalam sistem.',
        'Optional: Upload a JPG or PNG profile picture.': 'Pilihan: Muat naik gambar profil JPG atau PNG.',
        'Create Account': 'Buat Akaun',
        'Already have an account?': 'Sudah mempunyai akaun?',
        
        # Change Language
        'Current': 'Semasa',
        
        # Additional translations
        'Select your preferred language.': 'Pilih bahasa pilihan anda.',
        'Available': 'Tersedia',
        'Back to Hub': 'Kembali ke Hub',
        'Profile': 'Profil',
        'Settings': 'Tetapan',
        'Help': 'Bantuan',
        'Points': 'Poin',
        
        # Common Actions
        'Submit': 'Hantar',
        'Send': 'Hantar',
        'Edit': 'Edit',
        'Delete': 'Padam',
        'Save': 'Simpan',
        'Cancel': 'Batal',
        'Back': 'Kembali',
        'Close': 'Tutup',
        'Confirm': 'Sahkan',
        'Yes': 'Ya',
        'No': 'Tidak',
        'Loading': 'Memuatkan',
        
        # Messages
        'Error': 'Ralat',
        'Success': 'Berjaya',
        'Warning': 'Amaran',
        'Info': 'Maklumat',
        'No results found': 'Tiada hasil ditemui',
        'Are you sure?': 'Anda pasti?',
        'Saved successfully': 'Disimpan dengan berjaya',
        'Deleted successfully': 'Dipadam dengan berjaya',
        'Please try again': 'Sila cuba lagi',
        'Access denied': 'Akses ditolak',
        'Invalid input': 'Input tidak sah',
        'Required field': 'Medan diperlukan',
        
        # Forms
        'Email': 'E-mel',
        'Password': 'Kata Laluan',
        'Username': 'Nama Pengguna',
        'Name': 'Nama',
        'Description': 'Penerangan',
        'Category': 'Kategori',
        'Subject': 'Subjek',
        'Message': 'Mesej',
        'Upload': 'Muat Naik',
        'Submit Report': 'Hantar Laporan',
        'Location': 'Lokasi',
        'Date': 'Tarikh',
        'Status': 'Status',
        
        # Complaint Related
        'Make Complaint': 'Buat Aduan',
        'Report Waste': 'Laporkan Sampah',
        'View Complaints': 'Lihat Aduan',
        'Complaint Status': 'Status Aduan',
        'Pending': 'Menunggu',
        'In Action': 'Sedang Diproses',
        'Completed': 'Selesai',
        
        # Rewards Related
        'Recycle & Earn': 'Kitar & Hasilkan Poin',
        'Request Points': 'Minta Poin',
        'Redeem Points': 'Tukar Poin',
        'Available Points': 'Poin Tersedia',
        'Pending Points': 'Poin Menunggu',
        'Total Points': 'Jumlah Poin',
        
        # Chat Related
        'Live Chat': 'Sembang Langsung',
        'Chat Support': 'Sokongan Sembang',
        'Type your message': 'Taip mesej anda',
        'Type your response': 'Taip respons anda',
        'Response sent': 'Respons dihantar',
        'Message sent': 'Mesej dihantar',
        'Select a resident to message': 'Pilih pemastautin untuk berkomunikasi',
        
        # Helpline
        'Support Center': 'Pusat Sokongan',
        'Contact Us': 'Hubungi Kami',
        'Hotline': 'Talian Panas',
        'FAQ': 'Soalan Lazim',
        'Email Support': 'Sokongan E-mel',
        'Chat with us': 'Sembang dengan kami',
        
        # Feedback
        'Give Us Feedback': 'Berikan Maklum Balas',
        'Thank you for your feedback': 'Terima kasih atas maklum balas anda',
        
        # News
        'Latest News': 'Berita Terbaru',
        'No news available': 'Tiada berita tersedia',
        'Read More': 'Baca Lagi',
        
        # Admin Dashboard
        'Admin Dashboard': 'Papan Pemuka Admin',
        'Welcome back, ': 'Selamat kembali, ',
        '. Here is the community overview.': '. Berikut adalah gambaran keseluruhan komuniti.',
        'Residents': 'Pemastautin',
        'Pending Dispatch': 'Penghantaran Tertangguh',
        'Point Requests': 'Permintaan Poin',
        'Resolved Cases': 'Kes Diselesaikan',
        'Management Tools': 'Alat Pengurusan',
        'Dispatch Center': 'Pusat Penghantaran',
        'Verify Point Requests': 'Sahkan Permintaan Poin',
        'Feedback Hub': 'Hub Maklum Balas',
        'Manage News Hub': 'Urus Hub Berita',
        'User Database': 'Pangkalan Data Pengguna',
        'Recent Urgent Reports': 'Laporan Mendesak Terbaru',
        'View All Activity': 'Lihat Semua Aktiviti',
        'Resident': 'Pemastautin',
        'Type': 'Jenis',
        'Action': 'Tindakan',
        
        # Dashboard Summary Page
        'Live overview of city-wide waste collection and collector performance.': 'Gambaran keseluruhan langsung pengumpulan sampah dan prestasi pengumpul di seluruh kota.',
        'Live Volume': 'Volum Langsung',
        'Total Waste Volume': 'Jumlah Volum Sampah',
        'kg': 'kg',
        'View Detailed Logs': 'Lihat Log Terperinci',
        'Recycling Rate': 'Kadar Kitar Semula',
        'Verified': 'Disahkan',
        'Analyze Reward Impact': 'Analisis Kesan Ganjaran',
        'Monitor Active Routes': 'Pantau Laluan Aktif',
        'Task Completion': 'Penyelesaian Tugas',
        'Performance': 'Prestasi',
        'System Status: Operational': 'Status Sistem: Beroperasi',
        'Administrative Control Center': 'Pusat Kawalan Pentadbiran',
        'This dashboard aggregates real-time data from': 'Papan pemuka ini mengumpulkan data masa nyata daripada',
        'Collector Reports': 'Laporan Pengumpul',
        'and': 'dan',
        '. Verified entries automatically update the volume and sustainability metrics.': '. Entri yang disahkan secara automatik mengemas kini metrik volum dan keberlanjutan.',
        'Detailed Analytics': 'Analitik Terperinci',
        'Refresh Data': 'Segarkan Data',
        
        # Pending Assignments Page
        'Pending Assignments': 'Tugasan Tertangguh',
        'ID': 'ID',
        'Date Reported': 'Tarikh Dilaporkan',
        'Manage & Assign': 'Urus & Tugaskan',
        
        # Verify Points Page
        'Material:': 'Bahan:',
        'Weight:': 'Berat:',
        'Potential Points:': 'Poin Berpotensi:',
        'Approve': 'Setuju',
        'Reject': 'Tolak',
        'No pending point requests to verify.': 'Tiada permintaan poin tertangguh untuk disahkan.',
        
        # Helpline Management Page
        'Helpline Management Hub': 'Hub Pengurusan Talian Bantuan',
        'Control all support channels, contact information, and resident resources.': 'Kawal semua saluran sokongan, maklumat hubungan, dan sumber pemastautin.',
        'Edit Hotline': 'Edit Talian Panas',
        'Set the official support address.': 'Tetapkan alamat sokongan rasmi.',
        'Edit Email': 'Edit E-mel',
        'Manage active chat channels.': 'Urus saluran sembang aktif.',
        'FAQs': 'Soalan Lazim',
        'Manage common questions.': 'Urus soalan biasa.',
        'Manage FAQ': 'Urus Soalan Lazim',
        
        # Chat Management
        'Chat Channels': 'Saluran Sembang',
        'Manage your live support channels for residents.': 'Urus saluran sokongan langsung anda untuk pemastautin.',
        'New Channel': 'Saluran Baru',
        'Channel Name': 'Nama Saluran',
        'Active': 'Aktif',
        'Inactive': 'Tidak Aktif',
        'Delete this channel?': 'Padam saluran ini?',
        'No channels created yet.': 'Tiada saluran dibuat lagi.',
        
        # Complaints Management
        'No photo available': 'Tiada foto tersedia',
        'Status:': 'Status:',
        'Reporter': 'Pelapor',
        
        # Feedback Management
        'Review and manage feedback submitted by residents.': 'Semak dan urus maklum balas yang dikemukakan oleh pemastautin.',
        'View Details': 'Lihat Butiran',
        'No feedback has been submitted yet.': 'Tiada maklum balas dikemukakan lagi.',
        
        # News Management
        'Manage community announcements and alerts': 'Urus pengumuman dan amaran komuniti',
        'Add New Post': 'Tambah Siaran Baru',
        'Posted Date': 'Tarikh Disiarkan',
        'Article Summary': 'Ringkasan Artikel',
        'Permanent delete: are you sure?': 'Padam kekal: anda pasti?',
        
        # User Management
        'No residents registered yet.': 'Tiada pemastautin didaftar lagi.',
        'pts': 'pts',
        'Tier': 'Peringkat',
        'Role': 'Peranan',
        
        # FAQ Management
        'Frequently Asked Questions': 'Soalan Lazim',
        'Create, update, or remove help articles for residents.': 'Buat, kemas kini, atau buang artikel bantuan untuk pemastautin.',
        'Add New FAQ': 'Tambah Soalan Lazim Baru',
        'Manage FAQs': 'Urus Soalan Lazim',
        'Are you sure you want to delete this FAQ?': 'Anda pasti mahu mempadam Soalan Lazim ini?',
        'No FAQs found': 'Tiada Soalan Lazim ditemui',
        'Start by adding your first question for the residents.': 'Mulakan dengan menambah soalan pertama anda untuk pemastautin.',
        'Add First FAQ': 'Tambah Soalan Lazim Pertama',
        
        # Additional Resident Translations
        'No announcements today.': 'Tiada pengumuman hari ini.',
        'Recent Community Activity': 'Aktiviti Komuniti Terbaru',
        'Waste reported': 'Sampah dilaporkan',
        'No news posts available at the moment.': 'Tiada siaran berita tersedia pada masa ini.',
        'No recycling history found.': 'Tiada sejarah kitar semula ditemui.',
        'Complaint Terminology': 'Istilah Aduan',
        'Learn the difference between Domestic, Public, and Bulk waste.': 'Pelajari perbezaan antara sampah Domestik, Awam, dan Pukal.',
        'Waste Reporting Center': 'Pusat Pelaporan Sampah',
        'Select an option below to manage your waste reports or learn about categories.': 'Pilih pilihan di bawah untuk menguruskan laporan sampah anda atau pelajari tentang kategori.',
        'Make a New Report': 'Buat Laporan Baru',
        'Upload a photo and pin the location of waste on the map.': 'Muat naik foto dan letakkan pindia lokasi sampah di peta.',
        'Check Complaint Status': 'Semak Status Aduan',
        'View your history and track progress of your submissions.': 'Lihat sejarah anda dan jejaki kemajuan penyerahan anda.',
        'Complaint Terminology Guide': 'Panduan Istilah Aduan',
        'In Progress': 'Sedang Diproses',
        
        # Language Selection
        'Language changed to': 'Bahasa berubah ke',
        'English': 'Bahasa Inggeris',
        'Bahasa Melayu': 'Bahasa Melayu',
        
        # Waste Collector - Home Dashboard
        'Collector Dashboard': 'Papan Pemuka Pengumpul',
        'Welcome back,': 'Selamat kembali,',
        'Here is your pickup schedule.': 'Berikut adalah jadual pengambilan anda.',
        'GPS:': 'GPS:',
        'Initializing...': 'Memulakan...',
        'System Online': 'Sistem Dalam Talian',
        'Active Pickups': 'Pengambilan Aktif',
        'Tracking Status': 'Status Pelacakan',
        'Waiting for location permission...': 'Menunggu kebenaran lokasi...',
        'Refresh GPS': 'Segarkan GPS',
        'Current Assignments': 'Tugasan Semasa',
        'Report ID': 'ID Laporan',
        'Location Coords': 'Koordinat Lokasi',
        'Waste Type': 'Jenis Sampah',
        'Action': 'Tindakan',
        'Details': 'Butiran',
        'No active tasks assigned!': 'Tiada tugasan aktif ditugaskan!',
        
        # Waste Collector - Profile
        'Verified Collector': 'Pengumpul Disahkan',
        'Jobs Done': 'Pekerjaan Selesai',
        'KG Collected': 'KG Dikumpul',
        'Account Details': 'Butiran Akaun',
        'Access Level': 'Tahap Akses',
        'Waste Collector': 'Pengumpul Sampah',
        'Online': 'Dalam Talian',
        'Edit Profile': 'Edit Profil',
        'Tasks': 'Tugasan',
        
        # Waste Collector - Assignments
        'Your Assignments': 'Tugasan Anda',
        'Click on a card to view full details and update the collection status.': 'Klik pada kad untuk melihat butiran lengkap dan kemas kini status pengumpulan.',
        'Reported:': 'Dilaporkan:',
        'View Details': 'Lihat Butiran',
        'No Assigned Complaints': 'Tiada Aduan Ditugaskan',
        'You are all caught up! Check back later for new tasks.': 'Anda sudah bersedia! Semak semula kemudian untuk tugas baru.',
        'Back to Dashboard': 'Kembali ke Papan Pemuka',
        
        # Waste Collector - Complaint Detail
        'Back to Tasks': 'Kembali ke Tugasan',
        'Update Work Progress': 'Kemas Kini Kemajuan Kerja',
        'CURRENT STATUS': 'STATUS SEMASA',
        'In Action (Still Working)': 'Sedang Diproses (Masih Bekerja)',
        'Completed (Work Finished)': 'Selesai (Kerja Selesai)',
        'WASTE VOLUME (KG)': 'VOLUM SAMPAH (KG)',
        'COLLECTION EVIDENCE (PHOTO)': 'BUKTI PENGUMPULAN (FOTO)',
        'No photo provided': 'Tiada foto disediakan',
        'Previous evidence uploaded. Upload again to replace.': 'Bukti terdahulu dimuat naik. Muat naik semula untuk menggantikan.',
        'Upload photo of the cleared area as proof.': 'Muat naik foto kawasan yang dibersihkan sebagai bukti.',
        'Update Task & Save Progress': 'Kemas Kini Tugasan & Simpan Kemajuan',
        
        # Feedback Form
        'Nature of Feedback': 'Sifat Maklum Balas',
        'Suggestion': 'Cadangan',
        'Compliment': 'Pujian',
        'Service Issue': 'Isu Perkhidmatan',
        'Subject': 'Subjek',
        'What is this about?': 'Ini tentang apa?',
        'Your Message': 'Mesej Anda',
        'Share your thoughts here...': 'Kongsikan pemikiran anda di sini...',
        'Send Feedback': 'Hantar Maklum Balas',
        'Your message is too short.': 'Mesej anda terlalu pendek.',
        'We value your suggestions to make EcoClean better.': 'Kami menghargai cadangan anda untuk membuat EcoClean lebih baik.',
    },
    'zh': {  # Simplified Chinese
        # ==== From templates extracted by pybabel ====
        # Navigation & Layout
        'Home': '主页',
        'News': '新闻',
        'Complaints': '投诉',
        'Rewards': '奖励',
        'Feedback': '反馈',
        'Helpline': '帮助热线',
        'Update Status': '更新状态',
        'Dashboard': '仪表板',
        'Assign Hub': '分配中心',
        'Verify Points': '验证积分',
        'Manage Helpline': '管理帮助热线',
        'News Hub': '新闻中心',
        'My Profile': '我的个人资料',
        'Admin Profile': '管理员个人资料',
        'Language Hub': '语言中心',
        'Logout': '退出登录',
        'Login': '登录',
        'Register': '注册',
        
        # Login Page
        'Welcome Back': '欢迎回来',
        'Access your waste management dashboard': '访问您的废物管理仪表板',
        'New here?': '初来乍到?',
        'Sign Up Now': '立即注册',
        
        # Sign Up Page
        'Join EcoClean': '加入EcoClean',
        'Help keep our city clean and sustainable.': '帮助保持我们的城市清洁和可持续。',
        'Select your primary role in the system.': '在系统中选择您的主要角色。',
        'Optional: Upload a JPG or PNG profile picture.': '可选：上传JPG或PNG个人资料图片。',
        'Create Account': '创建账户',
        'Already have an account?': '已有账户?',
        
        # Change Language
        'Current': '当前',
        
        # Additional translations
        'Select your preferred language.': '选择您的首选语言。',
        'Available': '可用',
        'Back to Hub': '返回中心',
        'Profile': '个人资料',
        'Settings': '设置',
        'Help': '帮助',
        'Points': '积分',
        
        # Common Actions
        'Submit': '提交',
        'Send': '发送',
        'Edit': '编辑',
        'Delete': '删除',
        'Save': '保存',
        'Cancel': '取消',
        'Back': '返回',
        'Close': '关闭',
        'Confirm': '确认',
        'Yes': '是',
        'No': '否',
        'Loading': '加载中',
        
        # Messages
        'Error': '错误',
        'Success': '成功',
        'Warning': '警告',
        'Info': '信息',
        'No results found': '未找到结果',
        'Are you sure?': '您确定吗?',
        'Saved successfully': '保存成功',
        'Deleted successfully': '删除成功',
        'Please try again': '请重试',
        'Access denied': '访问被拒绝',
        'Invalid input': '输入无效',
        'Required field': '必填字段',
        
        # Forms
        'Email': '电子邮件',
        'Password': '密码',
        'Username': '用户名',
        'Name': '姓名',
        'Description': '描述',
        'Category': '类别',
        'Subject': '主题',
        'Message': '消息',
        'Upload': '上传',
        'Submit Report': '提交报告',
        'Location': '位置',
        'Date': '日期',
        'Status': '状态',
        
        # Complaint Related
        'Make Complaint': '提出投诉',
        'Report Waste': '报告废物',
        'View Complaints': '查看投诉',
        'Complaint Status': '投诉状态',
        'Pending': '待处理',
        'In Action': '处理中',
        'Completed': '已完成',
        
        # Rewards Related
        'Recycle & Earn': '回收并赚取积分',
        'Request Points': '申请积分',
        'Redeem Points': '兑换积分',
        'Available Points': '可用积分',
        'Pending Points': '待审核积分',
        'Total Points': '总积分',
        
        # Chat Related
        'Live Chat': '实时聊天',
        'Chat Support': '聊天支持',
        'Type your message': '输入您的消息',
        'Type your response': '输入您的响应',
        'Response sent': '响应已发送',
        'Message sent': '消息已发送',
        'Select a resident to message': '选择一个居民进行消息传递',
        
        # Helpline
        'Support Center': '支持中心',
        'Contact Us': '联系我们',
        'Hotline': '热线',
        'FAQ': '常见问题',
        'Email Support': '电子邮件支持',
        'Chat with us': '与我们聊天',
        
        # Feedback
        'Give Us Feedback': '给我们反馈',
        'Thank you for your feedback': '感谢您的反馈',
        
        # News
        'Latest News': '最新新闻',
        'No news available': '没有可用的新闻',
        'Read More': '阅读更多',
        
        # Admin Dashboard
        'Admin Dashboard': '管理仪表板',
        'Welcome back, ': '欢迎回来, ',
        '. Here is the community overview.': '。以下是社区概览。',
        'Residents': '居民',
        'Pending Dispatch': '待派遣',
        'Point Requests': '积分请求',
        'Resolved Cases': '已解决案例',
        'Management Tools': '管理工具',
        'Dispatch Center': '派遣中心',
        'Verify Point Requests': '验证积分请求',
        'Feedback Hub': '反馈中心',
        'Manage News Hub': '管理新闻中心',
        'User Database': '用户数据库',
        'Recent Urgent Reports': '最近紧急报告',
        'View All Activity': '查看所有活动',
        'Resident': '居民',
        'Type': '类型',
        'Action': '操作',
        
        # Dashboard Summary Page
        'Live overview of city-wide waste collection and collector performance.': '城市范围内废物收集和收集者绩效的实时概览。',
        'Live Volume': '实时体积',
        'Total Waste Volume': '总废物体积',
        'kg': '公斤',
        'View Detailed Logs': '查看详细日志',
        'Recycling Rate': '回收率',
        'Verified': '已验证',
        'Analyze Reward Impact': '分析奖励影响',
        'Monitor Active Routes': '监控活跃路线',
        'Task Completion': '任务完成',
        'Performance': '性能',
        'System Status: Operational': '系统状态：正常运行',
        'Administrative Control Center': '行政控制中心',
        'This dashboard aggregates real-time data from': '此仪表板聚合来自以下内容的实时数据',
        'Collector Reports': '收集者报告',
        'and': '和',
        '. Verified entries automatically update the volume and sustainability metrics.': '。已验证的条目自动更新体积和可持续性指标。',
        'Detailed Analytics': '详细分析',
        'Refresh Data': '刷新数据',
        
        # Pending Assignments Page
        'Pending Assignments': '待处理任务',
        'ID': 'ID',
        'Date Reported': '报告日期',
        'Manage & Assign': '管理和分配',
        
        # Verify Points Page
        'Material:': '材料:',
        'Weight:': '重量:',
        'Potential Points:': '潜在积分:',
        'Approve': '批准',
        'Reject': '拒绝',
        'No pending point requests to verify.': '没有待验证的积分请求。',
        
        # Helpline Management Page
        'Helpline Management Hub': '帮助热线管理中心',
        'Control all support channels, contact information, and resident resources.': '控制所有支持渠道、联系信息和居民资源。',
        'Edit Hotline': '编辑热线',
        'Set the official support address.': '设置官方支持地址。',
        'Edit Email': '编辑电子邮件',
        'Manage active chat channels.': '管理活跃聊天频道。',
        'FAQs': '常见问题',
        'Manage common questions.': '管理常见问题。',
        'Manage FAQ': '管理常见问题',
        
        # Chat Management
        'Chat Channels': '聊天频道',
        'Manage your live support channels for residents.': '为居民管理您的实时支持频道。',
        'New Channel': '新频道',
        'Channel Name': '频道名称',
        'Active': '活跃',
        'Inactive': '不活跃',
        'Delete this channel?': '删除此频道?',
        'No channels created yet.': '还没有创建频道。',
        
        # Complaints Management
        'No photo available': '没有可用的照片',
        'Status:': '状态:',
        'Reporter': '报告人',
        
        # Feedback Management
        'Review and manage feedback submitted by residents.': '审查和管理居民提交的反馈。',
        'View Details': '查看详情',
        'No feedback has been submitted yet.': '还没有提交任何反馈。',
        
        # News Management
        'Manage community announcements and alerts': '管理社区公告和警报',
        'Add New Post': '添加新帖子',
        'Posted Date': '发布日期',
        'Article Summary': '文章摘要',
        'Permanent delete: are you sure?': '永久删除：您确定吗?',
        
        # User Management
        'No residents registered yet.': '还没有注册任何居民。',
        'pts': 'pts',
        'Tier': '等级',
        'Role': '角色',
        
        # FAQ Management
        'Create, update, or remove help articles for residents.': '为居民创建、更新或删除帮助文章。',
        'Add New FAQ': '添加新常见问题',
        'Manage FAQs': '管理常见问题',
        'Are you sure you want to delete this FAQ?': '您确定要删除此常见问题吗?',
        'No FAQs found': '未找到常见问题',
        'Start by adding your first question for the residents.': '首先为居民添加您的第一个问题。',
        'Add First FAQ': '添加第一个常见问题',
        
        # Additional Resident Translations
        'No announcements today.': '今天没有公告。',
        'Recent Community Activity': '最近的社区活动',
        'Waste reported': '报告的废物',
        'No news posts available at the moment.': '目前没有可用的新闻帖子。',
        'No recycling history found.': '未找到回收历史记录。',
        'Complaint Terminology': '投诉术语',
        'Learn the difference between Domestic, Public, and Bulk waste.': '了解家庭、公共和散装废物之间的区别。',
        'Waste Reporting Center': '废物报告中心',
        'Select an option below to manage your waste reports or learn about categories.': '选择下面的选项来管理您的废物报告或了解类别。',
        'Make a New Report': '提出新报告',
        'Upload a photo and pin the location of waste on the map.': '上传照片并在地图上标记废物的位置。',
        'Check Complaint Status': '检查投诉状态',
        'View your history and track progress of your submissions.': '查看您的历史记录并跟踪提交进度。',
        'Complaint Terminology Guide': '投诉术语指南',
        'In Progress': '处理中',
        
        # Language Selection
        'Language changed to': '语言已更改为',
        'English': '英文',
        'Bahasa Melayu': '马来语',
        
        # Waste Collector - Home Dashboard
        'Collector Dashboard': '收集器仪表板',
        'Welcome back,': '欢迎回来,',
        'Here is your pickup schedule.': '这是您的取货计划。',
        'GPS:': 'GPS:',
        'Initializing...': '正在初始化...',
        'System Online': '系统在线',
        'Active Pickups': '活跃取货',
        'Tracking Status': '追踪状态',
        'Waiting for location permission...': '等待位置权限...',
        'Refresh GPS': '刷新 GPS',
        'Current Assignments': '当前分配',
        'Report ID': '报告 ID',
        'Location Coords': '位置坐标',
        'Waste Type': '废物类型',
        'Action': '操作',
        'Details': '详情',
        'No active tasks assigned!': '未分配活跃任务!',
        
        # Waste Collector - Profile
        'Verified Collector': '已验证收集器',
        'Jobs Done': '完成的工作',
        'KG Collected': '公斤已收集',
        'Account Details': '账户详情',
        'Access Level': '访问级别',
        'Waste Collector': '废物收集器',
        'Online': '在线',
        'Edit Profile': '编辑个人资料',
        'Tasks': '任务',
        
        # Waste Collector - Assignments
        'Your Assignments': '您的分配',
        'Click on a card to view full details and update the collection status.': '单击卡片查看完整详情并更新收集状态。',
        'Reported:': '报告:',
        'View Details': '查看详情',
        'No Assigned Complaints': '无分配投诉',
        'You are all caught up! Check back later for new tasks.': '您已赶上进度!稍后查看新任务。',
        'Back to Dashboard': '返回仪表板',
        
        # Waste Collector - Complaint Detail
        'Back to Tasks': '返回任务',
        'Update Work Progress': '更新工作进度',
        'CURRENT STATUS': '当前状态',
        'In Action (Still Working)': '处理中 (仍在工作)',
        'Completed (Work Finished)': '已完成 (工作已完成)',
        'WASTE VOLUME (KG)': '废物体积 (KG)',
        'COLLECTION EVIDENCE (PHOTO)': '收集证据 (照片)',
        'No photo provided': '未提供照片',
        'Previous evidence uploaded. Upload again to replace.': '以前的证据已上传。重新上传以替换。',
        'Upload photo of the cleared area as proof.': '上传已清空区域的照片作为证明。',
        'Update Task & Save Progress': '更新任务并保存进度',
        
        # Feedback Form
        'Nature of Feedback': '反馈性质',
        'Suggestion': '建议',
        'Compliment': '表扬',
        'Service Issue': '服务问题',
        'Subject': '主题',
        'What is this about?': '这是关于什么的?',
        'Your Message': '您的消息',
        'Share your thoughts here...': '在这里分享您的想法...',
        'Send Feedback': '发送反馈',
        'Your message is too short.': '您的消息太短。',
        'We value your suggestions to make EcoClean better.': '我们重视您的建议，以使EcoClean更好。',
    }
}

def populate_translations():
    """Populate the .po files with translations"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    for lang, translations in TRANSLATIONS.items():
        po_path = os.path.join(base_path, f'application/translations/{lang}/LC_MESSAGES/messages.po')
        
        if not os.path.exists(po_path):
            print(f"⚠️  {po_path} not found")
            continue
        
        po = polib.pofile(po_path)
        translated_count = 0
        
        # Update translations
        for entry in po:
            if entry.msgid and entry.msgid in translations:
                entry.msgstr = translations[entry.msgid]
                translated_count += 1
        
        # Save the file
        po.save(po_path)
        print(f"✓ Updated {lang.upper()}: {translated_count} strings translated ({po_path})")

if __name__ == '__main__':
    populate_translations()
    print("\n✓ Translation population complete!")
    print("Next step: Run 'pybabel compile -d application/translations'")
