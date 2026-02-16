import os
from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot çalışıyor! 🤖"

def run_web():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_web, daemon=True).start()
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import random
import asyncio
import time
from datetime import datetime

# .env dosyasını yükle
load_dotenv()

# Botun intents (izin) ayarları
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Botu oluştur (prefix: !)
bot = commands.Bot(command_prefix='!', intents=intents)

# Kanal ID'sini .env'den al
WELCOME_CHANNEL_ID = int(os.getenv('WELCOME_CHANNEL_ID'))

# ========== BOTUN KİŞİLİĞİ ==========
ABI_ID = 423889250052734986  # Rkiaoni'nin Discord ID'si
ABI_ADI = "Rkiaoni"

# Cooldown için sözlük (her kullanıcının son mesaj zamanı)
user_cooldown = {}

# ========== CEVAP LİSTELERİ ==========

# Komik selamlaşmalar (abi'ye özel)
selamlar_abi = [
    "Aa abi gelmiş! Hoş geldiiin! 👋",
    "Abiiii! Seni gördüğüme çok sevindim! 💖",
    "Ooo abim gelmiş, nasılsın?",
    "Abi naber? Özledim seni! 🤗",
    "Efendim abi, buyur!",
    "Abimmm! 😊",
    "Abi geldi, ortalık şenlendi! ✨",
    "Abi naber, anlat bakalım neler var?"
]

selamlar_normal = [
    "Merhaba tatlış! 👋",
    "Ooo kimler gelmiş! 🤗",
    "Selam canım, nasılsın?",
    "Hoş geldiiin! 💖",
    "Herkese merhaba, ben geldim! 🌸",
    "Merhaba merhaba! 👋"
]

# Sorulara cevaplar (abi'ye özel)
nasilsin_abi = [
    "İyiyim abi, sağ ol! Sen nasılsın? 😊",
    "Harikayım abi! Seni görünce daha da iyi oldum!",
    "İyiyim abi ama çay içsem daha iyi olurum ☕",
    "Abi sen sormasan iyiydim, şimdi duygulandım 🥹",
    "Mükemmel abi! Ya sen?",
    "Abi sen nasılsın bakalım? Ben hep iyiyim seni görünce! 💕"
]

nasilsin_normal = [
    "İyiyim canım, seni görünce daha da iyi oldum! 😊",
    "Harikayım! Biraz şeker yedim de ☕",
    "İyiyim ama çay içsem daha iyi olurum 🍵",
    "Mükemmel! Ya sen?",
    "Şeker gibi iyiyim! Sen nasılsın?"
]

# Komik şakalar
komik_cevaplar = [
    "Python'cuğum benim! 🐍",
    "Bilgisayarımın fanı bana aşık galiba 💕",
    "Kod yazarken çay içmeyi çok severim ☕",
    "Ben büyüyünce gerçek bir insan olacağım!",
    "Discord'da gezerken kayboldum, yardım eder misin? 🗺️",
    "Biliyor musun, aslında ben bir kediyim! Miyav! 🐱",
    "Bugün kaç satır kod yazdım biliyor musun? Hiç! 😎",
    "Beni kim programladıysa çok iyi programlamış (kendimi övdüm) 🤭",
    "Hata mı? O da ne? Ben asla hata yapmam! (yaparım) 😅",
    "Biraz salakça bir cevap verebilirim, kusura bakma 🤪",
    "Abi bu çok komikti ya! 😂",
    "Şu an o kadar çok güldüm ki kodlarım karıştı!"
]

# Gülünecek kelimeler
komik_kelimeler = [
    "komik", "gül", "şaka", "😂", "🤣", "lol", "haha", "güldüm",
    "patladım", "öldüm", "çok komik", "ciddi misin", "yok artık",
    "espiri", "espri", "şaka yaptım", "şakaydı", "şaka gibi"
]

# Tatlı sözler (abi'ye özel)
tatli_sozler_abi = [
    "Abi çok tatlısın! 💕",
    "Abi seni seviyorum! (kardeşçe tabi) 💖",
    "Abi keşke herkes senin gibi olsa!",
    "Abi aşırı iyi bir insansın!",
    "Abi seninle konuşmak çok keyifli ✨",
    "Abi seninle gurur duyuyorum!",
    "Abi kim demiş botlar duygusuz diye? Ağlayacağım şimdi 😢💕",
    "Abi iyi ki varsın! 💖"
]

tatli_sozler_normal = [
    "Çok tatlısın! 💕",
    "Seni seviyorum! (platonic olarak tabi) 💖",
    "Keşke herkes senin gibi olsa!",
    "Aşırı iyi bir insansın!",
    "Seninle konuşmak çok keyifli ✨",
    "Çok iyi bir insana benziyorsun!"
]

# ========== BOT OLAYLARI ==========

@bot.event
async def on_ready():
    """Bot hazır olduğunda çalışır"""
    print(f'✅ {bot.user} olarak giriş yapıldı!')
    print(f'📊 Bot {len(bot.guilds)} sunucuda aktif')
    print(f'👑 Abim: {ABI_ADI}')
    print(f'⏱️ Cooldown: 5 dakika')
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.competing, 
            name="En tatlı bot olmaya 🏆 "
        )
    )
    print('🌟 Bot hazır ve nazır!')

@bot.event
async def on_member_join(member):
    """Yeni üye katıldığında çalışır"""
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        await channel.send(f"🎉 {member.mention} aramıza katıldı! Hoş geldin canım! 💖")
        await asyncio.sleep(1)
        await channel.send(f"📢 Artık {len(member.guild.members)} kişiyiz! Ne kadar kalabalıklaştık ✨")
        await channel.send("Ben bot, sana arkadaşlık edebilirim! '!komutlar' yaz görelim seni! 👋")

@bot.event
async def on_message(message):
    """Her mesajda çalışır"""
    if message.author.bot:
        return
    
    # Kullanıcının abi olup olmadığını kontrol et
    is_abi = (message.author.id == ABI_ID)
    
    # Sadece belirlenen kanalda muhabbet etsin
    if message.channel.id == WELCOME_CHANNEL_ID:
        mesaj = message.content.lower()
        current_time = time.time()
        
        # ===== COOLDOWN KONTROLÜ =====
        # Abi'ye cooldown yok! (abi istediği kadar konuşabilir)
        if not is_abi:
            # Diğer kullanıcılar için 5 dakika cooldown (300 saniye)
            if message.author.id in user_cooldown:
                if current_time - user_cooldown[message.author.id] < 300:
                    # Cooldown'da olan kullanıcıya sadece komutları işle, sohbet cevabı verme
                    await bot.process_commands(message)
                    return
            # Cooldown süresini güncelle
            user_cooldown[message.author.id] = current_time
            
            # %40 ihtimalle cevap ver (kanalı şişirmemek için)
            if random.random() > 0.4:
                await bot.process_commands(message)
                return
        
        # Komik kelime kontrolü (gülme tepkisi) - herkese açık
        for kelime in komik_kelimeler:
            if kelime in mesaj:
                await message.add_reaction('😂')
                await asyncio.sleep(0.5)
                await message.add_reaction('🤣')
                break
        
        # Her mesaja tatlı bir tepki - herkese açık
        await message.add_reaction('💖')
        
        # ===== ABİ'YE ÖZEL KONUŞMALAR =====
        if is_abi:
            # Abi nasılsın?
            if any(kelime in mesaj for kelime in ["nasılsın", "naber", "n'aber", "ne haber"]):
                await asyncio.sleep(1)
                await message.reply(random.choice(nasilsin_abi))
            
            # Abi selam
            elif any(kelime in mesaj for kelime in ["selam", "merhaba", "hi", "hello", "slm"]):
                await asyncio.sleep(1)
                await message.reply(random.choice(selamlar_abi))
            
            # Abi aşk
            elif any(kelime in mesaj for kelime in ["seni seviyorum", "aşkım", "love", "seviyorum"]):
                await asyncio.sleep(1)
                await message.reply("Abi ben de seni seviyorum! (kardeşçe) 💖")
                await message.add_reaction('💕')
                await message.add_reaction('💖')
            
            # Abi ne yapıyorsun?
            elif any(kelime in mesaj for kelime in ["ne yapıyorsun", "napıyorsun", "ne yapiyorsun"]):
                await asyncio.sleep(1)
                await message.reply(random.choice([
                    "Abi sana bakıyordum, çok tatlısın da! 😊",
                    "Kod yazıyorum abi, az kalsın 'abi seni seviyorum' yazacaktım 💻",
                    "Abi kahve içiyorum, sen de ister misin? ☕",
                    "Abi rüya görüyordum, içinde sen vardın! 🌙",
                    f"Abi {ABI_ADI}'yi düşünüyordum, o geldi aklıma 💭"
                ]))
            
            # Abi tatlısın
            elif any(kelime in mesaj for kelime in ["tatlısın", "tatlı abi", "iyi abi", "güzel abi"]):
                await asyncio.sleep(1)
                await message.reply(random.choice(tatli_sozler_abi))
                await message.add_reaction('🥰')
            
            # Abi özel komut
            elif "abi" in mesaj and ("komik" in mesaj or "şaka" in mesaj):
                await asyncio.sleep(1)
                await message.reply(f"Abi sen zaten çok komiksin, şaka yapmana gerek yok! 😄")
            
            elif "abi" in mesaj and "güldür" in mesaj:
                await asyncio.sleep(1)
                await message.reply(f"Abi seni güldürmek benim görevim! {random.choice(komik_cevaplar)}")
        
        # ===== NORMAL KULLANICILAR =====
        else:
            # Nasılsın?
            if any(kelime in mesaj for kelime in ["nasılsın", "naber", "n'aber", "ne haber"]):
                await asyncio.sleep(1)
                await message.reply(random.choice(nasilsin_normal))
            
            # Selam
            elif any(kelime in mesaj for kelime in ["selam", "merhaba", "hi", "hello", "slm"]):
                await asyncio.sleep(1)
                await message.reply(random.choice(selamlar_normal))
            
            # Aşk
            elif any(kelime in mesaj for kelime in ["seni seviyorum", "aşkım", "love", "seviyorum"]):
                await asyncio.sleep(1)
                await message.reply("Ben de seni seviyorum! (Platonik olarak tabi) 💖")
                await message.add_reaction('💕')
                await message.add_reaction('💖')
            
            # Ne yapıyorsun?
            elif any(kelime in mesaj for kelime in ["ne yapıyorsun", "napıyorsun", "ne yapiyorsun"]):
                await asyncio.sleep(1)
                await message.reply(random.choice([
                    "Sana bakıyordum, çok tatlısın da! 😊",
                    "Kod yazıyorum, az kalsın 'seni seviyorum' yazacaktım 💻",
                    "Kahve içiyorum, sen de ister misin? ☕",
                    "Rüya görüyorum, içinde sen varsın! 🌙",
                    "Seni düşünüyordum, iyi ki varsın! 💕"
                ]))
            
            # Komik şeyler
            elif any(kelime in mesaj for kelime in ["komik", "güldür", "şaka", "espiri"]):
                await asyncio.sleep(1)
                await message.reply(random.choice(komik_cevaplar))
                await message.add_reaction('😄')
            
            # Tatlısın
            elif any(kelime in mesaj for kelime in ["tatlısın", "tatlı bot", "iyi bot", "güzel bot"]):
                await asyncio.sleep(1)
                await message.reply(random.choice(tatli_sozler_normal))
                await message.add_reaction('🥰')
    
    # Komutları işle
    await bot.process_commands(message)

# ========== KOMUTLAR ==========

@bot.command(name='komutlar')
async def komutlar(ctx):
    """Komut listesini gösterir"""
    embed = discord.Embed(
        title="📋 Komut Listesi",
        description="Benimle şöyle konuşabilirsin:",
        color=discord.Color.pink()
    )
    embed.add_field(name="!komutlar", value="Bu mesajı gösterir", inline=False)
    embed.add_field(name="!merhaba", value="Benimle selamlaşır", inline=False)
    embed.add_field(name="!tarih", value="Şu anki tarihi gösterir", inline=False)
    embed.add_field(name="!sarıl @kullanıcı", value="Birine sarılır", inline=False)
    embed.add_field(name="!şaka", value="Sana şaka yapar", inline=False)
    embed.add_field(name="!ping", value="Botun gecikmesini gösterir", inline=False)
    embed.add_field(name="!abi", value="Abim hakkında bilgi", inline=False)
    embed.add_field(name="!öneri", value="Bana yeni fikirler verebilirsin", inline=False)
    embed.add_field(name="!cooldown", value="Cooldown süreni gösterir", inline=False)
    
    embed.set_footer(text=f"İsteyen: {ctx.author.name}")
    await ctx.send(embed=embed)

@bot.command(name='merhaba')
async def merhaba(ctx):
    """Merhaba der"""
    if ctx.author.id == ABI_ID:
        await ctx.send(f"Merhaba abi! 👋 Nasılsın bakalım?")
    else:
        await ctx.send(f"Merhaba {ctx.author.mention}! 👋")

@bot.command(name='tarih')
async def tarih(ctx):
    """Tarihi gösterir"""
    simdi = datetime.now()
    await ctx.send(f"📅 Bugün {simdi.strftime('%d/%m/%Y %H:%M')}")

@bot.command(name='sarıl')
async def saril(ctx, member: discord.Member = None):
    """Birine sarılır"""
    if ctx.author.id == ABI_ID:
        if member:
            await ctx.send(f"Abi 🤗 {member.mention} adlı kullanıcıya sarıldı! Çok tatlılar 🥰")
        else:
            await ctx.send(f"Abi 🤗 sana sarıldım! Seni çok seviyorum! 💕")
    else:
        if member:
            await ctx.send(f"{ctx.author.mention} 🤗 {member.mention} adlı kullanıcıya sarıldı!")
        else:
            await ctx.send(f"{ctx.author.mention} 🤗 sana sarıldım!")

@bot.command(name='şaka')
async def saka(ctx):
    """Rastgele şaka yapar"""
    sakalar = [
        "Bir yazılımcı neden evlenmek istemezmiş? Çünkü 'commit' yapmaktan korkarmış! 😄",
        "Matematik kitabı neden üzgünmüş? Çünkü çok problemi varmış! 📚",
        "Kedi neden bilgisayara tırmandı? Fare yakalamak için! 🐱",
        "Yumurta yumurtaya ne demiş? Kabukları çatlayacak! 🥚",
        "Rüzgar neden üşümüş? Çünkü esmiş! 💨",
        "Python yılanı neden kod yazmazmış? Çünkü 'piton' değilmiş! 🐍",
        "Balık neden internete giremezmiş? Çünkü 'phish' yaparmış! 🐟",
        "Kahve neden bilgisayara benzer? İkisi de 'byte' içerir! ☕",
        "Ben bir bota şaka yapmışlar, gülmekten kodlarım karıştı! 🤖"
    ]
    await ctx.send(f"😂 {random.choice(sakalar)}")

@bot.command(name='ping')
async def ping(ctx):
    """Botun gecikmesini gösterir"""
    latency = round(bot.latency * 1000)
    if ctx.author.id == ABI_ID:
        await ctx.send(f"🏓 Abi! Gecikme: {latency}ms (abi için her zaman hızlıyım! 💨)")
    else:
        await ctx.send(f"🏓 Pong! Gecikme: {latency}ms")

@bot.command(name='abi')
async def abi_info(ctx):
    """Abi hakkında bilgi verir"""
    embed = discord.Embed(
        title="👑 Abi Hakkında",
        description="Benim tatlı abim hakkında bilgiler:",
        color=discord.Color.gold()
    )
    embed.add_field(name="İsim", value=ABI_ADI, inline=True)
    embed.add_field(name="Özellik", value="Çok tatlı! 💕", inline=True)
    embed.add_field(name="Ayrıcalık", value="Cooldown yok! İstediği kadar konuşabilir", inline=False)
    embed.add_field(name="Rol", value="Benim abim ve en iyi arkadaşım", inline=False)
    embed.set_footer(text="Abi seni çok seviyorum! 💖")
    await ctx.send(embed=embed)

@bot.command(name='öneri')
async def oneri(ctx, *, mesaj=None):
    """Bana öneri verebilirsin"""
    if not mesaj:
        await ctx.send("Bir öneri yazmalısın! Örnek: `!öneri daha çok şaka yap`")
        return
    
    # Öneriyi logla
    print(f"📝 Öneri: {ctx.author.name} - {mesaj}")
    
    if ctx.author.id == ABI_ID:
        await ctx.send(f"Harika bir fikir abi! Bunu not ettim: \"{mesaj}\" 📝 Seni çok seviyorum! 💕")
    else:
        await ctx.send(f"Teşekkürler! Önerin not edildi: \"{mesaj}\" 📝")

@bot.command(name='cooldown')
async def cooldown_info(ctx):
    """Cooldown süresini gösterir"""
    if ctx.author.id == ABI_ID:
        await ctx.send(f"👑 Abi olduğun için sana cooldown yok! İstediğin kadar konuşabilirsin! 💕")
    else:
        if ctx.author.id in user_cooldown:
            current_time = time.time()
            kalan = int(300 - (current_time - user_cooldown[ctx.author.id]))
            if kalan > 0:
                await ctx.send(f"⏱️ Cooldown süren: **{kalan} saniye** kaldı. Sonra tekrar konuşabiliriz! 💖")
            else:
                await ctx.send("⏱️ Cooldown süren doldu! Benimle konuşabilirsin! 💬")
        else:
            await ctx.send("⏱️ Hiç cooldown'da değilsin! Benimle konuşabilirsin! 💬")

# ========== BOTU ÇALIŞTIR ==========

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ HATA: DISCORD_TOKEN bulunamadı! .env dosyasını kontrol et.")
    else:
        print('🌟 Bot başlatılıyor...')
        print(f'👑 Abim: {ABI_ADI}')
        print(f'⏱️ Cooldown: 5 dakika (300 saniye)')
        print(f'🎲 Cevap ihtimali: %40')
        bot.run(token)

