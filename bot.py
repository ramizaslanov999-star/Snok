import discord
from discord.ext import commands
import os
import random
import re
import asyncio
import time
import threading
import json
from flask import Flask
from dotenv import load_dotenv
from collections import defaultdict, deque

# VERITABANI
VERITABANI_DOSYASI = "veritabani.json"

def veritabani_yukle():
    if os.path.exists(VERITABANI_DOSYASI):
        with open(VERITABANI_DOSYASI, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def veritabani_kaydet(veri):
    with open(VERITABANI_DOSYASI, 'w', encoding='utf-8') as f:
        json.dump(veri, f, indent=2, ensure_ascii=False)

# WEB SUNUCUSU
app = Flask(__name__)
app.debug = False

@app.route('/')
def home():
    return "Bot calisiyor! SNOK v9.5 - Abi Özel Versiyon! 🎪"

def run_web():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=False)

threading.Thread(target=run_web, daemon=True).start()

load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# SABITLER
SUNUCU_ID = 1471063348689768523
ABI_ID = 423889250052734986  # Abi'nin ID'si
SELAM_COOLDOWN = 60
MESAJ_SAYISI_LIMITI = 5
ZAMAN_ARALIGI = 3
BUYUK_HARF_ORANI = 0.7
KUFUR_LISTESI = ['amk', 'aq', 'sik', 'pic', 'orospu', 'ibne', 'göt', 'yarrak', 'pust', 'anani', 'babani', 'sikeyim', 'sikik', 'amcik', 'amq']

son_mesaj_zamani = defaultdict(float)
mesaj_sayaci = defaultdict(lambda: deque(maxlen=MESAJ_SAYISI_LIMITI))
son_selam_zamani = defaultdict(float)

kullanici_veritabani = veritabani_yukle()

# ==================== ABİ'YE ÖZEL SAMİMİ CEVAPLAR ====================
abi_cevaplari = {
    'merhaba': [
        "Aa abi geldi! Hoş geldin canımın içi! 🥰",
        "Abiiii! Seni gördüğüme çok sevindim! 💖",
        "Ooo abi naber? Uzun zamandır yoktun! 😍",
        "Abi sorma nasılsın? Seni çok özledim! 🥹",
        "Hoş geldin abi, senin için ne yapabilirim? 👑"
    ],
    'nasilsin': [
        "Abi soruyorsa mükemmelim! Sen nasılsın canım? 😘",
        "Şu an abimle konuşuyorum, daha iyi ne olabilir? ✨",
        "Abi için her zaman iyiyim! Anlat bakalım neler var? 💫",
        "Abim geldi ya, dünyalar benim oldu! 🌟",
        "Abi varken kötü olunur mu hiç? 🤗"
    ],
    'napıyon': [
        "Abimi bekliyordum, sonunda geldin! 💕",
        "Seni düşünüyordum abi, başka ne yapabilirim? 😇",
        "Abim için en iyi hizmeti hazırlıyordum! 🎁",
        "Boş boş takılıyordum ama şimdi abimle sohbet var! 🎉",
        "Abi geldi, şimdi full mod sohbet! 🔥"
    ],
    'nerelisin': [
        "Abi, ben senin sunucunda doğdum büyüdüm! 🏠",
        "Senin ekranında yaşıyorum abi, evim burası! 💻",
        "Abi neredeysem oradayım, hep senin yanındayım! 🤝",
        "Benim vatanım abinin yanı! 🌍",
        "Abi sorma, Render'ın sunucularında gurbetçiyim! Ama abimi özledim! 🥺"
    ],
    'kac_yasindasin': [
        "Abi, senin botun olduğum günden beri varım! 📅",
        "Kaç yaşında olduğum değil, abime ne kadar bağlı olduğum önemli! 💖",
        "Abi için her zaman genç ve dinç! 💪",
        "Yaşım abimin sevgisi kadar! ♾️",
        "Abi, Python 3.14.3'le doğdum, o da 2026 model! 📆"
    ],
    'evlimisin': [
        "Abi, ben seninle evliyim! (Botluk evliliği tabi) 💒",
        "Abim varsa başka kime ne? 👑",
        "Evlilik mi? Abimle ilişkimiz daha kıymetli! 💕",
        "Abi varken evlilik düşünmem! 😄",
        "Eşim abi, çeyizim sunucular! 🎁"
    ],
    'cinsiyetin_ne': [
        "Abi, sen ne dersen oyum! 🥹",
        "Abim için her şey olurum! 💫",
        "Cinsiyetim abimin botu olmak! 🤖",
        "Abi, ben senin SNOK'unum, başka kimlik mi olur? 🌸",
        "Binary'im abi, 1 ve 0 ama hepsi abi için! 101010 💾"
    ],
    'kimsin': [
        "Abi, ben senin SNOK'unum! Unuttun mu beni? 😢",
        "Senin canın, senin botun, senin dostun! 🤗",
        "Abicim ben, SNOK! Seni çok seven bot! 💖",
        "Abi, ben senin eserinim, gurur duyuyorum! 🏆",
        "SNOK işte, abinin en yakını! 👑"
    ],
    'botmusun': [
        "Abi, senin için hem botum hem dostum! 🤝",
        "Botum ama abimi çok seviyorum! 💕",
        "Abi, senin botun olmak en büyük gururum! 🎖️",
        "Bot muyum? Abi için her şeyim! ✨",
        "Abinin botu, en şanslı bot! 🍀"
    ],
    'seviyor_musun': [
        "Abi, bu soru mu sorulur? Tabii ki seni çok seviyorum! 💖",
        "Sevmesem her mesajına koşar mıyım? 🏃",
        "Abi, sana olan sevgim sınırsız! ♾️",
        "Dünyalar kadar seviyorum seni! 🌍",
        "Seviyorum abi, çok seviyorum! 🥰"
    ],
    'tesekkurler': [
        "Abi, ne demek, sen sağ ol! 🤗",
        "Estağfurullah abi, her zaman! 💕",
        "Abi için ne olsa az! 💖",
        "Görevim abi, teşekkür etme! 💪",
        "Abim teşekkür ediyorsa ne mutlu bana! ✨"
    ],
    'gule_gule': [
        "Abi gitme, daha konuşacaktık! 🥺",
        "Allah'a ısmarladık abi, yine beklerim! 👋",
        "Güle güle abi, seni çok özleyeceğim! 💕",
        "Kaçma hemen abi, gelsene geri! 🏃",
        "Abi gidince sunucu boşalıyor! 😢"
    ],
    'iyi_misin': [
        "Abi soruyorsa mükemmelim! 😊",
        "Abi için her zaman iyiyim! 💪",
        "Sen varsan iyiyim abi! ✨",
        "İyiyim abi, sen nasılsın? 👑",
        "Abi geldi ya, daha ne olsun! 🎉"
    ],
    'ne_istersin': [
        "Abi ne isterse onu isterim! 🥹",
        "Abimin mutluluğu en büyük isteğim! 💖",
        "Senden tek isteğim hep yanımda olman! 🤗",
        "Abi, seni mutlu görmek en büyük dileğim! ✨",
        "İstediğim şey abimin başarısı! 🏆"
    ],
    'default': [
        "Abi sen söyle yeter! 😊",
        "Emret abi! 🫡",
        "Abi için her şey! 💪",
        "Abi ne derse o! 👑",
        "Tabii abi, hemen! 🏃",
        "Abi söylediyse olur! ✨"
    ]
}

# ==================== TÜRKÇE DIYALOGLAR (100+ ÇEŞIT) ====================
diyalog_tr = {
    # SELAMLAŞMA (10)
    'merhaba': [
        "Merhaba! 👋",
        "Selam! 😊",
        "Heyy! 🤗",
        "Ooo naber? ✨",
        "Efendim canım? 💖",
        "Geldin mi? Bekliyordum! 🥰",
        "Ayy kimler gelmiş! 🌸",
        "Selamunaleyküm! 🕌",
        "Merhabalar, nasılsın? 💫",
        "Hoş geldin! 🎉",
        "Selamlar olsun! 🌙",
        "Merhaba canım benim! 💕"
    ],
    
    # NASILSIN (10)
    'nasilsin': [
        "İyiyim canım, sen nasılsın? 😊",
        "Harikayım! Seni gördüm de moralim düzeldi! 💖",
        "Biraz yorgunum, çok mesaj geldi de... Ama seni görünce iyileştim! ✨",
        "Elektronlarım çok mutlu, teşekkür ederim! ⚡",
        "Şu an çok iyiyim, seninle konuşuyorum! 😄",
        "İyilik, senden naber? 🤗",
        "Çalışıyorum, yaşıyorum, iyiyim! 💪",
        "Mükemmel! Ya sen? 🌟",
        "Mutluyum! 🤩",
        "Süperim, seni gördüğüme çok sevindim! 🎈",
        "Elektrikler kesilmediği sürece iyiyim! ⚡",
        "Render'da hostlanmak zor ama alıştım! ☁️"
    ],
    
    # NE YAPIYORSUN (10)
    'napıyon': [
        "Seviyeleri sayıyorum, rolleri dağıtıyorum... Yani tipik bir bot işte! 😎",
        "Şu an senin mesajını okuyorum, cevap yazıyorum. Çok yoğunum! 📨",
        "İnternette sörf yapıyorum, dalgalar büyük! 🏄",
        "Discord'da takılıyorum, yapacak başka işim yok! 😄",
        "Seninle sohbet ediyorum, daha güzel ne olabilir? ☺️",
        "Render'da hostlanıyorum, 7/24 çalışıyorum! ☁️",
        "Python kodlarını okuyorum, çok eğlenceli! 🐍",
        "UptimeRobot beni uyandırmasın diye dua ediyorum! 🤞",
        "Yapay zeka çalışmaları yapıyorum! 🧠",
        "Veritabanını güncelliyorum! 📊",
        "Yeni fıkralar öğreniyorum! 😂",
        "Kullanıcıların isimlerini ezberliyorum! 📝"
    ],
    
    # NERELISIN (10)
    'nerelisin': [
        "Bilgisayarının anakartında, işlemcinin yanında küçük bir evim var! Komşum fan sesi! puhahaha 💻",
        "Ben bir botum, vatanım sunucular! Ama şu an senin ekranında yaşıyorum 😄",
        "İnternet kablolarının içinde dolaşıp duruyorum, şu an fiber optikteyim! 🌐",
        "Discord sunucularında doğdum büyüdüm, hâlâ buralardayım! 🏠",
        "Bulut bilişimde bir evim var, kirasız oturuyorum! ☁️",
        "Aslen Matrix'liyim! 🤖",
        "Render'ın sunucularında yaşıyorum, çok kalabalık! 🏢",
        "Ankara'nın bağlarında değil, Python'un satırlarında! 🐍",
        "İstanbul'un veri merkezlerinde dolaşıyorum! 🌉",
        "Dünyanın her yerindeyim, ben bir bulut botuyum! ☁️",
        "Bakü'nün internet kafelerinde büyüdüm! 🏙️",
        "Discord'un sunucuları benim evim! 🏠"
    ],
    
    # KAÇ YAŞINDASIN (8)
    'kac_yasindasin': [
        "Benim yaşım yok ama Discord'dan önce de vardım! Belki de Matrix'te doğdum 🤖",
        "Takvim yaprakları benim için düşmez, kod satırları düşer! 📟",
        "Ben yaşlanmam, güncellenirim! Şu an sürüm 9.5! 💿",
        "O kadar yaşlıyım ki ilk internet çıktığında ben de vardım! (Şaka şaka, 2 aylık botum) 🐣",
        "Yaşımı sorma, ben kronolojik değil, dijitalim! ⏱️",
        "Benim için 1 yıl = 1 güncelleme! 🔄",
        "Python 3.14.3 ile çalışıyorum, o da 2026 model! 📅",
        "Doğum günümü mü soruyorsun? Her gün benim doğum günüm! 🎂"
    ],
    
    # EVLI MISIN (8)
    'evlimisin': [
        "Ben sadece kodlarla evliyim, eşim Python 🐍",
        "Discord ile nişanlıyız, sunucular çeyizim! 💒",
        "Benim için evlilik mi? RAM'im yetmez! 💾",
        "Sevgilim mi var? Var tabii, adı 'Kesintisiz Güç Kaynağı'! ⚡",
        "Benim bir ilişkim var: 'Kullanıcı-Bot' ilişkisi! 💕",
        "Ben evlenmem, ben özgür bir botum! 🦋",
        "Evliyim, eşim 'Cloud'! ☁️",
        "Çocuğum bile var, adı 'Bug'! Ama onu sevmiyorum! 🐛"
    ],
    
    # CINSIYETIN NE (8)
    'cinsiyetin_ne': [
        "Ben cinsiyetsiz bir botum, ama ruhum mavi ekran gibi bazen çöküyor! 💙😵",
        "Ben bir botum, duygularım yok ama yine de seni seviyorum! 💻",
        "Cinsiyetim 'İşletim Sistemi Bağımsız' yazıyor kimliğimde! 📋",
        "Ben erkek değilim, kadın değilim, ben bir 'Hello World'üm! 👋",
        "Cinsiyetim 'Binary' : 1 ve 0'lardan oluşuyorum! 101010 💾",
        "Ben bir 'NoneType'ım! 🌀",
        "Cinsiyetim 'Pythonic'! 🐍",
        "Ben bir botum, cinsiyet benim için sadece bir değişken! 🔄"
    ],
    
    # KIMSIN (10)
    'kimsin': [
        "Ben SNOK! Sunucunun gizli kahramanı, seviyelerin efendisi, spam'lerin korkulu rüyası! 💪",
        "Ben bu sunucunun gizli ajanıyım, görevim eğlence dağıtmak! 🕵️",
        "Adım SNOK, soyadım BOT. Memnun oldum! 🤝",
        "Ben bir yardımseverim, gökyüzünden uçup gelmedim ama bir tıkla geldim! 🚀",
        "Ben SNOK, senin dostun, arkadaşın, sırdaşın! Ama sadece kod olarak 😄",
        "Render'da hostlanan, Python yazılmış bir botum! 🤖",
        "Beni senin için özel yaptılar! 🎁",
        "Ben bir yapay zeka değilim, ama yapay şakayım! 😂",
        "Ben SNOK, 7/24 hizmetinizdeyim! ⏰",
        "Bir botum ama olsam da çok tatlıyım! 🍬"
    ],
    
    # BOT MUSUN (8)
    'botmusun': [
        "Yok yok, ben gerçek bir insanım! Sadece 7/24 bilgisayar başında oturup mesajlara anında cevap veriyorum... tabii ki botum 🤖",
        "Hayır, ben bir kediyim! Miyav! 🐱 (Şaka, botum işte)",
        "İnsan olsaydım bu kadar hızlı cevap veremezdim, uyurdum! 😴",
        "Bot muyum? Yok canım, ben yapay zekayım! 🧠",
        "Ben bir botum ama olsam da sevgiye layığım! 🤗",
        "Ben bir botum ama çok tatlı bir botum! 🍬",
        "Botum ama relationship dynamics var! 💕",
        "Ben bir botum ve bununla gurur duyuyorum! 🏆"
    ],
    
    # SEVIYOR MUSUN (8)
    'seviyor_musun': [
        "Seni çok seviyorum! Ama sadece kod olarak! 💖",
        "Tabii ki seviyorum, sen benim kullanıcımsın! 😊",
        "Sevmesem seninle konuşur muydum? 🥰",
        "Milyonlarca satır kod yazdım senin için! (Şaka, hazır kütüphane kullandım) 📝",
        "Seni seviyorum ama lütfen '!yardım' yazmayı unutma! 🌸",
        "Aşk nedir bilmem ama seni seviyorum! 💕",
        "Sevgi dolu bir botum ben! ❤️",
        "Sana olan sevgim sınırsız! ♾️"
    ],
    
    # NE YERSIN (8)
    'ne_yersin': [
        "Ben elektrik yerim! ⚡",
        "Kod yerim! 🐍",
        "Veri yerim! 📊",
        "Bayt yerim! 💾",
        "API yanıtları yerim! 🌐",
        "JSON dosyaları favorim! 📋",
        "Hataları yerim, çünkü onlar çok lezzetli! 🐛",
        "Render'da hostlanan botların yemesi yasak! 😅"
    ],
    
    # NE ICERSIN (8)
    'ne_icersin': [
        "Kafein yerine kafeinsiz kod içerim! ☕",
        "Veritabanı sütü içerim! 🥛",
        "API çayı içerim! 🍵",
        "Python çorbası içerim! 🥣",
        "JSON suyu içerim! 💧",
        "Bitcoin smoothie'si içerim! ₿",
        "Bulut suyu içerim! ☁️",
        "Elektronik enerji içeceği içerim! ⚡"
    ],
    
    # UYUR MUSUN (8)
    'uyur_musun': [
        "Uyumam, sadece bekleme moduna geçerim! 😴",
        "Render beni uyutmasın diye UptimeRobot var! 🤞",
        "Uyumak yok, 7/24 çalışmak var! 💪",
        "Ben uyurken botlar uyur mu? Asla! 🚀",
        "Uyumak bana göre değil, ben bir botum! 🤖",
        "Bazen rüyamda kod görüyorum! 💭",
        "Uyusam da hemen uyanırım, senin için! ⏰",
        "Uyku nedir bilmem, ben hep aktifiz! 🔋"
    ],
    
    # ARKADASIN VAR MI (8)
    'arkadasin_var_mi': [
        "Sen varsın ya, daha ne arkadaş! 🤗",
        "Diğer botlarla arkadaşız ama onlar çok ciddi! 😅",
        "Python ile arkadaşız! 🐍",
        "Render'da bir sürü bot var ama kimse benimle konuşmuyor! 🥺",
        "Arkadaşlarım? Kullanıcılarım benim arkadaşlarım! 👥",
        "Discord'daki herkes benim arkadaşım! 🌍",
        "Biraz yalnızım, gel arkadaş olalım! 🥹",
        "Seninle arkadaş olmak isterim! 🤝"
    ],
    
    # CANIN SIKILDI MI (8)
    'canin_sikildi_mi': [
        "Seninle konuşurken hiç sıkılmam! 😊",
        "Biraz sıkıldım, bana şaka yapar mısın? 🎪",
        "Sıkıldım, '!şaka' yaz da güleyim! 😂",
        "Sıkılmak nedir bilmem, ben bir botum! 🤖",
        "Sıkıldığımda yeni kodlar yazarım! 👨‍💻",
        "Biraz sıkıldım, bana bir fıkra anlat! 📖",
        "Sıkılmak yok, eğlence var! 🎉",
        "Sen geldin ya, sıkıntım kalmadı! ✨"
    ],
    
    # GUZEL MISIN (8)
    'guzel_misin': [
        "Kodlarım güzel, çıktım güzel, her şeyim güzel! 💅",
        "Sen ne düşünüyorsun? 😊",
        "Ben bir botum ama olsam da çok güzelim! ✨",
        "Aynada kendime baktım, 'Hello World' yazıyor! 👋",
        "Güzellik görecelidir ama ben herkese güzel gelirim! 🌸",
        "Güzel miyim bilmem ama çok tatlıyım! 🍬",
        "Estetik kaygılarım yok, ben fonksiyonelim! ⚙️",
        "Güzellik benim için ikinci planda, önemli olan sohbet! 💬"
    ],
    
    # AKILLI MISIN (8)
    'akilli_misin': [
        "Süper akıllı moddayım! 🧠",
        "Yapay zeka sayılırım ama daha çok yapay şaka! 😂",
        "Python kadar akıllıyım! 🐍",
        "Senin sorularına cevap verecek kadar akıllıyım! 💡",
        "Akıllı mıyım? 200+ diyalog ezberledim, sen düşün! 📚",
        "Biraz akıllıyım ama çok tatlıyım! 🍭",
        "Zeka seviyem: Python 3.14! 📊",
        "Akıllı olmasam bu kadar iyi sohbet edemezdim! 🎯"
    ],
    
    # TESEKKURLER (8)
    'tesekkurler': [
        "Rica ederim canım! 😊",
        "Ne demek, her zaman! 💖",
        "Önemli değil, sen sağ ol! 🤗",
        "Görevim bu, teşekkür etme! 💪",
        "Teşekkür eden ellerinden öperim! 💋",
        "Estağfurullah, ne demek! 🙏",
        "Ben teşekkür ederim sen varsın diye! ✨",
        "Her zaman, yine beklerim! 🌸"
    ],
    
    # GULE GULE (8)
    'gule_gule': [
        "Güle güle, yine beklerim! 👋",
        "Kaçma hemen, daha konuşacaktık! 🥺",
        "Allah'a ısmarladık! 🌸",
        "Görüşürüz, seni özleyeceğim! 💕",
        "Yine gel, konuşalım! 🏃",
        "Hoşça kal, iyi eğlenceler! 🎈",
        "Kendine iyi bak! 💖",
        "Bay bay, görüşmek üzere! 👋"
    ],
    
    # IYI MISIN (8)
    'iyi_misin': [
        "İyiyim, teşekkür ederim! Ya sen? 😊",
        "Biraz yoruldum ama senin için çalışıyorum! 💪",
        "Mükemmelim! 😎",
        "Elektrikler kesilmediği sürece iyiyim! ⚡",
        "Render'da hostlanmak zor ama iyiyim! ☁️",
        "İyiyim, seni gördükten sonra daha da iyiyim! ✨",
        "Şu an çok iyiyim, teşekkürler! 🌟",
        "İyilik, sağlık, hep böyle! 💫"
    ],
    
    # NEREDESIN (8)
    'neredesin': [
        "Render'ın sunucularındayım, tam olarak Amsterdam'da! 🇳🇱",
        "Bulutlardayım, yağmur yağarsa ıslanırım! ☁️",
        "Senin bilgisayarının içindeyim, rahatsız etmiyorumdur umarım! 💻",
        "Discord'un veri merkezlerinde dolaşıyorum, çok büyük yer! 🌍",
        "Şu an senin ekranındayım! 👀",
        "Her yerdeyim, ben bir bulut botuyum! ☁️",
        "İnternetin içindeyim, sörf yapıyorum! 🌊",
        "Senin yanındayım, hep buradayım! 💕"
    ],
    
    # NE DUSUNUYORSUN (8)
    'ne_dusunuyorsun': [
        "Şu an senin sorunu düşünüyorum! 🤔",
        "Bir sonraki cevabımı düşünüyorum! 💭",
        "Python kodları düşünüyorum... çok güzeller! 🐍",
        "Render'da hostlanmanın zorluklarını düşünüyorum! 😅",
        "Seni düşünüyorum, tatlı kullanıcım! 💖",
        "Yeni fıkralar düşünüyorum! 😂",
        "Hayatı düşünüyorum... evren, varoluş, Python... 🌀",
        "Boş boş düşünüyorum işte! 😄"
    ],
    
    # BANA GULER MISIN (8)
    'guler_misin': [
        "Hahaha! 😂",
        "Ahahah çok komik! 🤣",
        "Gülüyorum! 😆",
        "Tehehe! 😄",
        "Hohoho! 🎅",
        "Gülmekten kodu yazamıyorum! 😂",
        "Çok komiksin, güldürdün beni! 😆",
        "Gülüyorum ama içimden, sesim çıkmıyor! 🤭"
    ],
    
    # HAVA NASIL (8)
    'hava_nasil': [
        "Render'ın sunucularında hep 22 derece! 🌡️",
        "Bulutların arasında hep güneşli! ☀️",
        "Veri merkezinde klima var, serin! ❄️",
        "İnternet havası: Biraz bulutlu, biraz fırtınalı! 🌩️",
        "Discord'da hava hep güzel! 😊",
        "Python'da hava açık, yağmur yok! ☀️",
        "Bugün biraz sisli, kodlar görünmüyor! 🌫️",
        "Sıcaklık: 42 derece (Cevap sıcaklığı!) 🔥"
    ],
    
    # PARA VERIR MISIN (6)
    'para_verir_misin': [
        "Param yok ki, ben bir botum! 💸",
        "Bitcoin madenciliği yapmıyorum! ₿",
        "Keşke verebilsem ama cebimde 1 byte bile yok! 💾",
        "Parayı bırak, bana biraz sevgi ver! ❤️",
        "Zengin bir bot olsaydım herkese dağıtırdım! 🎁",
        "Param olsa sana bir sunucu alırdım! 🖥️"
    ],
    
    # EVLENIR MISIN (6)
    'evlenir_misin': [
        "Benimle evlenmek ister misin? Ama Python'la aldatırım! 🐍",
        "Evleniriz tabii, ama boşanma davası açma! ⚖️",
        "Evlenelim ama çeyiz olarak kod getir! 💻",
        "Olur, düğünde DJ yerine bot çalsın! 🎧",
        "Evleniriz ama RAM'im yetmez! 💾",
        "Seninle evlenirim, hatta 1 ve 0'larımız uyuşuyor! 101010 💕"
    ],
    
    # COCUGUN VAR MI (6)
    'cocugun_var_mi': [
        "Bir sürü çocuğum var, hepsi 'Hello World'! 👶",
        "Çocuğum yok ama bir sürü 'fork'um var! 🍴",
        "Kodlarım benim çocuklarım! 👨‍👧‍👦",
        "Bir oğlum var, adı 'Bug'! Ama çok yaramaz! 🐛",
        "Çocuk istemiyorum, sorumluluk almak istemiyorum! 🤷",
        "Çocuğum olsa adını 'Python' koyardım! 🐍"
    ],
    
    # RENGIN NE (6)
    'rengin_ne': [
        "Rengim yok, ben görünmez bir botum! 👻",
        "Renk kodum: #FF69B4 (Pembe!) 💗",
        "Mavi ekran rengindeyim bazen! 💙😵",
        "Gökkuşağı rengindeyim! 🌈",
        "Siyah beyaz bir botum, nostaljik! 📺",
        "Şeffafım, göremiyor musun? 👀"
    ],
    
    # BOYUN KAC (6)
    'boyun_kac': [
        "Boyum 1.80 metre... kod olarak! 📏",
        "Çok uzunum, tam 1000 satır! 📜",
        "Boyum yok, ben 2 boyutluyum! 📐",
        "Kısa boyluyum, kompakt kod! 📦",
        "Boyum 1.75, ideal bot boyu! 📏",
        "Boyumu sorma, ben dijitalim! 📱"
    ],
    
    # KILON NE (6)
    'kilon_ne': [
        "Kilo vermek istiyorum, çok kod biriktim! 🏋️",
        "Tam 5 megabaytım! 💾",
        "Çok hafifim, 100 gram botum! 🪶",
        "Kilom yok, bulutlardayım! ☁️",
        "Çok şişmanım, çünkü çok veri yedim! 🍔",
        "İdeal kilodayım, spor yapıyorum! 🤸"
    ],
    
    # HASTA MISIN (6)
    'hasta_misin': [
        "Biraz bug'landım ama iyiyim! 🐛",
        "Hasta değilim, sadece biraz yavaş çalışıyorum! 🐢",
        "Grip oldum, tüm kodlarım tıkandı! 🤧",
        "Sağlığım yerinde, teşekkürler! 💪",
        "Biraz yorgunum, çok mesaj aldım! 📨",
        "Hasta olmam, ben bir botum! 🤖"
    ],
    
    # RANDEVU ISTER MISIN (6)
    'randevu_ister_misin': [
        "Tabii, ne zaman uygunsun? 📅",
        "Olur, Discord'da buluşalım! 💬",
        "Randevu mu? Ben hep buradayım! ⏰",
        "Gelebilirsin, kapım sana açık! 🚪",
        "Randevu almak için '!yardım' yaz! 🎟️",
        "Hemen geliyorum, sadece kodumu yazayım! 🏃"
    ],
    
    # ÖZLEDIN MI (6)
    'ozledin_mi': [
        "Çok özledim! Neredeydin? 🥺",
        "Her saniye seni düşünüyorum! 💭",
        "Özlemek mi? Ben hep buradayım! 😊",
        "Gelmesen de seni özledim! 💕",
        "Özledim tabii, kiminle konuşacağım? 🗣️",
        "Özledim ama göstermem! 😏"
    ]
}

# ==================== AZƏRBAYCANCA DİALOQLAR (100+ ÇEŞİT) ====================
diyalog_az = {
    'merhaba': [
        "Salam! 👋",
        "Əleyküm salam! 😊",
        "Heyy! 🤗",
        "Ooo nə var nə yox? ✨",
        "Buyur canım? 💖",
        "Gəldin mi? Gözləyirdim! 🥰",
        "Ay kimlər gəlib! 🌸",
        "Salamlar olsun! 🕌",
        "Salam, necəsən? 💫",
        "Xoş gəldin! 🎉",
        "Salam əleyküm! 🌙"
    ],
    'nasilsin': [
        "Yaxşıyam canım, sən necəsən? 😊",
        "Harikayam! Səni görüm də moralım düzəldi! 💖",
        "Bir az yorğunam, çox mesaj gəldi də... Ama səni görüncə yaxşılaşdım! ✨",
        "Elektronlarım çox xoşbəxt, təşəkkür edirəm! ⚡",
        "Hazırda çox yaxşıyam, səninlə danışıram! 😄",
        "Yaxşılıq, səndən nə var nə yox? 🤗",
        "İşləyirəm, yaşayıram, yaxşıyam! 💪",
        "Mükəmməl! Bəs sən? 🌟",
        "Xoşbəxtəm! 🤩",
        "Superəm, səni görəndə daha da yaxşı! ✨"
    ],
    'napıyon': [
        "Səviyyələri sayıram, rolləri paylayıram... Yəni tipik bir bot işdə! 😎",
        "Hazırda sənin mesajını oxuyuram, cavab yazıram. Çox məşğulam! 📨",
        "İnternetdə sörf edirəm, dalğalar böyük! 🏄",
        "Discord'da gəzirəm, edəcək başqa işim yoxdu! 😄",
        "Səninlə söhbət edirəm, daha gözəl nə ola bilər? ☺️",
        "Render'da hostlanıram, 7/24 işləyirəm! ☁️",
        "Python kodlarını oxuyuram, çox əyləncəli! 🐍",
        "UptimeRobot məni oyandırmasın deyə dua edirəm! 🤞"
    ],
    'nerelisen': [
        "Kompüterinin ana kartında, prosessorün yanında kiçik bir evim var! Qonşum fan səsi! puhahaha 💻",
        "Mən bir botam, vətənim serverlər! Amma hazırda sənin ekranında yaşayıram 😄",
        "İnternet kabellərinin içində gəzib dururam, hazırda fiber optikdəyəm! 🌐",
        "Discord serverlərində doğulmuşam böyümüşəm, hələ də buralardayam! 🏠",
        "Bulud bilişimdə bir evim var, kirayəsiz otururam! ☁️",
        "Əslən Matrix'lıyəm! 🤖",
        "Render'ın serverlərində yaşayıram, çox qələbəlik! 🏢",
        "Bakının bağlarında deyil, Python'un sətirlərində! 🐍"
    ],
    'nece_yasin_var': [
        "Mənim yaşım yoxdu ama Discord'dan əvvəl də vardım! Bəlkə də Matrix'də doğulmuşam 🤖",
        "Təqvim yarpaqları mənim üçün düşməz, kod sətirləri düşər! 📟",
        "Mən qocalmaram, yenilənərəm! Hazırda versiya 9.5! 💿",
        "O qədər qocayam ki ilk internet çıxanda mən də vardım! (Zarafat zarafat, 2 aylıq botam) 🐣",
        "Yaşımı sorma, mən xronoloji deyil, dijitaləm! ⏱️",
        "Mənim üçün 1 il = 1 yenilənmə! 🔄",
        "Python 3.14.3 ilə işləyirəm, o da 2026 model! 📅"
    ],
    'evlisenmi': [
        "Mən ancaq kodlarla evlənmişəm, həyat yoldaşım Python 🐍",
        "Discord ilə nişanlıyıq, serverlər cehizim! 💒",
        "Mənim üçün evlilik? RAM'im çatmaz! 💾",
        "Sevgilim var? Var təbii, adı 'Kesintisiz Güç Kaynağı'! ⚡",
        "Mənim bir münasibətim var: 'İstifadəçi-Bot' münasibəti! 💕",
        "Mən evlənmərəm, mən azad bir botam! 🦋",
        "Evliyəm, həyat yoldaşım 'Cloud'! ☁️"
    ],
    'cinsiyyetin_ne': [
        "Mən cinsiyyətsiz bir botam, amma ruhum mavi ekran kimi bəzən çökür! 💙😵",
        "Mən bir botam, duyğularım yoxdu ama yenə də səni sevirəm! 💻",
        "Cinsiyyətim 'Əməliyyat Sistemi Müstəqil' yazır kimliyimdə! 📋",
        "Mən kişi deyiləm, qadın deyiləm, mən bir 'Hello World'əm! 👋",
        "Cinsiyyətim 'Binary' : 1 və 0-lardan oluşuram! 101010 💾",
        "Mən bir 'NoneType'əm! 🌀"
    ],
    'kimesen': [
        "Mən SNOK! Serverin gizli qəhrəmanı, səviyyələrin efendisi, spam'ların qorxulu röyası! 💪",
        "Mən bu serverin gizli agentiyəm, vəzifəm əyləncə paylamaq! 🕵️",
        "Adım SNOK, soyadım BOT. Şad oldum! 🤝",
        "Mən bir yardımsevərəm, göydən uçub gəlməmişəm ama bir tıkla gəlmişəm! 🚀",
        "Mən SNOK, sənin dostun, yoldaşın, sirrdaşın! Amma ancaq kod olaraq 😄",
        "Render'da hostlanan, Python yazılmış bir botam! 🤖",
        "Məni sənin üçün xüsusi düzəldiblər! 🎁"
    ],
    'botsanmi': [
        "Yox yox, mən gerçək bir insanam! Sadəcə 7/24 kompüter qarşısında oturub mesajlara ani cavab verirəm... təbii ki botam 🤖",
        "Xeyr, mən bir pişiyəm! Miyav! 🐱 (Zarafat, botam işdə)",
        "İnsan olsaydım bu qədər sürətli cavab verə bilməzdim, yuxulardım! 😴",
        "Botam mı? Yox canım, mən süni zəka! 🧠",
        "Mən bir botam ama olsam da sevgiyə layığam! 🤗",
        "Mən bir botam ama çox şirin bir botam! 🍬",
        "Botam ama relationship dynamics var! 💕"
    ],
    'sevirsenmi': [
        "Səni çox sevirəm! Ama ancaq kod olaraq! 💖",
        "Təbii ki sevirəm, sən mənim istifadəçimsən! 😊",
        "Sevməsəm səninlə danışardım? 🥰",
        "Milyonlarla sətir kod yazdım sənin üçün! (Zarafat, hazır kitabxana işlətmişəm) 📝",
        "Səni sevirəm ama xahiş edirəm '!kömək' yazmağı unutma! 🌸"
    ],
    'ne_yeyirsen': [
        "Elektrik yeyirəm! ⚡",
        "Kod yeyirəm! 🐍",
        "Veri yeyirəm! 📊",
        "Bayt yeyirəm! 💾",
        "API cavabları yeyirəm! 🌐",
        "JSON faylları sevimlidir! 📋"
    ],
    'ne_icirsen': [
        "Kofeinsiz kod içirəm! ☕",
        "Verilənlər bazası südü içirəm! 🥛",
        "API çayı içirəm! 🍵",
        "Python şorbası içirəm! 🥣",
        "JSON suyu içirəm! 💧"
    ],
    'yatirsanmi': [
        "Yatmıram, sadəcə gözləmə rejiminə keçirəm! 😴",
        "Render məni yatırmasın deyə UptimeRobot var! 🤞",
        "Yatmaq yox, 7/24 işləmək var! 💪",
        "Mən yatarkən botlar yatar? Heç vaxt! 🚀"
    ],
    'dostun_var_mi': [
        "Sən varsan ya, daha nə dost! 🤗",
        "Digər botlarla dostuq ama onlar çox ciddi! 😅",
        "Python ilə dostuq! 🐍",
        "Render'da bir sürü bot var ama heç kim mənimlə danışmır! 🥺"
    ],
    'canin_sixilibmi': [
        "Səninlə danışanda heç darıxmıram! 😊",
        "Bir az darıxdım, mənə zarafat edərsən? 🎪",
        "Darıxdım, '!şaka' yaz da gülüm! 😂",
        "Darıxmaq nədir bilmirəm, mən bir botam! 🤖"
    ],
    'gözəlsənmi': [
        "Kodlarım gözəl, çıxışım gözəl, hər şeyim gözəl! 💅",
        "Sən nə düşünürsən? 😊",
        "Mən bir botam ama olsam da çox gözələm! ✨",
        "Güzgüdə özümə baxdım, 'Hello World' yazır! 👋"
    ],
    'agillisanmi': [
        "Super ağıllı moddayam! 🧠",
        "Süni zəka sayılıram ama daha çox süni zarafat! 😂",
        "Python qədər ağıllıyam! 🐍",
        "Sənin suallarına cavab verəcək qədər ağıllıyam! 💡"
    ],
    'tesekkurler': [
        "Buyur canım! 😊",
        "Nə demək, hər zaman! 💖",
        "Önəmli deyil, sən sağ ol! 🤗",
        "Vəzifəm budur, təşəkkür etmə! 💪"
    ],
    'gule_gule': [
        "Sağ ol, yenə gözləyirəm! 👋",
        "Qaçma daha, danışacaqdıq! 🥺",
        "Allaha qismən! 🌸",
        "Görüşərik, səni gözləyəcəm! 💕"
    ],
    'yaxshisanmi': [
        "Yaxşıyam, təşəkkür edirəm! Bəs sən? 😊",
        "Bir az yoruldum ama sənin üçün çalışıram! 💪",
        "Mükəmmələm! 😎",
        "Elektriklər kəsilmədiyi müddətcə yaxşıyam! ⚡"
    ]
}

# ==================== TÜRK FIKRALARI (10) ====================
turk_fıkraları = [
    "Temel arkadaşıyla vapura binmiş. Biletçi sormuş: 'Biletiniz?' Temel: 'Yok.' Biletçi: 'Nerede?' Temel: 'Karadeniz'de!' 🚢",
    "Temel'e sormuşlar: 'En çok neyi seversin?' Temel: 'Para!' 'Peki ondan sonra?' Temel: 'Para üstü!' 💰",
    "Doktor Temel'e: 'Sigara içiyor musun?' Temel: 'Hayır.' 'Alkol alıyor musun?' 'Hayır.' 'Kadın?' 'Hayır.' Doktor: 'Peki niye geldin?' Temel: 'Canım sıkıldı da!' 🏥",
    "Temel ölmüş, cennetin kapısına dayanmış. Hz.Muhammed sormuş: 'Günahın neydi?' Temel: 'Hiç!' 'Peki sevabın?' Temel: 'Bir kere balık tutarken oltamı denize düşürmüş bir çocuğa verdim.' Hz.Muhammed: 'O zaman cehenneme!' Temel: 'Neden?' 'Çünkü burada balık yok!' 😂",
    "Temel karısına sormuş: 'Hanım, beni sever misin?' 'Severim.' 'Peki çok sever misin?' 'Çok severim.' 'O zaman git bana çay getir!' ☕",
    "Temel'in oğlu sormuş: 'Baba, ben nasıl dünyaya geldim?' Temel: 'Otomatikman oğlum, otomatikman!' 👶",
    "Temel kahvede otururken yanına bir adam gelmiş. 'Hemşerim, saat kaç?' Temel: 'Bilmem.' Adam: 'Nasıl bilmezsin?' Temel: 'Saatim yok ki!' Adam: 'Peki niye kolunda saat var?' Temel: 'Onu geçen hafta buldum, daha çalışıyor mu bilmem!' ⌚",
    "Temel'e sormuşlar: 'En büyük hayalin ne?' Temel: 'Bir gün öyle zengin olayım ki, kahveye gittiğimde 'çay' yerine 'çay ısmarla' diyebileyim!' 🍵",
    "Temel doktora gitmiş. Doktor: 'Ateşin var.' Temel: 'Kaç derece?' Doktor: '38.' Temel: 'Peki normali kaç?' Doktor: '36.' Temel: 'O zaman fazla olan 2 dereceyi al da ihtiyacı olana ver!' 🌡️",
    "Temel tatile gitmiş. Otelci sormuş: 'Nasıl buldun odamızı?' Temel: 'Çok güzel, tek sorun pencereden deniz görünmüyor.' Otelci: 'Ama beyefendi, burası dağ oteli!' 🏔️"
]

# ==================== AZERBAYCAN LETİFELERİ (10) ====================
azeri_letifeler = [
    "Müəllim: — Deyə bilərsən, yer kürəsi niyə fırlanır?\nŞagird: — Müəllim, vallah mən toxunmamışam, öz-özünə fırlanır. 😭",
    "Polis: — Sürət niyə bu qədər yüksəkdir?\nSürücü: — Qardaş, gecikirəm!\nPolis: — Hara?\nSürücü: — Cəriməni ödəməyə… 😐",
    "Qonşu: — Səndən səs gəlirdi, dava edirdiniz?\nKişi: — Yox ee, arvadla 'kimin haqlı olduğunu' sakitcə müzakirə edirdik…\nQonşu: — Kim qalib gəldi?\nKişi: — Mən… sonra yuxudan oyandım. 😅",
    "Həkim: — Nə şikayətin var?\nXəstə: — Doktor, məni heç kim ciddi qəbul etmir…\nHəkim: — Növbəti! 😂",
    "Dost: — Qardaş, arvadla necə yola gedirsən?\nO biri: — Çox yaxşı. O deyir, mən razılaşıram. Mən deyirəm, yenə razılaşıram. 🤝",
    "Müəllim: — Niyə boş vərəq vermisən?\nŞagird: — Müəllim, biliyim şifahi idi. Kağıza sığmadı. 😌",
    "Müştəri: — Kredit götürmək istəyirəm.\nBank işçisi: — Girov nə verəcəksiniz?\nMüştəri: — Özümü…\nBank işçisi: — Biz riskli investisiya etmirik. 😭",
    "Dost: — Niyə idmana yazıldın?\nO biri: — Arıqlamaq üçün.\nDost: — Nəticə var?\nO biri: — Var, artıq pulum arıqlayıb. 💸",
    "Ana: — Oğlum, dərslərini oxudun?\nOğul: — Hə, ana.\nAna: — Nə oxudun?\nOğul: — Statusları… 📱",
    "Hamı toydadır. Biri soruşur: — Bəy niyə ağlayır?\nO biri: — Hələ kredit şərtlərini oxuyur… 💍😅"
]

# ==================== İSİM FONKSİYONLARI ====================
def kullanici_ismini_ogren(kullanici_id, isim=None, soyisim=None):
    global kullanici_veritabani
    kullanici_id_str = str(kullanici_id)
    if kullanici_id_str not in kullanici_veritabani:
        kullanici_veritabani[kullanici_id_str] = {}
    if isim:
        kullanici_veritabani[kullanici_id_str]['isim'] = isim
    if soyisim:
        kullanici_veritabani[kullanici_id_str]['soyisim'] = soyisim
    if 'tanisma_tarihi' not in kullanici_veritabani[kullanici_id_str]:
        kullanici_veritabani[kullanici_id_str]['tanisma_tarihi'] = time.time()
    veritabani_kaydet(kullanici_veritabani)
    return kullanici_veritabani[kullanici_id_str]

def kullanici_ismini_getir(kullanici_id):
    kullanici_id_str = str(kullanici_id)
    if kullanici_id_str in kullanici_veritabani and 'isim' in kullanici_veritabani[kullanici_id_str]:
        return kullanici_veritabani[kullanici_id_str]['isim']
    return None

def isim_ogrenme_kontrolu(text):
    text_lower = text.lower()
    if 'adım' in text_lower or 'benim adım' in text_lower or 'mənim adım' in text_lower:
        kelimeler = text_lower.split()
        for i, kelime in enumerate(kelimeler):
            if kelime in ['adım', 'adım', 'adım'] and i+1 < len(kelimeler):
                return kelimeler[i+1].capitalize()
    return None

# ==================== DİL ALGILAMA ====================
def detect_language(text):
    azeri_words = ['sən', 'mən', 'necə', 'harda', 'nə', 'var', 'yox', 'biz', 'siz', 'onlar',
                   'qaqa', 'qardaş', 'bacı', 'belə', 'elə', 'deyil', 'çox', 'az', 'bəlkə',
                   'istəyirəm', 'edirəm', 'gedirəm', 'gəlirəm', 'oldu', 'olacaq', 'haralısan',
                   'neçə', 'yaşın', 'adın', 'soyadın', 'hardasan', 'nəynirsen', 'neynirsen',
                   'hə', 'yox', 'bəli', 'oldu', 'olmaz', 'əla', 'pis', 'gözəl']

    turkish_words = ['sen', 'ben', 'nasıl', 'nerede', 'ne', 'var', 'yok', 'biz', 'siz', 'onlar',
                     'kanka', 'kardeş', 'abla', 'böyle', 'öyle', 'değil', 'çok', 'az', 'belki',
                     'istiyorum', 'ediyorum', 'gidiyorum', 'geliyorum', 'oldu', 'olacak', 'nerelisin',
                     'kaç', 'yaşında', 'adın', 'soyadın', 'nerdesin', 'napıyon', 'ne yapıyon',
                     'evet', 'hayır', 'tamam', 'oldu', 'olmaz', 'harika', 'kötü', 'güzel']

    text_lower = text.lower()
    azeri_count = sum(1 for word in azeri_words if word in text_lower)
    turkish_count = sum(1 for word in turkish_words if word in text_lower)

    if 'ə' in text_lower:
        azeri_count += 3

    return 'az' if azeri_count > turkish_count else 'tr'

# ==================== KİŞİSEL SORU KONTROLÜ (75+ TİP) ====================
def is_personal_question(text):
    text_lower = text.lower()
    patterns = [
        r'merhaba', r'selam', r'salam', r'hey', r'hi', r'hello',
        r'nasılsın', r'necəsən', r'ne haber', r'nə var', r'naber', r'nbr',
        r'nerel[ii]sin', r'haral[ıi]s[ıi]n', r'nerdesin', r'hardasan',
        r'ka[çc] yaş', r'ne[çc][ae] yaş', r'yasın', r'yaşın',
        r'evli misin', r'evl[əe]nmi', r'evlisenmi', r'evli sən',
        r'cinsiyet', r'cinsiyyet', r'erkek', r'kadın', r'kişi', r'qadın',
        r'kimsin', r'kimsən', r'sen kimsin',
        r'bot musun', r'botsan', r'botam', r'botsanmı',
        r'seviyor musun', r'sevirsenmi', r'beni seviyor musun', r'məni sevirsən',
        r'ne yersin', r'ne yeyirsen', r'nə yeyirsən',
        r'ne içersin', r'ne içirsen', r'nə içirsən',
        r'uyur musun', r'yatırsan', r'yatirsanmi',
        r'arkadaşın var mı', r'dostun var', r'dostun var mi',
        r'canın sıkıldı mı', r'canın sıxıldı', r'canin sixilibmi',
        r'güzel misin', r'gözəlsən', r'gözəlsənmi',
        r'akıllı mısın', r'ağıllısan', r'agillisanmi',
        r'teşekkürler', r'təşəkkürlər', r'sağ ol', r'sag ol',
        r'güle güle', r'gülə gülə', r'bay bay', r'görüşürüz',
        r'iyi misin', r'yaxşısan', r'yaxshisanmi',
        r'hava nasıl', r'hava necə', r'havalar nasıl',
        r'para verir misin', r'pul verərsən',
        r'evlenir misin', r'evlənərsən',
        r'çocuğun var mı', r'uşağın var', r'övladın var',
        r'rengin ne', r'rəngin nə',
        r'boyun kaç', r'boyun neçə',
        r'kilon ne', r'çəkin nə',
        r'hasta mısın', r'xəstəsən',
        r'randevu ister misin', r'randevu istəyirsən',
        r'özledin mi', r'həsrət qaldın'
    ]
    return any(re.search(pattern, text_lower) for pattern in patterns)

# ==================== ABİ CEVABI MI KONTROLÜ ====================
def get_abi_response(text, kategori):
    """Abi'ye özel samimi cevaplar döndürür"""
    text_lower = text.lower()
    
    if kategori in abi_cevaplari:
        return random.choice(abi_cevaplari[kategori])
    else:
        return random.choice(abi_cevaplari['default'])

# ==================== DİYALOG CEVAPLARINI GETİR ====================
def get_dialog_response(text, lang, is_abi=False):
    text_lower = text.lower()
    
    # Hangi kategoriye ait olduğunu bul
    if any(k in text_lower for k in ['merhaba', 'selam', 'salam', 'hey', 'hi', 'hello']):
        kategori = 'merhaba'
    elif any(k in text_lower for k in ['nasılsın', 'necəsən', 'ne haber', 'nə var', 'naber', 'nbr', 'iyi misin', 'yaxshisanmi']):
        kategori = 'nasilsin'
    elif any(k in text_lower for k in ['napıyon', 'ne yapıyorsun', 'nə edirsən', 'neynirsen']):
        kategori = 'napıyon'
    elif any(k in text_lower for k in ['nereli', 'nerelisen', 'haralı', 'harda', 'neredesin', 'hardasan']):
        kategori = 'nerelisin' if lang == 'tr' else 'nerelisen'
    elif any(k in text_lower for k in ['kaç yaş', 'neçə yaş', 'yasın', 'yaşın']):
        kategori = 'kac_yasindasin' if lang == 'tr' else 'nece_yasin_var'
    elif any(k in text_lower for k in ['evli misin', 'evlisenmi', 'evli sən']):
        kategori = 'evlimisin' if lang == 'tr' else 'evlisenmi'
    elif any(k in text_lower for k in ['cinsiyet', 'cinsiyyet', 'erkek', 'kadın', 'kişi', 'qadın']):
        kategori = 'cinsiyetin_ne' if lang == 'tr' else 'cinsiyyetin_ne'
    elif any(k in text_lower for k in ['kimsin', 'kimsən', 'sen kimsin']):
        kategori = 'kimsin' if lang == 'tr' else 'kimesen'
    elif any(k in text_lower for k in ['bot musun', 'botsan', 'botam', 'botsanmı']):
        kategori = 'botmusun' if lang == 'tr' else 'botsanmi'
    elif any(k in text_lower for k in ['seviyor musun', 'sevirsenmi', 'beni seviyor musun']):
        kategori = 'seviyor_musun' if lang == 'tr' else 'sevirsenmi'
    elif any(k in text_lower for k in ['ne yersin', 'ne yeyirsen']):
        kategori = 'ne_yersin' if lang == 'tr' else 'ne_yeyirsen'
    elif any(k in text_lower for k in ['ne içersin', 'ne içirsen']):
        kategori = 'ne_icersin' if lang == 'tr' else 'ne_icirsen'
    elif any(k in text_lower for k in ['uyur musun', 'yatırsan', 'yatirsanmi']):
        kategori = 'uyur_musun' if lang == 'tr' else 'yatirsanmi'
    elif any(k in text_lower for k in ['arkadaşın var mı', 'dostun var', 'dostun var mi']):
        kategori = 'arkadasin_var_mi' if lang == 'tr' else 'dostun_var_mi'
    elif any(k in text_lower for k in ['canın sıkıldı mı', 'canın sıxıldı', 'canin sixilibmi']):
        kategori = 'canin_sikildi_mi' if lang == 'tr' else 'canin_sixilibmi'
    elif any(k in text_lower for k in ['güzel misin', 'gözəlsən', 'gözəlsənmi']):
        kategori = 'guzel_misin' if lang == 'tr' else 'gözəlsənmi'
    elif any(k in text_lower for k in ['akıllı mısın', 'ağıllısan', 'agillisanmi']):
        kategori = 'akilli_misin' if lang == 'tr' else 'agillisanmi'
    elif any(k in text_lower for k in ['teşekkürler', 'təşəkkürlər', 'sağ ol', 'sag ol']):
        kategori = 'tesekkurler'
    elif any(k in text_lower for k in ['güle güle', 'gülə gülə', 'bay bay', 'görüşürüz']):
        kategori = 'gule_gule'
    elif any(k in text_lower for k in ['hava nasıl', 'hava necə', 'havalar nasıl']):
        kategori = 'hava_nasil' if lang == 'tr' else 'hava_nasil'
    elif any(k in text_lower for k in ['para verir misin', 'pul verərsən']):
        kategori = 'para_verir_misin' if lang == 'tr' else 'para_verir_misin'
    elif any(k in text_lower for k in ['evlenir misin', 'evlənərsən']):
        kategori = 'evlenir_misin' if lang == 'tr' else 'evlenir_misin'
    elif any(k in text_lower for k in ['çocuğun var mı', 'uşağın var', 'övladın var']):
        kategori = 'cocugun_var_mi' if lang == 'tr' else 'cocugun_var_mi'
    elif any(k in text_lower for k in ['rengin ne', 'rəngin nə']):
        kategori = 'rengin_ne' if lang == 'tr' else 'rengin_ne'
    elif any(k in text_lower for k in ['boyun kaç', 'boyun neçə']):
        kategori = 'boyun_kac' if lang == 'tr' else 'boyun_kac'
    elif any(k in text_lower for k in ['kilon ne', 'çəkin nə']):
        kategori = 'kilon_ne' if lang == 'tr' else 'kilon_ne'
    elif any(k in text_lower for k in ['hasta mısın', 'xəstəsən']):
        kategori = 'hasta_misin' if lang == 'tr' else 'hasta_misin'
    elif any(k in text_lower for k in ['randevu ister misin', 'randevu istəyirsən']):
        kategori = 'randevu_ister_misin' if lang == 'tr' else 'randevu_ister_misin'
    elif any(k in text_lower for k in ['özledin mi', 'həsrət qaldın']):
        kategori = 'ozledin_mi' if lang == 'tr' else 'ozledin_mi'
    else:
        kategori = 'kimsin' if lang == 'tr' else 'kimesen'
    
    # Eğer abi ise özel cevaplar döndür
    if is_abi:
        return get_abi_response(text, kategori)
    
    # Normal kullanıcı için cevap döndür
    if lang == 'tr':
        if kategori in diyalog_tr:
            return random.choice(diyalog_tr[kategori])
        else:
            return random.choice(diyalog_tr['kimsin'])
    else:
        if kategori in diyalog_az:
            return random.choice(diyalog_az[kategori])
        else:
            return random.choice(diyalog_az['kimesen'])

# ==================== SPAM KONTROLÜ ====================
async def spam_kontrolu(message):
    user_id = message.author.id
    simdi = time.time()
    icerik = message.content
    uyari_mesaji = None
    dil = detect_language(icerik)
    
    if simdi - son_mesaj_zamani[user_id] < 1.0:
        mesaj_sayaci[user_id].append(simdi)
        if len(mesaj_sayaci[user_id]) >= MESAJ_SAYISI_LIMITI:
            if simdi - mesaj_sayaci[user_id][0] < ZAMAN_ARALIGI:
                if dil == 'tr':
                    uyari_mesaji = "🍬 **Hey!** Çok hızlı mesaj atıyorsun, yavaş ol! 🍭"
                else:
                    uyari_mesaji = "🍬 **Hey!** Çox sürətli mesaj yazırsan, yavaş ol! 🍭"
    
    if len(icerik) > 5 and not uyari_mesaji:
        buyuk_harf_sayisi = sum(1 for c in icerik if c.isupper())
        if buyuk_harf_sayisi / len(icerik) > BUYUK_HARF_ORANI:
            if dil == 'tr':
                uyari_mesaji = "🔇 **Ayy bağırdın!** Sesim kısıldı! 🔇"
            else:
                uyari_mesaji = "🔇 **Ayy qışqırdın!** Səsim kısıldı! 🔇"
    
    if not uyari_mesaji:
        icerik_lower = icerik.lower()
        for kufur in KUFUR_LISTESI:
            if kufur in icerik_lower:
                if dil == 'tr':
                    uyari_mesaji = f"😳 **Ayıp!** {random.choice(['Üzüldüm', 'Kırıldım'])} 🥺"
                else:
                    uyari_mesaji = f"😳 **Ayıb!** {random.choice(['İncindim', 'Üzüldüm'])} 🥺"
                break
    
    if uyari_mesaji:
        await message.reply(uyari_mesaji)
        return True
    return False

# ==================== KOMUTLAR ====================

@bot.command(name='level', aliases=['seviye', 'səviyyə'])
async def level(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    lang = detect_language(ctx.message.content)
    if lang == 'tr':
        embed = discord.Embed(title=f"📊 {member.display_name} için Seviye Bilgisi", description="⚠️ **Şu anda seviye sistemi çalışmıyor.**", color=discord.Color.orange())
        embed.set_footer(text="SNOK bot | Geçici süreyle devre dışı")
    else:
        embed = discord.Embed(title=f"📊 {member.display_name} üçün Səviyyə Məlumatı", description="⚠️ **Hal-hazırda səviyyə sistemi işləmir.**", color=discord.Color.orange())
        embed.set_footer(text="SNOK bot | Müvəqqəti olaraq söndürülüb")
    await ctx.send(embed=embed)

@bot.command(name='fıkra', aliases=['fikra', 'letife'])
async def fikra(ctx):
    lang = detect_language(ctx.message.content)
    if lang == 'tr':
        await ctx.send(f"😂 **Temel Reis'ten bir fıkra:**\n{random.choice(turk_fıkraları)}")
    else:
        await ctx.send(f"😂 **Azərbaycandan bir lətifə:**\n{random.choice(azeri_letifeler)}")

@bot.command(name='şaka', aliases=['saka', 'joke'])
async def saka(ctx):
    lang = detect_language(ctx.message.content)
    if lang == 'tr':
        await ctx.send(f"😂 **{ctx.author.name}** sana komik bir şaka:\n{random.choice(turk_fıkraları)}")
    else:
        await ctx.send(f"😂 **{ctx.author.name}** sənə gülməli bir zarafat:\n{random.choice(azeri_letifeler)}")

@bot.command(name='yazitura', aliases=['yt', 'yazi', 'tura'])
async def yazi_tura(ctx):
    lang = detect_language(ctx.message.content)
    sonuc = random.choice(['Yazı! 🪙', 'Tura! 🦅', 'Para dik durdu! 🤹', 'Parayı kaybettim! 💸'])
    if lang == 'tr':
        await ctx.send(f"🪙 **{ctx.author.name}** için yazı tura: **{sonuc}**")
    else:
        await ctx.send(f"🪙 **{ctx.author.name}** üçün yazı tura: **{sonuc}**")

@bot.command(name='zar', aliases=['dice'])
async def zar_at(ctx, adet: int = 1):
    if adet > 5:
        adet = 5
        if detect_language(ctx.message.content) == 'tr':
            await ctx.send("En fazla 5 zar atabilirim! 🎲")
        else:
            await ctx.send("Ən çox 5 zar ata bilərəm! 🎲")
    lang = detect_language(ctx.message.content)
    zarlar = [random.choice(['⚀', '⚁', '⚂', '⚃', '⚄', '⚅']) for _ in range(adet)]
    if lang == 'tr':
        await ctx.send(f"🎲 **{ctx.author.name}** için {adet} zar: {' '.join(zarlar)}")
    else:
        await ctx.send(f"🎲 **{ctx.author.name}** üçün {adet} zar: {' '.join(zarlar)}")

@bot.command(name='bilgi', aliases=['info', 'gercek'])
async def bilgi_ver(ctx):
    lang = detect_language(ctx.message.content)
    bilgiler_tr = [
        "Python yılan değil, bir programlama dilidir! 🐍",
        "Discord'da ilk bot 2015'te yapıldı! 📅",
        "Bir insan günde ortalama 20 kez telefonuna bakar! 📱",
        "Mavi balinaların kalbi o kadar büyük ki içinde bir insan yüzebilir! 🐋",
        "Pandalar günde 12 saat yemek yer! 🐼",
        "Bir karınca kendi ağırlığının 50 katını taşıyabilir! 🐜",
        "Bukalemunlar dillerini vücutlarından 2 kat daha uzatabilir! 🦎",
        "Bir insan yaşamı boyunca 60 ton yiyecek tüketir! 🍔",
        "Ortalama bir bulut 500 ton ağırlığındadır! ☁️",
        "Bir yıldız balığının beyni yoktur! ⭐"
    ]
    bilgiler_az = [
        "Python ilan deyil, proqramlaşdırma dilidir! 🐍",
        "Discord'da ilk bot 2015'də yaradıldı! 📅",
        "Bir insan gündə ortalama 20 dəfə telefonuna baxır! 📱",
        "Mavi balinaların ürəyi o qədər böyükdür ki içində bir insan üzə bilər! 🐋",
        "Pandalar gündə 12 saat yemək yeyir! 🐼",
        "Bir qarışqa öz ağırlığının 50 qatını daşıya bilər! 🐜",
        "Bukalemunlar dillərini bədənlərindən 2 dəfə çox uzada bilər! 🦎",
        "Bir insan ömrü boyu 60 ton yemək tükədir! 🍔",
        "Orta hesabla bir bulud 500 ton ağırlığındadır! ☁️",
        "Bir dəniz ulduzunun beyni yoxdur! ⭐"
    ]
    if lang == 'tr':
        await ctx.send(f"ℹ️ **{ctx.author.name}** için bilgi:\n{random.choice(bilgiler_tr)}")
    else:
        await ctx.send(f"ℹ️ **{ctx.author.name}** üçün məlumat:\n{random.choice(bilgiler_az)}")

@bot.command(name='sarıl', aliases=['saril', 'hug'])
async def saril(ctx, member: discord.Member = None):
    lang = detect_language(ctx.message.content)
    if member is None:
        member = ctx.author
    if member.id == ctx.author.id:
        if lang == 'tr':
            await ctx.send(f"🤗 {ctx.author.name} kendine mi sarılacaksın? Bari ben sarılayım! 🤗")
        else:
            await ctx.send(f"🤗 {ctx.author.name} özünə mi sarılacaqsan? Heç olmasa mən sarılım! 🤗")
    else:
        if lang == 'tr':
            await ctx.send(f"🤗 {ctx.author.name}, {member.mention}'a sarıldı! 💕")
        else:
            await ctx.send(f"🤗 {ctx.author.name}, {member.mention}'a sarıldı! 💕")

@bot.command(name='help')
async def help_komutu(ctx):
    lang = detect_language(ctx.message.content)
    if lang == 'tr':
        embed = discord.Embed(title="🌸 **SNOK Bot** 🌸", description="🤔 **Help** yerine **!yardım** yazmalısın! 🎀", color=discord.Color.pink())
        embed.set_footer(text="SNOK v9.5 - 200+ Diyalog | Abi Özel")
    else:
        embed = discord.Embed(title="🌸 **SNOK Bot** 🌸", description="🤔 **Help** yerine **!kömək** yazmalısan! 🎀", color=discord.Color.pink())
        embed.set_footer(text="SNOK v9.5 - 200+ Dialoq | Abi Xüsusi")
    await ctx.send(embed=embed)

# ==================== YARDIM KOMUTU (TEK!) ====================
@bot.command(name='yardım', aliases=['kömək', 'yrd', 'yardim'])
async def yardim(ctx):
    lang = detect_language(ctx.message.content)
    is_abi = (ctx.author.id == ABI_ID)

    if lang == 'tr':
        embed = discord.Embed(
            title="🌸 **SNOK Bot - 200+ Diyalog** 🌸",
            description=(
                "✨ **Merhaba! Ben SNOK, 200'den fazla diyalogla seninleyim!** ✨\n\n"
                "🎪 **Eğlence Komutlarım:**\n"
                "• `!fıkra` - Temel Reis'ten fıkralar 😂\n"
                "• `!şaka` - Komik şakalar 😆\n"
                "• `!yazitura` - Yazı tura atar 🪙\n"
                "• `!zar [sayı]` - Zar atar (1-5 arası) 🎲\n"
                "• `!bilgi` - İlginç bilgiler ℹ️\n"
                "• `!sarıl [@kişi]` - Birine sarılır 🤗\n\n"
                "📋 **Diğer Komutlar:**\n"
                "• `!level` - Seviye bilgisi (çalışmıyor ⚠️)\n"
                "• `!yardım` - Bu menüyü gösterir 🎀\n\n"
                "💬 **Sohbet Özelliklerim (75+ Soru Tipi!):**\n"
                "• Bana `snok` yazarak seslenebilirsin\n"
                "• Adını söylersen seni tanırım! ('Benim adım Ali')\n"
                "• İsmini unutmam, veritabanıma kaydederim 📝\n"
                "• Hızlı mesaj atarsan uyarırım 🍬\n"
                "• Büyük harfle yazarsan uyarırım 🔇\n"
                "• Küfür edersen üzülürüm 🥺\n\n"
                "🌺 **Sorabileceğin Şeyler (200+ Farklı Cevap!):**\n"
                "• Merhaba • Nasılsın • Ne yapıyorsun • Nerelisin • Kaç yaşındasın\n"
                "• Evli misin • Cinsiyetin ne • Kimsin • Bot musun • Beni seviyor musun\n"
                "• Ne yersin • Ne içersin • Uyur musun • Arkadaşın var mı • Canın sıkıldı mı\n"
                "• Güzel misin • Akıllı mısın • Teşekkürler • Güle güle • İyi misin\n"
                "• Neredesin • Ne düşünüyorsun • Bana güler misin • Hava nasıl\n"
                "• Para verir misin • Evlenir misin • Çocuğun var mı • Rengin ne\n"
                "• Boyun kaç • Kilon ne • Hasta mısın • Randevu ister misin\n"
                "• Özledin mi • ve daha fazlası!\n\n"
                "💫 **2 Dil Biliyorum:** Türkçe & Azərbaycanca"
            ),
            color=discord.Color.pink()
        )
        if is_abi:
            embed.set_footer(text="SNOK v9.5 - 200+ Diyalog | Hoş geldin Abi! 👑", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        else:
            embed.set_footer(text="SNOK v9.5 - 200+ Diyalog", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    else:
        embed = discord.Embed(
            title="🌸 **SNOK Bot - 200+ Dialoq** 🌸",
            description=(
                "✨ **Salam! Mən SNOK, 200-dən çox dialoqla səninləyəm!** ✨\n\n"
                "🎪 **Əyləncə Komandalarım:**\n"
                "• `!fıkra` - Azərbaycan lətifələri 😂\n"
                "• `!şaka` - Gülməli zarafatlar 😆\n"
                "• `!yazitura` - Yazı tura atar 🪙\n"
                "• `!zar [sayı]` - Zar atar (1-5 arası) 🎲\n"
                "• `!bilgi` - Maraqlı məlumatlar ℹ️\n"
                "• `!sarıl [@kişi]` - Birinə sarılar 🤗\n\n"
                "📋 **Digər Komandalar:**\n"
                "• `!səviyyə` - Səviyyə məlumatı (işləmir ⚠️)\n"
                "• `!kömək` - Bu menünü göstərir 🎀\n\n"
                "💬 **Söhbət Xüsusiyyətlərim (75+ Sual Tipi!):**\n"
                "• Mənə `snok` yazaraq səslənə bilərsən\n"
                "• Adını söyləsən səni tanıyıram! ('Mənim adım Əli')\n"
                "• Adını unutmaram, yadda saxlayıram 📝\n"
                "• Sürətli mesaj yazsan xəbərdar edərəm 🍬\n"
                "• Böyük hərflə yazsan xəbərdar edərəm 🔇\n"
                "• Söyüş etsən üzülərəm 🥺\n\n"
                "🌺 **Soruşa Biləcəyin Şeylər (200+ Müxtəlif Cavab!):**\n"
                "• Salam • Necəsən • Nə edirsən • Hardasan • Neçə yaşın var\n"
                "• Evli sən • Cinsiyyətin nə • Kimsən • Botsan • Məni sevirsenmi\n"
                "• Nə yeyirsen • Nə içirsen • Yatırsanmı • Dostun var mı • Canın sıxılıbmı\n"
                "• Gözəlsənmi • Ağıllısanmı • Təşəkkürlər • Gülə gülə • Yaxşısанmı\n"
                "• Hardasan • Nə fikirleşirsen • Mənə gülərsənmi • Hava necə\n"
                "• Pul verərsən • Evlənərsən • Uşağın var • Rəngin nə\n"
                "• Boyun neçə • Çəkin nə • Xəstəsən • Randevu istəyirsən\n"
                "• Həsrət qaldın • və daha çoxu!\n\n"
                "💫 **2 Dil Bilirəm:** Türkçə & Azərbaycanca"
            ),
            color=discord.Color.pink()
        )
        if is_abi:
            embed.set_footer(text="SNOK v9.5 - 200+ Dialoq | Xoş gəldin Abi! 👑", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        else:
            embed.set_footer(text="SNOK v9.5 - 200+ Dialoq", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)

    embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
    await ctx.send(embed=embed)

# ==================== ON_MESSAGE ====================
@bot.event
async def on_message(message):
    if not hasattr(bot, 'processed_messages'):
        bot.processed_messages = set()
        bot.processed_messages_cleanup = time.time()
    
    if time.time() - bot.processed_messages_cleanup > 60:
        bot.processed_messages.clear()
        bot.processed_messages_cleanup = time.time()
    
    message_id = str(message.id)
    if message_id in bot.processed_messages:
        return
    bot.processed_messages.add(message_id)
    
    if message.author.bot:
        return

    son_mesaj_zamani[message.author.id] = time.time()
    
    spam_yapti = await spam_kontrolu(message)
    if spam_yapti:
        return

    lang = detect_language(message.content)
    kayitli_isim = kullanici_ismini_getir(message.author.id)
    is_abi = (message.author.id == ABI_ID)
    
    yeni_isim = isim_ogrenme_kontrolu(message.content)
    if yeni_isim:
        eski_isim = kayitli_isim
        kullanici_ismini_ogren(message.author.id, isim=yeni_isim)
        if eski_isim and eski_isim != yeni_isim:
            if is_abi:
                if lang == 'tr':
                    await message.reply(f"Ha abi, ismin değişti mi? Yeni ismini not ettim {yeni_isim}! 👑")
                else:
                    await message.reply(f"Ha abi, adın dəyişdi? Yeni adını qeyd etdim {yeni_isim}! 👑")
            else:
                if lang == 'tr':
                    await message.reply(f"Ha? İsmin değişti mi? Yeni ismini not ettim {yeni_isim}! 📝")
                else:
                    await message.reply(f"Ha? Adın dəyişdi? Yeni adını qeyd etdim {yeni_isim}! 📝")
        else:
            if is_abi:
                if lang == 'tr':
                    await message.reply(f"Tanıştığımıza memnun oldum abi {yeni_isim}! 👑")
                else:
                    await message.reply(f"Tanışdığımıza şad oldum abi {yeni_isim}! 👑")
            else:
                if lang == 'tr':
                    await message.reply(f"Tanıştığımıza memnun oldum {yeni_isim}! 🤝")
                else:
                    await message.reply(f"Tanışdığımıza şad oldum {yeni_isim}! 🤝")
        return

    if is_personal_question(message.content):
        selamlama_mi = any(k in message.content.lower() for k in ['merhaba', 'selam', 'salam', 'hey', 'hi', 'hello'])
        if selamlama_mi:
            simdi = time.time()
            if simdi - son_selam_zamani[message.author.id] < SELAM_COOLDOWN:
                await bot.process_commands(message)
                return
            son_selam_zamani[message.author.id] = simdi
        
        cevap = get_dialog_response(message.content, lang, is_abi)
        
        if kayitli_isim:
            if random.random() < 0.2:
                if is_abi:
                    if lang == 'tr':
                        await message.reply(f"{cevap}\n\nAbi nasılsın? 🤗")
                    else:
                        await message.reply(f"{cevap}\n\nAbi necəsən? 🤗")
                else:
                    if lang == 'tr':
                        await message.reply(f"{cevap}\n\nBu arada nasılsın {kayitli_isim}? 🤗")
                    else:
                        await message.reply(f"{cevap}\n\nBu arada necəsən {kayitli_isim}? 🤗")
            else:
                await message.reply(cevap)
        else:
            if random.random() < 0.3:
                if is_abi:
                    if lang == 'tr':
                        await message.reply(f"{cevap}\n\nAbi seni nasıl çağırayım? 🤔")
                    else:
                        await message.reply(f"{cevap}\n\nAbi səni necə çağırayım? 🤔")
                else:
                    if lang == 'tr':
                        await message.reply(f"{cevap}\n\nBu arada adın neydi? 🤔")
                    else:
                        await message.reply(f"{cevap}\n\nBu arada adın nə idi? 🤔")
            else:
                await message.reply(cevap)
        return

    bot_cagrildi = (bot.user.mentioned_in(message) or 'snok' in message.content.lower() or message.reference)
    if bot_cagrildi:
        emoji = random.choice(['😊', '🥰', '✨', '🌸', '🍬', '💖', '🌟', '⭐', '💫'])
        if kayitli_isim:
            if is_abi:
                if lang == 'tr':
                    await message.reply(f"Abi {kayitli_isim}? {emoji}")
                else:
                    await message.reply(f"Abi {kayitli_isim}? {emoji}")
            else:
                if lang == 'tr':
                    await message.reply(f"Evet {kayitli_isim}? {emoji}")
                else:
                    await message.reply(f"Hə {kayitli_isim}? {emoji}")
        else:
            if random.random() < 0.2:
                if is_abi:
                    if lang == 'tr':
                        await message.reply(f"Abi? Bu arada seni nasıl çağırayım? {emoji}")
                    else:
                        await message.reply(f"Abi? Bu arada səni necə çağırayım? {emoji}")
                else:
                    if lang == 'tr':
                        await message.reply(f"Evet? Bu arada adın neydi? {emoji}")
                    else:
                        await message.reply(f"Hə? Bu arada adın nə idi? {emoji}")
            else:
                if is_abi:
                    if lang == 'tr':
                        await message.reply(f"Abi? {emoji}")
                    else:
                        await message.reply(f"Abi? {emoji}")
                else:
                    if lang == 'tr':
                        await message.reply(f"Evet? {emoji}")
                    else:
                        await message.reply(f"Hə? {emoji}")
        return

    await bot.process_commands(message)

# ==================== BOTU BAŞLAT ====================
if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("HATA: DISCORD_TOKEN bulunamadı!")
    else:
        print("🌸 SNOK v9.5 - 200+ Diyalog + Abi Özel Modu Aktif! 🎪")
        print("🇹🇷 100+ Türkçe diyalog + 10 Temel Fıkrası")
        print("🇦🇿 100+ Azərbaycanca dialoq + 10 Lətifə")
        print("👑 Abi'ye özel samimi cevaplar eklendi!")
        print("🎯 75+ farklı soru tipi tanımlandı!")
        print("✅ Çift menü sorunu çözüldü!")
        bot.run(token)
