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

# VERİTABANI
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
    return "Bot calisiyor! SNOK v6.0 - Fıkra Üstadı 🎪"

def run_web():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=False)

threading.Thread(target=run_web, daemon=True).start()

load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# SABİTLER
SUNUCU_ID = 1471063348689768523
ABI_ID = 423889250052734986
SELAM_COOLDOWN = 60
MESAJ_SAYISI_LIMITI = 5
ZAMAN_ARALIGI = 3
BUYUK_HARF_ORANI = 0.7
KUFUR_LISTESI = ['amk', 'aq', 'sik', 'piç', 'orospu', 'ibne', 'göt', 'yarrak', 'puşt', 'ananı', 'babanı', 'sikeyim', 'sikik', 'amcık', 'amq']

son_mesaj_zamani = defaultdict(float)
mesaj_sayaci = defaultdict(lambda: deque(maxlen=MESAJ_SAYISI_LIMITI))
son_selam_zamani = defaultdict(float)

kullanici_veritabani = veritabani_yukle()

# ==================== TÜRK FIKRALARI (TEMEL) ====================
turk_fıkraları = [
    "Temel arkadaşıyla vapura binmiş. Biletçi sormuş: 'Biletiniz?' Temel: 'Yok.' Biletçi: 'Nerede?' Temel: 'Karadeniz'de!' 🚢",
    "Temel’e sormuşlar: 'En çok neyi seversin?' Temel: 'Para!' 'Peki ondan sonra?' Temel: 'Para üstü!' 💰",
    "Doktor Temel’e: 'Sigara içiyor musun?' Temel: 'Hayır.' 'Alkol alıyor musun?' 'Hayır.' 'Kadın?' 'Hayır.' Doktor: 'Peki niye geldin?' Temel: 'Canım sıkıldı da!' 🏥",
    "Temel ölmüş, cennetin kapısına dayanmış. Hz.Muhammed sormuş: 'Günahın neydi?' Temel: 'Hiç!' 'Peki sevabın?' Temel: 'Bir kere balık tutarken oltamı denize düşürmüş bir çocuğa verdim.' Hz.Muhammed: 'O zaman cehenneme!' Temel: 'Neden?' 'Çünkü burada balık yok!' 😂",
    "Temel karısına sormuş: 'Hanım, beni sever misin?' 'Severim.' 'Peki çok sever misin?' 'Çok severim.' 'O zaman git bana çay getir!' ☕",
    "Temel’in oğlu sormuş: 'Baba, ben nasıl dünyaya geldim?' Temel: 'Otomatikman oğlum, otomatikman!' 👶",
    "Temel kahvede otururken yanına bir adam gelmiş. 'Hemşerim, saat kaç?' Temel: 'Bilmem.' Adam: 'Nasıl bilmezsin?' Temel: 'Saatim yok ki!' Adam: 'Peki niye kolunda saat var?' Temel: 'Onu geçen hafta buldum, daha çalışıyor mu bilmem!' ⌚",
    "Temel’e sormuşlar: 'En büyük hayalin ne?' Temel: 'Bir gün öyle zengin olayım ki, kahveye gittiğimde 'çay' yerine 'çay ısmarla' diyebileyim!' 🍵",
    "Temel doktora gitmiş. Doktor: 'Ateşin var.' Temel: 'Kaç derece?' Doktor: '38.' Temel: 'Peki normali kaç?' Doktor: '36.' Temel: 'O zaman fazla olan 2 dereceyi al da ihtiyacı olana ver!' 🌡️",
    "Temel tatile gitmiş. Otelci sormuş: 'Nasıl buldun odamızı?' Temel: 'Çok güzel, tek sorun pencereden deniz görünmüyor.' Otelci: 'Ama beyefendi, burası dağ oteli!' 🏔️"
]

# ==================== AZERBAYCAN LETİFELERİ (HABİL ƏLİYEV) ====================
azeri_letifeler = [
    "Habil Əliyev sorusur: 'Mənim adım nədi?' Cavab: 'Habil.' 'Yox, səhv dedin. Mənim adım Habil Əliyevdi, sən mənə hörmət eləməlisən!' 😂",
    "Habil Əliyev mağazaya girir: 'Salam, mənə iki kilo şəkər verin.' Satıcı: 'Baş üstə, Habil müəllim!' Habil: 'Yox, sən mənə hörmət eləmə, şəkəri ver get!' 🛒",
    "Bir dəfə Habil Əliyevdən sorusurlar: 'Sən niyə həmişə qalstuk taxırsan?' Habil: 'Mən qalstuk taxmıram, bu mənim boyunbağımdı, onu da anam mənə bağlayıb!' 👔",
    "Habil Əliyev küçədə gedir, bir qadın sorusur: 'Habil müəllim, siz məni tanımırsınız?' Habil: 'Tanımayacam da, sən kimsən?' Qadın: 'Mən sizin arvadınızam!' Habil: 'Aha, indi tanıdım!' 👩",
    "Habil Əliyevə sorusurlar: 'Habil müəllim, siz neçə yaşınızdasınız?' Habil: 'Mən 60 yaşımdayam, amma özümü 30 kimi hiss edirəm. Bəs sən neçə yaşındasan?' O biri: 'Mən 40.' Habil: 'Bax, mən sənin yaşında olanda özümü 20 kimi hiss edirdim!' 🎂",
    "Habil Əliyevə sorusurlar: 'Siz necə sağlam qalırsınız?' Habil: 'Çox sadə: hər gün bir diş sarımsaq yeyirəm, bir stəkan ayran içirəm, və heç kimlə danışmıram!' 🧄",
    "Habil Əliyev küçədə bir adam görür, yanına yaxınlaşır: 'Salam, mən Habil Əliyev!' Adam: 'Məmnun oldum, mən də Rüfət.' Habil: 'Yox, sən məmnun olmamalısan, mən məmnun olmalıyam!' 🤝",
    "Habil Əliyevdən sorusurlar: 'Habil müəllim, pul nədir?' Habil: 'Pul kağız parçasıdır. Amma o kağız parçası olmadan heç kim sənə hörmət eləmir!' 💵",
    "Habil Əliyev restorana girir: 'Mənə bir çay verin!' Garson: 'Baş üstə, Habil müəllim!' Habil: 'Yox, sən mənə hörmət eləmə, çayı tez gətir!' ☕",
    "Habil Əliyevdən sorusurlar: 'Habil müəllim, evlilik nədir?' Habil: 'Evlilik bir oyundur. Qaydası yoxdur, amma uduzan həmişə kişidir!' 💍"
]

# ==================== DİĞER KOMİK ŞAKALAR ====================
karisik_sakalar_tr = [
    "Bir bilgisayar virüsü hastaneye gitmiş. Doktor sormuş: 'Şikayetiniz?' Virüs: 'Her yerim dökülüyor!' 💻",
    "İnekler neden sürekli bilgisayar başında durur? Çünkü onların 'notebook'ları varmış! 🐄",
    "Bir gün çay şekere sormuş: 'Neden hep bana karışıyorsun?' Şeker: 'Yok canım, sadece tatlandırmaya çalışıyorum!' 🍵",
    "Temel bilgisayarcıya gitmiş: 'Bu bilgisayar çok yavaş.' Bilgisayarcı: 'Ne yapalım?' Temel: 'Bari hız sınırını kaldıralım!' 🚗",
    "Bir erkek evlenmeden önce kız arkadaşına sormuş: 'Yemek yapmayı biliyor musun?' Kız: 'Tabii ki!' 'Peki temizlik?' 'Elbette!' 'Çamaşır?' 'Bilirim.' Adam düşünmüş: 'O zaman sana ne gerek var?' 🤵"
]

karisik_sakalar_az = [
    "Bir kompüter virusu xəstəxanaya gedib. Həkim soruşub: 'Nə şikayətin var?' Virus: 'Hər yerim tökülür!' 💻",
    "İnəklər niyə həmişə kompüter qarşısında durur? Çünki onların 'notebook'ları var! 🐄",
    "Bir gün çay qəndə soruşub: 'Niyə həmişə mənə qarışırsan?' Qənd: 'Yox canım, sadəcə şirinləşdirməyə çalışıram!' 🍵",
    "Habil Əliyev kompüterçiyə gedib: 'Bu kompüter çox yavaşdı.' Kompüterçi: 'Nə edək?' Habil: 'Heç olmasa sürət həddini götürək!' 🚗",
    "Bir kişi evlənməmişdən qabaq qız yoldaşına soruşub: 'Yemək bişirməyi bilirsən?' Qız: 'Əlbəttə!' 'Bəs təmizlik?' 'Təbii!' 'Paltaryuma?' 'Bilirəm.' Kişi düşünüb: 'Onda sənə nə ehtiyac var?' 🤵"
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
        r'napıyon', r'ne yapıyorsun', r'nə edirsən', r'neynirsen'
    ]
    return any(re.search(pattern, text_lower) for pattern in patterns)

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

@bot.command(name='fıkra', aliases=['fıkra', 'fikra', 'letife'])
async def fikra(ctx):
    lang = detect_language(ctx.message.content)
    if lang == 'tr':
        await ctx.send(f"😂 **Temel Reis'ten bir fıkra:**\n{random.choice(turk_fıkraları)}")
    else:
        await ctx.send(f"😂 **Habil Əliyevdən bir lətifə:**\n{random.choice(azeri_letifeler)}")

@bot.command(name='şaka', aliases=['saka', 'joke'])
async def saka(ctx):
    lang = detect_language(ctx.message.content)
    if lang == 'tr':
        await ctx.send(f"😂 **{ctx.author.name}** sana komik bir şaka:\n{random.choice(karisik_sakalar_tr)}")
    else:
        await ctx.send(f"😂 **{ctx.author.name}** sənə gülməli bir zarafat:\n{random.choice(karisik_sakalar_az)}")

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
        await ctx.send(f"🎲 **{ctx.author.name}** için {adet} zar: {zarlar}")
    else:
        await ctx.send(f"🎲 **{ctx.author.name}** üçün {adet} zar: {zarlar}")

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
        embed.set_footer(text="SNOK v6.0 - Fıkra Üstadı")
    else:
        embed = discord.Embed(title="🌸 **SNOK Bot** 🌸", description="🤔 **Help** yerine **!kömək** yazmalısan! 🎀", color=discord.Color.pink())
        embed.set_footer(text="SNOK v6.0 - Lətifə Ustadı")
    await ctx.send(embed=embed)

# ==================== YARDIM KOMUTU (TEK VE TEK!) ====================
@bot.command(name='yardım', aliases=['kömək', 'yrd', 'yardim'])
async def yardim(ctx):
    lang = detect_language(ctx.message.content)

    if lang == 'tr':
        embed = discord.Embed(
            title="🌸 **SNOK Bot - Fıkra Üstadı** 🌸",
            description=(
                "✨ **Merhaba! Ben SNOK, sana nasıl yardımcı olabilirim?** ✨\n\n"
                "🎪 **Eğlence Komutlarım:**\n"
                "• `!fıkra` - Temel Reis'ten enfes fıkralar 😂\n"
                "• `!şaka` - Komik şakalar 😆\n"
                "• `!yazitura` - Yazı tura atar 🪙\n"
                "• `!zar [sayı]` - Zar atar (1-5 arası) 🎲\n"
                "• `!bilgi` - İlginç bilgiler ℹ️\n"
                "• `!sarıl [@kişi]` - Birine sarılır 🤗\n\n"
                "📋 **Diğer Komutlar:**\n"
                "• `!level` - Seviye bilgisi (çalışmıyor ⚠️)\n"
                "• `!yardım` - Bu menüyü gösterir 🎀\n\n"
                "💬 **Sohbet Özelliklerim:**\n"
                "• Bana `snok` yazarak seslenebilirsin\n"
                "• Adını söylersen seni tanırım! ('Benim adım Ali')\n"
                "• İsmini unutmam, veritabanıma kaydederim 📝\n"
                "• Hızlı mesaj atarsan uyarırım 🍬\n"
                "• Büyük harfle yazarsan uyarırım 🔇\n"
                "• Küfür edersen üzülürüm 🥺\n\n"
                "🌺 **Sorabileceğin Şeyler:**\n"
                "Merhaba, Nasılsın, Nerelisin, Kaç yaşındasın, Evli misin, Bot musun, Kimsin...\n\n"
                "💫 **2 Dil Biliyorum:** Türkçe & Azərbaycanca"
            ),
            color=discord.Color.pink()
        )
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        embed.set_footer(text="SNOK v6.0 - Fıkra Üstadı", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    else:
        embed = discord.Embed(
            title="🌸 **SNOK Bot - Lətifə Ustadı** 🌸",
            description=(
                "✨ **Salam! Mən SNOK, sənə necə kömək edə bilərəm?** ✨\n\n"
                "🎪 **Əyləncə Komandalarım:**\n"
                "• `!fıkra` - Habil Əliyev lətifələri 😂\n"
                "• `!şaka` - Gülməli zarafatlar 😆\n"
                "• `!yazitura` - Yazı tura atar 🪙\n"
                "• `!zar [sayı]` - Zar atar (1-5 arası) 🎲\n"
                "• `!bilgi` - Maraqlı məlumatlar ℹ️\n"
                "• `!sarıl [@kişi]` - Birinə sarılar 🤗\n\n"
                "📋 **Digər Komandalar:**\n"
                "• `!səviyyə` - Səviyyə məlumatı (işləmir ⚠️)\n"
                "• `!kömək` - Bu menünü göstərir 🎀\n\n"
                "💬 **Söhbət Xüsusiyyətlərim:**\n"
                "• Mənə `snok` yazaraq səslənə bilərsən\n"
                "• Adını söyləsən səni tanıyıram! ('Mənim adım Əli')\n"
                "• Adını unutmaram, yadda saxlayıram 📝\n"
                "• Sürətli mesaj yazsan xəbərdar edərəm 🍬\n"
                "• Böyük hərflə yazsan xəbərdar edərəm 🔇\n"
                "• Söyüş etsən üzülərəm 🥺\n\n"
                "🌺 **Soruşa Biləcəyin Şeylər:**\n"
                "Salam, Necəsən, Hardasan, Neçə yaşın var, Evli sən, Botsan, Kimsən...\n\n"
                "💫 **2 Dil Bilirəm:** Türkçə & Azərbaycanca"
            ),
            color=discord.Color.pink()
        )
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        embed.set_footer(text="SNOK v6.0 - Lətifə Ustadı", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)

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
        
        if kayitli_isim:
            if lang == 'tr':
                await message.reply(f"Efendim {kayitli_isim}? 😊")
            else:
                await message.reply(f"Buyur {kayitli_isim}? 😊")
        else:
            if random.random() < 0.3:
                if lang == 'tr':
                    await message.reply("Efendim? Bu arada adın neydi? 🤔")
                else:
                    await message.reply("Buyur? Bu arada adın nə idi? 🤔")
            else:
                if lang == 'tr':
                    await message.reply("Efendim? 😊")
                else:
                    await message.reply("Buyur? 😊")
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
        print("🌸 SNOK v6.0 - Fıkra Üstadı Modu Aktif! 🎪")
        print("🇹🇷 10 Temel Fıkrası + 🇦🇿 10 Habil Lətifəsi yüklendi!")
        bot.run(token)
