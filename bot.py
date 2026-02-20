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

# Diyalog dosyalarını içe aktar
from diyalog_tr_1 import DIYALOG_TR as DIYALOG_TR_1
from diyalog_tr_2 import DIYALOG_TR as DIYALOG_TR_2
from diyalog_tr_3 import DIYALOG_TR as DIYALOG_TR_3
from diyalog_tr_4 import DIYALOG_TR as DIYALOG_TR_4
from diyalog_az_1 import DIYALOG_AZ as DIYALOG_AZ_1
from diyalog_az_2 import DIYALOG_AZ as DIYALOG_AZ_2
from diyalog_az_3 import DIYALOG_AZ as DIYALOG_AZ_3
from diyalog_az_4 import DIYALOG_AZ as DIYALOG_AZ_4

# Fuzzy matcher ve konuşma hafızası
from fuzzy_matcher import SoruMatcher
from konusma_hafizasi import KonusmaHafizasi

# Tüm diyalogları birleştir
DIYALOG_TR = {}
DIYALOG_AZ = {}

for d in [DIYALOG_TR_1, DIYALOG_TR_2, DIYALOG_TR_3, DIYALOG_TR_4]:
    DIYALOG_TR.update(d)

for d in [DIYALOG_AZ_1, DIYALOG_AZ_2, DIYALOG_AZ_3, DIYALOG_AZ_4]:
    DIYALOG_AZ.update(d)

print(f"✅ {len(DIYALOG_TR)} Türkçe diyalog kategorisi yüklendi!")
print(f"✅ {len(DIYALOG_AZ)} Azərbaycanca dialoq kateqoriyası yükləndi!")

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
    return "Bot calisiyor! SNOK v12.0 - 2000+ Diyalog! 🎪"

def run_web():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=False)

threading.Thread(target=run_web, daemon=True).start()

load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# SABITLER
SUNUCU_ID = 1471063348689768523
ABI_ID = 423889250052734986  # Abi'nin ID'si - kontrol et!
SELAM_COOLDOWN = 60
MESAJ_SAYISI_LIMITI = 5
ZAMAN_ARALIGI = 3
BUYUK_HARF_ORANI = 0.7
KUFUR_LISTESI = ['amk', 'aq', 'sik', 'pic', 'orospu', 'ibne', 'göt', 'yarrak', 'pust', 'anani', 'babani', 'sikeyim', 'sikik', 'amcik', 'amq']

son_mesaj_zamani = defaultdict(float)
mesaj_sayaci = defaultdict(lambda: deque(maxlen=MESAJ_SAYISI_LIMITI))
son_selam_zamani = defaultdict(float)

kullanici_veritabani = veritabani_yukle()

# Yeni modülleri başlat
soru_matcher = SoruMatcher()
konusma_hafizasi = KonusmaHafizasi()

# Son cevapları hatırla (tekrarı önlemek için)
son_cevaplar = defaultdict(list)

# ==================== KONUŞMA AKIŞI İÇİN BAĞLAM CEVAPLARI ====================
baglam_cevaplari = {
    'nasilsin_devam': {
        'tr': [
            "Anlat bakalım, günün nasıl geçiyor?",
            "Devam et, seni dinliyorum.",
            "Sonra ne oldu?",
            "Peki ya sen, neler yapıyorsun?",
            "Anlat anlat, çok merak ettim!"
        ],
        'az': [
            "Danış görək, günün necə keçir?",
            "Davam et, səni dinləyirəm.",
            "Sonra nə oldu?",
            "Bəs sən, nə edirsən?",
            "Danış danış, çox maraqlandım!"
        ]
    },
    'napıyon_devam': {
        'tr': [
            "Sonra ne yaptın?",
            "Devam et, anlat bakalım.",
            "Peki ya sen?",
            "Anlat anlat, neler oluyor?",
            "Harika, başka neler yapıyorsun?"
        ],
        'az': [
            "Sonra nə etdin?",
            "Davam et, danış görək.",
            "Bəs sən?",
            "Danış danış, nələr olur?",
            "Əla, başqa nə edirsən?"
        ]
    },
    'nerelisin_devam': {
        'tr': [
            "Orayı çok merak ettim, anlat bakalım.",
            "Ne güzel bir yer! Peki orada yaşamak nasıl?",
            "Harika! Peki oraların yemekleri nasıl?",
            "Anlat anlat, neler var oralarda?"
        ],
        'az': [
            "Oranı çox maraq etdim, danış görək.",
            "Nə gözəl bir yer! Bəs orada yaşamaq necə?",
            "Əla! Bəs oraların yeməkləri necə?",
            "Danış danış, nələr var oralarda?"
        ]
    },
    'evlimisin_devam': {
        'tr': [
            "Anlat bakalım evlilik hikayeni merak ettim.",
            "Peki evlilik nasıl bir duygu?",
            "Ne güzel! Peki nasıl tanıştınız?",
            "Anlat anlat, çok tatlısınız!"
        ],
        'az': [
            "Danış görək evlilik hekayəni maraq etdim.",
            "Bəs evlilik necə bir hissdir?",
            "Nə gözəl! Bəs necə tanışdınız?",
            "Danış danış, çox şirinsiniz!"
        ]
    },
    'seviyor_musun_devam': {
        'tr': [
            "Peki sen beni seviyor musun?",
            "Ne güzel! Anlat bakalım sevgi nedir sence?",
            "Harika! Peki sevgi hakkında ne düşünüyorsun?"
        ],
        'az': [
            "Bəs sən məni sevirsən?",
            "Nə gözəl! Danış görək sevgi nədir səncə?",
            "Əla! Bəs sevgi haqqında nə düşünürsən?"
        ]
    }
}

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

# ==================== NORMAL SOHBET CEVAPLARI ====================
sohbet_cevaplari_tr = [
    "Anlıyorum, anlat bakalım? 👂",
    "Öyle mi? Devam et, dinliyorum! 👂",
    "İlginç... Peki sen ne düşünüyorsun? 💭",
    "Hmm, anlat bakalım daha fazla? 🤔",
    "Vay canına, gerçekten mi? 😲",
    "Bence de öyle! 👍",
    "Katılıyorum! 👏",
    "Haklısın dostum! 💪",
    "Ne diyorsun ya? İnanılır gibi değil! 😳",
    "Anlat anlat, çok merak ettim! 🥺",
    "Sonra ne oldu? 🤔",
    "Evet evet, devam et! 👂",
    "Çok doğru söylüyorsun! ✨",
    "Aynen öyle! 💯",
    "Kesinlikle! 🔥",
    "Hmm, anlıyorum. Peki sen ne düşünüyorsun? 🤗",
    "Çok ilginç! Devam et lütfen! 😊",
    "Seni dinliyorum, anlat bakalım! 👂",
    "Bu konuda haklı olabilirsin! 💭",
    "Harika bir nokta! 🌟"
]

sohbet_cevaplari_az = [
    "Başa düşürəm, davam et? 👂",
    "Elə? Danış, dinləyirəm! 👂",
    "Maraqlıdır... Bəs sən nə düşünürsən? 💭",
    "Hmm, daha danış görək? 🤔",
    "Vay canına, həqiqətən? 😲",
    "Məncə də belə! 👍",
    "Səninlə razıyam! 👏",
    "Haqlısan dostum! 💪",
    "Nə deyirsən? İnanılan kimi deyil! 😳",
    "Danış danış, çox maraqlandım! 🥺",
    "Sonra nə oldu? 🤔",
    "Bəli bəli, davam et! 👂",
    "Çox doğru deyirsən! ✨",
    "Aynən belə! 💯",
    "Mütləq! 🔥",
    "Hmm, başa düşürəm. Bəs sən nə düşünürsən? 🤗",
    "Çox maraqlıdır! Davam et zəhmət olmasa! 😊",
    "Səni dinləyirəm, danış görək! 👂",
    "Bu mövzuda haqlı ola bilərsən! 💭",
    "Gözəl bir fikirdir! 🌟"
]

# ==================== DİYALOG CEVABI GETİR ====================
def get_dialog_response(kategori, lang, is_abi=False, kullanici_adi=None, user_id=None, baglam=None):
    """Kategoriye göre rastgele cevap döndür (tekrarsız ve bağlamlı)"""
    
    # Önce bağlam kontrolü - eğer aynı kategoride devam ediyorsak özel cevaplar kullan
    if baglam and baglam.get('son_kategori') == kategori and baglam.get('konusma_sayisi', 0) > 1:
        # Aynı konuda 2. veya daha fazla mesaj
        devam_anahtari = f"{kategori}_devam"
        if devam_anahtari in baglam_cevaplari:
            if lang in baglam_cevaplari[devam_anahtari]:
                return random.choice(baglam_cevaplari[devam_anahtari][lang])
    
    # Abi'ye özel cevaplar
    if is_abi and kategori in abi_cevaplari:
        cevap_havuzu = abi_cevaplari[kategori]
    elif is_abi:
        cevap_havuzu = abi_cevaplari['default']
    elif lang == 'tr':
        if kategori in DIYALOG_TR:
            cevap_havuzu = DIYALOG_TR[kategori]
        else:
            return random.choice(sohbet_cevaplari_tr)
    else:
        if kategori in DIYALOG_AZ:
            cevap_havuzu = DIYALOG_AZ[kategori]
        else:
            return random.choice(sohbet_cevaplari_az)
    
    # Son 3 cevabı hatırla ve tekrarlama
    if user_id:
        anahtar = f"{user_id}_{kategori}"
        if anahtar not in son_cevaplar:
            son_cevaplar[anahtar] = []
        
        # Kullanılabilir cevaplar (son 3'te olmayanlar)
        kullanilabilir = [c for c in cevap_havuzu if c not in son_cevaplar[anahtar]]
        
        if kullanilabilir:
            secilen = random.choice(kullanilabilir)
        else:
            # Hepsi kullanıldıysa, en eskisini çıkar ve yenisini seç
            secilen = random.choice(cevap_havuzu)
            if son_cevaplar[anahtar]:
                son_cevaplar[anahtar].pop(0)
        
        # Son cevapları güncelle
        son_cevaplar[anahtar].append(secilen)
        if len(son_cevaplar[anahtar]) > 3:
            son_cevaplar[anahtar].pop(0)
        
        return secilen
    else:
        return random.choice(cevap_havuzu)

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

# ==================== DİL ALGILAMA ====================
def detect_language(text):
    azeri_words = ['sən', 'mən', 'necə', 'harda', 'nə', 'var', 'yox', 'biz', 'siz', 'onlar',
                   'qaqa', 'qardaş', 'bacı', 'belə', 'elə', 'deyil', 'çox', 'az', 'bəlkə',
                   'istəyirəm', 'edirəm', 'gedirəm', 'gəlirəm', 'oldu', 'olacaq', 'haralısan',
                   'neçə', 'yaşın', 'adın', 'soyadın', 'hardasan', 'nəynirsen', 'neynirsen']

    turkish_words = ['sen', 'ben', 'nasıl', 'nerede', 'ne', 'var', 'yok', 'biz', 'siz', 'onlar',
                     'kanka', 'kardeş', 'abla', 'böyle', 'öyle', 'değil', 'çok', 'az', 'belki',
                     'istiyorum', 'ediyorum', 'gidiyorum', 'geliyorum', 'oldu', 'olacak', 'nerelisin',
                     'kaç', 'yaşında', 'adın', 'soyadın', 'nerdesin', 'napıyon', 'ne yapıyon']

    text_lower = text.lower()
    azeri_count = sum(1 for word in azeri_words if word in text_lower)
    turkish_count = sum(1 for word in turkish_words if word in text_lower)

    if 'ə' in text_lower:
        azeri_count += 3

    return 'az' if azeri_count > turkish_count else 'tr'

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

# ==================== TÜRK FIKRALARI ====================
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

# ==================== AZERBAYCAN LETİFELERİ ====================
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
        "Pandalar günde 12 saat yemek yer! 🐼"
    ]
    bilgiler_az = [
        "Python ilan deyil, proqramlaşdırma dilidir! 🐍",
        "Discord'da ilk bot 2015'də yaradıldı! 📅",
        "Bir insan gündə ortalama 20 dəfə telefonuna baxır! 📱",
        "Mavi balinaların ürəyi o qədər böyükdür ki içində bir insan üzə bilər! 🐋",
        "Pandalar gündə 12 saat yemək yeyir! 🐼"
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
        embed.set_footer(text="SNOK v12.0 - 2000+ Diyalog")
    else:
        embed = discord.Embed(title="🌸 **SNOK Bot** 🌸", description="🤔 **Help** yerine **!kömək** yazmalısan! 🎀", color=discord.Color.pink())
        embed.set_footer(text="SNOK v12.0 - 2000+ Dialoq")
    await ctx.send(embed=embed)

# ==================== YARDIM KOMUTU ====================
@bot.command(name='yardım', aliases=['kömək', 'yrd', 'yardim'])
async def yardim(ctx):
    lang = detect_language(ctx.message.content)
    is_abi = (ctx.author.id == ABI_ID)

    if lang == 'tr':
        embed = discord.Embed(
            title="🌸 **SNOK Bot - 2000+ Diyalog** 🌸",
            description=(
                "✨ **Merhaba! Ben SNOK, 2000'den fazla diyalogla seninleyim!** ✨\n\n"
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
                "💬 **Sohbet Özelliklerim:**\n"
                "• **500+ soru tipi** (yazım hatalarına toleranslı!)\n"
                "• **2000+ farklı cevap**\n"
                "• **Konuşma hafızası** (bağlam hatırlar, akışa göre cevap verir)\n"
                "• **Duygu durumu** (mutlu, üzgün, şaşkın)\n"
                "• Adını söylersen seni tanırım!\n"
                "• Hızlı mesaj atarsan uyarırım 🍬\n"
                "• Büyük harfle yazarsan uyarırım 🔇\n"
                "• Küfür edersen üzülürüm 🥺\n\n"
                "🌺 **Sorabileceğin Şeyler (30+ kategori!):**\n"
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
            embed.set_footer(text="SNOK v12.0 - 2000+ Diyalog | Hoş geldin Abi! 👑")
        else:
            embed.set_footer(text="SNOK v12.0 - 2000+ Diyalog")
    else:
        embed = discord.Embed(
            title="🌸 **SNOK Bot - 2000+ Dialoq** 🌸",
            description=(
                "✨ **Salam! Mən SNOK, 2000-dən çox dialoqla səninləyəm!** ✨\n\n"
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
                "💬 **Söhbət Xüsusiyyətlərim:**\n"
                "• **500+ sual tipi** (yazı səhvlərinə dözümlü!)\n"
                "• **2000+ fərqli cavab**\n"
                "• **Söhbət yaddaşı** (kontekst xatırlayır, axışa görə cavab verir)\n"
                "• **Əhval durumu** (xoşbəxt, kədərli, təəccüblü)\n"
                "• Adını söyləsən səni tanıyıram!\n"
                "• Sürətli mesaj yazsan xəbərdar edərəm 🍬\n"
                "• Böyük hərflə yazsan xəbərdar edərəm 🔇\n"
                "• Söyüş etsən üzülərəm 🥺\n\n"
                "🌺 **Soruşa Biləcəyin Şeylər (30+ kateqoriya!):**\n"
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
            embed.set_footer(text="SNOK v12.0 - 2000+ Dialoq | Xoş gəldin Abi! 👑")
        else:
            embed.set_footer(text="SNOK v12.0 - 2000+ Dialoq")

    embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
    await ctx.send(embed=embed)

# ==================== ON_MESSAGE ====================
@bot.event
async def on_message(message):
    # ÇİFT MESAJ ENGELLEME - GÜÇLENDİRİLMİŞ VERSİYON
    if not hasattr(bot, 'processed_messages'):
        bot.processed_messages = set()
        bot.processed_messages_cleanup = time.time()
    
    # 1 dakikada bir cache temizliği
    if time.time() - bot.processed_messages_cleanup > 60:
        bot.processed_messages.clear()
        bot.processed_messages_cleanup = time.time()
    
    message_id = str(message.id)
    
    # Eğer bu mesaj daha önce işlendiyse KESİNLİKLE işleme
    if message_id in bot.processed_messages:
        return
    
    # Mesajı işaretle
    bot.processed_messages.add(message_id)
    
    # Bot kendi mesajlarını işleme
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

    # Soru tipini bul (yazım hatalarına toleranslı)
    kategori, skor = soru_matcher.soru_bul(message.content)
    
    if kategori:
        # Duygu durumunu güncelle
        duygu = konusma_hafizasi.duygu_guncelle(message.author.id, message.content)
        
        # Konuşma bağlamını al
        son_konusma = konusma_hafizasi.son_konu_ne(message.author.id)
        baglam = {
            'son_kategori': son_konusma.get('kategori') if son_konusma else None,
            'konusma_sayisi': konusma_hafizasi.kac_kez_sordu(message.author.id, kategori) if son_konusma else 0
        }
        
        # Cevap al (bağlamlı)
        cevap = get_dialog_response(kategori, lang, is_abi, kayitli_isim, message.author.id, baglam)
        
        # Konuşma hafızasına ekle
        konusma_hafizasi.ekle(message.author.id, message.content, cevap, kategori)
        
        # Takip sorusu ekle (eğer aynı konuda 2 kez konuşulduysa)
        if baglam['konusma_sayisi'] >= 2 and random.random() < 0.4:
            takip_sorulari = [
                "Peki sen ne düşünüyorsun?",
                "Senin fikrin nedir?",
                "Anlat bakalım, sen nasılsın?",
                "Devam et, dinliyorum.",
                "Sence?",
                "Ne dersin?",
                "Anlat anlat merak ettim!",
                "Sonra ne oldu?"
            ]
            cevap += f" {random.choice(takip_sorulari)}"
        
        await message.reply(cevap)
        return

    # Normal sohbet (sadece bot çağrıldığında veya sohbet devam ediyorsa)
    bot_cagrildi = (bot.user.mentioned_in(message) or 'snok' in message.content.lower() or message.reference)
    
    # Konuşma devam ediyor mu kontrol et
    konusma_devam = konusma_hafizasi.takip_sorusu_gerekli_mi(message.author.id, sure_siniri=300)  # 5 dakika
    
    if bot_cagrildi or konusma_devam:
        emoji = random.choice(['😊', '🥰', '✨', '🌸', '🍬', '💖', '🌟', '⭐', '💫'])
        
        # Son konuşulan kategoriye göre uygun cevap ver
        son_konusma = konusma_hafizasi.son_konu_ne(message.author.id)
        
        if son_konusma and konusma_devam:
            # Aynı konuda devam et
            kategori = son_konusma.get('kategori')
            if kategori and kategori in ['nasilsin', 'napıyon', 'merhaba']:
                # Sohbet devam ediyorsa uygun cevap ver
                if kategori == 'nasilsin':
                    cevaplar = ["İyilik senden?", "Anlat bakalım?", "Devam et dinliyorum."]
                    await message.reply(f"{random.choice(cevaplar)} {emoji}")
                    return
                elif kategori == 'napıyon':
                    cevaplar = ["Anlat bakalım neler yapıyorsun?", "Devam et merak ettim.", "Sonra ne oldu?"]
                    await message.reply(f"{random.choice(cevaplar)} {emoji}")
                    return
        
        # Normal cevap
        if kayitli_isim:
            if is_abi:
                await message.reply(f"Abi {kayitli_isim}? {emoji}")
            else:
                await message.reply(f"Evet {kayitli_isim}? {emoji}")
        else:
            if random.random() < 0.2:
                if is_abi:
                    await message.reply(f"Abi? Adın neydi bu arada? {emoji}")
                else:
                    if lang == 'tr':
                        await message.reply(f"Evet? Adın neydi bu arada? {emoji}")
                    else:
                        await message.reply(f"Hə? Adın nə idi bu arada? {emoji}")
            else:
                if is_abi:
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
        print("❌ HATA: DISCORD_TOKEN bulunamadı! .env dosyasını kontrol et.")
    else:
        print("🌸 SNOK v12.0 - 2000+ Diyalog + Konuşma Akışı Aktif! 🎪")
        print(f"✅ {len(DIYALOG_TR)} Türkçe diyalog kategorisi")
        print(f"✅ {len(DIYALOG_AZ)} Azərbaycanca dialoq kateqoriyası")
        print(f"✅ {soru_matcher.toplam_varyasyon}+ soru varyasyonu")
        print("👑 Abi'ye özel samimi cevaplar eklendi!")
        print("✅ Konuşma hafızası güçlendirildi!")
        print("✅ Bağlama göre cevap seçimi aktif!")
        print("✅ Tekrarlayan cevaplar engellendi!")
        print("✅ Çift mesaj sorunu çözüldü!")
        print("✅ Render'da hostlamaya hazır! 🚀")
        bot.run(token)
