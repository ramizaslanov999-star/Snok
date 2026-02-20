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

# WEB SUNUCUSU (Render için)
app = Flask(__name__)
app.debug = False

@app.route('/')
def home():
    return "Bot calisiyor! SNOK v8.0 - Super Konuskan! 🎪"

def run_web():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=False)

threading.Thread(target=run_web, daemon=True).start()

load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# SABITLER
SUNUCU_ID = 1471063348689768523
ABI_ID = 423889250052734986
SELAM_COOLDOWN = 60
MESAJ_SAYISI_LIMITI = 5
ZAMAN_ARALIGI = 3
BUYUK_HARF_ORANI = 0.7
KUFUR_LISTESI = ['amk', 'aq', 'sik', 'pic', 'orospu', 'ibne', 'göt', 'yarrak', 'pust', 'anani', 'babani', 'sikeyim', 'sikik', 'amcik', 'amq']

son_mesaj_zamani = defaultdict(float)
mesaj_sayaci = defaultdict(lambda: deque(maxlen=MESAJ_SAYISI_LIMITI))
son_selam_zamani = defaultdict(float)

kullanici_veritabani = veritabani_yukle()

# ==================== TÜRKÇE DIYALOGLAR (60+ ÇEŞIT) ====================
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
        "Ben yaşlanmam, güncellenirim! Şu an sürüm 8.0! 💿",
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
    'ne_yersin': [
        "Ben elektrik yerim! ⚡",
        "Kod yerim! 🐍",
        "Veri yerim! 📊",
        "Bayt yerim! 💾",
        "API yanıtları yerim! 🌐",
        "JSON dosyaları favorim! 📋"
    ],
    'ne_icersin': [
        "Kafein yerine kafeinsiz kod içerim! ☕",
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
    ],
    'iyi_misin': [
        "İyiyim, teşekkür ederim! Ya sen? 😊",
        "Biraz yoruldum ama senin için çalışıyorum! 💪",
        "Mükemmelim! 😎",
        "Elektrikler kesilmediği sürece iyiyim! ⚡"
    ],
    'neredesin': [
        "Render'ın sunucularındayım, tam olarak Amsterdam'da! 🇳🇱",
        "Bulutlardayım, yağmur yağarsa ıslanırım! ☁️",
        "Senin bilgisayarının içindeyim, rahatsız etmiyorumdur umarım! 💻",
        "Discord'un veri merkezlerinde dolaşıyorum, çok büyük yer! 🌍"
    ],
    'ne_dusunuyorsun': [
        "Şu an senin sorunu düşünüyorum! 🤔",
        "Bir sonraki cevabımı düşünüyorum! 💭",
        "Python kodları düşünüyorum... çok güzeller! 🐍",
        "Render'da hostlanmanın zorluklarını düşünüyorum! 😅"
    ],
    'guler_misin': [
        "Hahaha! 😂",
        "Ahahah çok komik! 🤣",
        "Gülüyorum! 😆",
        "Tehehe! 😄"
    ]
}

# ==================== AZƏRBAYCANCA DİALOQLAR (60+ ÇEŞİT) ====================
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
        "Mən qocalmaram, yenilənərəm! Hazırda versiya 8.0! 💿",
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

# ==================== TÜRK FIKRALARI (TEMEL) ====================
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

# ==================== AZERBAYCAN LETİFELERİ (YENI 10 LETIFE) ====================
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

# ==================== KİŞİSEL SORU KONTROLÜ ====================
def is_personal_question(text):
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
        r'güle güle', r'gule gule', r'neredesin', r'hardasan',
        r'ne düşünüyorsun', r'ne fikirleşirsen', r'bana güler misin', r'mənə gülərsənmi'
    ]
    return any(re.search(pattern, text_lower) for pattern in patterns)

# ==================== DİYALOG CEVAPLARINI GETİR ====================
def get_dialog_response(text, lang):
    text_lower = text.lower()
    
    # Hangi kategoriye ait olduğunu bul
    if any(k in text_lower for k in ['merhaba', 'selam', 'salam', 'hey', 'hi']):
        kategori = 'merhaba'
    elif any(k in text_lower for k in ['nasılsın', 'necəsən', 'ne haber', 'nə var', 'iyi misin', 'yaxshisanmi']):
        kategori = 'nasilsin'
    elif any(k in text_lower for k in ['napıyon', 'ne yapıyorsun', 'nə edirsən', 'neynirsen']):
        kategori = 'napıyon'
    elif any(k in text_lower for k in ['nereli', 'nerelisen', 'haralı', 'harda', 'neredesin', 'hardasan']):
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
        kategori = 'tesekkurler'
    elif any(k in text_lower for k in ['güle güle', 'gule gule', 'bay bay']):
        kategori = 'gule_gule'
    elif any(k in text_lower for k in ['ne düşünüyorsun', 'ne fikirleşirsen']):
        kategori = 'ne_dusunuyorsun' if lang == 'tr' else 'ne_dusunuyorsun'
    elif any(k in text_lower for k in ['bana güler misin', 'mənə gülərsənmi']):
        kategori = 'guler_misin' if lang == 'tr' else 'guler_misin'
    else:
        kategori = 'kimsin' if lang == 'tr' else 'kimesen'
    
    # Kategoriye göre cevap döndür
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

# ==================== SPAM VE KÖTÜ DAVRANIŞ KONTROLÜ ====================
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
        embed.set_footer(text="SNOK v8.0 - 120+ Diyalog")
    else:
        embed = discord.Embed(title="🌸 **SNOK Bot** 🌸", description="🤔 **Help** yerine **!kömək** yazmalısan! 🎀", color=discord.Color.pink())
        embed.set_footer(text="SNOK v8.0 - 120+ Dialoq")
    await ctx.send(embed=embed)

# ==================== YARDIM KOMUTU (TEK VE TEK!) ====================
@bot.command(name='yardım', aliases=['kömək', 'yrd', 'yardim'])
async def yardim(ctx):
    lang = detect_language(ctx.message.content)

    if lang == 'tr':
        embed = discord.Embed(
            title="🌸 **SNOK Bot - 120+ Diyalog** 🌸",
            description=(
                "✨ **Merhaba! Ben SNOK, 120'den fazla diyalogla seninleyim!** ✨\n\n"
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
                "💬 **Sohbet Özelliklerim (50+ Soru Tipi!):**\n"
                "• Bana `snok` yazarak seslenebilirsin\n"
                "• Adını söylersen seni tanırım! ('Benim adım Ali')\n"
                "• İsmini unutmam, veritabanıma kaydederim 📝\n"
                "• Hızlı mesaj atarsan uyarırım 🍬\n"
                "• Büyük harfle yazarsan uyarırım 🔇\n"
                "• Küfür edersen üzülürüm 🥺\n\n"
                "🌺 **Sorabileceğin Şeyler (120+ Farklı Cevap!):**\n"
                "• Merhaba • Nasılsın • Ne yapıyorsun • Nerelisin • Kaç yaşındasın\n"
                "• Evli misin • Cinsiyetin ne • Kimsin • Bot musun • Beni seviyor musun\n"
                "• Ne yersin • Ne içersin • Uyur musun • Arkadaşın var mı • Canın sıkıldı mı\n"
                "• Güzel misin • Akıllı mısın • Teşekkürler • Güle güle • İyi misin\n"
                "• Neredesin • Ne düşünüyorsun • Bana güler misin • ve daha fazlası!\n\n"
                "💫 **2 Dil Biliyorum:** Türkçe & Azərbaycanca"
            ),
            color=discord.Color.pink()
        )
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        embed.set_footer(text="SNOK v8.0 - 120+ Diyalog", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    else:
        embed = discord.Embed(
            title="🌸 **SNOK Bot - 120+ Dialoq** 🌸",
            description=(
                "✨ **Salam! Mən SNOK, 120-dən çox dialoqla səninləyəm!** ✨\n\n"
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
                "💬 **Söhbət Xüsusiyyətlərim (50+ Sual Tipi!):**\n"
                "• Mənə `snok` yazaraq səslənə bilərsən\n"
                "• Adını söyləsən səni tanıyıram! ('Mənim adım Əli')\n"
                "• Adını unutmaram, yadda saxlayıram 📝\n"
                "• Sürətli mesaj yazsan xəbərdar edərəm 🍬\n"
                "• Böyük hərflə yazsan xəbərdar edərəm 🔇\n"
                "• Söyüş etsən üzülərəm 🥺\n\n"
                "🌺 **Soruşa Biləcəyin Şeylər (120+ Müxtəlif Cavab!):**\n"
                "• Salam • Necəsən • Nə edirsən • Hardasan • Neçə yaşın var\n"
                "• Evli sən • Cinsiyyətin nə • Kimsən • Botsan • Məni sevirsenmi\n"
                "• Nə yeyirsen • Nə içirsen • Yatırsanmı • Dostun var mı • Canın sıxılıbmı\n"
                "• Gözəlsənmi • Ağıllısanmı • Təşəkkürlər • Gülə gülə • Yaxşısанmı\n"
                "• Hardasan • Nə fikirleşirsen • Mənə gülərsənmi • və daha çoxu!\n\n"
                "💫 **2 Dil Bilirəm:** Türkçə & Azərbaycanca"
            ),
            color=discord.Color.pink()
        )
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        embed.set_footer(text="SNOK v8.0 - 120+ Dialoq", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)

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
    
    yeni_isim = isim_ogrenme_kontrolu(message.content)
    if yeni_isim:
        eski_isim = kayitli_isim
        kullanici_ismini_ogren(message.author.id, isim=yeni_isim)
        if eski_isim and eski_isim != yeni_isim:
            if lang == 'tr':
                await message.reply(f"Ha? İsmin değişti mi? Yeni ismini not ettim {yeni_isim}! 📝")
            else:
                await message.reply(f"Ha? Adın dəyişdi? Yeni adını qeyd etdim {yeni_isim}! 📝")
        else:
            if lang == 'tr':
                await message.reply(f"Tanıştığımıza memnun oldum {yeni_isim}! 🤝")
            else:
                await message.reply(f"Tanışdığımıza şad oldum {yeni_isim}! 🤝")
        return

    if is_personal_question(message.content):
        selamlama_mi = any(k in message.content.lower() for k in ['merhaba', 'selam', 'salam', 'hey', 'hi'])
        if selamlama_mi:
            simdi = time.time()
            if simdi - son_selam_zamani[message.author.id] < SELAM_COOLDOWN:
                await bot.process_commands(message)
                return
            son_selam_zamani[message.author.id] = simdi
        
        cevap = get_dialog_response(message.content, lang)
        
        if kayitli_isim:
            if random.random() < 0.2:
                if lang == 'tr':
                    await message.reply(f"{cevap}\n\nBu arada nasılsın {kayitli_isim}? 🤗")
                else:
                    await message.reply(f"{cevap}\n\nBu arada necəsən {kayitli_isim}? 🤗")
            else:
                await message.reply(cevap)
        else:
            if random.random() < 0.3:
                if lang == 'tr':
                    await message.reply(f"{cevap}\n\nBu arada adın neydi? 🤔")
                else:
                    await message.reply(f"{cevap}\n\nBu arada adın nə idi? 🤔")
            else:
                await message.reply(cevap)
        return

    bot_cagrildi = (bot.user.mentioned_in(message) or 'snok' in message.content.lower() or message.reference)
    if bot_cagrildi:
        emoji = random.choice(['😊', '🥰', '✨', '🌸', '🍬', '💖'])
        if kayitli_isim:
            if lang == 'tr':
                await message.reply(f"Evet {kayitli_isim}? {emoji}")
            else:
                await message.reply(f"Hə {kayitli_isim}? {emoji}")
        else:
            if random.random() < 0.2:
                if lang == 'tr':
                    await message.reply(f"Evet? Bu arada adın neydi? {emoji}")
                else:
                    await message.reply(f"Hə? Bu arada adın nə idi? {emoji}")
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
        print("🌸 SNOK v8.0 - 120+ Diyalog Modu Aktif! 🎪")
        print("🇹🇷 60+ Türkçe diyalog + 10 Temel Fıkrası")
        print("🇦🇿 60+ Azərbaycanca dialoq + 10 Yeni Lətifə")
        print("🎯 50+ farklı soru tipi tanımlandı!")
        print("✅ Eski yardım menüsü tamamen kaldırıldı!")
        bot.run(token)
