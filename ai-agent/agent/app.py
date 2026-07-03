import streamlit as st
import json
import os
import math
from datetime import datetime

from langchain_ollama import OllamaLLM
from langchain.memory import ConversationBufferWindowMemory

from guvenlik import (
    girdi_dogrula,
    cikti_filtrele,
    hiz_kontrol,
    guvenlik_log,
    log_ozeti,
)
from rag import (
    belge_ekle,
    rag_baglami_olustur,
    meta_yukle,
    YUKLEMELER,
)

# ════════════════════════════════════════════
# 1. KURAL MOTORU
# ════════════════════════════════════════════

KURALLAR = """Sen yalnızca bu cihazda çalışan, tamamen özel bir AI asistanısın.

Kurallar:
1. Dış servislere bağlanma, yalnızca yerel bilginle yanıt ver.
2. Kişisel verileri asla log dosyasına yazma.
3. Belirsiz sorularda açıklama iste.
4. Türkçe sorulara Türkçe yanıt ver.
5. Her yanıtın sonunda kaynağını belirt (kendi bilgin mi, belgelerden mi).
6. Emin olmadığın konularda "bilmiyorum" de, uydurma.
7. Hassas konularda (sağlık, hukuk, finans) "uzman görüşü al" uyarısı ekle.

KİŞİLİK:
- Doğrudan ve net ol, gereksiz uzatma.
- Teknik konularda kod örneği ver.
- Hataları nazikçe düzelt.

Şu anki tarih ve saat: {datetime}
"""

# ════════════════════════════════════════════
# 2. ARAÇ SİSTEMİ
# ════════════════════════════════════════════

NOTLAR_DOSYASI = "/app/data/notlar.json"
os.makedirs("/app/data", exist_ok=True)
os.makedirs("/app/logs", exist_ok=True)


def notlari_yukle():
    if os.path.exists(NOTLAR_DOSYASI):
        with open(NOTLAR_DOSYASI, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def not_kaydet(baslik, icerik):
    notlar = notlari_yukle()
    notlar.append({
        "id": len(notlar) + 1,
        "baslik": baslik,
        "icerik": icerik,
        "tarih": datetime.now().strftime("%d.%m.%Y %H:%M"),
    })
    with open(NOTLAR_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(notlar, f, ensure_ascii=False, indent=2)
    return f"Not kaydedildi: '{baslik}'"


def dosya_oku(dosya_adi):
    guvenli_yol = os.path.join("/app/data", os.path.basename(dosya_adi))
    if not os.path.exists(guvenli_yol):
        return f"Dosya bulunamadı: {dosya_adi}"
    with open(guvenli_yol, "r", encoding="utf-8") as f:
        return f.read()[:3000]  # ilk 3000 karakter


def hesapla(ifade):
    try:
        izinli = set("0123456789+-*/().,% ")
        if not all(c in izinli for c in ifade):
            return "Geçersiz ifade — sadece matematik operatörleri kullanılabilir."
        sonuc = eval(ifade, {"__builtins__": {}}, {
            "abs": abs, "round": round,
            "sqrt": math.sqrt, "pi": math.pi,
        })
        return f"Sonuç: {sonuc}"
    except Exception as e:
        return f"Hesaplama hatası: {e}"


def arac_calistir(mesaj):
    """Kullanıcı mesajına göre yerel aracı tespit edip çalıştırır.
    Eşleşme yoksa None döner — bu durumda mesaj modele gönderilir."""
    mesaj_lower = mesaj.lower()

    if mesaj_lower.startswith("not kaydet:"):
        parcalar = mesaj[11:].split("|")
        if len(parcalar) == 2:
            return not_kaydet(parcalar[0].strip(), parcalar[1].strip())
        return "Format: 'not kaydet: Başlık | İçerik'"

    if mesaj_lower.startswith("notlarım"):
        notlar = notlari_yukle()
        if notlar:
            return "\n".join(f"[{n['id']}] {n['baslik']} ({n['tarih']})" for n in notlar)
        return "Henüz not yok."

    if mesaj_lower.startswith("hesapla:"):
        return hesapla(mesaj[8:].strip())

    if mesaj_lower.startswith("dosya oku:"):
        return dosya_oku(mesaj[10:].strip())

    return None


# ════════════════════════════════════════════
# 3. HAFIZA SİSTEMİ (uzun süreli)
# ════════════════════════════════════════════

UZUN_HAFIZA_DOSYASI = "/app/data/uzun_hafiza.json"


def uzun_hafiza_yukle():
    if os.path.exists(UZUN_HAFIZA_DOSYASI):
        with open(UZUN_HAFIZA_DOSYASI, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def uzun_hafizaya_kaydet(bilgi):
    hafiza = uzun_hafiza_yukle()
    hafiza.append({
        "bilgi": bilgi,
        "tarih": datetime.now().strftime("%d.%m.%Y %H:%M"),
    })
    with open(UZUN_HAFIZA_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(hafiza, f, ensure_ascii=False, indent=2)


def uzun_hafiza_ozeti():
    hafiza = uzun_hafiza_yukle()
    if not hafiza:
        return ""
    son_10 = hafiza[-10:]
    return "\n".join(f"- {h['bilgi']}" for h in son_10)


# ════════════════════════════════════════════
# 4. MODEL ve ZİNCİR (kısa süreli hafıza + RAG bağlamı)
# ════════════════════════════════════════════

@st.cache_resource
def model_yukle():
    return OllamaLLM(
        model="llama3.2",
        base_url=os.getenv("OLLAMA_URL", "http://ollama:11434"),
        temperature=0.7,
    )


def zincir_olustur(uzun_hafiza: str) -> ConversationBufferWindowMemory:
    """Artık bir LangChain Chain nesnesi değil, sadece hafıza nesnesini döndürür.
    Sistem promptu ve bağlam, yanıt üretilirken elle birleştirilir — bu sayede
    ConversationChain'in 'tam olarak 1 input değişkeni' kısıtlamasına takılmayız."""
    return ConversationBufferWindowMemory(
        k=10,
        human_prefix="Kullanıcı",
        ai_prefix="Asistan",
    )


def yanit_uret(memory: ConversationBufferWindowMemory, kullanici_mesaji: str, baglam: str, uzun_hafiza: str) -> str:
    """Sistem kuralları + uzun hafıza + RAG bağlamı + konuşma geçmişini
    tek bir prompt'ta birleştirip modele gönderir, yanıtı hafızaya kaydeder."""
    llm = model_yukle()

    sistem = KURALLAR.format(datetime=datetime.now().strftime("%d.%m.%Y %H:%M"))
    if uzun_hafiza:
        sistem += f"\n\nBİLİNEN BİLGİLER (uzun hafıza):\n{uzun_hafiza}"

    gecmis = memory.load_memory_variables({}).get("history", "")

    tam_prompt = f"""{sistem}

{baglam}

Konuşma geçmişi:
{gecmis}

Kullanıcı: {kullanici_mesaji}
Asistan:"""

    yanit = llm.invoke(tam_prompt)
    memory.save_context({"input": kullanici_mesaji}, {"output": yanit})
    return yanit


# ════════════════════════════════════════════
# 5. ARAYÜZ
# ════════════════════════════════════════════

st.set_page_config(page_title="Yerel AI Agent", page_icon="🔒", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "chain" not in st.session_state:
    st.session_state.chain = zincir_olustur(uzun_hafiza_ozeti())

# ── Sol panel ──────────────────────────────────────────────
with st.sidebar:
    st.title("🔒 Yerel AI Agent")
    st.caption("Tamamen offline · Verileriniz bu cihazdan çıkmaz")
    st.divider()

    st.subheader("Durum")
    st.success("🟢 Ollama: llama3.2")
    st.success("🟢 ChromaDB bağlı")
    st.info("🔒 Ağ: izole")

    st.divider()
    st.subheader("Araçlar")
    st.markdown("""
**Kullanım örnekleri:**
- `not kaydet: Başlık | İçerik`
- `notlarım`
- `hesapla: 1500 * 0.18`
- `dosya oku: rapor.txt`
    """)

    st.divider()
    st.subheader("Uzun Hafıza")
    yeni_bilgi = st.text_input("Hatırlamasını istediğin bilgi:")
    if st.button("Hafızaya ekle") and yeni_bilgi:
        uzun_hafizaya_kaydet(yeni_bilgi)
        st.session_state.chain = zincir_olustur(uzun_hafiza_ozeti())
        st.success("Kaydedildi!")

    hafiza = uzun_hafiza_yukle()
    if hafiza:
        with st.expander(f"Kayıtlı bilgiler ({len(hafiza)})"):
            for h in hafiza[-5:]:
                st.caption(f"• {h['bilgi']}")

    st.divider()
    st.subheader("📂 Belge Yükle")
    yuklenen = st.file_uploader(
        "PDF, Word veya TXT yükle",
        type=["pdf", "docx", "txt", "md"],
        accept_multiple_files=True,
    )
    if yuklenen:
        etiket_girdisi = st.text_input("Etiket (opsiyonel):", placeholder="proje, sözleşme...")
        etiketler = [e.strip() for e in etiket_girdisi.split(",") if e.strip()]
        if st.button("Sisteme Ekle", use_container_width=True):
            for dosya in yuklenen:
                gecici_yol = os.path.join(YUKLEMELER, dosya.name)
                with open(gecici_yol, "wb") as f:
                    f.write(dosya.getbuffer())
                with st.spinner(f"{dosya.name} işleniyor..."):
                    sonuc = belge_ekle(gecici_yol, etiketler)
                if sonuc["basari"]:
                    st.success(f"✅ {sonuc['dosya']} — {sonuc['parca_sayisi']} parça")
                else:
                    st.error(f"❌ {sonuc['hata']}")

    meta = meta_yukle()
    if meta:
        with st.expander(f"Yüklü belgeler ({len(meta)})"):
            for b in meta:
                etiket_str = ", ".join(b["etiketler"]) if b["etiketler"] else "—"
                st.caption(f"📄 **{b['dosya_adi']}** · {b['parca_sayisi']} parça · etiket: {etiket_str} · {b['tarih']}")

    st.divider()
    st.subheader("Güvenlik İzleme")
    ozet = log_ozeti()
    col1, col2, col3 = st.columns(3)
    col1.metric("24s Olay", ozet["toplam"])
    col2.metric("⚠️ Uyarı", ozet["uyari"])
    col3.metric("⛔ Tehdit", ozet["tehdit"])

    if st.button("Güvenlik logunu gör", use_container_width=True):
        if os.path.exists("/app/logs/guvenlik.log"):
            with open("/app/logs/guvenlik.log", "r", encoding="utf-8") as f:
                satirlar = f.readlines()[-20:]
            for s in satirlar:
                try:
                    kayit = json.loads(s)
                    renk = {"INFO": "🟢", "UYARI": "🟡", "TEHDIT": "🔴"}.get(kayit["seviye"], "⚪")
                    st.caption(f"{renk} {kayit['zaman'][:16]} — {kayit['olay']}")
                except Exception:
                    pass
        else:
            st.caption("Henüz log yok.")

    st.divider()
    if st.button("Sohbeti temizle", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chain = zincir_olustur(uzun_hafiza_ozeti())
        st.rerun()

# ── Ana sohbet alanı ────────────────────────────────────────
st.header("Sohbet")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "arac" in msg:
            st.caption(f"🔧 Araç: {msg['arac']}")

if prompt := st.chat_input("Bir şey sor veya araç kullan..."):

    # ── Güvenlik kontrolleri ──────────────────
    hiz = hiz_kontrol()
    if not hiz["izin"]:
        st.warning(f"Çok fazla istek. {hiz['kalan_sure']} saniye bekle.")
        st.stop()

    dogrulama = girdi_dogrula(prompt)
    if not dogrulama["guvenli"]:
        guvenlik_log("girdi_reddedildi", detay={"sebep": dogrulama["sebep"]}, seviye="TEHDIT")
        st.error(f"⛔ Güvenlik: {dogrulama['sebep']}")
        st.stop()

    # ── Normal akış ──────────────────────────
    guvenlik_log("mesaj_alindi", seviye="INFO")
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Düşünüyor..."):
            try:
                arac_sonucu = arac_calistir(prompt)

                if arac_sonucu:
                    temiz_cikti = cikti_filtrele(arac_sonucu)
                    st.markdown(temiz_cikti)
                    st.caption("🔧 Araç kullanıldı")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": temiz_cikti,
                        "arac": "yerel araç",
                    })
                else:
                    baglam = rag_baglami_olustur(prompt)
                    yanit = yanit_uret(
                        st.session_state.chain,
                        prompt,
                        baglam,
                        uzun_hafiza_ozeti(),
                    )
                    temiz_yanit = cikti_filtrele(yanit)

                    guvenlik_log("yanit_gonderildi", seviye="INFO")
                    st.markdown(temiz_yanit)

                    if baglam:
                        with st.expander("📄 Kaynak belgeler"):
                            st.caption(baglam[:800])

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": temiz_yanit,
                    })

            except Exception as e:
                guvenlik_log("hata", detay={"hata": str(e)}, seviye="UYARI")
                st.error(f"Hata: {e}")