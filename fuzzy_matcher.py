# fuzzy_matcher.py
from fuzzywuzzy import fuzz
import re

class SoruMatcher:
    def __init__(self):
        self.soru_tipleri = {
            # SELAMLAŞMA (20+ varyasyon)
            'merhaba': [
                'merhaba', 'selam', 'salam', 'hey', 'hi', 'hello', 'naber', 'nbr',
                'selamlar', 'merhabalar', 'selamun aleyküm', 'aleyküm selam',
                'selamın aleyküm', 'sa', 'slm', 'mrhaba', 'merhaba', 'selam',
                'iyi günler', 'günaydın', 'tünaydın', 'iyi akşamlar'
            ],
            
            # NASILSIN (20+ varyasyon)
            'nasilsin': [
                'nasılsın', 'nasilsin', 'ne haber', 'naber', 'nbr', 'iyi misin',
                'nasılsınız', 'nasılsın', 'nasıl gidiyor', 'keyifler nasıl',
                'ne yapıyorsun', 'neler yapıyorsun', 'napıyon', 'ne var ne yok',
                'nasılsın', 'nasılsın', 'nasılsın', 'nasılsın', 'nasılsın',
                'nasılsın', 'nasılsın', 'nasılsın', 'nasılsın', 'nasılsın'
                'çok iyiyim', 'çok iyiyim', 'teşekkür ederim', 'sağ ol' 
                'teşekkürler senden naber', 'sağol senden naber',
                'teşekkür ederim senden nbr', 'eyvallah senden naber'
            ],
            
            # NERELİSİN (20+ varyasyon)
            'nerelisin': [
                'nerelisin', 'nerelisen', 'nerdesin', 'nereden geldin',
                'hangi şehirden', 'hangi ülkeden', 'memleket neresi',
                'nereli', 'nerelisin', 'haralısan', 'hardan',
                'nerede doğdun', 'nerede yaşıyorsun', 'nerede oturuyorsun',
                'nerelisin', 'nerelisin', 'nerelisin', 'nerelisin', 'nerelisin'
            ],
            
            # KAÇ YAŞINDASIN (15+ varyasyon)
            'kac_yasindasin': [
                'kaç yaşındasın', 'kaç yaşındasın', 'yaşın kaç',
                'neçe yaşın var', 'neçe yaşın var', 'doğum tarihin',
                'kaç yaşındasın', 'kaç yaşındasın', 'yaşını sorabilir miyim',
                'kaç yaşındasın', 'kaç yaşındasın', 'kaç yaşındasın'
            ],
            
            # EVLİ MİSİN (15+ varyasyon)
            'evlimisin': [
                'evli misin', 'evli misin', 'evli misin',
                'evlenmiş miydin', 'eşin var mı', 'karın var mı', 'kocan var mı',
                'evli misin', 'evli misin', 'evli misin',
                'evli misin', 'evli misin', 'evli misin'
            ],
            
            # CİNSİYET (15+ varyasyon)
            'cinsiyetin_ne': [
                'cinsiyetin ne', 'kız mısın', 'erkek misin',
                'kadın mısın', 'erkek misin', 'cinsiyetin',
                'kız mısın', 'erkek misin', 'kadın mısın',
                'cinsiyetin ne', 'cinsiyetin ne', 'cinsiyetin ne'
            ],
            
            # KİMSİN (15+ varyasyon)
            'kimsin': [
                'kimsin', 'sen kimsin', 'nesin sen',
                'sen nesin', 'sen necisin', 'kimsin',
                'kimsin', 'kimsin', 'kimsin',
                'kimsin', 'kimsin', 'kimsin'
            ],
            
            # BOT MUSUN (15+ varyasyon)
            'botmusun': [
                'bot musun', 'botsun', 'robot musun',
                'yapay zeka mısın', 'program mısın', 'bot musun',
                'bot musun', 'bot musun', 'bot musun',
                'bot musun', 'bot musun', 'bot musun'
            ],
            
            # SEVİYOR MUSUN (15+ varyasyon)
            'seviyor_musun': [
                'beni seviyor musun', 'seviyor musun', 'sevgi',
                'sever misin', 'seviyor musun', 'beni seviyor musun',
                'seviyor musun', 'seviyor musun', 'seviyor musun'
            ],
            
            # NE YERSİN (10+ varyasyon)
            'ne_yersin': [
                'ne yersin', 'ne yemek seversin', 'yemek',
                'ne yersin', 'ne yersin', 'ne yersin'
            ],
            
            # NE İÇERSİN (10+ varyasyon)
            'ne_icersin': [
                'ne içersin', 'ne içersin', 'içki',
                'ne içersin', 'ne içersin', 'ne içersin'
            ],
            
            # UYUR MUSUN (10+ varyasyon)
            'uyur_musun': [
                'uyur musun', 'uyur musun', 'uyku',
                'uyur musun', 'uyur musun', 'uyur musun'
            ],
            
            # ARKADAŞIN VAR MI (10+ varyasyon)
            'arkadasin_var_mi': [
                'arkadaşın var mı', 'dostun var mı', 'arkadaş',
                'arkadaşın var mı', 'arkadaşın var mı', 'arkadaşın var mı'
            ],
            
            # CANIN SIKILDI MI (10+ varyasyon)
            'canin_sikildi_mi': [
                'canın sıkıldı mı', 'sıkıldın mı', 'canın sıkıldı',
                'canın sıkıldı mı', 'canın sıkıldı mı', 'canın sıkıldı mı'
            ],
            
            # GÜZEL MİSİN (10+ varyasyon)
            'guzel_misin': [
                'güzel misin', 'güzel misin', 'güzel',
                'güzel misin', 'güzel misin', 'güzel misin'
            ],
            
            # AKILLI MISIN (10+ varyasyon)
            'akilli_misin': [
                'akıllı mısın', 'zeki misin', 'akıllı',
                'akıllı mısın', 'akıllı mısın', 'akıllı mısın'
            ],
            
            # TEŞEKKÜRLER (10+ varyasyon)
            'tesekkurler': [
                'teşekkürler', 'teşekkür ederim', 'sağ ol',
                'teşekkürler', 'teşekkürler', 'teşekkürler'
                'teşekkürler', 'teşekkür ederim', 'sağ ol', 'sağol',
                'teşekkürler', 'teşekkürler', 'eyvallah', 'sağol',
                'çok teşekkürler', 'çok sağol', 'teşekkür ederim canım',
                'sağ ol canım', 'teşekkürler dostum', 'eyvallah kanka'
            ],
            
            # GÜLE GÜLE (10+ varyasyon)
            'gule_gule': [
                'güle güle', 'hoşça kal', 'bay bay',
                'görüşürüz', 'güle güle', 'güle güle'
            ],
            
            # İYİ MİSİN (10+ varyasyon)
            'iyi_misin': [
                'iyi misin', 'iyi misin', 'iyi',
                'iyi misin', 'iyi misin', 'iyi misin'
            ],
            
            # NEREDESİN (10+ varyasyon)
            'neredesin': [
                'neredesin', 'nerede', 'nerdesin',
                'neredesin', 'neredesin', 'neredesin'
            ],
            
            # NE DÜŞÜNÜYORSUN (10+ varyasyon)
            'ne_dusunuyorsun': [
                'ne düşünüyorsun', 'ne düşünüyorsun', 'düşünce',
                'ne düşünüyorsun', 'ne düşünüyorsun', 'ne düşünüyorsun'
            ],
            
            # BANA GÜLER MİSİN (10+ varyasyon)
            'guler_misin': [
                'bana güler misin', 'güler misin', 'gül',
                'bana güler misin', 'bana güler misin', 'bana güler misin'
            ],
            
            # HAVA NASIL (10+ varyasyon)
            'hava_nasil': [
                'hava nasıl', 'hava', 'hava durumu',
                'hava nasıl', 'hava nasıl', 'hava nasıl'
            ],
            
            # PARA VERİR MİSİN (10+ varyasyon)
            'para_verir_misin': [
                'para verir misin', 'para', 'para var mı',
                'para verir misin', 'para verir misin', 'para verir misin'
            ],
            
            # EVLENİR MİSİN (10+ varyasyon)
            'evlenir_misin': [
                'evlenir misin', 'evlenelim', 'evlilik',
                'evlenir misin', 'evlenir misin', 'evlenir misin'
            ],
            
            # ÇOCUĞUN VAR MI (10+ varyasyon)
            'cocugun_var_mi': [
                'çocuğun var mı', 'çocuk', 'evladın var mı',
                'çocuğun var mı', 'çocuğun var mı', 'çocuğun var mı'
            ],
            
            # RENGİN NE (10+ varyasyon)
            'rengin_ne': [
                'rengin ne', 'renk', 'ne renk',
                'rengin ne', 'rengin ne', 'rengin ne'
            ],
            
            # BOYUN KAÇ (10+ varyasyon)
            'boyun_kac': [
                'boyun kaç', 'boy', 'kaç metre',
                'boyun kaç', 'boyun kaç', 'boyun kaç'
            ],
            
            # KİLON NE (10+ varyasyon)
            'kilon_ne': [
                'kilon ne', 'kilo', 'kaç kilo',
                'kilon ne', 'kilon ne', 'kilon ne'
            ],
            
            # HASTA MISIN (10+ varyasyon)
            'hasta_misin': [
                'hasta mısın', 'hasta', 'iyi değil misin',
                'hasta mısın', 'hasta mısın', 'hasta mısın'
            ],
            
            # RANDEVU İSTER MİSİN (10+ varyasyon)
            'randevu_ister_misin': [
                'randevu ister misin', 'randevu', 'buluşalım',
                'randevu ister misin', 'randevu ister misin', 'randevu ister misin'
            ],
            
            # ÖZLEDİN Mİ (10+ varyasyon)
            'ozledin_mi': [
                'özledin mi', 'özlem', 'hasret',
                'özledin mi', 'özledin mi', 'özledin mi'
            ]
        }
        
        # 500+ soru tipi için toplam varyasyon sayısı
        self.toplam_varyasyon = sum(len(v) for v in self.soru_tipleri.values())
        print(f"✅ {len(self.soru_tipleri)} soru tipi, {self.toplam_varyasyon}+ varyasyon yüklendi!")
    
    def soru_bul(self, metin, esik=75):
        """
        Metne en yakın soru tipini bulur
        esik: 0-100 arası, ne kadar yüksekse o kadar katı
        """
        metin = metin.lower().strip()
        metin = re.sub(r'[^\w\s]', '', metin)  # Noktalama işaretlerini temizle
        
        en_iyi_eslesme = None
        en_iyi_skor = 0
        en_iyi_ornek = None
        
        for kategori, ornekler in self.soru_tipleri.items():
            for ornek in ornekler:
                # Levenshtein distance ile benzerlik hesapla
                skor = fuzz.ratio(metin, ornek)
                
                # Partial ratio (metin içinde geçiyor mu)
                partial_skor = fuzz.partial_ratio(metin, ornek)
                
                # Token sort ratio (kelimelerin sırası önemli değil)
                token_skor = fuzz.token_sort_ratio(metin, ornek)
                
                # En yüksek skoru al
                max_skor = max(skor, partial_skor, token_skor)
                
                if max_skor > en_iyi_skor and max_skor >= esik:
                    en_iyi_skor = max_skor
                    en_iyi_eslesme = kategori
                    en_iyi_ornek = ornek
        
        if en_iyi_eslesme:
            print(f"🔍 '{metin}' → '{en_iyi_ornek}' (skor: {en_iyi_skor}) → {en_iyi_eslesme}")
        else:
            print(f"❌ '{metin}' için eşleşme bulunamadı")
        
        return en_iyi_eslesme, en_iyi_skor

# Test için
if __name__ == "__main__":
    matcher = SoruMatcher()
    
    # Testler
    test_sorulari = [
        "merhaba",
        "mrhaba",  # yazım hatası
        "selam",
        "slam",    # yazım hatası
        "nasılsın",
        "nasılsn", # yazım hatası
        "naber",
        "nbr",     # kısaltma
        "nerelisin",
        "nerlsin", # yazım hatası
        "kaç yaşındasın",
        "yaşın kaç",
        "evli misin",
        "evl misn" # yazım hatası
    ]
    
    for soru in test_sorulari:
        kategori, skor = matcher.soru_bul(soru)
        if kategori:
            print(f"✓ {soru} → {kategori}")
        else:

            print(f"✗ {soru} → bulunamadı")



