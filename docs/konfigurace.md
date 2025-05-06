## ⚙️ Konfigurace

Chování systému je řízeno pomocí souboru `config.yml`, který se nachází v kořenovém adresáři projektu. Tento soubor se načítá automaticky a slouží k nastavení všech hlavních parametrů inferenčního procesu. Uživatel jej může **ručně upravit** podle potřeby.

---

### 🔤 OCR – Rozpoznávání textu

| Parametr           | Popis                                 | Možné hodnoty                          | Výchozí hodnota |
|--------------------|----------------------------------------|----------------------------------------|------------------|
| `ocr_method`       | Zvolená metoda OCR                    | `tesseract`, `easyocr`, `paddleocr`   | `tesseract`      |
| `TESS_LANG`        | Jazyková sada Tesseract OCR           | `ces`, `eng`, `cesLEGACY`, ...        | `ces`            |
| `TESS_OEM`         | Typ enginu (OCR Engine Mode)          | `0`, `1`, `2`, `3`                     | `2`              |
| `TESS_PSM`         | Režim rozpoznávání rozvržení stránky  | `3`, `6`, `11`, `12`                   | `12`             |
| `EASY_LANG`        | Jazyk pro EasyOCR                     | `"cs"`, `"en"`, `"de"`, ...           | `"cs"`           |
| `EASY_GPU`         | Použít GPU pro EasyOCR?               | `True`, `False`                        | `False`          |
| `EASY_RECOGNITION_MODEL` | Model pro rozpoznávání textu    | `"lating_1"`, `"lating_2"`                | `"latin_g2"`     |
| `EASY_DETECTION_MODEL`   | Model pro detekci textu         | `"craft"`, `"db18"`                      | `"craft"`        |
| `PADDLE_LANG`      | Jazyk pro PaddleOCR                   | `"cs"`, `"en"`, ...                   | `"cs"`           |
| `PADDLE_USE_GPU`   | Použít GPU pro PaddleOCR?             | `True`, `False`                        | `False`          |

---

### 🎬 Segmentace videa

| Parametr                | Popis                                  | Možné hodnoty                        | Výchozí |
|-------------------------|-----------------------------------------|--------------------------------------|---------|
| `scene_detect_method`   | Vybraná metoda segmentace videa        | `ffprobe`, `scenedetect`, `transnet`, `autoshot` | `scenedetect` |
| `PYSCENE_THRESHOLD`     | Prah pro detekci scén (nižší = citlivější) | libovolné číslo ≥ 0              | `27`    |
| `PYSCENE_MIN_SCENE_LEN` | Minimální délka scény (v počtu snímků) | celé číslo ≥ 0                        | `15`    |
| `TRANSNET_MODEL_DIR`    | Cesta k modelu TransNet V2             | relativní cesta                      | `TransNetV2/inference/transnetv2-weights` |
| `TRANSNET_THRESHOLD`    | Prahová hodnota detekce u TransNet     | 0.0 – 1.0                             | `0.5`   |
| `AUTOSHOT_THRESHOLD`    | Prah pro detekci u Autoshot            | 0.0 – 1.0                             | `0.296` |
| `AUTOSHOT_MODEL_PATH`   | Cesta k modelu Autoshot                | relativní cesta                      | `Autoshot/weights.pth` |

*Poznámka: metoda `ffprobe` nevyužívá žádné konfigurační parametry.*

---

### 👤 Detekce a identifikace osob

| Parametr           | Popis                                         | Výchozí hodnota                        |
|--------------------|-----------------------------------------------|----------------------------------------|
| `PEOPLE_DB_PATH`   | Cesta ke složce s databází obličejů           | `PeopleFinder/People/database`         |

---

### 📺 Detekce televizních log

| Parametr           | Popis                                         | Výchozí hodnota        |
|--------------------|-----------------------------------------------|--------------------------|
| `YOLO_MODEL_PATH`  | Cesta k natrénovanému modelu YOLO             | `yolo/yolov5s.pt`        |

---

### 🌐 API

| Parametr    | Popis                                 | Výchozí hodnota                                    |
|-------------|----------------------------------------|----------------------------------------------------|
| `API_URL`   | URL, na kterou se odesílají inference požadavky | `http://localhost:8000/api/v1/NewsVideoMiner/inference` |

---

Všechny cesty v konfiguračním souboru jsou relativní vůči kořenovému adresáři projektu.

