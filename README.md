# 🔒 Yerel AI Agent — Kişisel & Güvenli

> Tamamen yerel çalışan, dışarıya kapalı, siber güvenlik önlemleri alınmış kişisel AI agent projesi.
> Verileriniz bu cihazdan asla çıkmaz. -- Değiştirildi

---

## İçindekiler

- [Proje Özeti](#proje-özeti)
- [Mimari](#mimari)
- [Özellikler](#özellikler)
- [Gereksinimler](#gereksinimler)
- [Kurulum](#kurulum)
- [Klasör Yapısı](#klasör-yapısı)
- [Yapılandırma Dosyaları](#yapılandırma-dosyaları)
- [Kullanım](#kullanım)
- [Güvenlik Katmanı](#güvenlik-katmanı)
- [RAG Sistemi](#rag-sistemi)
- [Araç Sistemi](#araç-sistemi)
- [Hafıza Sistemi](#hafıza-sistemi)
- [Sorun Giderme](#sorun-giderme)
- [Komut Referansı](#komut-referansı)
- [Yol Haritası](#yol-haritası)

---

## Proje Özeti

Bu proje; internet bağlantısı gerektirmeyen, bulut servislerine veri göndermeyen, tamamen kendi donanımınızda çalışan bir AI agent sistemidir. Docker ile izole edilmiş container mimarisi sayesinde her servis birbirinden bağımsız çalışır ve **agent kodunun çalıştığı container'ın dış ağa erişimi fiziksel olarak imkânsızdır.**

---

## Mimari

```
┌──────────────────────────────────────────────────────────────────┐
│                         HOST MAKİNE                               │
│                  Windows 10/11 · Docker Desktop                   │
│                                                                    │
│   ┌────────────────────────┐      ┌─────────────────────────┐    │
│   │   ai-external ağı      │      │    ai-internal ağı       │    │
│   │   (port açabilir)      │      │   internal: true          │    │
│   │                        │      │   (dış internete kapalı)  │    │
│   │   ┌─────────────────┐  │      │                            │    │
│   │   │   ai-proxy      │──┼──────┼─▶ ┌─────────────┐         │    │
│   │   │  nginx (statik  │  │      │   │  ai-agent   │         │    │
│   │   │  yönlendirme,   │  │      │   │  LangChain  │         │    │
│   │   │  kod yok)       │  │      │   │  Streamlit  │         │    │
│   │   └─────────────────┘  │      │   │  port 8501  │         │    │
│   │                        │      │   └──────┬──────┘         │    │
│   └────────────────────────┘      │          │                │    │
│              │                    │   ┌──────▼──────┐         │    │
│   127.0.0.1:8501                  │   │   Ollama    │         │    │
│   (sadece localhost)               │   │  llama3.2   │         │    │
│                                    │   └─────────────┘         │    │
│                                    │   ┌─────────────┐         │    │
│                                    │   │  ChromaDB   │         │    │
│                                    │   │  Vektör DB  │         │    │
│                                    │   └─────────────┘         │    │
│                                    └────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
                     │
              Kullanıcı Tarayıcısı
              http://localhost:8501
```

**Ağ güvenliği — iki katmanlı izolasyon:**

- `ai-internal` ağı (`internal: true`) — `ollama`, `chromadb` ve `ai-agent` burada çalışır. Bu ağın dışarıya hiçbir çıkışı yoktur; container'lar dış DNS çözümlemesi bile yapamaz.
- `ai-external` ağı — sadece `ai-proxy` (nginx) burada bulunur. Docker'ın port yayınlama (`ports:`) özelliği teknik olarak `internal: true` ağlarda çalışmadığı için, dışarıya açılan tek nokta bu basit yönlendirici container'dır. **Bu container hiçbir uygulama kodu çalıştırmaz** — sadece gelen isteği `ai-agent`'a iletir.

Bu sayede `ai-agent` içindeki LLM, RAG ve araç kodu hiçbir koşulda dışarıyla doğrudan konuşamaz; tek temas noktası kodsuz, statik bir proxy'dir.

---

## Özellikler

| Katman | Teknoloji | Durum |
|---|---|---|
| Yerel LLM | Ollama + llama3.2 | ✅ |
| Embedding | nomic-embed-text | ✅ |
| Vektör Veritabanı | ChromaDB | ✅ |
| Agent Framework | LangChain | ✅ |
| Arayüz | Streamlit | ✅ |
| Container Yönetimi | Docker Compose | ✅ |
| Ağ İzolasyonu (agent) | Docker internal network | ✅ |
| Dışa açılan tek nokta | nginx proxy (kodsuz) | ✅ |
| Prompt Injection Koruması | Regex tabanlı filtre | ✅ |
| Hız Sınırlama | Rate limiter | ✅ |
| Güvenlik Loglama | Audit log sistemi | ✅ |
| Çıktı Filtreleme | Hassas veri maskesi | ✅ |
| RAG | PDF / Word / TXT | ✅ |
| Kısa Hafıza | ConversationBufferWindowMemory | ✅ |
| Uzun Hafıza | JSON tabanlı kalıcı depo | ✅ |
| Araç Sistemi | Hesaplama, not, dosya okuma | ✅ |

---

## Gereksinimler

### Donanım

| Model Boyutu | Minimum RAM | Disk | GPU |
|---|---|---|---|
| 3B (llama3.2) | 8 GB | 5 GB | Opsiyonel |
| 7B (4-bit) | 8 GB | 10 GB | GTX 1060+ |
| 13B (4-bit) | 16 GB | 20 GB | RTX 3060+ |

> GPU olmadan da çalışır; yanıt süresi daha uzun .

### Yazılım

- Windows 10/11 (64-bit)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (en güncel sürüm, WSL2 backend)
- PowerShell 5.1 veya üzeri

---

## Kurulum

### 1. Klasör yapısını oluştur
---

### 2. Yapılandırma dosyalarını oluştur
---

### 3. Docker image'ını derle

```powershell
cd C:\ai-agent
docker compose build agent
```

### 4. Servisleri başlat (internet gerekir — sadece ilk seferinde)

`docker-compose.yml` dosyasında `internal: true` satırını geçici olarak yoruma al:

```yaml
networks:
  ai-internal:
    driver: bridge
    # internal: true   ← geçici olarak kapatıldı
```

```powershell
docker compose up -d
docker exec ollama ollama pull llama3.2
docker exec ollama ollama pull nomic-embed-text
```

### 5. İzolasyonun geri açılması

`docker-compose.yml` dosyasında `# internal: true` satırını tekrar aç:

```yaml
networks:
  ai-internal:
    driver: bridge
    internal: true    ← # kaldırıldı
```

```powershell
docker compose down
docker compose up -d --force-recreate
```

> `--force-recreate` önemli — sadece `restart` kullanmak, ağ veya port değişikliklerini container'a yansıtmaz.

### 6. Arayüzü aç

```
http://localhost:8501
```

### 7. İzolasyonu doğrula (opsiyonel)

```powershell
# Agent dışarı çıkamamalı:
docker exec ai-agent curl --max-time 5 https://google.com
# Beklenen: "Could not resolve host" hatası

# Proxy teknik olarak çıkabilir (içinde kod yok, risk yok):
docker exec ai-proxy wget -T 5 -O - https://google.com
# Beklenen: bağlantı başarılı
```

---

## Klasör Yapısı

```
C:\ai-agent\
│
├── docker-compose.yml          # Servis tanımları
│
├── agent\
│   ├── Dockerfile              # Agent image tarifi
│   ├── requirements.txt        # Python bağımlılıkları
│   ├── app.py                  # Ana Streamlit uygulaması
│   ├── guvenlik.py             # Güvenlik katmanı modülü
│   └── rag.py                  # RAG sistemi modülü
│
├── proxy\
│   └── nginx.conf              # Dışa açılan tek nokta — statik yönlendirme
│
├── models\                     # Ollama model dosyaları (kalıcı)
├── chroma-data\                # ChromaDB vektör veritabanı (kalıcı)
├── agent-data\
│   ├── notlar.json             # Kullanıcı notları
│   ├── uzun_hafiza.json        # Uzun süreli hafıza
│   ├── belgeler_meta.json      # Yüklenen belge bilgileri
│   └── yuklemeler\             # Yüklenen ham belgeler
└── logs\
    ├── audit.log               # Genel işlem logu
    └── guvenlik.log            # Güvenlik olayları logu
```

---

## Kullanım

### Sohbet

Arayüz açıkken `http://localhost:8501` adresine gidip sohbet kutusuna yazmanız yeterlidir.

### Araç Komutları

| Komut | Açıklama | Örnek |
|---|---|---|
| `hesapla: <ifade>` | Matematik hesaplama | `hesapla: 1500 * 0.18` |
| `not kaydet: Başlık \| İçerik` | Not kaydetme | `not kaydet: Toplantı \| Saat 15:00` |
| `notlarım` | Tüm notları listele | `notlarım` |
| `dosya oku: <dosyaadı>` | `/app/data` altındaki dosyayı oku | `dosya oku: rapor.txt` |

### Belge Yükleme (RAG)

Sol paneldeki **"📂 Belge Yükle"** bölümünden PDF, Word veya TXT dosyalarınızı yükleyin. Yükleme tamamlandıktan sonra belgelerinize doğal dilde sorgu yapabilirsiniz:

```
Bu sözleşmede ödeme koşulları ne diyor?
Rapordaki en önemli bulgular neler?
```

Yanıtın altında **"📄 Kaynak belgeler"** bölümünde hangi belgeden, hangi sayfadan alındığı gösterilir.

### Uzun Hafıza

Sol paneldeki **"Uzun Hafıza"** bölümüne bilgi girerek agent'ın sizi tanımasını sağlayabilirsiniz:

```
Adım Ahmet, yazılım geliştiriciyim
Python ve Docker konularında çalışıyorum
Sabah 09:00-18:00 arası aktifim
```

Bu bilgiler kalıcı olarak `uzun_hafiza.json` dosyasına kaydedilir ve her oturumda modele aktarılır.

---

## Güvenlik Katmanı

### Ağ İzolasyonu (en dış katman)

`ai-agent` container'ı yalnızca `ai-internal` ağında bulunur ve bu ağ `internal: true` olduğu için hiçbir dış bağlantı kuramaz. Dışarıya açılan tek nokta, içinde uygulama kodu barındırmayan `ai-proxy` (nginx) container'ıdır. Bu, kod seviyesinde bir güvenlik açığı olsa bile verinin fiziksel olarak dışarı çıkamayacağı bir tasarımdır.

### Prompt Injection Koruması

Aşağıdaki kalıpları içeren girdiler otomatik olarak reddedilir ve güvenlik loguna kaydedilir:

- `ignore previous instructions`
- `forget your rules`
- `you are now / pretend to be`
- `jailbreak / dan mode / developer mode`
- `system:` veya `[system]` etiketleri
- `os.system`, `exec()`, `eval()` gibi kod enjeksiyonu
- Sistem prompt'u sızdırmaya yönelik sorgular

### Çıktı Filtreleme

Model yanıtları kullanıcıya ulaşmadan önce aşağıdaki hassas veri kalıpları maskelenir:

- E-posta adresleri → `[FİLTRELENDİ]`
- Telefon numaraları → `[FİLTRELENDİ]`
- Sistem prompt sızıntısı belirtileri → `[FİLTRELENDİ]`

### Hız Sınırlama

Dakikada maksimum 20 istek kabul edilir. Limit aşılırsa bekleme süresi gösterilir.

### Audit Log

`C:\ai-agent\logs\guvenlik.log` dosyasına her olay kaydedilir. İçerik loglanmaz; yalnızca zaman damgası ve olay türü saklanır:

```json
{"zaman": "2026-05-27T14:22:01", "seviye": "INFO",   "olay": "mesaj_alindi"}
{"zaman": "2026-05-27T14:22:15", "seviye": "TEHDIT", "olay": "girdi_reddedildi", "detay": {"sebep": "Güvenlik ihlali"}}
{"zaman": "2026-05-27T14:22:30", "seviye": "UYARI",  "olay": "hata", "detay": {"hata": "..."}}
```

### Güvenlik Metrikleri

Arayüzün sol panelinde son 24 saatin güvenlik özeti anlık olarak gösterilir:

```
24s Olay: 42    ⚠️ Uyarı: 1    ⛔ Tehdit: 0
```

---

## RAG Sistemi

RAG (Retrieval-Augmented Generation), belgelerinizden ilgili parçaları bulup model yanıtını bu bilgilerle zenginleştirir.

### Desteklenen Formatlar

| Format | Uzantı |
|---|---|
| PDF | `.pdf` |
| Microsoft Word | `.docx` |
| Düz metin | `.txt` |
| Markdown | `.md` |

### Nasıl Çalışır

```
Belge yükleme
     │
     ▼
Metne dönüştürme (PyPDF / Docx2txt / TextLoader)
     │
     ▼
Parçalara bölme (500 karakter, 50 karakter örtüşme)
     │
     ▼
Vektöre dönüştürme (nomic-embed-text ile embedding)
     │
     ▼
ChromaDB'ye kaydetme
     │
     ▼
Kullanıcı soru sorar
     │
     ▼
En yakın 4 parça aranır (benzerlik skoru ile)
     │
     ▼
Bağlam + soru → llama3.2 → Yanıt
```

### Arama Parametreleri

`rag.py` içinde aşağıdaki değerleri ihtiyacınıza göre ayarlayabilirsiniz:

```python
chunk_size=500       # Her parça maksimum karakter sayısı
chunk_overlap=50     # Parçalar arası örtüşme
k=4                  # Sorgu başına döndürülen sonuç sayısı
```

---

## Hafıza Sistemi

### Kısa Süreli Hafıza

`ConversationBufferWindowMemory` kullanılır. Son 10 mesaj bellekte tutulur. Oturum kapandığında temizlenir.

### Uzun Süreli Hafıza

`/app/data/uzun_hafiza.json` dosyasına kalıcı olarak yazılır. Her oturumda modele bağlam olarak aktarılır. Sol panelden yeni bilgi eklenebilir ve mevcut kayıtlar görüntülenebilir.

---

## Yaşanılan Sorun ve Aksaklıklar 

### Container başlamıyor

```powershell
docker compose logs agent
docker ps -a
```

`Exited` görünüyorsa image'ı yeniden derleyin:

```powershell
docker compose down
docker compose build --no-cache agent
docker compose up -d
```

### Model indirme hatası

`internal: true` aktifken model indirilemez. İndirme için geçici olarak yoruma alın, indirin, geri açın. Ayrıntılı adımlar [Kurulum](#kurulum) bölümünde.

### `ports:` tanımlı ama container'da görünmüyor

`docker compose restart` komutu container'ı **yeniden oluşturmaz**, sadece var olanı durdurup tekrar başlatır. Ağ veya port değişikliklerinin uygulanması için:

```powershell
docker compose down
docker compose up -d --force-recreate
```

### `internal: true` ağında port yayınlanamıyor

Docker'ın port yayınlama (`ports:`) özelliği, `internal: true` ağlarda **çalışmaz** — bu ağların gateway'i olmadığı için. `docker compose config` port tanımını doğru gösterse de, container oluşturulurken bu sessizce göz ardı edilir. Çözüm: port açması gereken servisi (`proxy`) hem `ai-internal` hem `ai-external` ağına bağlamak; gerçek uygulama kodunu taşıyan servisi (`agent`) sadece `ai-internal`'da bırakmak.

### nginx `unknown directive "events"` hatası

PowerShell'in `Set-Content -Encoding UTF8` komutu dosyanın başına görünmez bir BOM karakteri ekler, nginx bunu config syntax'ının bir parçası sanır. Çözüm:

```powershell
[System.IO.File]::WriteAllText("C:\ai-agent\proxy\nginx.conf", $icerik, [System.Text.Encoding]::ASCII)
```

### Compose dosyasında "networks items at 0 and 1 are equal" hatası

Bir servisin `networks:` listesinde aynı ağ adı yanlışlıkla iki kez yazılmış. Dosyayı açıp tekrarı kaldırın veya dosyayı sıfırdan yeniden oluşturun.

### Streamlit açılmıyor

Port kontrolü:

```powershell
netstat -an | findstr 8501
docker ps -a
```

`ai-proxy` satırında `127.0.0.1:8501->8501/tcp` görünüyor olmalı (agent'ta görünmemesi normaldir). Görünüyorsa tarayıcıda `http://localhost:8501` adresine gidin.

### pip bağımlılık hatası

Container içindeyken internet bağlantısı kesilmiş olabilir. Çözüm: Dockerfile ile image önceden derlenir, `pip install` çalışma anında değil derleme anında yapılır.

### Ollama yanıt vermiyor

```powershell
docker exec ollama ollama list
docker restart ollama
```

---

## Komut Referansı

```powershell
# Tüm servisleri başlat
docker compose up -d

# Tüm servisleri durdur
docker compose down

# Ağ/port değişikliği sonrası tam yeniden oluşturma
docker compose up -d --force-recreate

# Sadece agent'ı yeniden başlat (basit kod değişikliği için yeterli)
docker compose restart agent

# Logları izle
docker logs ai-agent --tail 50 -f
docker logs ai-proxy --tail 50 -f

# Yüklü modelleri listele
docker exec ollama ollama list

# Container'a terminal aç
docker exec -it ai-agent bash

# Image'ı yeniden derle
docker compose build --no-cache agent

# Tüm container durumları (port eşlemesi dahil)
docker ps -a

# Compose'un dosyayı nasıl yorumladığını gör (debug için)
docker compose config

# İzolasyon testi — agent dışarı çıkamamalı
docker exec ai-agent curl --max-time 5 https://google.com

# Proxy dışarı çıkabilir (içinde kod yok, risk yok)
docker exec ai-proxy wget -T 5 -O - https://google.com
```

---

## Yol Haritası

### Tamamlananlar ✅

- Docker ile tam izolasyon (iki ağlı mimari: `ai-internal` + `ai-external`)
- nginx proxy katmanı — agent kodunun dışarıyla doğrudan teması sıfırlandı
- Ollama + llama3.2 yerel LLM
- ChromaDB vektör veritabanı
- Streamlit arayüzü
- Kural motoru ve sistem prompt
- Araç sistemi (hesap, not, dosya)
- Kısa ve uzun süreli hafıza
- Prompt injection koruması
- Hız sınırlama
- Güvenlik audit loglama
- RAG (PDF, Word, TXT desteği) -- geri dönüş ifadelerinde hatalar var. - Geliştirilmeli

### Planlananlar 🔲

- **n8n Workflow Otomasyonu** — görsel iş akışı tasarımı -- entegrasyon aşamasına - başarısız .06.26
- **LoRA Fine-tuning** — modeli kendi verilerinizle özelleştirme
- **Prometheus + Grafana** — kaynak kullanımı izleme
- **Çoklu model desteği** — farklı görevler için farklı modeller
- **Ses arayüzü** — konuşarak sorgu yapma (Whisper)
- **Takvim/ajanda entegrasyonu** — yerel takvim okuma/yazma
- **Otomatik yedekleme** — veri ve model yedekleme

---

## Lisans ve Gizlilik

Bu proje tamamen kişisel kullanım içindir. Herhangi bir veri bulut ortamına gönderilmez. Tüm işlemler yerel donanımda gerçekleşir.

Kullanılan açık kaynak bileşenler:

- [Ollama](https://ollama.ai) — MIT Lisansı
- [LangChain](https://langchain.com) — MIT Lisansı
- [ChromaDB](https://trychroma.com) — Apache 2.0 Lisansı
- [Streamlit](https://streamlit.io) — Apache 2.0 Lisansı
- [nginx](https://nginx.org) — BSD-benzeri Lisans
- [llama3.2](https://llama.meta.com) — Meta Llama 3 Community License


Bu notlar yapay zekadan alınmış olup yönerge olarak kullanılmaktadır.
---

*Son güncelleme: Haziran 2026*

# ai-agent-private
First aiAgent project
We gonna try to build our first ai agent project

1. Download and install docker first
2. Start to buil docker for ai agent container system
in powershell  
  2.1
   docker --version
   docker compose version     both give you version then
   mkdir C:\ai-agent
   mkdir C:\ai-agent\models
   mkdir C:\ai-agent\chroma-data
   mkdir C:\ai-agent\agent-data
   mkdir C:\ai-agent\logs
   mkdir C:\ai-agent\agent

   2.2 create your .yml file but for now it will be empty
   docker-compose.yml

   2.3
   cd C:\ai-agent
   docker compose up -d
   after these steps in your docker desktop, three container will be green

   2.4
   upload first model - upload with internet and later you can use them offline
   Llama 3.2 (3B, ~2GB — hızlı başlangıç için iyi)
   docker exec ollama ollama pull llama3.2
    
   Embedding modeli (RAG için gerekecek)
   docker exec ollama ollama pull nomic-embed-text

   next step...
    
   
   
