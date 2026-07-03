# Yerel AI Agent Projesi — Süreç ve İlerleme Raporu

**Rapor tarihi:** Mayıs 2026
**Platform:** Windows 10/11 + Docker Desktop
**Kapsam:** Projenin başlangıcından bugüne kadar yürütülen tüm adımlar

---

## İçindekiler

1. [Genel Çerçeve — Yerel AI Agent Kurulumunda Yapılması Gerekenler](#1-genel-çerçeve--yerel-ai-agent-kurulumunda-yapılması-gerekenler)
2. [Bizim Yaptıklarımız — Kronolojik Süreç](#2-bizim-yaptıklarımız--kronolojik-süreç)
3. [Karşılaşılan Sorunlar ve Çözümleri](#3-karşılaşılan-sorunlar-ve-çözümleri)
4. [Şu Anki Durum](#4-şu-anki-durum)
5. [Henüz Yapılmayanlar](#5-henüz-yapılmayanlar)
6. [Genel Değerlendirme](#6-genel-değerlendirme)

---

## 1. Genel Çerçeve — Yerel AI Agent Kurulumunda Yapılması Gerekenler

Literatür taraması ve uygulama deneyimine dayanarak, dışarıya kapalı ve güvenli bir kişisel AI agent kurulumu beş aşamada tamamlanır:

| Aşama | İçerik |
|---|---|
| **1. Altyapı & izolasyon** | Donanım planlaması, Docker kurulumu, ağ izolasyonu |
| **2. Yerel LLM kurulumu** | Model çalıştırma motoru (Ollama), model indirme, kuantizasyon |
| **3. Agent çekirdeği** | Sistem kuralları, araç sistemi, hafıza yönetimi, arayüz |
| **4. Güvenlik katmanı** | Girdi/çıktı filtreleme, hız sınırlama, audit log |
| **5. Genişleme** | RAG, otomasyon, fine-tuning, izleme (bu rapor tarihine kadar kısmen tamamlandı) |

Her aşamanın kendi içinde önkoşulları vardır — örneğin ağ izolasyonu açıkken model indirmek mümkün değildir, bu nedenle sıralama ve geçici istisnalar önem taşır. Bu durum, aşağıda görüleceği gibi sürecimizde defalarca karşımıza çıkmıştır.

---

## 2. Bizim Yaptıklarımız — Kronolojik Süreç

### 2.1 Planlama Aşaması

İlk adımda projenin tüm yol haritası görsel diyagram ve detaylı metin olarak çıkarıldı. Beş aşamalı bir plan belirlendi: altyapı, model, agent çekirdeği, güvenlik, otomasyon/genişleme.

### 2.2 Platform Kararı

Başlangıçta Ubuntu Linux önerildi, ancak kullanıcının elinde Windows makine olduğu belirlenince platform Windows + Docker Desktop olarak netleştirildi. Linux'a özgü `ufw`/`LUKS` gibi araçlar yerine Windows karşılıkları (Windows Firewall, BitLocker) not edildi; ancak proje pratikte Docker Desktop üzerinden ilerletildiği için bu katman henüz uygulamaya geçirilmedi.

### 2.3 Altyapı Kurulumu

Aşağıdaki bileşenler oluşturuldu:

- `C:\ai-agent` klasör yapısı (`models`, `chroma-data`, `agent-data`, `logs`, `agent`)
- `docker-compose.yml` — üç servisli yapı: `ollama`, `chromadb`, `agent`
- Ağ izolasyonu: `ai-internal` adlı Docker bridge ağı, `internal: true` ile dış internete kapatıldı
- Streamlit portu (`8501`) yalnızca `127.0.0.1`'e bağlandı, dışa açılmadı

### 2.4 Model İndirme

`llama3.2` ve `nomic-embed-text` modelleri Ollama container'ı üzerinden indirildi. Bu adımda izolasyon nedeniyle DNS çözümleme hatası alındığı için `internal: true` geçici olarak devre dışı bırakıldı, indirme tamamlandıktan sonra tekrar etkinleştirildi.

### 2.5 Agent Container ve Streamlit

İlk aşamada `agent` servisi `python:3.12-slim` image'ı ile `sleep infinity` komutu kullanılarak "boş" şekilde başlatıldı; amaç önce altyapıyı ayağa kaldırmaktı. Sonrasında:

- `requirements.txt` ve `app.py` dosyaları oluşturuldu
- Bağımlılıkların container içinde çalışma zamanında `pip install` ile kurulması denendi
- Bu yöntem ağ izolasyonu nedeniyle başarısız olunca, **Dockerfile tabanlı build** yaklaşımına geçildi — bağımlılıklar artık image derleme anında, izolasyon dışı bir aşamada kuruluyor

### 2.6 Agent Çekirdeği

Kullanıcının seçimiyle önce **agent çekirdeği** geliştirildi. `app.py` dosyası tamamen yeniden yazılarak şu bileşenler eklendi:

- **Kural motoru:** Sistem promptunda tanımlı zorunlu kurallar (dış bağlantı kurmama, kişisel veri loglamama, Türkçe yanıt verme vb.)
- **Araç sistemi:** `hesapla:`, `not kaydet:`, `notlarım`, `dosya oku:` komutları
- **Hafıza sistemi:** Kısa süreli hafıza (`ConversationBufferWindowMemory`, son 10 mesaj) ve uzun süreli hafıza (JSON dosyasına kalıcı kayıt)
- **Arayüz:** Sol panelde durum göstergeleri, araç kullanım kılavuzu, uzun hafıza yönetimi

### 2.7 Güvenlik Katmanı

Ayrı bir `guvenlik.py` modülü oluşturuldu ve `app.py`'ye entegre edildi:

- **Prompt injection koruması:** Regex tabanlı kalıp tespiti (`ignore previous instructions`, `jailbreak`, `system:` vb.)
- **Çıktı filtreleme:** E-posta, telefon numarası gibi hassas verilerin model yanıtlarından maskelenmesi
- **Hız sınırlama:** Dakikada maksimum 20 istek
- **Audit log:** İçerik değil, yalnızca zaman damgası ve olay türü kaydı (`guvenlik.log`)
- Arayüze güvenlik metrikleri paneli eklendi (24 saatlik olay/uyarı/tehdit sayacı)

### 2.8 RAG Sistemi

Ayrı bir `rag.py` modülü oluşturuldu:

- PDF, Word (`.docx`), TXT ve Markdown desteği (`PyPDFLoader`, `Docx2txtLoader`, `TextLoader`)
- `RecursiveCharacterTextSplitter` ile 500 karakterlik, 50 karakter örtüşmeli parçalama
- `nomic-embed-text` ile embedding, ChromaDB'ye kayıt
- Benzerlik aramasıyla en yakın 4 parçanın bulunup model bağlamına eklenmesi
- Arayüze belge yükleme paneli ve yüklü belge listesi eklendi

### 2.9 Belgeleme

- Projenin teknik dokümantasyonu için kapsamlı bir **`README.md`** hazırlandı (mimari, kurulum, kullanım, sorun giderme, komut referansı dahil)
- Konuyla ilgili akademik ve endüstriyel kaynakları derleyen bir **literatür taraması** raporu hazırlandı (yerel LLM dağıtımı, RAG, agent hafızası, prompt injection savunmaları, gizlilik, konteyner izolasyonu başlıklarında)

---

## 3. Karşılaşılan Sorunlar ve Çözümleri

Süreç boyunca karşılaşılan teknik sorunlar ve nasıl çözüldükleri aşağıda özetlenmiştir — bu kayıtlar ileride benzer bir kurulum yapacaklar için referans niteliğindedir.

| # | Sorun | Sebep | Çözüm |
|---|---|---|---|
| 1 | `ollama pull` sırasında DNS çözümleme hatası (`server misbehaving`) | `internal: true` ağı dış DNS'e erişimi engelliyordu | `internal: true` satırı geçici olarak yoruma alındı, model indirildi, sonra geri açıldı |
| 2 | PowerShell'de `ollama: command not found` | Ollama Windows host'a değil, sadece container'a kurulmuştu | Komutun `docker exec ollama ollama ...` formatında çalıştırılması gerektiği netleştirildi |
| 3 | Container içinde `pip install` başarısız (`Temporary failure in name resolution`) | Ağ izolasyonu çalışma zamanı pip kurulumunu da engelliyordu | Bağımlılıkların image **build** aşamasında (izolasyon dışı) kurulmasını sağlayan Dockerfile yaklaşımına geçildi |
| 4 | `docker compose up -d` sonrası `agent` container loglarının boş görünmesi | `docker-compose.yml`'de unutulmuş `command: sleep infinity` satırı, Streamlit'in hiç başlatılmamasına yol açıyordu | İlgili `command` satırı silindi, container varsayılan Dockerfile `CMD`'sini kullanacak şekilde yeniden yapılandırıldı |
| 5 | `version` alanı için "obsolete" uyarısı | Docker Compose artık bu alanı gerektirmiyor | Bilgi amaçlı not edildi; dosyadan kaldırılması önerildi |

**Genel çıkarım:** Bu projede tekrar eden temel gerilim, **ağ izolasyonu** (`internal: true`) ile **internet gerektiren kurulum işlemleri** (model indirme, pip kurulumu) arasındaki çakışmaydı. Bu, literatürde de "hava boşluklu sistemlerde başlangıç kurulumunun ayrı ele alınması gerektiği" şeklinde karşılığını bulan, beklenen bir mühendislik sorunu olarak değerlendirilebilir.

---

## 4. Şu Anki Durum

Bu rapor tarihi itibarıyla sistemde aşağıdaki bileşenler **çalışır durumda**:

✅ Docker Compose ile üç container (`ollama`, `chromadb`, `ai-agent`)
✅ `internal: true` ile tam ağ izolasyonu (kalıcı model/veri hariç dış bağlantı yok)
✅ `llama3.2` ve `nomic-embed-text` modelleri yerel olarak kayıtlı
✅ Streamlit arayüzü `http://localhost:8501` üzerinden sadece yerel erişime açık
✅ Kural motoru, araç sistemi (hesaplama, not, dosya okuma), kısa/uzun süreli hafıza
✅ Prompt injection koruması, çıktı filtreleme, hız sınırlama, audit log
✅ PDF/Word/TXT belgeleri için RAG sorgu desteği
✅ `README.md` ve literatür taraması belgeleri hazırlandı

---

## 5. Henüz Yapılmayanlar

Önceki konuşmalarda planlanmış ancak henüz uygulamaya geçirilmemiş kalemler:

- ❌ Windows tarafı disk şifreleme (BitLocker) yapılandırması
- ❌ Windows Firewall ile ek ağ kısıtlaması (şu an yalnızca Docker'ın kendi izolasyonuna güveniliyor)
- ❌ n8n ile workflow otomasyonu
- ❌ LoRA / fine-tuning ile modelin özelleştirilmesi
- ❌ Prometheus + Grafana ile kaynak izleme
- ❌ Otomatik yedekleme mekanizması

---

## 6. Genel Değerlendirme

Proje, planlanan beş aşamadan dördünü (altyapı, model, agent çekirdeği, güvenlik) tamamlamış, beşinci aşamanın (genişleme) bir alt bileşeni olan RAG'ı da hayata geçirmiştir. Süreç boyunca yaşanan sorunların büyük kısmı, ağ izolasyonu ile kurulum gereksinimleri arasındaki beklenen çakışmalardan kaynaklanmış ve her biri kalıcı, tekrarlanabilir çözümlerle giderilmiştir.

Sistemin şu andaki hali, tamamen yerel çalışan, dışarıya veri sızdırmayan ve temel siber güvenlik önlemlerini barındıran fonksiyonel bir kişisel AI agent olarak değerlendirilebilir. Kalan kalemler (disk şifreleme, otomasyon, izleme) sistemin temel işlevselliğini etkilemeyen, ek güçlendirme ve genişletme adımlarıdır.

---

*Bu rapor, bu sohbet oturumu boyunca yapılan tüm teknik adımların, kararların ve çözülen sorunların kronolojik bir özetidir.*
