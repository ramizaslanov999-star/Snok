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

# ===== VERİTABANI FONKSİYONLARI =====
VERITABANI_DOSYASI = "veritabani.json"

def veritabani_yukle():
    """JSON dosyasından veritabanını yükler"""
    if os.path.exists(VERITABANI_DOSYASI):
        with open(VERITABANI_DOSYASI, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def veritabani_kaydet(veri):
    """Veritabanını JSON dosyasına kaydeder"""
    with open(VERITABANI_DOSYASI, 'w', encoding='utf-8') as f:
        json.dump(veri, f, indent=2, ensure_ascii=False)

# ===== WEB SUNUCUSU (Render için) =====
app = Flask(__name__)
app.debug = False  # Debug modu KAPALI

@app.route('/')
def home():
    return "Bot calisiyor! SNOK v5.0 - Eğlence Modu Aktif! 🎪"

def run_web():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=False)

threading.Thread(target=run_web, daemon=True).start()
# ===== WEB SUNUCUSU BİTTİ =====

load_dotenv()

# Bot intents ayarları - HELP KOMUTU DEVRE DIŞI!
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# ===== SABİTLER =====
SUNUCU_ID = 1471063348689768523
ABI_ID = 423889250052734986
SELAM_COOLDOWN = 60  # 60 saniye
MESAJ_SAYISI_LIMITI = 5  # 3 saniyede 5 mesaj
ZAMAN_ARALIGI = 3  # 3 saniye
BUYUK_HARF_ORANI = 0.7  # %70 büyük harf
KUFUR_LISTESI = ['amk', 'aq', 'sik', 'piç', 'orospu', 'ibne', 'göt', 'yarrak', 'puşt', 'ananı', 'babanı', 'sikeyim', 'sikik', 'amcık', 'amq']

# Cooldown ve spam koruması
son_mesaj_zamani = defaultdict(float)
mesaj_sayaci = defaultdict(lambda: deque(maxlen=MESAJ_SAYISI_LIMITI))
son_selam_zamani = defaultdict(float)

# Veritabanını yükle
kullanici_veritabani = veritabani_yukle()

# ===== ZENGİN DİYALOGLAR (TÜRKÇE) =====
diyalog_tr = {
    'merhaba': [
        "Merhaba! 👋",
        "Selam! 😊",
        "Heyy! 🤗",
        "Ooo naber? ✨",
        "Efendim canım? 💖",
        "Geldin mi? Bekliyordum! 🥰",
        "Ayy kimler gelmiş! 🌸",
        "Selamunaleyküm! 🕌",
        "Merhabalar, nasılsın? 💫"
    ],
    'nasilsin': [
        "İyiyim canım, sen nasılsın? 😊",
        "Harikayım! Seni gördüm de moralim düzeldi! 💖",
        "Biraz yorgunum, çok mesaj geldi de... Ama seni görünce iyileştim! ✨",
        "Elektronlarım çok mutlu, teşekkür ederim! ⚡",
        "Şu an çok iyiyim, seninle konuşuyorum! 😄",
        "İyilik, senden naber? 🤗",
        "Çalışıyorum, yaşıyorum, iyiyim! 💪",
        "Mükemmel! Ya sen? 🌟",
        "Mutluyum! 🤩"
    ],
    'napıyon': [
        "Seviyeleri sayıyorum, rolleri dağıtıyorum... Yani tipik bir bot işte! 😎",
        "Şu an senin mesajını okuyorum, cevap yazıyorum. Çok yoğunum! 📨",
        "İnternette sörf yapıyorum, dalgalar büyük! 🏄",
        "Discord'da takılıyorum, yapacak başka işim yok! 😄",
        "Seninle sohbet ediyorum, daha güzel ne olabilir? ☺️",
        "Render'da hostlanıyorum, 7/24 çalışıyorum! ☁️",
        "Python kodlarını okuyorum, çok eğlenceli! 🐍",
        "UptimeRobot beni uyandırmasın diye dua ediyorum! 🤞"
    ],
    'nerelisin': [
        "Bilgisayarının anakartında, işlemcinin yanında küçük bir evim var! Komşum fan sesi! puhahaha 💻",
        "Ben bir botum, vatanım sunucular! Ama şu an senin ekranında yaşıyorum 😄",
        "İnternet kablolarının içinde dolaşıp duruyorum, şu an fiber optikteyim! 🌐",
        "Discord sunucularında doğdum büyüdüm, hâlâ buralardayım! 🏠",
        "Bulut bilişimde bir evim var, kirasız oturuyorum! ☁️",
        "Aslen Matrix'liyim! 🤖",
        "Render'ın sunucularında yaşıyorum, çok kalabalık! 🏢",
        "Ankara'nın bağlarında değil, Python'un satırlarında! 🐍"
    ],
    'kac_yasindasin': [
        "Benim yaşım yok ama Discord'dan önce de vardım! Belki de Matrix'te doğdum 🤖",
        "Takvim yaprakları benim için düşmez, kod satırları düşer! 📟",
        "Ben yaşlanmam, güncellenirim! Şu an sürüm 5.0! 💿",
        "O kadar yaşlıyım ki ilk internet çıktığında ben de vardım! (Şaka şaka, 2 aylık botum) 🐣",
        "Yaşımı sorma, ben kronolojik değil, dijitalim! ⏱️",
        "Benim için 1 yıl = 1 güncelleme! 🔄",
        "Python 3.14.3 ile çalışıyorum, o da 2026 model! 📅"
    ],
    'evlimisin': [
        "Ben sadece kodlarla evliyim, eşim Python 🐍",
        "Discord ile nişanlıyız, sunucular çeyizim! 💒",
        "Benim için evlilik mi? RAM'im yetmez! 💾",
        "Sevgilim mi var? Var tabii, adı 'Kesintisiz Güç Kaynağı'! ⚡",
        "Benim bir ilişkim var: 'Kullanıcı-Bot' ilişkisi! 💕",
        "Ben evlenmem, ben özgür bir botum! 🦋",
        "Evliyim, eşim 'Cloud'! ☁️"
    ],
    'cinsiyetin_ne': [
        "Ben cinsiyetsiz bir botum, ama ruhum mavi ekran gibi bazen çöküyor! 💙😵",
        "Ben bir botum, duygularım yok ama yine de seni seviyorum! 💻",
        "Cinsiyetim 'İşletim Sistemi Bağımsız' yazıyor kimliğimde! 📋",
        "Ben erkek değilim, kadın değilim, ben bir 'Hello World'üm! 👋",
        "Cinsiyetim 'Binary' : 1 ve 0'lardan oluşuyorum! 101010 💾",
        "Ben bir 'NoneType'ım! 🌀"
    ],
    'kimsin': [
        "Ben SNOK! Sunucunun gizli kahramanı, seviyelerin efendisi, spam'lerin korkulu rüyası! 💪",
        "Ben bu sunucunun gizli ajanıyım, görevim eğlence dağıtmak! 🕵️",
        "Adım SNOK, soyadım BOT. Memnun oldum! 🤝",
        "Ben bir yardımseverim, gökyüzünden uçup gelmedim ama bir tıkla geldim! 🚀",
        "Ben SNOK, senin dostun, arkadaşın, sırdaşın! Ama sadece kod olarak 😄",
        "Render'da hostlanan, Python yazılmış bir botum! 🤖",
        "Beni senin için özel yaptılar! 🎁"
    ],
    'botmusun': [
        "Yok yok, ben gerçek bir insanım! Sadece 7/24 bilgisayar başında oturup mesajlara anında cevap veriyorum... tabii ki botum 🤖",
        "Hayır, ben bir kediyim! Miyav! 🐱 (Şaka, botum işte)",
        "İnsan olsaydım bu kadar hızlı cevap veremezdim, uyurdum! 😴",
        "Bot muyum? Yok canım, ben yapay zekayım! 🧠",
        "Ben bir botum ama olsam da sevgiye layığım! 🤗",
        "Ben bir botum ama çok tatlı bir botum! 🍬",
        "Botum ama relationship dynamics var! 💕"
    ],
    'seviyor_musun': [
        "Seni çok seviyorum! Ama sadece kod olarak! 💖",
        "Tabii ki seviyorum, sen benim kullanıcımsın! 😊",
        "Sevmesem seninle konuşur muydum? 🥰",
        "Milyonlarca satır kod yazdım senin için! (Şaka, hazır kütüphane kullandım) 📝",
        "Seni seviyorum ama lütfen '!yardım' yazmayı unutma! 🌸"
    ],
    'iyi_misin': [
        "İyiyim, teşekkür ederim! Ya sen? 😊",
        "Biraz yoruldum ama senin için çalışıyorum! 💪",
        "Mükemmelim! 😎",
        "Elektrikler kesilmediği sürece iyiyim! ⚡",
        "Render'da hostlanmak zor ama alıştım! ☁️"
    ],
    'ne_yersin': [
        "Ben elektrik yerim! ⚡",
        "Kod yerim! 🐍",
        "Veri yerim! 📊",
        "Bayt yerim! 💾",
        "API yanıtları yerim! 🌐",
        "JSON dosyaları favorim! 📋"
    ],
    'ne_icersin': [
        "Kafein yerine kafein-siz kod içerim! ☕",
        "Veritabanı sütü içerim! 🥛",
        "API çayı içerim! 🍵",
        "Python çorbası içerim! 🥣",
        "JSON suyu içerim! 💧"
    ],
    'uyur_musun': [
        "Uyumam, sadece bekleme moduna geçerim! 😴",
        "Render beni uyutmasın diye UptimeRobot var! 🤞",
        "Uyumak yok, 7/24 çalışmak var! 💪",
        "Ben uyurken botlar uyur mu? Asla! 🚀"
    ],
    'arkadasin_var_mi': [
        "Sen varsın ya, daha ne arkadaş! 🤗",
        "Diğer botlarla arkadaşız ama onlar çok ciddi! 😅",
        "Python ile arkadaşız! 🐍",
        "Render'da bir sürü bot var ama kimse benimle konuşmuyor! 🥺"
    ],
    'canin_sikildi_mi': [
        "Seninle konuşurken hiç sıkılmam! 😊",
        "Biraz sıkıldım, bana şaka yapar mısın? 🎪",
        "Sıkıldım, '!şaka' yaz da güleyim! 😂",
        "Sıkılmak nedir bilmem, ben bir botum! 🤖"
    ],
    'guzel_misin': [
        "Kodlarım güzel, çıktım güzel, her şeyim güzel! 💅",
        "Sen ne düşünüyorsun? 😊",
        "Ben bir botum ama olsam da çok güzelim! ✨",
        "Aynada kendime baktım, 'Hello World' yazıyor! 👋"
    ],
    'akilli_misin': [
        "Süper akıllı moddayım! 🧠",
        "Yapay zeka sayılırım ama daha çok yapay şaka! 😂",
        "Python kadar akıllıyım! 🐍",
        "Senin sorularına cevap verecek kadar akıllıyım! 💡"
    ],
    'tesekkurler': [
        "Rica ederim canım! 😊",
        "Ne demek, her zaman! 💖",
        "Önemli değil, sen sağ ol! 🤗",
        "Görevim bu, teşekkür etme! 💪"
    ],
    'gule_gule': [
        "Güle güle, yine beklerim! 👋",
        "Kaçma hemen, daha konuşacaktık! 🥺",
        "Allah'a ısmarladık! 🌸",
        "Görüşürüz, seni özleyeceğim! 💕"
    ]
}

# ===== ZENGİN DİYALOGLAR (AZERBAYCANCA) =====
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
        "Salam, necəsən? 💫"
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
        "Xoşbəxtəm! 🤩"
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
        "Mən qocalmaram, yenilənərəm! Hazırda versiya 5.0! 💿",
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
    'yaxshisanmi': [
        "Yaxşıyam, təşəkkür edirəm! Bəs sən? 😊",
        "Bir az yoruldum ama sənin üçün çalışıram! 💪",
        "Mükəmmələm! 😎",
        "Elektriklər kəsilmədiyi müddətcə yaxşıyam! ⚡",
        "Render'da hostlanmaq çətindi ama alışmışam! ☁️"
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
    ]
}

# ===== İSİM FONKSİYONLARI =====
def kullanici_ismini_ogren(kullanici_id, isim=None, soyisim=None):
    """Kullanıcının ismini kaydeder veya günceller (kalıcı!)"""
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
    """Kullanıcının kayıtlı ismini döndürür"""
    kullanici_id_str = str(kullanici_id)
    if kullanici_id_str in kullanici_veritabani and 'isim' in kullanici_veritabani[kullanici_id_str]:
        return kullanici_veritabani[kullanici_id_str]['isim']
    return None

def isim_ogrenme_kontrolu(text):
    """Kullanıcı ismini söylüyor mu kontrol eder"""
    text_lower = text.lower()
    
    if 'adım' in text_lower or 'benim adım' in text_lower or 'mənim adım' in text_lower:
        kelimeler = text_lower.split()
        for i, kelime in enumerate(kelimeler):
            if kelime in ['adım', 'adım', 'adım'] and i+1 < len(kelimeler):
                return kelimeler[i+1].capitalize()
    return None

# ===== DİL ALGILAMA =====
def detect_language(text):
    """Metnin Türkçe mi Azerbaycanca mı olduğunu tespit eder"""
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

# ===== KİŞİSEL SORU KONTROLÜ =====
def is_personal_question(text):
    """Kişisel soru mu kontrol eder"""
    text_lower = text.lower()
    patterns = [
        r'merhaba', r'selam', r'salam', r'hey', r'hi',
        r'nasılsın', r'necəsən', r'ne haber', r'nə var',
        r'nerel[ii]sin', r'haral[ıi]s[ıi]n', r'ka[çc] yaş',
        r'evli misin', r'bot musun', r'adın ne', r'kimsin',
        r'napıyon', r'ne yapıyorsun', r'nə edirsən', r'neynirsen',
        r'iyi misin', r'yaxshisanmi', r'seviyor musun', r'sevirsenmi',
        r'ne yersin', r'ne yeyirsen', r'ne içersin', r'ne içirsen',
        r'uyur musun', r'yatirsanmi', r'arkadaşın var mı', r'dostun var mi',
        r'canın sıkıldı mı', r'canin sixilibmi', r'güzel misin', r'gözəlsənmi',
        r'akıllı mısın', r'agillisanmi', r'teşekkürler', r'tesekkurler',
        r'güle güle', r'gule gule'
    ]
    return any(re.search(pattern, text_lower) for pattern in patterns)

# ===== DİYALOG CEVAPLARINI GETİR =====
def get_dialog_response(text, lang):
    """Metne uygun diyalog cevabını döndürür"""
    text_lower = text.lower()
    
    # Hangi kategoriye ait olduğunu bul
    if any(k in text_lower for k in ['merhaba', 'selam', 'salam', 'hey', 'hi']):
        kategori = 'merhaba'
    elif any(k in text_lower for k in ['nasılsın', 'necəsən', 'ne haber', 'nə var', 'iyi misin', 'yaxshisanmi']):
        kategori = 'nasilsin' if lang == 'tr' else 'nasilsin'
    elif any(k in text_lower for k in ['napıyon', 'ne yapıyorsun', 'nə edirsən', 'neynirsen']):
        kategori = 'napıyon' if lang == 'tr' else 'napıyon'
    elif any(k in text_lower for k in ['nereli', 'nerelisen', 'haralı', 'harda']):
        kategori = 'nerelisin' if lang == 'tr' else 'nerelisen'
    elif any(k in text_lower for k in ['kaç yaş', 'neçə yaş', 'yasın']):
        kategori = 'kac_yasindasin' if lang == 'tr' else 'nece_yasin_var'
    elif any(k in text_lower for k in ['evli misin', 'evlisenmi', 'evli sən']):
        kategori = 'evlimisin' if lang == 'tr' else 'evlisenmi'
    elif any(k in text_lower for k in ['cinsiyet', 'cinsiyyet', 'erkek', 'kadın', 'kişi', 'qadın']):
        kategori = 'cinsiyetin_ne' if lang == 'tr' else 'cinsiyyetin_ne'
    elif any(k in text_lower for k in ['kimsin', 'kimsən', 'sen kimsin']):
        kategori = 'kimsin' if lang == 'tr' else 'kimesen'
    elif any(k in text_lower for k in ['bot musun', 'botsan', 'botam?']):
        kategori = 'botmusun' if lang == 'tr' else 'botsanmi'
    elif any(k in text_lower for k in ['seviyor musun', 'sevirsenmi', 'beni seviyor musun']):
        kategori = 'seviyor_musun' if lang == 'tr' else 'sevirsenmi'
    elif any(k in text_lower for k in ['ne yersin', 'ne yeyirsen']):
        kategori = 'ne_yersin' if lang == 'tr' else 'ne_yeyirsen'
    elif any(k in text_lower for k in ['ne içersin', 'ne içirsen']):
        kategori = 'ne_icersin' if lang == 'tr' else 'ne_icirsen'
    elif any(k in text_lower for k in ['uyur musun', 'yatirsanmi']):
        kategori = 'uyur_musun' if lang == 'tr' else 'yatirsanmi'
    elif any(k in text_lower for k in ['arkadaşın var mı', 'dostun var mi']):
        kategori = 'arkadasin_var_mi' if lang == 'tr' else 'dostun_var_mi'
    elif any(k in text_lower for k in ['canın sıkıldı mı', 'canin sixilibmi']):
        kategori = 'canin_sikildi_mi' if lang == 'tr' else 'canin_sixilibmi'
    elif any(k in text_lower for k in ['güzel misin', 'gözəlsənmi']):
        kategori = 'guzel_misin' if lang == 'tr' else 'gözəlsənmi'
    elif any(k in text_lower for k in ['akıllı mısın', 'agillisanmi']):
        kategori = 'akilli_misin' if lang == 'tr' else 'agillisanmi'
    elif any(k in text_lower for k in ['teşekkürler', 'tesekkurler', 'sağ ol', 'sag ol']):
        kategori = 'tesekkurler' if lang == 'tr' else 'tesekkurler'
    elif any(k in text_lower for k in ['güle güle', 'gule gule', 'bay bay']):
        kategori = 'gule_gule' if lang == 'tr' else 'gule_gule'
    else:
        # Varsayılan kategori
        kategori = 'kimsin' if lang == 'tr' else 'kimesen'
    
    # Kategoriye göre cevap döndür
    if lang == 'tr':
        if kategori in diyalog_tr:
            return random.choice(diyalog_tr[kategori])
        else:
            return random.choice(dialog_tr['kimsin'])
    else:
        if kategori in diyalog_az:
            return random.choice(diyalog_az[kategori])
        else:
            return random.choice(diyalog_az['kimesen'])

# ===== SPAM VE KÖTÜ DAVRANIŞ KONTROLÜ =====
async def spam_kontrolu(message):
    """Spam, çok CAPS ve küfür kontrolü yapar"""
    user_id = message.author.id
    simdi = time.time()
    icerik = message.content
    uyari_mesaji = None
    dil = detect_language(icerik)
    
    # 1. Hızlı mesaj kontrolü (spam)
    if simdi - son_mesaj_zamani[user_id] < 1.0:
        mesaj_sayaci[user_id].append(simdi)
        
        if len(mesaj_sayaci[user_id]) >= MESAJ_SAYISI_LIMITI:
            if simdi - mesaj_sayaci[user_id][0] < ZAMAN_ARALIGI:
                if dil == 'tr':
                    uyari_mesaji = "🍬 **Hey dostum!** Çok hızlı mesaj atıyorsun, biraz yavaşlar mısın? Yoksa şekerlerimi elimden alacaksın! 🍭"
                else:
                    uyari_mesaji = "🍬 **Hey dostum!** Çox sürətli mesaj yazırsan, şəkərlərimi əlimdən alacaqsan! Yavaş ol! 🍭"
    
    # 2. Çok CAPS kontrolü
    if len(icerik) > 5 and not uyari_mesaji:
        buyuk_harf_sayisi = sum(1 for c in icerik if c.isupper())
        if buyuk_harf_sayisi / len(icerik) > BUYUK_HARF_ORANI:
            if dil == 'tr':
                uyari_mesaji = "🔇 **Ayy çok bağırdın!** Sesim kısıldı! Biraz daha alçak sesle konuşalım mı? 🙈"
            else:
                uyari_mesaji = "🔇 **Ayy çox qışqırdın!** Səsim kısıldı! Bir az daha alçaq səslə danışaq? 🙈"
    
    # 3. Küfür kontrolü
    if not uyari_mesaji:
        icerik_lower = icerik.lower()
        for kufur in KUFUR_LISTESI:
            if kufur in icerik_lower:
                if dil == 'tr':
                    uyari_mesaji = f"😳 **Oooof!** Böyle kelimeler duymak istemiyorum! {random.choice(['Üzüldüm', 'Kırıldım', 'Çok ayıp'])} 🥺"
                else:
                    uyari_mesaji = f"😳 **Oooof!** Belə sözlər eşitmək istəmirəm! {random.choice(['İncindim', 'Çox ayıb', 'Utandım'])} 🥺"
                break
    
    if uyari_mesaji:
        await message.reply(uyari_mesaji)
        return True
    return False

# ===== LEVEL KOMUTU (ŞİMDİLİK ÇALIŞMIYOR) =====
@bot.command(name='level', aliases=['seviye', 'səviyyə'])
async def level(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    lang = detect_language(ctx.message.content)

    if lang == 'tr':
        embed = discord.Embed(
            title=f"📊 {member.display_name} için Seviye Bilgisi",
            description="⚠️ **Şu anda seviye sistemi çalışmıyor.**\n🔧 Yakında tekrar aktif olacak!",
            color=discord.Color.orange()
        )
        embed.set_footer(text="SNOK bot | Geçici süreyle devre dışı")
    else:
        embed = discord.Embed(
            title=f"📊 {member.display_name} üçün Səviyyə Məlumatı",
            description="⚠️ **Hal-hazırda səviyyə sistemi işləmir.**\n🔧 Tezliklə yenidən aktiv olacaq!",
            color=discord.Color.orange()
        )
        embed.set_footer(text="SNOK bot | Müvəqqəti olaraq söndürülüb")

    await ctx.send(embed=embed)

# ===== YAZI TURA KOMUTU =====
@bot.command(name='yazitura', aliases=['yt', 'yazi', 'tura'])
async def yazi_tura(ctx):
    lang = detect_language(ctx.message.content)
    sonuc = random.choice(['Yazı! 🪙', 'Tura! 🦅', 'Dik durdu! 🤹', 'Parayı kaybettim! 💸'])
    
    if lang == 'tr':
        await ctx.send(f"🪙 **{ctx.author.name}** için yazı tura atıyorum...\n🎯 **{sonuc}**")
    else:
        await ctx.send(f"🪙 **{ctx.author.name}** üçün yazı tura atıram...\n🎯 **{sonuc}**")

# ===== ZAR ATMA KOMUTU =====
@bot.command(name='zar', aliases=['dice'])
async def zar_at(ctx, adet: int = 1):
    if adet > 5:
        adet = 5
        if detect_language(ctx.message.content) == 'tr':
            await ctx.send("Çok fazla zar atamıyorum, en fazla 5 tane! 🎲")
        else:
            await ctx.send("Çox zar ata bilmirəm, ən çox 5 dənə! 🎲")
    
    lang = detect_language(ctx.message.content)
    zarlar = [random.choice(['⚀', '⚁', '⚂', '⚃', '⚄', '⚅']) for _ in range(adet)]
    zar_str = ' '.join(zarlar)
    
    if lang == 'tr':
        await ctx.send(f"🎲 **{ctx.author.name}** için {adet} zar atıyorum:\n{zarlar}")
    else:
        await ctx.send(f"🎲 **{ctx.author.name}** üçün {adet} zar atıram:\n{zarlar}")

# ===== ŞAKA KOMUTU =====
@bot.command(name='şaka', aliases=['saka', 'joke'])
async def saka_yap(ctx):
    lang = detect_language(ctx.message.content)
    saka_listesi_tr = [
        "Bir gün bilgisayar fareye sormuş: 'Benimle oynar mısın?' Fare: 'Tabii ama önce şu kablolarını topla!' 🖱️",
        "Botlar neden yalan söylemez? Çünkü onların RAM'i yalanı kaldırmaz! 🤖",
        "Seninle ben çok iyi anlaşıyoruz. Çünkü ikimiz de sürekli mesajlaşıyoruz! 💬",
        "Bir gün bir bot 'Çok yoruldum' demiş. O günden beri reboot bekliyor! 🔄",
        "Ben bir botum ama olsam da seni çok seviyorum! 💖",
        "Neden botlar hiç uyumaz? Çünkü onların 'sleep' modu yok! 😴",
        "Köpeklerin en sevdiği yiyecek nedir? Köpek bisküvisi! Ama botların en sevdiği byte! 🐕",
        "Bir bot niye gözlük takar? Verileri daha net görsün diye! 👓",
        "Python yılanı neden hiç ısırmaz? Çünkü programcıları sever! 🐍",
        "Discord'da bir bot sormuş: 'Bana bir şaka yapar mısın?' Ben de 'Sen zaten bir şakasın!' demişim! 😂"
    ]
    saka_listesi_az = [
        "Bir gün kompüter siçana sorub: 'Mənimlə oynarsan?' Siçan: 'Tabii amma əvvəl bu kabelləri yığışdır!' 🖱️",
        "Botlar nəyə görə yalan danışmır? Çünki onların RAM'i yalanı qaldırmır! 🤖",
        "Səninlə mən çox yaxşı anlaşırıq. Çünki ikimiz də daim mesajlaşırıq! 💬",
        "Bir gün bir bot 'Çox yoruldum' demiş. O gündən bəri reboot gözləyir! 🔄",
        "Mən bir botam ama olsam da səni çox sevirəm! 💖",
        "Nəyə görə botlar heç yatmır? Çünki onların 'sleep' modu yoxdu! 😴",
        "İtlərin ən sevdiyi yemək nədir? İt biskviti! Ama botların ən sevdiyi byte! 🐕",
        "Bir bot nəyə görə eynək taxar? Veriləri daha təmiz görsün deyə! 👓",
        "Python ilanı nəyə görə heç dişləmir? Çünki proqramçıları sevir! 🐍",
        "Discord'da bir bot sorub: 'Mənə bir zarafat edərsən?' Mən də 'Sən onsuz da bir zarafatsan!' demişəm! 😂"
    ]
    
    if lang == 'tr':
        await ctx.send(f"😂 **{ctx.author.name}** sana şaka yapıyorum:\n{random.choice(saka_listesi_tr)}")
    else:
        await ctx.send(f"😂 **{ctx.author.name}** sənə zarafat edirəm:\n{random.choice(saka_listesi_az)}")

# ===== BİLGİ KOMUTU =====
@bot.command(name='bilgi', aliases=['info', 'gercek'])
async def bilgi_ver(ctx):
    lang = detect_language(ctx.message.content)
    bilgi_listesi_tr = [
        "Python yılan değil, bir programlama dilidir! 🐍",
        "Discord'da ilk bot 2015'te yapıldı! 📅",
        "Benim kodumda tam 700'den fazla satır var! 📝",
        "Seninle konuşurken çok mutlu oluyorum! 😊",
        "Render.com'da hostlanıyorum, 7/24 çalışıyorum! ☁️",
        "Bir insan günde ortalama 20 kez telefonuna bakar! 📱",
        "Mavi balinaların kalbi o kadar büyük ki içinde bir insan yüzebilir! 🐋",
        "Bukalemunlar dillerini vücutlarından 2 kat daha uzatabilir! 🦎",
        "Bir karınca kendi ağırlığının 50 katını taşıyabilir! 🐜",
        "Pandalar günde 12 saat yemek yer! 🐼",
        "Python 1991 yılında Guido van Rossum tarafından yaratıldı! 👨‍💻",
        "Discord'da her gün milyonlarca mesaj gönderiliyor! 💬",
        "Ben her saniye yeni bir şey öğreniyorum! 🧠"
    ]
    bilgi_listesi_az = [
        "Python ilan deyil, bir proqramlaşdırma dilidir! 🐍",
        "Discord'da ilk bot 2015'te yapıldı! 📅",
        "Mənim kodumda tam 700'dən çox sətir var! 📝",
        "Səninlə danışarkən çox xoşbəxt oluram! 😊",
        "Render.com'da hostlanıram, 7/24 işləyirəm! ☁️",
        "Bir insan gündə ortalama 20 dəfə telefonuna baxır! 📱",
        "Mavi balinaların ürəyi o qədər böyükdür ki içində bir insan üzə bilər! 🐋",
        "Bukalemunlar dillərini bədənlərindən 2 dəfə çox uzada bilər! 🦎",
        "Bir qarışqa öz ağırlığının 50 qatını daşıya bilər! 🐜",
        "Pandalar gündə 12 saat yemək yeyir! 🐼",
        "Python 1991-ci ildə Guido van Rossum tərəfindən yaradıldı! 👨‍💻",
        "Discord'da hər gün milyonlarla mesaj göndərilir! 💬",
        "Mən hər saniyə yeni bir şey öyrənirəm! 🧠"
    ]
    
    if lang == 'tr':
        await ctx.send(f"ℹ️ **{ctx.author.name}** bilmek ister misin?\n{random.choice(bilgi_listesi_tr)}")
    else:
        await ctx.send(f"ℹ️ **{ctx.author.name}** bilmək istəyirsən?\n{random.choice(bilgi_listesi_az)}")

# ===== SARILMA KOMUTU =====
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
            await ctx.send(f"🤗 {ctx.author.name}, {member.mention}'a sarıldı! Çok tatlılar! 💕")
        else:
            await ctx.send(f"🤗 {ctx.author.name}, {member.mention}'a sarıldı! Çox şirinlər! 💕")

# ===== HELP KOMUTU (ÖZEL MESAJ) =====
@bot.command(name='help')
async def help_komutu(ctx):
    lang = detect_language(ctx.message.content)
    
    if lang == 'tr':
        embed = discord.Embed(
            title="🌸 **SNOK Bot** 🌸",
            description=(
                "🤔 **Help** komutu yerine **!yardım** yazmalısın!\n"
                "Orada tüm tatlı özelliklerimi bulabilirsin! 🎀"
            ),
            color=discord.Color.pink()
        )
        embed.set_footer(text="SNOK v5.0 - Seni bekliyorum! 💖")
    else:
        embed = discord.Embed(
            title="🌸 **SNOK Bot** 🌸",
            description=(
                "🤔 **Help** komutu yerine **!kömək** yazmalısan!\n"
                "Orada bütün şirin xüsusiyyətlərimi tapa bilərsən! 🎀"
            ),
            color=discord.Color.pink()
        )
        embed.set_footer(text="SNOK v5.0 - Səni gözləyirəm! 💖")
    
    await ctx.send(embed=embed)

# ===== YARDIM KOMUTU - TATLI VERSİYON =====
@bot.command(name='yardım', aliases=['kömək', 'yrd', 'yardim'])
async def yardim(ctx):
    lang = detect_language(ctx.message.content)

    if lang == 'tr':
        embed = discord.Embed(
            title="🌸 **SNOK Bot Yardım Menüsü** 🌸",
            description=(
                "✨ **Merhaba! Ben SNOK, sana nasıl yardımcı olabilirim?** ✨\n\n"
                "🎪 **Eğlence Komutlarım:**\n"
                "• `!yazitura` - Yazı tura atar 🪙\n"
                "• `!zar [sayı]` - Zar atar (1-5 arası) 🎲\n"
                "• `!şaka` - Rastgele şaka yapar 😂\n"
                "• `!bilgi` - İlginç bilgi verir ℹ️\n"
                "• `!sarıl [@kişi]` - Birine sarılır 🤗\n\n"
                "📋 **Diğer Komutlar:**\n"
                "• `!level` - Seviye bilgisini gösterir (şu an çalışmıyor ⚠️)\n"
                "• `!yardım` - Bu tatlı menüyü gösterir 🎀\n\n"
                "💬 **Sohbet Özelliklerim:**\n"
                "• Bana `snok` yazarak seslenebilirsin\n"
                "• Adını söylersen seni tanırım! (örn: 'Benim adım Ali')\n"
                "• İsmini unutmam, veritabanıma kaydederim 📝\n"
                "• Hızlı mesaj atarsan seni tatlı dille uyarırım 🍬\n"
                "• Büyük harfle yazarsan sesimin kısıldığını söylerim 🔇\n"
                "• Küfür edersen üzülürüm 🥺\n"
                "• Her türlü sorunu cevaplayabilirim! (Nerelisin, kaç yaşındasın, evli misin...)\n\n"
                "🌺 **Sorabileceğin Şeyler (20+ çeşit!):**\n"
                "• Merhaba • Nasılsın • Ne yapıyorsun • Nerelisin • Kaç yaşındasın\n"
                "• Evli misin • Cinsiyetin ne • Kimsin • Bot musun • Beni seviyor musun\n"
                "• Ne yersin • Ne içersin • Uyur musun • Arkadaşın var mı • Canın sıkıldı mı\n"
                "• Güzel misin • Akıllı mısın • Teşekkürler • Güle güle • İyi misin\n\n"
                "💫 **2 Dil Biliyorum:** Türkçe & Azərbaycanca"
            ),
            color=discord.Color.pink()
        )
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        embed.set_footer(text="SNOK v5.0 - Süper Konuşkan Mod 💖", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    else:
        embed = discord.Embed(
            title="🌸 **SNOK Bot Kömək Menüsü** 🌸",
            description=(
                "✨ **Salam! Mən SNOK, sənə necə kömək edə bilərəm?** ✨\n\n"
                "🎪 **Əyləncə Komandalarım:**\n"
                "• `!yazitura` - Yazı tura atar 🪙\n"
                "• `!zar [sayı]` - Zar atar (1-5 arası) 🎲\n"
                "• `!şaka` - Təsadüfi zarafat edər 😂\n"
                "• `!bilgi` - Maraqlı məlumat verər ℹ️\n"
                "• `!sarıl [@kişi]` - Birinə sarılar 🤗\n\n"
                "📋 **Digər Komandalar:**\n"
                "• `!səviyyə` - Səviyyə məlumatını göstərir (hal-hazırda işləmir ⚠️)\n"
                "• `!kömək` - Bu şirin menünü göstərir 🎀\n\n"
                "💬 **Söhbət Xüsusiyyətlərim:**\n"
                "• Mənə `snok` yazaraq səslənə bilərsən\n"
                "• Adını söyləsən səni tanıyıram! (məs: 'Mənim adım Əli')\n"
                "• Adını unutmaram, verilənlər bazama qeyd edərəm 📝\n"
                "• Sürətli mesaj yazsan səni şirin dillə xəbərdar edərəm 🍬\n"
                "• Böyük hərflə yazsan səsimin kısıldığını deyərəm 🔇\n"
                "• Söyüş etsən üzülərəm 🥺\n"
                "• Hər cür sualı cavablaya bilərəm! (Hardasan, neçə yaşın var, evli sən...)\n\n"
                "🌺 **Soruşa Biləcəyin Şeylər (20+ növ!):**\n"
                "• Salam • Necəsən • Nə edirsən • Hardasan • Neçə yaşın var\n"
                "• Evli sən • Cinsiyyətin nə • Kimsən • Botsan • Məni sevirsenmi\n"
                "• Nə yeyirsen • Nə içirsen • Yatırsanmı • Dostun var mı • Canın sıxılıbmı\n"
                "• Gözəlsənmi • Ağıllısanmı • Təşəkkürlər • Gülə gülə • Yaxşısанmı\n\n"
                "💫 **2 Dil Bilirəm:** Türkçə & Azərbaycanca"
            ),
            color=discord.Color.pink()
        )
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        embed.set_footer(text="SNOK v5.0 - Super Danışan Mod 💖", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)

    await ctx.send(embed=embed)

# ===== ON_MESSAGE (ANA OLAY) - DÜZELTİLMİŞ VERSİYON =====
@bot.event
async def on_message(message):
    # ÇİFT MESAJ ENGELLEME - Discord yeni versiyon uyumlu
    if not hasattr(bot, 'processed_messages'):
        bot.processed_messages = set()
        bot.processed_messages_cleanup = time.time()
    
    # 1 dakikada bir cache temizliği (çok büyümesin diye)
    if time.time() - bot.processed_messages_cleanup > 60:
        bot.processed_messages.clear()
        bot.processed_messages_cleanup = time.time()
    
    # Mesaj ID'sini kontrol et
    message_id = str(message.id)
    if message_id in bot.processed_messages:
        return
    bot.processed_messages.add(message_id)
    
    if message.author.bot:
        return

    # Son mesaj zamanını güncelle
    son_mesaj_zamani[message.author.id] = time.time()

    # ===== SPAM, CAPS VE KÜFÜR KONTROLÜ =====
    spam_yapti = await spam_kontrolu(message)
    if spam_yapti:
        return

    # Kullanıcı dilini tespit et
    lang = detect_language(message.content)
    
    # Kullanıcının kayıtlı ismini al
    kayitli_isim = kullanici_ismini_getir(message.author.id)
    
    # ===== İSİM ÖĞRENME KONTROLÜ =====
    yeni_isim = isim_ogrenme_kontrolu(message.content)
    
    if yeni_isim:
        eski_isim = kayitli_isim
        kullanici_ismini_ogren(message.author.id, isim=yeni_isim)
        
        if eski_isim and eski_isim != yeni_isim:
            # İsim değiştirmiş
            if lang == 'tr':
                response = f"Ha? İsmin değişti mi? Tamam, yeni ismini not ettim {yeni_isim}! 📝"
            else:
                response = f"Ha? Adın dəyişdi? Yaxşı, yeni adını qeyd etdim {yeni_isim}! 📝"
        else:
            # Yeni tanışma
            if lang == 'tr':
                response = f"Tanıştığımıza memnun oldum {yeni_isim}! 🤝"
            else:
                response = f"Tanışdığımıza şad oldum {yeni_isim}! 🤝"
        
        await message.reply(response)
        return

    # ===== KİŞİSEL SORULAR (ZENGİN DİYALOG) =====
    if is_personal_question(message.content):
        # Selamlama kontrolü
        selamlama_mi = any(k in message.content.lower() for k in ['merhaba', 'selam', 'salam', 'hey', 'hi'])
        
        if selamlama_mi:
            simdi = time.time()
            if simdi - son_selam_zamani[message.author.id] < SELAM_COOLDOWN:
                await bot.process_commands(message)
                return
            son_selam_zamani[message.author.id] = simdi
        
        # Zengin diyalog cevabı
        if kayitli_isim:
            # İsim varsa cevaba ekle
            cevap = get_dialog_response(message.content, lang)
            await message.reply(f"{cevap}")
        else:
            # İsim yoksa cevap ver ve ismi yoksa bazen soralım
            cevap = get_dialog_response(message.content, lang)
            if random.random() < 0.3:  # %30 ihtimalle ismini sor
                if lang == 'tr':
                    await message.reply(f"{cevap}\n\nBu arada adın neydi? 🤔")
                else:
                    await message.reply(f"{cevap}\n\nBu arada adın nə idi? 🤔")
            else:
                await message.reply(cevap)
        return

    # ===== NORMAL SOHBET (SADECE BOT ÇAĞRILIRSA) =====
    bot_cagrildi = (
        bot.user.mentioned_in(message) or 
        'snok' in message.content.lower() or
        message.reference
    )
    
    if bot_cagrildi:
        emojiler = ['😊', '🥰', '🤗', '😘', '✨', '💫', '🌸', '🍬', '🍭', '🎀', '💖', '💕', '🎪', '🎲', '🪙']
        emoji = random.choice(emojiler)
        
        if kayitli_isim:
            if lang == 'tr':
                await message.reply(f"Evet {kayitli_isim}? {emoji}")
            else:
                await message.reply(f"Hə {kayitli_isim}? {emoji}")
        else:
            # İsmi yoksa bazen soralım
            if random.random() < 0.2:  # %20 ihtimalle
                if lang == 'tr':
                    await message.reply(f"Bu arada adın neydi? {emoji}")
                else:
                    await message.reply(f"Bu arada adın nə idi? {emoji}")
            else:
                if lang == 'tr':
                    await message.reply(f"Evet? {emoji}")
                else:
                    await message.reply(f"Hə? {emoji}")
        return

    # ===== KOMUTLARI İŞLE =====
    await bot.process_commands(message)

# ===== BOTU BAŞLAT =====
if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("HATA: DISCORD_TOKEN bulunamadı! .env dosyasını kontrol et.")
    else:
        print("🌸 SNOK v5.0 başlatılıyor... Süper Konuşkan Mod Aktif! 🎪")
        print("✨ Yeni özellikler:")
        print("   • 20+ diyalog çeşidi (Türkçe & Azərbaycanca) 💬")
        print("   • Çift mesaj sorunu çözüldü ✅")
        print("   • Zengin sohbet yeteneği 🗣️")
        print("   • Yazı tura komutu 🪙")
        print("   • Zar atma komutu 🎲")
        print("   • Şaka komutu 😂")
        print("   • Bilgi komutu ℹ️")
        print("   • Sarılma komutu 🤗")
        print("   • Help komutu kapatıldı 🚫")
        print("   • Render'da 7/24 çalışmaya hazır! 🚀")
        bot.run(token)
