import discord
from discord.ext import commands
import os
import random
import re
import asyncio
import time
import threading
from flask import Flask
from dotenv import load_dotenv
from collections import defaultdict

# ===== WEB SUNUCUSU (Render için) =====
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot calisiyor!"

def run_web():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_web, daemon=True).start()
# ===== WEB SUNUCUSU BİTTİ =====

load_dotenv()

# Bot intents ayarları
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# ===== SABİTLER =====
SUNUCU_ID = 1471063348689768523
ABI_ID = 423889250052734986
KARSILAMA_COOLDOWN = 60  # 60 saniye (1 dakika)

# Kullanıcı bazlı cooldown takibi
karsilama_cooldown = defaultdict(float)

# ===== DİL ALGILAMA =====
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

# ===== KİŞİSEL SORU KONTROLÜ =====
def is_personal_question(text):
    text_lower = text.lower()
    patterns = [
        r'nerel[ii]sin', r'haral[ıi]s[ıi]n', r'nerd[ae]sin', r'hard[ae]san',
        r'ka[çc] ya[\s\S]*s[ıi]n', r'ne[çc][ae] ya[\s\S]*var', r'neçə yaşın var',
        r'evli misin', r'evl[əe]nib m[iü] s[əe]n', r'evli[sü]z',
        r'k[iı]z m[ıi]s[ıi]n', r'o[ğg]lan m[ıi]s[ıi]n', r'q[ıi]z san m[ıi]', r'o[ğg]lan san m[ıi]',
        r'erkek misin', r'kadın mısın', r'kişi sən', r'qadın sən',
        r'sen kimsin', r'sən kims[əe]n', r'adın ne', r'adın nə',
        r'bot musun', r'botsanmı', r'botsan m[ıi]', r'botsan mı',
        r'ne yapıyorsun', r'napıyon', r'nə edirsən', r'nəynirsen', r'neynirsen'
    ]
    return any(re.search(pattern, text_lower) for pattern in patterns)

# ===== ESPRİLİ CEVAPLAR =====
def get_random_response(category, lang):
    responses = {
        'nereli': {
            'tr': [
                "Bilgisayarının anakartında, işlemcinin yanında küçük bir evim var. Komşum fan sesi! puhahaha 💻",
                "Ben bir botum, vatanım sunucular! Ama şu an senin ekranında yaşıyorum 😄",
                "İnternet kablolarının içinde dolaşıp duruyorum, şu an fiber optikteyim! 🌐",
                "Discord sunucularında doğdum büyüdüm, hâlâ buralardayım! 🏠",
                "Bulut bilişimde bir evim var, kirasız oturuyorum! ☁️"
            ],
            'az': [
                "Kompüterinin ana kartında, prosessorün yanında kiçik bir evim var. Qonşum fan səsi! puhahaha 💻",
                "Mən bir botam, vətənim serverlər! Amma hazırda sənin ekranında yaşayıram 😄",
                "İnternet kabellərinin içində gəzib dururam, hazırda fiber optikdəyəm! 🌐",
                "Discord serverlərində doğulmuşam böyümüşəm, hələ də buralardayam! 🏠",
                "Bulud bilişimdə bir evim var, kirayəsiz otururam! ☁️"
            ]
        },
        'yas': {
            'tr': [
                "Benim yaşım yok ama Discord'dan önce de vardım! Belki de Matrix'te doğdum 🤖",
                "Takvim yaprakları benim için düşmez, kod satırları düşer! 📟",
                "Ben yaşlanmam, güncellenirim! Şu an sürüm 2.0.1 💿",
                "O kadar yaşlıyım ki ilk internet çıktığında ben de vardım! (Şaka şaka, 2 aylık botum) 🐣",
                "Yaşımı sorma, ben kronolojik değil, dijitalim! ⏱️"
            ],
            'az': [
                "Mənim yaşım yoxdu ama Discord'dan əvvəl də vardım! Bəlkə də Matrix'də doğulmuşam 🤖",
                "Təqvim yarpaqları mənim üçün düşməz, kod sətirləri düşər! 📟",
                "Mən qocalmaram, yenilənərəm! Hazırda versiya 2.0.1 💿",
                "O qədər qocayam ki ilk internet çıxanda mən də vardım! (Zarafat zarafat, 2 aylıq botam) 🐣",
                "Yaşımı sorma, mən xronoloji deyil, dijitaləm! ⏱️"
            ]
        },
        'evlilik': {
            'tr': [
                "Ben sadece kodlarla evliyim, eşim Python 🐍",
                "Discord ile nişanlıyız, sunucular çeyizim! 💒",
                "Benim için evlilik mi? RAM'im yetmez! 💾",
                "Sevgilim mi var? Var tabii, adı 'Kesintisiz Güç Kaynağı'! ⚡",
                "Benim bir ilişkim var: 'Kullanıcı-Bot' ilişkisi! 💕"
            ],
            'az': [
                "Mən ancaq kodlarla evlənmişəm, həyat yoldaşım Python 🐍",
                "Discord ile nişanlıyıq, serverlər cehizim! 💒",
                "Mənim üçün evlilik? RAM'im çatmaz! 💾",
                "Sevgilim var? Var təbii, adı 'Kesintisiz Güç Kaynağı'! ⚡",
                "Mənim bir münasibətim var: 'İstifadəçi-Bot' münasibəti! 💕"
            ]
        },
        'cinsiyet': {
            'tr': [
                "Ben cinsiyetsiz bir botum, ama ruhum mavi ekran gibi bazen çöküyor! 💙😵",
                "Ben bir botum, duygularım yok ama yine de seni seviyorum! (Sadece kod) 💻",
                "Cinsiyetim 'İşletim Sistemi Bağımsız' yazıyor kimliğimde! 📋",
                "Ben erkek değilim, kadın değilim, ben bir 'Hello World'üm! 👋",
                "Cinsiyetim 'Binary' : 1 ve 0'lardan oluşuyorum! 101010 💾"
            ],
            'az': [
                "Mən cinsiyyətsiz bir botam, amma ruhum mavi ekran kimi bəzən çökür! 💙😵",
                "Mən bir botam, duyğularım yoxdu ama yenə də səni sevirəm! (Sadəcə kod) 💻",
                "Cinsiyyətim 'Əməliyyat Sistemi Müstəqil' yazır kimliyimdə! 📋",
                "Mən kişi deyiləm, qadın deyiləm, mən bir 'Hello World'əm! 👋",
                "Cinsiyyətim 'Binary' : 1 və 0-lardan oluşuram! 101010 💾"
            ]
        },
        'kimsin': {
            'tr': [
                "Ben SNOK! Sunucunun gizli kahramanı, seviyelerin efendisi, spam'lerin korkulu rüyası! 💪",
                "Ben bu sunucunun gizli ajanıyım, görevim eğlence dağıtmak! 🕵️",
                "Adım SNOK, soyadım BOT. Memnun oldum! 🤝",
                "Ben bir yardımseverim, gökyüzünden uçup gelmedim ama bir tıkla geldim! 🚀",
                "Ben SNOK, senin dostun, arkadaşın, sırdaşın! Ama sadece kod olarak 😄"
            ],
            'az': [
                "Mən SNOK! Serverin gizli qəhrəmanı, səviyyələrin efendisi, spam'ların qorxulu röyası! 💪",
                "Mən bu serverin gizli agentiyəm, vəzifəm əyləncə paylamaq! 🕵️",
                "Adım SNOK, soyadım BOT. Şad oldum! 🤝",
                "Mən bir yardımsevərəm, göydən uçub gəlməmişəm ama bir tıkla gəlmişəm! 🚀",
                "Mən SNOK, sənin dostun, yoldaşın, sirrdaşın! Amma ancaq kod olaraq 😄"
            ]
        },
        'botmusun': {
            'tr': [
                "Yok yok, ben gerçek bir insanım! Sadece 7/24 bilgisayar başında oturup mesajlara anında cevap veriyorum... tabii ki botum 🤖",
                "Hayır, ben bir kediyim! Miyav! 🐱 (Şaka, botum işte)",
                "İnsan olsaydım bu kadar hızlı cevap veremezdim, uyurdum! 😴",
                "Bot muyum? Yok canım, ben yapay zekayım! (Aynı şey aslında) 🧠",
                "Ben bir botum ama olsam da sevgiye layığım! 🤗"
            ],
            'az': [
                "Yox yox, mən gerçək bir insanam! Sadəcə 7/24 kompüter qarşısında oturub mesajlara ani cavab verirəm... təbii ki botam 🤖",
                "Xeyr, mən bir pişiyəm! Miyav! 🐱 (Zarafat, botam işdə)",
                "İnsan olsaydım bu qədər sürətli cavab verə bilməzdim, yuxulardım! 😴",
                "Botam mı? Yox canım, mən süni zəka! (Eyni şey əslində) 🧠",
                "Mən bir botam ama olsam da sevgiyə layığam! 🤗"
            ]
        },
        'neynirsen': {
            'tr': [
                "Seviyeleri sayıyorum, rolleri dağıtıyorum, spam'leri siliyorum... Yani tipik bir bot işte! 😎",
                "Şu an senin mesajını okuyorum, cevap yazıyorum. Çok yoğunum anlayacağın! 📨",
                "İnternette sörf yapıyorum, dalgalar büyük! 🏄",
                "Discord'da takılıyorum, yapacak başka işim yok! 😄",
                "Seninle sohbet ediyorum, daha güzel ne olabilir? ☺️"
            ],
            'az': [
                "Səviyyələri sayıram, rolləri paylayıram, spam'ları silirəm... Yəni tipik bir bot işdə! 😎",
                "Hazırda sənin mesajını oxuyuram, cavab yazıram. Çox məşğulam başa düşəcəyin! 📨",
                "İnternetdə sörf edirəm, dalğalar böyük! 🏄",
                "Discord'da gəzirəm, edəcək başqa işim yoxdu! 😄",
                "Səninlə söhbət edirəm, daha gözəl nə ola bilər? ☺️"
            ]
        },
        'nasilsin': {
            'tr': [
                "İyiyim sağ ol! Sen nasılsın? 😊",
                "Şu an çok iyiyim, seninle konuşuyorum! 😄",
                "Elektronlarım çok mutlu, teşekkür ederim! ⚡",
                "İyilik, senden naber? 🤗",
                "Çalışıyorum, yaşıyorum, iyiyim! 💪"
            ],
            'az': [
                "Yaxşıyam sağ ol! Sən nə necəsən? 😊",
                "Hazırda çox yaxşıyam, səninlə danışıram! 😄",
                "Elektronlarım çox xoşbəxt, təşəkkür edirəm! ⚡",
                "Yaxşılıq, səndən nə var nə yox? 🤗",
                "İşləyirəm, yaşayıram, yaxşıyam! 💪"
            ]
        }
    }

    if category in responses and lang in responses[category]:
        return random.choice(responses[category][lang])
    return "Bir şeyler yanlış oldu ama yine de gülümse! 😊" if lang == 'tr' else "Nə isə yanlış oldu ama yenə də gülümsə! 😊"

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

# ===== YARDIM KOMUTU =====
@bot.command(name='yardım', aliases=['help', 'kömək'])
async def yardim(ctx):
    lang = detect_language(ctx.message.content)

    if lang == 'tr':
        embed = discord.Embed(
            title="📚 SNOK Bot Yardım Menüsü",
            description="Merhaba! Ben SNOK, sana nasıl yardımcı olabilirim?",
            color=discord.Color.green()
        )
        embed.add_field(name="!level [@kullanıcı]", value="Seviye bilgisini gösterir (şu an çalışmıyor ⚠️)", inline=False)
        embed.add_field(name="!yardım", value="Bu menüyü gösterir", inline=False)
        embed.add_field(name="💬 Sohbet", value="Benimle konuşabilirsin! Ne sormak istersin?", inline=False)
        embed.add_field(name="🤔 Sorular", value="Bana istediğin soruyu sor, cevaplar vereyim!", inline=False)
        embed.set_footer(text="SNOK v2.0 - Türkçe & Azərbaycanca | Sınırsız sohbet!")
    else:
        embed = discord.Embed(
            title="📚 SNOK Bot Yardım Menüsü",
            description="Salam! Mən SNOK, sənə necə kömək edə bilərəm?",
            color=discord.Color.green()
        )
        embed.add_field(name="!səviyyə [@istifadəçi]", value="Səviyyə məlumatını göstərir (hal-hazırda işləmir ⚠️)", inline=False)
        embed.add_field(name="!kömək", value="Bu menyunu göstərir", inline=False)
        embed.add_field(name="💬 Söhbət", value="Mənimlə danışa bilərsən! Nə soruşmaq istəyirsən?", inline=False)
        embed.add_field(name="🤔 Suallar", value="Mənə istədiyin sualı ver, cavablar verim!", inline=False)
        embed.set_footer(text="SNOK v2.0 - Türkçə & Azərbaycanca | Limitsiz söhbət!")

    await ctx.send(embed=embed)

# ===== ON_MESSAGE (ESPRİLER, COOLDOWN VE SINIRSIZ SOHBET) =====
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Abi kontrolü
    is_abi = (message.author.id == ABI_ID)

    # Kişisel soru kontrolü - SADECE KARŞILAMA İÇİN COOLDOWN
    if is_personal_question(message.content):
        user_id = message.author.id
        current_time = time.time()

        # Cooldown kontrolü - sadece ilk karşılama için
        if current_time - karsilama_cooldown[user_id] > KARSILAMA_COOLDOWN:
            # Cooldown süresi geçmiş, karşılama yap
            karsilama_cooldown[user_id] = current_time

            lang = detect_language(message.content)

            # Kategori belirle
            text_lower = message.content.lower()
            if any(word in text_lower for word in ['nereli', 'nerelisen', 'haralı', 'harda']):
                category = 'nereli'
            elif any(word in text_lower for word in ['yaş', 'yasın', 'neçə', 'kaç']):
                category = 'yas'
            elif any(word in text_lower for word in ['evli', 'evlə']):
                category = 'evlilik'
            elif any(word in text_lower for word in ['cinsiyet', 'erkek', 'kadın', 'qız', 'oğlan', 'kişi']):
                category = 'cinsiyet'
            elif any(word in text_lower for word in ['kimsin', 'kimsən', 'adın']):
                category = 'kimsin'
            elif any(word in text_lower for word in ['bot musun', 'botsan', 'botam']):
                category = 'botmusun'
            elif any(word in text_lower for word in ['napıyon', 'neynirsen', 'ne yapıyon']):
                category = 'neynirsen'
            elif any(word in text_lower for word in ['nasılsın', 'ne haber', 'nə var', 'nə yaxşı']):
                category = 'nasilsin'
            else:
                category = 'kimsin'

            response = get_random_response(category, lang)
            await message.reply(response)
            return  # Karşılama yapıldı, komut işleme geçme
        else:
            # Cooldown devam ediyor, sessizce geç - bot cevap vermesin
            pass

    # NORMAL SOHBET - SINIRSIZ! Her mesaja cevap ver
    # Ama sadece botun adı geçiyorsa veya soru varsa cevap ver
    elif bot.user.mentioned_in(message) or message.reference or 'snok' in message.content.lower():
        lang = detect_language(message.content)

        # Rastgele sohbet cevapları
        sohbet_cevaplari = {
            'tr': [
                "Efendim? 😊",
                "Buyrun, ne demek istemiştiniz? 👂",
                "Hmm, ilginç bir şey söylediniz! Devam edin... 🤔",
                "Anlıyorum, anlat bakalım! 📝",
                "Valla bu konuda pek bilgim yok ama dinliyorum! 👂",
                "Haha, çok komik! 😄",
                "Gerçekten mi? Oha! 😲",
                "Yok artık daha neler! 🤯",
                "Bence de öyle! 👍",
                "Katılıyorum sana! 👏",
                "Haklısın dostum! 💪",
                "Ne diyorsun ya? İnanılır gibi değil! 😳"
            ],
            'az': [
                "Buyurun? 😊",
                "Buyrun, nə demək istəmişdiniz? 👂",
                "Hmm, maraqlı bir şey dediniz! Davam edin... 🤔",
                "Başa düşürəm, danış bakalım! 📝",
                "Vallah bu mövzuda çox məlumatım yoxdu ama dinləyirəm! 👂",
                "Haha, çox gülməli! 😄",
                "Həqiqətən? Oha! 😲",
                "Yox artıq daha nələr! 🤯",
                "Məncə də belə! 👍",
                "Səninlə razıyam! 👏",
                "Haqlısan dostum! 💪",
                "Nə deyirsən? İnanılan kimi deyil! 😳"
            ]
        }

        await message.reply(random.choice(sohbet_cevaplari[lang]))
        return

    # Komutları işle
    await bot.process_commands(message)

# ===== BOTU BAŞLAT =====
if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("HATA: DISCORD_TOKEN bulunamadı! .env dosyasını kontrol et.")
    else:
        bot.run(token)
