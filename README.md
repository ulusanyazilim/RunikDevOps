# Sistem Optimizasyon Aracı

Bu proje, Windows sistemlerde geliştirici ortamlarını optimize etmek ve yönetmek için geliştirilmiş kapsamlı bir araçtır. Özellikle SSD ve HDD disk yapılandırmasına sahip sistemlerde, programların doğru konumlandırılması ve yönetimi için tasarlanmıştır.

## Neden Bu Araç?

### Disk Optimizasyonu ve Program Konumlandırma
- SSD diskler hızlı erişim sunar ancak maliyetleri yüksektir ve yazma ömürleri sınırlıdır
- Programların veri dosyalarını HDD'ye taşıyarak:
  - SSD ömrünü uzatabilirsiniz
  - SSD'de daha fazla boş alan elde edebilirsiniz
  - Sistem performansını koruyabilirsiniz

### Geliştirici Ortamı Sorunları
- WSL, Docker, XAMPP gibi araçların varsayılan konumları sistem diskindedir
- Node.js, Python, Java gibi dillerin çoklu sürüm yönetimi karmaşıktır
- Cache dosyaları zamanla büyük yer kaplar
- Environment değişkenleri yönetimi zordur

## Özellikler ve Çözümler

### Disk ve Bellek Yönetimi
- Temp dosyaları, önbellekler ve gereksiz dosyaların temizliği
- Pagefile.sys ve hiberfil.sys boyutlandırma
- WSL konumunu HDD'ye taşıma
- Docker container ve image yönetimi

### XAMPP & MySQL Optimizasyonu
- MySQL hata dosyalarının (*.err) temizliği
- InnoDB log dosyalarının yönetimi
- Binary log dosyalarının temizliği
- Apache ve MySQL port yapılandırması
- Servis başlatma/durdurma yönetimi

### Geliştirici Araçları Yönetimi
- Node.js
  - Çoklu sürüm yönetimi
  - npm cache temizliği
  - Global paket yönetimi

- Python
  - Sürüm yönetimi
  - pip cache temizliği
  - Virtual environment yönetimi

- Java
  - JDK sürüm yönetimi
  - JAVA_HOME yapılandırması
  - Kullanılmayan sürümlerin temizliği

- Flutter/Android
  - SDK konumlandırma
  - Gradle cache yönetimi
  - Android Studio ayarları

- VS Code
  - Eklenti yönetimi
  - Workspace temizliği
  - Git ve Git LFS cache yönetimi

### Environment ve Path Yönetimi
- Sistem ve kullanıcı environment değişkenleri yönetimi
- Path değişkeni optimizasyonu
- Program yollarının otomatik eklenmesi

### Docker ve WSL
- Container ve image temizliği
- WSL dağıtımlarının konumlandırılması
- Docker Desktop ayarları

## Avantajlar

- Tek arayüzden tüm geliştirici araçlarının yönetimi
- Otomatik optimizasyon ve temizlik
- SSD ömrünü uzatma
- Sistem performansını artırma
- Disk alanından tasarruf
- Karmaşık yapılandırmaların basitleştirilmesi

## Güvenlik

Bu uygulama sistem seviyesinde değişiklikler yapabildiğinden yönetici haklarıyla çalıştırılmalıdır. Kullanmadan önce verilerinizi yedeklemeniz önerilir.

## Taşınan WSL Dosyası Çalışmıyorsa

Eğer taşınan WSL dosyası çalışmıyorsa, aşağıdaki adımları takip edebilirsiniz:

### 1) Mevcut WSL Dağıtımını Kapatın

```powershell
wsl --shutdown
```

### 2) Mevcut Dağıtımı Unregister Edin

```powershell
wsl --unregister Ubuntu  # veya hangi dağıtımı kullanıyorsanız
```

### 3a) VHDX Dosyasının Yeni Konumunu WSL'e Bildirin

```powershell
wsl --import-in-place Ubuntu D:\WSL\ext4.vhdx
```

### 3b) Bu Yöntem Çalışmazsa Alternatif Olarak

### 4) Yeni Bir WSL Dağıtımı Oluşturun ve VHDX'in Konumunu Belirtin

```powershell
wsl --import Ubuntu D:\WSL D:\WSL\ext4.vhdx
```

### 5) Hala Hata Alıyorsanız, WSL'i Tamamen Sıfırlayıp Yeniden Kurabilirsiniz

```powershell
wsl --unregister Ubuntu
wsl --shutdown
wsl --install Ubuntu
```

## İletişim ve Destek

- Website: [https://hucrem.com](https://hucrem.com)
- E-posta: ulusanyazilim@gmail.com
- Geliştirici: Mehmet Ali Uluşan

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakınız.

