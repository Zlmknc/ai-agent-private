# 🔒 Yerel AI Agent — Kişisel & Güvenli

> Tamamen yerel çalışan, dışarıya kapalı, siber güvenlik önlemleri alınmış kişisel AI agent projesi.
> Verileriniz bu cihazdan asla çıkmaz.

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
- [Yol Haritası](#yol-haritası)

---

## Proje Özeti

Bu proje; internet bağlantısı gerektirmeyen, bulut servislerine veri göndermeyen, tamamen kendi donanımınızda çalışan bir AI agent sistemidir. Docker ile izole edilmiş container mimarisi sayesinde her servis birbirinden bağımsız çalışır ve dış ağa erişim tamamen engellenir.

**Ne yapabilirsiniz:**
- Kendi kurallarınızı tanımladığınız bir AI asistanla sohbet edebilirsiniz
- PDF, Word ve TXT belgelerinizi sisteme tanıtarak sorgu yapabilirsiniz
- Matematiksel hesaplamalar, not alma ve dosya okuma araçlarını kullanabilirsiniz
- Kısa ve uzun süreli hafıza sayesinde agent geçmiş bilgileri hatırlar
- Güvenlik logları ile sistemdeki her olayı izleyebilirsiniz

---

## Mimari

```
┌─────────────────────────────────────────────────────┐
│                    HOST MAKİNE                       │
│              Windows 10/11 · Docker Desktop          │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │         DOCKER İZOLASYON KATMANI             │   │
│  │           internal: true ağı                 │   │
│  │                                              │   │
│  │  ┌─────────────┐     ┌──────────────────┐   │   │
│  │  │   Ollama    │◄────│   AI Agent       │   │   │
│  │  │  llama3.2   │     │  LangChain +     │   │   │
│  │  │ port: 11434 │     │  Streamlit       │   │   │
│  │  └─────────────┘     │  port: 8501      │   │   │
│  │                      └────────┬─────────┘   │   │
│  │  ┌─────────────┐             │              │   │
│  │  │  ChromaDB   │◄────────────┘              │   │
│  │  │  Vektör DB  │                            │   │
│  │  │ port: 8000  │                            │   │
│  │  └─────────────┘                            │   │
│  └──────────────────────────────────────────────┘   │
│                        │                            │
│              127.0.0.1:8501 (sadece localhost)       │
└─────────────────────────────────────────────────────┘
         │
   Kullanıcı Tarayıcısı
   http://localhost:8501
```

**Ağ güvenliği:** `internal: true` ile tüm container'lar dış internetten tamamen yalıtılmıştır. Container'lar yalnızca kendi iç ağlarında birbirleriyle iletişim kurabilir.

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
| Ağ İzolasyonu | Docker internal network | ✅ |
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

> GPU olmadan da çalışır; yanıt süresi daha uzun olur.

### Yazılım

- Windows 10/11 (64-bit)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (en güncel sürüm)
- PowerShell 5.1 veya üzeri

---

## Kurulum

### 1. Depoyu klonla veya klasörü oluştur

```powershell
mkdir C:\ai-agent
cd C:\ai-agent
mkdir models, chroma-data, agent-data, logs, agent
```

### 2. Yapılandırma dosyalarını oluştur

Aşağıdaki bölümlerde verilen dosyaları ilgili konumlara kopyala.

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

### 5. İzolasyonu geri aç

`docker-compose.yml` dosyasında `# internal: true` satırını tekrar aç:

```yaml
networks:
  ai-internal:
    driver: bridge
    internal: true    ← # kaldırıldı
```

```powershell
docker compose down
docker compose up -d
```

### 6. Arayüzü aç

```
http://localhost:8501
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

## Yapılandırma Dosyaları

### `docker-compose.yml`

```yaml
networks:
  ai-internal:
    driver: bridge
    internal: true

services:

  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    networks:
      - ai-internal
    volumes:
      - C:/ai-agent/models:/root/.ollama
    restart: unless-stopped

  chromadb:
    image: chromadb/chroma:latest
    container_name: chromadb
    networks:
      - ai-internal
    volumes:
      - C:/ai-agent/chroma-data:/chroma/chroma
    environment:
      - IS_PERSISTENT=TRUE
    restart: unless-stopped

  agent:
    build: ./agent
    container_name: ai-agent
    networks:
      - ai-internal
    ports:
      - "127.0.0.1:8501:8501"
    volumes:
      - C:/ai-agent/agent:/app
      - C:/ai-agent/agent-data:/app/data
      - C:/ai-agent/logs:/app/logs
    environment:
      - OLLAMA_URL=http://ollama:11434
      - CHROMA_URL=http://chromadb:8000
    depends_on:
      - ollama
      - chromadb
    restart: unless-stopped
```

### `agent/Dockerfile`

```dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd -m -u 1000 agentuser
USER agentuser

CMD ["streamlit", "run", "app.py", \
     "--server.address=0.0.0.0", \
     "--server.port=8501", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
```

### `agent/requirements.txt`

```
langchain==0.3.0
langchain-community==0.3.0
langchain-ollama==0.2.0
chromadb==0.5.0
sentence-transformers==3.0.0
streamlit==1.38.0
ollama==0.3.0
pypdf==4.3.0
python-docx==1.1.2
unstructured==0.15.0
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

## Sorun Giderme

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

### Streamlit açılmıyor

Port kontrolü:

```powershell
netstat -an | findstr 8501
```

`127.0.0.1:8501` görünüyorsa tarayıcıda `http://localhost:8501` adresine gidin.

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

# Sadece agent'ı yeniden başlat
docker compose restart agent

# Logları izle
docker logs ai-agent --tail 50 -f

# Yüklü modelleri listele
docker exec ollama ollama list

# Container'a terminal aç
docker exec -it ai-agent bash

# Image'ı yeniden derle
docker compose build --no-cache agent

# Tüm container durumları
docker compose ps
```

---

## Yol Haritası

### Tamamlananlar ✅

- Docker ile tam izolasyon
- Ollama + llama3.2 yerel LLM
- ChromaDB vektör veritabanı
- Streamlit arayüzü
- Kural motoru ve sistem prompt
- Araç sistemi (hesap, not, dosya)
- Kısa ve uzun süreli hafıza
- Prompt injection koruması
- Hız sınırlama
- Güvenlik audit loglama
- RAG (PDF, Word, TXT desteği)

### Planlananlar 🔲

- **n8n Workflow Otomasyonu** — görsel iş akışı tasarımı
- **LoRA Fine-tuning** — modeli kendi verilerinizle özelleştirme
- **Prometheus + Grafana** — kaynak kullanımı izleme
- **Çoklu model desteği** — farklı görevler için farklı modeller
- **Ses arayüzü** — konuşarak sorgu yapma (Whisper)
- **Takvim/ajanda entegrasyonu** — yerel takvim okuma/yazma
- **Otomatik yedekleme** — veri ve model yedekleme

---

## Lisans ve Gizlilik

Bu proje tamamen kişisel kullanım içindir. Herhangi bir veri bulut ortamına gönderilmez. Tüm işlemler yerel donanımınızda gerçekleşir.

Kullanılan açık kaynak bileşenler:

- [Ollama](https://ollama.ai) — MIT Lisansı
- [LangChain](https://langchain.com) — MIT Lisansı
- [ChromaDB](https://trychroma.com) — Apache 2.0 Lisansı
- [Streamlit](https://streamlit.io) — Apache 2.0 Lisansı
- [llama3.2](https://llama.meta.com) — Meta Llama 3 Community License

---

*Son güncelleme: Mayıs 2026*
