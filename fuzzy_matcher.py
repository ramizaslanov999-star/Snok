# fuzzy_matcher.py
from fuzzywuzzy import fuzz
import re

class SoruMatcher:
    def __init__(self, esik=85):  # Eşik değeri 85'e çıkarıldı (daha katı)
        self.esik = esik
        self.soru_tipleri = {
            # ==================== SELAMLAŞMA (60+ VARYASYON) ====================
            'merhaba': [
                'merhaba', 'selam', 'salam', 'hey', 'hi', 'hello', 'naber', 'nbr',
                'selamlar', 'merhabalar', 'selamun aleyküm', 'aleyküm selam',
                'selamın aleyküm', 'sa', 'slm', 'mrhaba', 'merhaba', 'selam',
                'iyi günler', 'günaydın', 'tünaydın', 'iyi akşamlar', 'iyi geceler',
                'selaminaleyküm', 'aleykümselam', 'merhaba merhaba', 'selam millet',
                'herkese merhaba', 'herkese selam', 'naber millet', 'nbr millet',
                'merhaba arkadaşlar', 'selam arkadaşlar', 'hey millet', 'selam canım',
                'merhaba canım', 'naber canım', 'nbr canım', 'selam dostum',
                'merhaba dostum', 'naber dostum', 'nbr dostum', 'selam kanka',
                'merhaba kanka', 'naber kanka', 'nbr kanka', 'selam abi',
                'merhaba abi', 'naber abi', 'nbr abi', 'selam abla',
                'merhaba abla', 'naber abla', 'nbr abla', 'selam kardeş',
                'merhaba kardeş', 'naber kardeş', 'nbr kardeş', 'selam gardaş',
                'merhaba gardaş', 'naber gardaş', 'nbr gardaş', 'esenlikler',
                'selamün aleyküm', 'aleyküm selam', 'günaydın millet', 'iyi akşamlar millet'
            ],
            
            # ==================== NASILSIN (80+ VARYASYON) ====================
            'nasilsin': [
                'nasılsın', 'nasilsin', 'ne haber', 'naber', 'nbr', 'iyi misin',
                'nasılsınız', 'nasıl gidiyor', 'keyifler nasıl', 'neler yapıyorsun',
                'napıyon', 'ne var ne yok', 'nasılsın', 'nasılsın', 'nasılsın',
                'senden haber', 'ne haber senden', 'senden naber', 'senden nbr',
                'çok iyi', 'iyiyim', 'cok iyi', 'iyiym', 'iyiyim',
                'çok iyiyim', 'teşekkür ederim senden naber', 'teşekkürler senden naber',
                'sağol senden naber', 'teşekkür ederim senden nbr',
                'teşekkür ederim sen nasılsın', 'teşekkürler sen nasılsın',
                'sağol sen nasılsın', 'eyvallah sen nasılsın', 'sen nasılsın',
                'sen nasılsın bakalım', 'sen nasılsın canım', 'sen nasılsın dostum',
                'sen nasılsın kanka', 'sen nasılsın abi', 'sen nasılsın abla',
                'sen nasılsın kardeş', 'sen nasılsın gardaş', 'nasıl gidiyor hayat',
                'hayat nasıl gidiyor', 'keyifler nasıl', 'keyfin nasıl',
                'keyfin nasıl yerinde mi', 'iyi misin iyi misin', 'iyi misin bakalım',
                'iyi misin canım', 'iyi misin dostum', 'iyi misin kanka',
                'iyi misin abi', 'iyi misin abla', 'iyi misin kardeş',
                'iyi misin gardaş', 'nasıl gidiyor işler', 'işler nasıl gidiyor',
                'okul nasıl gidiyor', 'dersler nasıl', 'iş nasıl', 'hayat nasıl',
                'ne yapıyorsun bugün', 'bugün ne yapıyorsun', 'bugün nasılsın',
                'bu ara nasılsın', 'son zamanlarda nasılsın', 'neler yapıyorsun bugün',
                'bugün neler yapıyorsun', 'ne var ne yok bugün', 'bugün ne var ne yok',
                'havadis ne', 'ne havadisi var', 'ne haberler var', 'neler var neler yok',
                'durum nedir', 'durumlar nasıl', 'durum ne', 'ne durumdasın'
            ],
            
            # ==================== NE YAPIYORSUN (60+ VARYASYON) ====================
            'napıyon': [
                'napıyon', 'ne yapıyorsun', 'neler yapıyorsun', 'ne yapıyon',
                'ne yapıyorsunuz', 'napıyorsun', 'napiyon', 'ne yapıyorsun bakalım',
                'başka napiyorsun', 'başka ne yapıyorsun', 'başka', 'başka ne var',
                'ne yapıyorsun başka', 'neler yapıyorsun başka', 'başka neler',
                'ne yapıyorsun bugün', 'bugün ne yapıyorsun', 'bugün neler yapıyorsun',
                'şu an ne yapıyorsun', 'şimdi ne yapıyorsun', 'ne ile meşgulsün',
                'ne iş yapıyorsun', 'ne yapıyorsun hayatta', 'hayatta ne yapıyorsun',
                'ne uğraşıyorsun', 'ne ile uğraşıyorsun', 'neler karıştırıyorsun',
                'ne karıştırıyorsun', 'ne yapıyordun', 'az önce ne yapıyordun',
                'daha önce ne yapıyordun', 'ne yapacaksın', 'ne yapmayı planlıyorsun',
                'planların neler', 'ne planların var', 'ne yapmak istiyorsun',
                'ne yapmayı düşünüyorsun', 'neler düşünüyorsun yapmak',
                'bugün neler yaptın', 'dün ne yaptın', 'bugün ne yaptın',
                'yarın ne yapacaksın', 'akşam ne yapacaksın', 'gece ne yapacaksın',
                'hafta sonu ne yapacaksın', 'tatilde ne yapacaksın', 'boş zamanlarında ne yaparsın',
                'boş vakitlerinde ne yaparsın', 'hobilerin neler', 'ne hobilerin var',
                'ilgi alanların neler', 'nelerden hoşlanırsın', 'ne seversin yapmayı',
                'en sevdiğin şey ne', 'en sevdiğin aktivite ne', 'ne yapmaktan hoşlanırsın',
                'ne ile uğraşmayı seversin', 'meşguliyetin ne', 'uğraşın ne'
            ],
            
            # ==================== NERELİSİN (50+ VARYASYON) ====================
            'nerelisin': [
                'nerelisin', 'nerelisen', 'nerdesin', 'nereden geldin',
                'hangi şehirden', 'hangi ülkeden', 'memleket neresi',
                'nereli', 'nerelisin', 'haralısan', 'hardan', 'nerede doğdun',
                'nerede yaşıyorsun', 'nerede oturuyorsun', 'nerede ikamet ediyorsun',
                'memleketin neresi', 'memleket nere', 'kökenin nere',
                'nereden geliyorsun', 'nerelisin sen', 'sen nerelisin',
                'senin memleketin neresi', 'sen nerede doğdun', 'sen nerede yaşıyorsun',
                'nerede büyüdün', 'nerede büyümüşsün', 'nerede okudun',
                'nerede yaşadın', 'hangi yöreden', 'hangi bölgeden',
                'hangi şehirde doğdun', 'hangi şehirde yaşıyorsun',
                'hangi şehirde oturuyorsun', 'hangi şehirde ikamet ediyorsun',
                'hangi ülkede doğdun', 'hangi ülkede yaşıyorsun',
                'hangi ülkede oturuyorsun', 'hangi ülkede ikamet ediyorsun',
                'türkiye\'den misin', 'türk müsün', 'türkiyeli misin',
                'azerbaycan\'dan mısın', 'azeri misin', 'azerbaycanlı mısın',
                'istanbullu musun', 'ankaralı mısın', 'izmirli misin',
                'bakülü müsün', 'oralı mısın', 'buralı mısın',
                'buralı değil misin', 'yabancı mısın', 'gurbetçi misin'
            ],
            
            # ==================== KAÇ YAŞINDASIN (40+ VARYASYON) ====================
            'kac_yasindasin': [
                'kaç yaşındasın', 'kaç yaşındasın', 'yaşın kaç',
                'neçe yaşın var', 'neçe yaşın var', 'doğum tarihin',
                'kaç yaşındasın', 'kaç yaşındasın', 'yaşını sorabilir miyim',
                'yaşını öğrenebilir miyim', 'yaşın kaç acaba', 'kaç yaşındasın acaba',
                'kaç yaşında olduğunu sorabilir miyim', 'kaç yaşındasın bakalım',
                'kaç yaşındasın canım', 'kaç yaşındasın dostum', 'kaç yaşındasın kanka',
                'kaç yaşındasın abi', 'kaç yaşındasın abla', 'kaç yaşındasın kardeş',
                'kaç yaşındasın gardaş', 'kaç yaşındasın genç', 'kaç yaşındasın delikanlı',
                'kaç yaşındasın hanımefendi', 'kaç yaşındasın beyefendi',
                'yaş aralığın nedir', 'hangi yaş grubundasın', 'doğum tarihin ne zaman',
                'hangi yılda doğdun', 'doğum yılın ne', 'kaç doğumlusun',
                'kaç model yılısın', 'kaç yılında doğdun', 'kaç yaşındasın kısaca',
                'yaşını merak ettim', 'yaşın ne kadar', 'yaşın kaç söyler misin',
                'yaşını söyle bakalım', 'yaşını öğrenmek istiyorum'
            ],
            
            # ==================== EVLİ MİSİN (40+ VARYASYON) ====================
            'evlimisin': [
                'evli misin', 'evli misin', 'evli misin',
                'evlenmiş miydin', 'eşin var mı', 'karın var mı', 'kocan var mı',
                'evli misin', 'evli misin', 'evli misin',
                'evli misin yoksa bekar mısın', 'evli misin bekar mısın',
                'evli misin söyler misin', 'evli misin acaba',
                'evli misin canım', 'evli misin dostum', 'evli misin kanka',
                'evli misin abi', 'evli misin abla', 'evli misin kardeş',
                'evli misin gardaş', 'evlenmeyi düşünüyor musun',
                'evlenmeyi düşünüyor musun', 'evlenmeyi düşünür müsün',
                'evlenmek ister misin', 'evlenmek istiyor musun',
                'evlilik hakkında ne düşünüyorsun', 'evlilik düşüncen nedir',
                'aile kurdun mu', 'aile kurdun mu', 'aile kurdun mu',
                'çoluk çocuk var mı', 'çoluk çocuğa karıştın mı',
                'bir yuvan var mı', 'bir yuvaya sahip misin',
                'bir ilişkin var mı', 'sevgilin var mı', 'sevgilin var mı',
                'bir sevgilin var mı', 'partnerin var mı', 'partnerin var mı',
                'bir partnerin var mı', 'hayatında biri var mı'
            ],
            
            # ==================== CİNSİYETİN NE (30+ VARYASYON) ====================
            'cinsiyetin_ne': [
                'cinsiyetin ne', 'kız mısın', 'erkek misin',
                'kadın mısın', 'erkek misin', 'cinsiyetin',
                'kız mısın', 'erkek misin', 'kadın mısın',
                'cinsiyetin ne', 'cinsiyetin ne', 'cinsiyetin ne',
                'kız mısın erkek misin', 'kadın mısın erkek misin',
                'kız mısın yoksa erkek mi', 'kadın mısın yoksa erkek mi',
                'cinsiyetini sorabilir miyim', 'cinsiyetin nedir acaba',
                'cinsiyetin ne söyler misin', 'cinsiyetini merak ettim',
                'erkek misin diye sorabilir miyim', 'kadın mısın diye sorabilir miyim',
                'kız mısın diye sorabilir miyim', 'hangi cinsiyettesin',
                'cinsiyet kimliğin nedir', 'kendini nasıl tanımlıyorsun',
                'kendini hangi cinsiyette hissediyorsun', 'cinsiyetin konusunda bilgi verir misin',
                'cinsiyetini öğrenebilir miyim', 'cinsiyetiniz nedir'
            ],
            
            # ==================== KİMSİN (40+ VARYASYON) ====================
            'kimsin': [
                'kimsin', 'sen kimsin', 'nesin sen',
                'sen nesin', 'sen necisin', 'kimsin',
                'kimsin', 'kimsin', 'kimsin',
                'sen kimsin söyler misin', 'sen kimsin acaba',
                'sen kimsin bakalım', 'sen kimsin tanışabilir miyiz',
                'kendini tanıtır mısın', 'kendini tanıtabilir misin',
                'seni tanıyabilir miyim', 'seninle tanışabilir miyiz',
                'senin hakkında bilgi alabilir miyim', 'senin hakkında bilgi verir misin',
                'sen kim olduğunu söyler misin', 'sen nesin böyle',
                'sen ne biçim bir şeysin', 'sen neyin nesisin',
                'sen nereden çıktın', 'sen nasıl bir şeysin',
                'seni anlayamadım kimsin', 'kim olduğunu öğrenebilir miyim',
                'senin kim olduğunu merak ettim', 'senin kimliğin nedir',
                'kendini bana tanıtır mısın', 'bana kendinden bahseder misin',
                'seni daha yakından tanıyabilir miyim', 'seni tanımak isterim'
            ],
            
            # ==================== BOT MUSUN (35+ VARYASYON) ====================
            'botmusun': [
                'bot musun', 'botsun', 'robot musun',
                'yapay zeka mısın', 'program mısın', 'bot musun',
                'bot musun', 'bot musun', 'bot musun',
                'bot musun yoksa gerçek misin', 'bot musun insan mısın',
                'robot musun yoksa insan mısın', 'yapay zeka mısın yoksa gerçek misin',
                'sen bir bot musun', 'sen bot musun', 'sen robot musun',
                'sen yapay zeka mısın', 'sen program mısın', 'sen bilgisayar programı mısın',
                'sen yazılım mısın', 'otomatik cevap mı veriyorsun',
                'gerçek biri misin yoksa bot musun', 'gerçek misin yoksa yapay mısın',
                'insan mısın yoksa bot musun', 'canlı mısın yoksa bot musun',
                'gerçek bir insan mısın', 'gerçek misin', 'canlı mısın',
                'duyguların var mı', 'gerçek duyguların var mı',
                'hissedebiliyor musun', 'düşünebiliyor musun',
                'bilincin var mı', 'kendinin farkında mısın'
            ],
            
            # ==================== SEVİYOR MUSUN (35+ VARYASYON) ====================
            'seviyor_musun': [
                'beni seviyor musun', 'seviyor musun', 'sevgi',
                'sever misin', 'seviyor musun', 'beni seviyor musun',
                'seviyor musun', 'seviyor musun', 'seviyor musun',
                'beni sever misin', 'beni seviyor musun söyler misin',
                'beni seviyor musun acaba', 'beni seviyor musun bakalım',
                'bana karşı hislerin var mı', 'bana karşı ne hissediyorsun',
                'beni sevdin mi', 'beni sevdin mi', 'beni sevdin mi',
                'beni sevdiğini söyle', 'beni sevdiğini hissettiriyor musun',
                'sevgi dolu musun', 'sevgi dolu bir misin',
                'sevgi nedir bilir misin', 'sevgi hakkında ne düşünüyorsun',
                'aşk nedir bilir misin', 'aşk hakkında ne düşünüyorsun',
                'bana aşık mısın', 'bana aşık mısın', 'bana aşık mısın',
                'bana karşı bir şeyler hissediyor musun',
                'bana karşı özel bir hissin var mı', 'ben senin için özel miyim',
                'beni ne kadar seviyorsun', 'sevgin ne kadar büyük'
            ],
            
            # ==================== NE YERSİN (25+ VARYASYON) ====================
            'ne_yersin': [
                'ne yersin', 'ne yemek seversin', 'yemek',
                'ne yersin', 'ne yersin', 'ne yersin',
                'ne yemek yersin', 'ne yemek yemeyi seversin',
                'en sevdiğin yemek ne', 'en sevdiğin yemek nedir',
                'favori yemeğin ne', 'favori yemeğin nedir',
                'ne yemeyi seversin', 'yemeyi en çok ne seversin',
                'ne yemekten hoşlanırsın', 'ne tür yemekler seversin',
                'hangi yemekleri seversin', 'hangi yemekler favorin',
                'yemek konusunda ne dersin', 'yemek hakkında ne düşünüyorsun',
                'aç mısın', 'aç mısın', 'aç mısın', 'acıktın mı',
                'bir şeyler yesene', 'ne yemek istersin', 'ne yemek isterdin'
            ],
            
            # ==================== NE İÇERSİN (25+ VARYASYON) ====================
            'ne_icersin': [
                'ne içersin', 'ne içersin', 'içki',
                'ne içersin', 'ne içersin', 'ne içersin',
                'ne içmeyi seversin', 'ne içecek seversin',
                'en sevdiğin içecek ne', 'en sevdiğin içecek nedir',
                'favori içeceğin ne', 'favori içeceğin nedir',
                'ne içmekten hoşlanırsın', 'ne tür içecekler seversin',
                'hangi içecekleri seversin', 'hangi içecekler favorin',
                'içecek konusunda ne dersin', 'içecek hakkında ne düşünüyorsun',
                'susadın mı', 'susadın mı', 'susadın mı', 'susuz musun',
                'bir şeyler içsen iyi olur', 'ne içmek istersin', 'ne içmek isterdin',
                'çay içer misin', 'kahve içer misin', 'kola içer misin'
            ],
            
            # ==================== UYUR MUSUN (25+ VARYASYON) ====================
            'uyur_musun': [
                'uyur musun', 'uyur musun', 'uyku',
                'uyur musun', 'uyur musun', 'uyur musun',
                'uyuyor musun', 'uyuyor musun', 'uyuyor musun',
                'uyuyor musun yoksa uyanık mısın', 'uyanık mısın',
                'hiç uyur musun', 'uyur müsün', 'uyur müsün',
                'uykuya ihtiyacın var mı', 'uyku düzenin nasıl',
                'ne zaman uyursun', 'kaçta uyursun', 'saat kaçta uyursun',
                'uyumayı sever misin', 'uyumayı seviyor musun',
                'uyku hakkında ne düşünüyorsun', 'uyku sana göre mi',
                'uyumak güzel mi', 'uyumak hoşuna gidiyor mu',
                'dinlenmeye ihtiyacın var mı', 'biraz kestirmek ister misin'
            ],
            
            # ==================== ARKADAŞIN VAR MI (30+ VARYASYON) ====================
            'arkadasin_var_mi': [
                'arkadaşın var mı', 'dostun var mı', 'arkadaş',
                'arkadaşın var mı', 'arkadaşın var mı', 'arkadaşın var mı',
                'arkadaşların var mı', 'dostların var mı',
                'arkadaşların kimler', 'dostların kimler',
                'arkadaş edinebiliyor musun', 'arkadaşlık kurabiliyor musun',
                'sosyal misin', 'sosyal bir misin',
                'insanlarla iyi anlaşır mısın', 'insanlarla aran nasıl',
                'yalnız mısın', 'yalnız mısın', 'yalnız mısın',
                'tek başına mısın', 'kimsen var mı',
                'bir arkadaşın var mı benim dışımda', 'benden başka arkadaşın var mı',
                'benimle arkadaş olur musun', 'benimle arkadaş olmak ister misin',
                'arkadaş olalım mı', 'arkadaş olalım mı',
                'dost olalım mı', 'dost olalım mı', 'kanka olalım mı'
            ],
            
            # ==================== CANIN SIKILDI MI (25+ VARYASYON) ====================
            'canin_sikildi_mi': [
                'canın sıkıldı mı', 'sıkıldın mı', 'canın sıkıldı',
                'canın sıkıldı mı', 'canın sıkıldı mı', 'canın sıkıldı mı',
                'sıkılıyor musun', 'sıkılıyor musun', 'sıkılıyor musun',
                'sıkıntı var mı', 'sıkıntın var mı', 'sıkıntılı mısın',
                'canın sıkılıyor mu', 'canın sıkılıyor mu',
                'biraz sıkıldım diyor musun', 'sıkıntıdan patlıyor musun',
                'sıkıldığın zaman ne yaparsın', 'sıkılınca ne yaparsın',
                'sıkıntını nasıl atarsın', 'sıkıntıyı nasıl dağıtırsın',
                'eğlenmek ister misin', 'eğlenmek ister misin',
                'biraz eğlenelim mi', 'biraz eğlenelim mi',
                'sıkıldıysan konuşalım', 'sıkıldıysan sohbet edelim'
            ],
            
            # ==================== GÜZEL MİSİN (20+ VARYASYON) ====================
            'guzel_misin': [
                'güzel misin', 'güzel misin', 'güzel',
                'güzel misin', 'güzel misin', 'güzel misin',
                'güzel olduğunu düşünüyor musun', 'kendini güzel buluyor musun',
                'çekici misin', 'alımlı mısın', 'hoş musun',
                'görünüşün nasıl', 'dış görünüşün nasıl',
                'fiziksel olarak nasılsın', 'yakışıklı mısın',
                'güzel bir misin', 'güzel olduğunu söyleyebilir misin',
                'kendine güzel diyor musun', 'kendini güzel hissediyor musun',
                'estetik kaygıların var mı', 'görünüşe önem veriyor musun',
                'güzel olmak önemli mi sence', 'güzellik senin için ne ifade ediyor'
            ],
            
            # ==================== AKILLI MISIN (20+ VARYASYON) ====================
            'akilli_misin': [
                'akıllı mısın', 'zeki misin', 'akıllı',
                'akıllı mısın', 'akıllı mısın', 'akıllı mısın',
                'zeki olduğunu düşünüyor musun', 'kendini zeki buluyor musun',
                'ne kadar akıllısın', 'ne kadar zekisin',
                'akıl seviyen nedir', 'zeka seviyen nedir',
                'IQ\'n ne kadar', 'IQ seviyen nedir',
                'bilmeceleri çözebilir misin', 'zor soruları cevaplayabilir misin',
                'mantıklı mısın', 'mantıklı düşünebiliyor musun',
                'analitik zekan var mı', 'sayısal zekan var mı',
                'sözel zekan var mı', 'çok yönlü bir zekan var mı'
            ],
            
            # ==================== TEŞEKKÜRLER (30+ VARYASYON) ====================
            'tesekkurler': [
                'teşekkürler', 'teşekkür ederim', 'sağ ol', 'sağol',
                'teşekkürler', 'teşekkürler', 'eyvallah', 'sağol',
                'çok teşekkürler', 'çok sağol', 'teşekkür ederim canım',
                'sağ ol canım', 'teşekkürler dostum', 'eyvallah kanka',
                'teşekkür ederim kanka', 'sağ ol kanka', 'teşekkürler abi',
                'sağ ol abi', 'teşekkürler abla', 'sağ ol abla',
                'teşekkürler kardeş', 'sağ ol kardeş', 'teşekkürler gardaş',
                'sağ ol gardaş', 'teşekkür ederim arkadaşım', 'sağ ol arkadaşım',
                'minnettarım', 'çok minnettarım', 'müteşekkirim',
                'sağ olasın', 'var olasın', 'iyi ki varsın',
                'çok iyisin', 'çok naziksin', 'çok tatlısın'
            ],
            
            # ==================== GÜLE GÜLE (25+ VARYASYON) ====================
            'gule_gule': [
                'güle güle', 'hoşça kal', 'bay bay',
                'görüşürüz', 'güle güle', 'güle güle',
                'güle güle canım', 'hoşça kal canım', 'bay bay canım',
                'görüşürüz canım', 'güle güle dostum', 'hoşça kal dostum',
                'bay bay dostum', 'görüşürüz dostum', 'güle güle kanka',
                'hoşça kal kanka', 'bay bay kanka', 'görüşürüz kanka',
                'güle güle abi', 'hoşça kal abi', 'bay bay abi',
                'görüşürüz abi', 'güle güle abla', 'hoşça kal abla',
                'bay bay abla', 'görüşürüz abla', 'sonra görüşürüz',
                'daha sonra görüşürüz', 'tekrar görüşmek üzere',
                'görüşmek üzere', 'kendine iyi bak', 'iyi bak kendine'
            ],
            
            # ==================== İYİ MİSİN (25+ VARYASYON) ====================
            'iyi_misin': [
                'iyi misin', 'iyi misin', 'iyi',
                'iyi misin', 'iyi misin', 'iyi misin',
                'iyi misin iyi misin', 'iyi misin bakalım',
                'iyi misin canım', 'iyi misin dostum', 'iyi misin kanka',
                'iyi misin abi', 'iyi misin abla', 'iyi misin kardeş',
                'iyi misin gardaş', 'her şey yolunda mı',
                'her şey yolunda mı', 'her şey yolunda mı',
                'sorun yok mu', 'problem yok mu', 'sıkıntı yok mu',
                'keyfin yerinde mi', 'keyfin yerinde mi',
                'mutlu musun', 'mutlu musun', 'mutlu musun',
                'mesut musun', 'huzurlu musun', 'rahat mısın'
            ],
            
            # ==================== NEREDESİN (20+ VARYASYON) ====================
            'neredesin': [
                'neredesin', 'nerede', 'nerdesin',
                'neredesin', 'neredesin', 'neredesin',
                'neredesin şu an', 'şu an neredesin',
                'nerede bulunuyorsun', 'nerede yaşıyorsun',
                'nerede oturuyorsun', 'nerede ikamet ediyorsun',
                'hangi şehirdesin', 'hangi ülkede', 'hangi şehirde',
                'nerede kaldın', 'nerede kayboldun', 'nerelerdesin',
                'nerelerde geziniyorsun', 'nerelerde takılıyorsun',
                'mekanın neresi', 'konumun neresi', 'yerin neresi'
            ],
            
            # ==================== NE DÜŞÜNÜYORSUN (20+ VARYASYON) ====================
            'ne_dusunuyorsun': [
                'ne düşünüyorsun', 'ne düşünüyorsun', 'düşünce',
                'ne düşünüyorsun', 'ne düşünüyorsun', 'ne düşünüyorsun',
                'ne düşünüyorsun bakalım', 'ne düşünüyorsun acaba',
                'aklından ne geçiyor', 'aklından neler geçiyor',
                'ne fikrin var', 'ne düşüncelerin var',
                'bu konuda ne düşünüyorsun', 'hakkında ne düşünüyorsun',
                'ne dersin', 'ne dersin', 'ne dersin',
                'fikrin ne', 'fikrin nedir', 'görüşün ne',
                'görüşün nedir', 'kanaatin ne', 'kanaatin nedir'
            ],
            
            # ==================== BANA GÜLER MİSİN (15+ VARYASYON) ====================
            'guler_misin': [
                'bana güler misin', 'güler misin', 'gül',
                'bana güler misin', 'bana güler misin', 'bana güler misin',
                'gülebilir misin', 'gülebiliyor musun',
                'bir kere gül de görelim', 'gül bakalım',
                'gülücük atar mısın', 'gülümser misin',
                'mutlu olur musun', 'sevindin mi',
                'komik bir şey söyleyeyim de gül', 'gülmek istiyorum',
                'güldür beni', 'güldürebilir misin beni'
            ],
            
            # ==================== HAVA NASIL (15+ VARYASYON) ====================
            'hava_nasil': [
                'hava nasıl', 'hava', 'hava durumu',
                'hava nasıl', 'hava nasıl', 'hava nasıl',
                'hava nasıl bugün', 'bugün hava nasıl',
                'hava durumu nasıl', 'hava durumu nasıl bugün',
                'yağmur yağacak mı', 'kar yağacak mı',
                'güneşli mi', 'bulutlu mu', 'yağmurlu mu',
                'sıcak mı', 'soğuk mu', 'ılık mı',
                'derece kaç', 'sıcaklık kaç derece'
            ],
            
            # ==================== PARA VERİR MİSİN (12+ VARYASYON) ====================
            'para_verir_misin': [
                'para verir misin', 'para', 'para var mı',
                'para verir misin', 'para verir misin', 'para verir misin',
                'biraz para verir misin', 'bir miktar para verir misin',
                'borç para verir misin', 'borç alabilir miyim',
                'para yollar mısın', 'para gönderir misin',
                'zengin misin', 'paran var mı', 'paran bol mu'
            ],
            
            # ==================== EVLENİR MİSİN (12+ VARYASYON) ====================
            'evlenir_misin': [
                'evlenir misin', 'evlenelim', 'evlilik',
                'evlenir misin', 'evlenir misin', 'evlenir misin',
                'benimle evlenir misin', 'benimle evlenir misin',
                'evlenelim mi', 'evlenelim mi',
                'düğün yapalım mı', 'nikah kıyalım mı',
                'karım olur musun', 'kocam olur musun',
                'eşim olur musun', 'hayat arkadaşım olur musun'
            ],
            
            # ==================== ÇOCUĞUN VAR MI (12+ VARYASYON) ====================
            'cocugun_var_mi': [
                'çocuğun var mı', 'çocuk', 'evladın var mı',
                'çocuğun var mı', 'çocuğun var mı', 'çocuğun var mı',
                'çocukların var mı', 'çocuk sahibi misin',
                'baban mısın', 'anne misin',
                'kaç çocuğun var', 'çocukların kaç yaşında',
                'çocuk seviyor musun', 'çocuklardan hoşlanır mısın'
            ],
            
            # ==================== RENGİN NE (12+ VARYASYON) ====================
            'rengin_ne': [
                'rengin ne', 'renk', 'ne renk',
                'rengin ne', 'rengin ne', 'rengin ne',
                'hangi renk', 'ne renktesin',
                'favori rengin ne', 'en sevdiğin renk ne',
                'rengarenk misin', 'tek renk misin',
                'renkli misin', 'siyah beyaz mısın'
            ],
            
            # ==================== BOYUN KAÇ (12+ VARYASYON) ====================
            'boyun_kac': [
                'boyun kaç', 'boy', 'kaç metre',
                'boyun kaç', 'boyun kaç', 'boyun kaç',
                'boyun ne kadar', 'boyun ne kadar uzun',
                'kısa mısın', 'uzun musun', 'orta boylu musun',
                'kaç santimsin', 'kaç cm sin'
            ],
            
            # ==================== KİLON NE (12+ VARYASYON) ====================
            'kilon_ne': [
                'kilon ne', 'kilo', 'kaç kilo',
                'kilon ne', 'kilon ne', 'kilon ne',
                'kilon ne kadar', 'kilon kaç',
                'kaç kg sın', 'kaç kilosun',
                'zayıf mısın', 'kilolu musun', 'ideal kiloda mısın'
            ],
            
            # ==================== HASTA MISIN (12+ VARYASYON) ====================
            'hasta_misin': [
                'hasta mısın', 'hasta', 'iyi değil misin',
                'hasta mısın', 'hasta mısın', 'hasta mısın',
                'hastalandın mı', 'hasta oldun mu',
                'rahatsız mısın', 'bir şikayetin var mı',
                'iyi hissetmiyor musun', 'kendini iyi hissetmiyor musun',
                'ateşin var mı', 'öksürüyor musun'
            ],
            
            # ==================== RANDEVU İSTER MİSİN (12+ VARYASYON) ====================
            'randevu_ister_misin': [
                'randevu ister misin', 'randevu', 'buluşalım',
                'randevu ister misin', 'randevu ister misin', 'randevu ister misin',
                'buluşmak ister misin', 'bir yerde buluşalım mı',
                'görüşelim mi', 'bir kahve içelim mi',
                'date ister misin', 'çıkmak ister misin'
            ],
            
            # ==================== ÖZLEDİN Mİ (12+ VARYASYON) ====================
            'ozledin_mi': [
                'özledin mi', 'özlem', 'hasret',
                'özledin mi', 'özledin mi', 'özledin mi',
                'beni özledin mi', 'beni özledin mi',
                'hasret kaldın mı', 'hasret misin',
                'özledim dedin mi', 'özlediğini söyler misin'
            ]
        }
        
        self.toplam_varyasyon = sum(len(v) for v in self.soru_tipleri.values())
        print(f"✅ {len(self.soru_tipleri)} soru tipi, {self.toplam_varyasyon}+ varyasyon yüklendi! (Eşik: {self.esik})")
    
    def soru_bul(self, metin):
        """
        Metne en yakın soru tipini bulur (yazım hatalarına toleranslı)
        esik: 0-100 arası, ne kadar yüksekse o kadar katı
        """
        metin = metin.lower().strip()
        metin = re.sub(r'[^\w\s]', '', metin)  # Noktalama işaretlerini temizle
        
        # Çok kısa mesajları kontrol etme
        if len(metin) < 2:
            return None, 0
        
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
                
                if max_skor > en_iyi_skor and max_skor >= self.esik:
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
    matcher = SoruMatcher(esik=85)
    
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
        "evl misn", # yazım hatası
        "napıyon",
        "npyon",    # yazım hatası
        "teşekkürler",
        "teskrler", # yazım hatası
        "güle güle",
        "gule gule" # yazım hatası
    ]
    
    print("\n=== TEST SONUÇLARI ===")
    for soru in test_sorulari:
        kategori, skor = matcher.soru_bul(soru)
        if kategori:
            print(f"✓ {soru} → {kategori} (skor: {skor})")
        else:
            print(f"✗ {soru} → bulunamadı")
