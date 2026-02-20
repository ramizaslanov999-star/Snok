# konusma_hafizasi.py
import time
from collections import defaultdict, deque

class KonusmaHafizasi:
    def __init__(self, max_gecmis=10):
        self.max_gecmis = max_gecmis
        self.son_konusmalar = defaultdict(lambda: deque(maxlen=max_gecmis))
        self.duygu_durumu = defaultdict(lambda: {
            'mutlu': 50,
            'uzgun': 0,
            'saskin': 0,
            'komik': 30,
            'samimi': 50
        })
        self.konusma_akisi = defaultdict(lambda: {
            'son_kategori': None,
            'son_zaman': 0,
            'kac_kez_sordu': 0
        })
    
    def ekle(self, kullanici_id, mesaj, cevap, kategori=None):
        """Konuşmayı hafızaya ekle"""
        self.son_konusmalar[kullanici_id].append({
            'mesaj': mesaj,
            'cevap': cevap,
            'kategori': kategori,
            'zaman': time.time()
        })
        
        if kategori:
            self.konusma_akisi[kullanici_id]['son_kategori'] = kategori
            self.konusma_akisi[kullanici_id]['son_zaman'] = time.time()
    
    def son_konu_ne(self, kullanici_id):
        """Son konuşulan konuyu döndür"""
        if kullanici_id in self.son_konusmalar and self.son_konusmalar[kullanici_id]:
            return self.son_konusmalar[kullanici_id][-1]
        return None
    
    def takip_sorusu_gerekli_mi(self, kullanici_id, sure_siniri=120):
        """Son konuşmanın üzerinden belirli süre geçti mi?"""
        if kullanici_id not in self.konusma_akisi:
            return False
        
        son_zaman = self.konusma_akisi[kullanici_id]['son_zaman']
        return (time.time() - son_zaman) < sure_siniri
    
    def ayni_konuda_mi(self, kullanici_id, kategori):
        """Aynı konuda mı konuşuyoruz?"""
        if kullanici_id not in self.konusma_akisi:
            return False
        
        return self.konusma_akisi[kullanici_id]['son_kategori'] == kategori
    
    def kac_kez_sordu(self, kullanici_id, kategori):
        """Bu kullanıcı aynı kategoriyi kaç kez sordu?"""
        if kullanici_id not in self.son_konusmalar:
            return 0
        
        sayac = 0
        for konusma in self.son_konusmalar[kullanici_id]:
            if konusma.get('kategori') == kategori:
                sayac += 1
        
        return sayac
    
    def duygu_guncelle(self, kullanici_id, mesaj):
        """Mesaja göre duygu durumunu güncelle"""
        duygu = self.duygu_durumu[kullanici_id]
        
        if '😊' in mesaj or '😄' in mesaj or '😂' in mesaj or ':)' in mesaj:
            duygu['mutlu'] = min(100, duygu['mutlu'] + 5)
            duygu['komik'] = min(100, duygu['komik'] + 3)
        
        if '😢' in mesaj or '😭' in mesaj or '🥺' in mesaj or ':(' in mesaj:
            duygu['uzgun'] = min(100, duygu['uzgun'] + 8)
            duygu['mutlu'] = max(0, duygu['mutlu'] - 5)
        
        if '?' in mesaj or 'soru' in mesaj:
            duygu['saskin'] = min(100, duygu['saskin'] + 3)
        
        # Zamanla duygular normale döner
        for key in duygu:
            if key != 'mutlu' and duygu[key] > 0:
                duygu[key] = max(0, duygu[key] - 1)
        
        return duygu
    
    def tepki_ekle(self, kullanici_id, mesaj):
        """Duyguya göre tepki emojisi ekle"""
        duygu = self.duygu_durumu[kullanici_id]
        
        if duygu['mutlu'] > 70:
            return random.choice(['😊', '😄', '🥰', '😍'])
        elif duygu['uzgun'] > 50:
            return random.choice(['🥺', '😢', '😔', '💔'])
        elif duygu['saskin'] > 50:
            return random.choice(['😲', '🤔', '😮', '🤯'])
        elif duygu['komik'] > 60:
            return random.choice(['😂', '🤣', '😆', '😁'])
        else:
            return random.choice(['😐', '🙂', '👋', '💬'])