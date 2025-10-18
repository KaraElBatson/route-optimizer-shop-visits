# Rota Optimizasyonu Kullanım Talimatları

Bu script, Excel dosyasındaki dükkan adreslerini okuyarak en optimize rotayı oluşturur. Trafik durumunu, mesafeyi ve zaman verimliliğini dikkate alır.

## Kurulum

1. Gerekli kütüphaneleri yükleyin:
```bash
pip install -r requirements.txt
```

## Kullanım

### Temel Kullanım
```bash
python route_optimizer.py "C:\Users\asus\Desktop\Ziyaret Rota\Kitap1  K MESEM.xlsx"
```

### Seçenekler
- `--api_key`: Google Maps API anahtarı (isteğe bağlı)
- `--address_column`: Adresleri içeren sütun adı (isteğe bağlı)
- `--start_address`: Başlangıç adresi (isteğe bağlı)
- `--output`: Çıktı dosyası adı (varsayılan: optimized_route.xlsx)

### Örnek Kullanımlar
```bash
# Google Maps API ile daha kesin sonuçlar için
python route_optimizer.py dosya.xlsx --api_key YOUR_API_KEY

# Belirli bir başlangıç adresi ile
python route_optimizer.py dosya.xlsx --start_address "Başlangıç Adresi"

# Belirli bir adres sütunu ile
python route_optimizer.py dosya.xlsx --address_column "Dükkan Adresleri"
```

## Özellikler

✅ **Otomatik Adres Tespiti**: Excel dosyasındaki adres sütununu otomatik olarak bulur
✅ **Trafik Optimizasyonu**: Saate göre trafik yoğunluğunu hesaba alır
✅ **Zaman Hesaplama**: Her durak için tahmini varış saatini gösterir
✅ **Google Maps Entegrasyonu**: Daha kesin konum bilgisi için API desteği
✅ **Google Maps Link Oluşturma**: Optimize edilmiş rotayı Google Maps'te görüntülemek için tıklanabilir link oluşturur
✅ **Excel Çıktısı**: Optimizasyon sonuçlarını Excel dosyasına kaydeder

## Trafik Faktörleri

- **Saat 07:00-09:00 ve 17:00-19:00**: Yoğun trafik (%50 daha yavaş)
- **Saat 10:00-16:00 ve 20:00-22:00**: Orta trafik (%20 daha yavaş)
- **Diğer saatler**: Normal trafik

## Çıktı

Script çalıştığında:
1. Konsolda rota özetini gösterir
2. **Google Maps Linki**: Optimize edilmiş rotayı Google Maps'te açmak için tıklanabilir URL oluşturur
3. Optimizasyon detaylarını içeren bir Excel dosyası oluşturur
4. Toplam mesafe, süre ve rota sırasını içerir

### Google Maps Linki

Script otomatik olarak bir Google Maps Yol Tarifi linki oluşturur:
- İlk adres başlangıç noktası olarak ayarlanır
- Son adres varış noktası olarak ayarlanır
- Aradaki tüm adresler ara duraklar (waypoints) olarak eklenir (maksimum 25 ara durak desteklenir)
- Adresler optimize edilmiş sırada düzenlenir

Konsol çıktısında veya Excel dosyasındaki linke tıklayarak rotanın tamamını Google Maps'te görüntüleyebilirsiniz.

## Notlar

- Google Maps API anahtarı kullanmak isterseniz, Google Cloud Console'dan bir anahtar almanız gerekir
- API anahtarı olmadan da çalışır, ancak daha az kesin sonuçlar verebilir
- Excel dosyanızdaki adres sütununu otomatik olarak bulmaya çalışır, bulamazsa size haber verir