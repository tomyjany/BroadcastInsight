## 📥 Instalace

Projekt lze spustit dvěma způsoby: pomocí Dockeru (doporučeno) nebo lokálně ve vlastním virtuálním prostředí.

---

### 🐳 Instalace přes Docker (doporučeno)

1. **Klonujte repozitář:**

   ```bash
   git clone https://github.com/tvminer/NewsVideoMiner.git (zatím nedostupné)
   cd NewsVideoMiner-docs
   ```

2. **Spusťte službu:**

   ```bash
   docker compose up -d
   ```

   Tento příkaz vytvoří kontejner s potřebným prostředím a automaticky spustí:
   - REST API (dostupné na adrese `http://localhost:8000`)
   - Webové rozhraní v prostředí Streamlit (dostupné na `http://localhost:8051`)

---

### 🧪 Lokální instalace bez Dockeru

1. **Ujistěte se, že máte Python ve verzi 3.10.x**

2. **Klonujte repozitář:**

   ```bash
   git clone https://github.com/tvminer/NewsVideoMiner.git
   cd NewsVideoMiner
   ```

3. **Vytvořte a aktivujte virtuální prostředí:**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux / macOS
   .venv\Scripts\activate     # Windows
   ```

4. **Nainstalujte závislosti:**

   ```bash
   pip install --upgrade pip
   pip install --no-deps --no-cache-dir --upgrade -r requirements.txt
   ```

5. **Ujistěte se, že máte nainstalované tyto systémové knihovny (Linux):**

   - `ffmpeg`
   - `tesseract-ocr` (včetně jazykových dat pro češtinu – např. `ces.traineddata`)
   - `poppler-utils`
   - další závislosti uvedené v Dockerfile (např. `libgl1`, `libglib2.0-0`, atd.)

6. **Spusťte rozhraní:**

   ```bash
   uvicorn api:app --host 0.0.0.0 --port 8000 &
   streamlit run streamlit_app.py --server.port 8051 --server.address 0.0.0.0
   ```

   Po spuštění najdete:
   - REST API na `http://localhost:8000`
   - Streamlit GUI na `http://localhost:8051`

---

### 📦 Stažení modelů

Pro správné fungování systému je nutné stáhnout předtrénované modely a uložit je na cesty uvedené v `config.yml`.  
Více informací o konfiguraci najdete v sekci [⚙️ Konfigurace](konfigurace.md).

#### 🔹 1. Autoshot

- Repozitář: [https://github.com/wentaozhu/AutoShot](https://github.com/wentaozhu/AutoShot)
- Váha: `ckpt_0_200_0.pth`
- Cesta: `Autoshot/ckpt_0_200_0.pth`

#### 🔹 2. TransNet V2

- Repozitář: [https://github.com/soCzech/TransNetV2](https://github.com/soCzech/TransNetV2)
- Cesta pro váhy: `TransNetV2/inference/transnetv2-weights`

#### 🔹 3. YOLO model pro detekci log

- Repozitář: [https://github.com/ultralytics/ultralytics](https://github.com/ultralytics/ultralytics)
- Model: `yolov11s.pt`
- Cesta: `yolo/yolov11s.pt`

---
