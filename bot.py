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
app.debug = False  # Debug modu KAPALI (çift mesajı engeller)

@app.route('/')
def home():
    return "Bot calisiyor! SNOK v3.0 - Süper Tatlı Mod 🍬"

def run_web():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=False)

threading.Thread(target=run_web, daemon=True).start()
# ===== WEB SUNUCUSU BİTTİ =====

load_dotenv()

# Bot intents ayarları
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

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

def kullanici_tam_ismini_getir(kullanici_id):
    """Kullanıcının tam ismini döndürür"""
    kullanici_id_str = str(kullanici_id)
    if kullanici_id_str in kullanici_veritabani:
        isim = kullanici_veritabani[kullanici_id_str].get('isim', '')
        soyisim = kullanici_veritabani[kullanici_id_str].get('soyisim', '')
        if isim and soyisim:
            return f"{isim} {soyisim}"
        elif isim:
            return isim
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
        r'evli misin', r'bot musun', r'adın ne', r'kimsin'
    ]
    return any(re.search(pattern, text_lower) for pattern in patterns)

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

# ===== YARDIM KOMUTU - TATLI VERSİYON =====
@bot.command(name='yardım', aliases=['kömək', 'yrd', 'help'])
async def yardim(ctx):
    lang = detect_language(ctx.message.content)

    if lang == 'tr':
        embed = discord.Embed(
            title="🌸 **SNOK Bot Yardım Menüsü** 🌸",
            description=(
                "✨ **Merhaba! Ben SNOK, sana nasıl yardımcı olabilirim?** ✨\n\n"
                "🍭 **Komutlarım:**\n"
                "• `!level` - Seviye bilgisini gösterir (şu an çalışmıyor ⚠️)\n"
                "• `!yardım` - Bu tatlı menüyü gösterir 🎀\n\n"
                "💬 **Sohbet Özelliklerim:**\n"
                "• Bana `snok` yazarak seslenebilirsin\n"
                "• Adını söylersen seni tanırım! (örn: 'Benim adım Ali')\n"
                "• İsmini unutmam, veritabanıma kaydederim 📝\n"
                "• Hızlı mesaj atarsan seni tatlı dille uyarırım 🍬\n"
                "• Büyük harfle yazarsan sesimin kısıldığını söylerim 🔇\n"
                "• Küfür edersen üzülürüm 🥺\n\n"
                "🌺 **Sorabileceğin Şeyler:**\n"
                "• Nerelisin? • Kaç yaşındasın? • Evli misin?\n"
                "• Bot musun? • Adın ne? • Ne yapıyorsun?\n\n"
                "💫 **2 Dil Biliyorum:** Türkçe & Azərbaycanca"
            ),
            color=discord.Color.pink()
        )
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        embed.set_footer(text="SNOK v3.0 - Süper Tatlı Mod 💖", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    else:
        embed = discord.Embed(
            title="🌸 **SNOK Bot Kömək Menüsü** 🌸",
            description=(
                "✨ **Salam! Mən SNOK, sənə necə kömək edə bilərəm?** ✨\n\n"
                "🍭 **Komandalarım:**\n"
                "• `!səviyyə` - Səviyyə məlumatını göstərir (hal-hazırda işləmir ⚠️)\n"
                "• `!kömək` - Bu şirin menünü göstərir 🎀\n\n"
                "💬 **Söhbət Xüsusiyyətlərim:**\n"
                "• Mənə `snok` yazaraq səslənə bilərsən\n"
                "• Adını söyləsən səni tanıyıram! (məs: 'Mənim adım Əli')\n"
                "• Adını unutmaram, verilənlər bazama qeyd edərəm 📝\n"
                "• Sürətli mesaj yazsan səni şirin dillə xəbərdar edərəm 🍬\n"
                "• Böyük hərflə yazsan səsimin kısıldığını deyərəm 🔇\n"
                "• Söyüş etsən üzülərəm 🥺\n\n"
                "🌺 **Soruşa Biləcəyin Şeylər:**\n"
                "• Hardasan? • Neçə yaşın var? • Evli sən?\n"
                "• Botsan? • Adın nə? • Nə edirsən?\n\n"
                "💫 **2 Dil Bilirəm:** Türkçə & Azərbaycanca"
            ),
            color=discord.Color.pink()
        )
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        embed.set_footer(text="SNOK v3.0 - Super Şirin Mod 💖", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)

    await ctx.send(embed=embed)

# ===== ON_MESSAGE (ANA OLAY) =====
@bot.event
async def on_message(message):
    # ÇİFT MESAJ ENGELLEME - Bu mesaj daha önce işlendiyse atla
    if hasattr(message, 'snok_processed'):
        return
    message.snok_processed = True
    
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
            response = f"Ha? İsmin değişti mi? Tamam, yeni ismini not ettim {yeni_isim}! 📝"
        else:
            # Yeni tanışma
            response = f"Tanıştığımıza memnun oldum {yeni_isim}! 🤝"
        
        await message.reply(response)
        return

    # ===== KİŞİSEL SORULAR =====
    if is_personal_question(message.content):
        # Selamlama kontrolü
        selamlama_mi = any(k in message.content.lower() for k in ['merhaba', 'selam', 'salam', 'hey', 'hi'])
        
        if selamlama_mi:
            simdi = time.time()
            if simdi - son_selam_zamani[message.author.id] < SELAM_COOLDOWN:
                await bot.process_commands(message)
                return
            son_selam_zamani[message.author.id] = simdi
        
        # Basit cevap
        if kayitli_isim:
            await message.reply(f"Efendim {kayitli_isim}? 😊")
        else:
            await message.reply("Efendim? 😊")
        return

    # ===== NORMAL SOHBET (SADECE BOT ÇAĞRILIRSA) =====
    bot_cagrildi = (
        bot.user.mentioned_in(message) or 
        'snok' in message.content.lower() or
        message.reference
    )
    
    if bot_cagrildi:
        emojiler = ['😊', '🥰', '🤗', '😘', '✨', '💫', '🌸', '🍬', '🍭', '🎀', '💖', '💕']
        emoji = random.choice(emojiler)
        
        if kayitli_isim:
            await message.reply(f"Evet {kayitli_isim}? {emoji}")
        else:
            # İsmi yoksa bazen soralım
            if random.random() < 0.2:  # %20 ihtimalle
                if lang == 'tr':
                    await message.reply(f"Bu arada adın neydi? {emoji}")
                else:
                    await message.reply(f"Bu arada adın nə idi? {emoji}")
            else:
                await message.reply(f"Evet? {emoji}")
        return

    # ===== KOMUTLARI İŞLE =====
    await bot.process_commands(message)

# ===== BOTU BAŞLAT =====
if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("HATA: DISCORD_TOKEN bulunamadı! .env dosyasını kontrol et.")
    else:
        print("🌸 SNOK v3.0 başlatılıyor... Süper Tatlı Mod Aktif! 🍭")
        print("✨ Bot şu özelliklerle çalışıyor:")
        print("   • İsim öğrenme ve hatırlama 📝")
        print("   • Spam koruması 🛡️")
        print("   • Küfür engeli 🥺")
        print("   • Çoklu dil desteği (Türkçe & Azərbaycanca) 🌍")
        print("   • Render'da 7/24 çalışmaya hazır! 🚀")
        bot.run(token)
