# Control-PC-with-PS4-Controller

[Read in English / İngilizce için tıklayın](README.md)

## Açıklama

Python ile yapılmış, mouse, klavye & bazı kısayolları kullanma, sesle yazma, sekme değiştirme vb. işlevler için bir uygulama.

## Kontroller

| 🎮 Kontrol                  | 💻 İşlev                        |
|----------------------------|---------------------------------|
| Sol analog                 | Mouse hareketi              |
| Sağ analog                 | Dikey kaydırma ve yatay kaydırma (OS X ve Linux, bazen Windows için)           |
| X / L3                      | Sol tıklama                     |
| R3                         | Sağ tıklama                     |
| Kare                       | Silme (Backspace)                          |
| Üçgen                      | Boşluk (Space)                          |
| Daire                      | ESC                             |
| Share                      | Enter                           |
| D-pad                      | Ok tuşları                      |
| R1 (basılı tut)            | Shift (basılı tut)              |
| R1 (1 kez)                 | Kopyalama                       |
| R1 (2 kez)                 | Kesme                           |
| L1                         | Yapıştırma                      |
| R2 (1 kez)                 | Geri al                         |
| R2 (2 kez)                 | İleri al                        |
| L2 (basılı tut)            | Alt                             |
| L2 + Sağ D-pad (basılı)    | Alt + Tab                             |
| Touchpad                   | Ekran klavyesi aç/kapa (Windows)          |
| Options                    | Sesli yazmayı aç/kapa           |

💡 **İpuçları:**
- R1'e basılı tutarken D-pad ile metin seçip, R1 ile kopyalayıp/kesip L1 ile yapıştırabilirsiniz.
- L2'ye basılı tutarken sağ D-pad ile sekmeler arası geçiş yapabilirsiniz!

⚠️ **Uyarı:** Uygulama sadece Windows 11'de test edilmiştir.

ℹ️ **Bilgi:** Ekran klavyesini kullanabilmek için: Ekran klavyesi > Seçenekler > Tuşların üzerine gel > Üzerinde durma süresi > 3 saniye

ℹ️ **Bilgi:** Sesli yazmayı kullanabilmek için [Speechmatics](https://www.speechmatics.com/) hesabı oluşturup API key'inizi uygulamaya girmeniz gerekmektedir. Speechmatics ücretsiz planda iyi bir kullanım süresi sunar.

ℹ️ **Bilgi:** API key bilgisi `settings.json` dosyasında tutulmaktadır. Silmek isterseniz manuel olarak veya uygulama üzerinden inputu boş bırakıp kaydete basarak dosyadan key bilginizi silebilirsiniz.

## İndirme ve Kurulum

1. Projeyi klonlayın:
   ```bash
   git clone https://github.com/AlperBayraktar/Control-PC-with-PS4-Controller.git
   cd Control-PC-with-PS4-Controller
   ```
2. (Opsiyonel) Sanal ortam oluşturun:
   - Windows:
     ```bash
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
3. Gerekli paketleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```
4. Uygulamayı başlatın:
   ```bash
   python main.py
   ```
5. (Sesli yazmayı kullanmak için) Speechmatics API anahtarınızı uygulamaya girin.

## AI Kullanımı

Uygulamanın arayüzü ve threading kodlarının önemli bir kısmı yapay zeka tarafından yazılmıştır. Ben yalnızca bazı düzeltmeler yaptım.

## Lisans

[MIT Lisansı](LICENSE) ile lisanslanmıştır.