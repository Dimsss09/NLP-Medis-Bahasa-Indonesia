# 4. Struktur Repo & Setup

<aside>
🧱

Panduan struktur repositori dan penyiapan lingkungan agar proyek rapi dan mudah diikuti.

</aside>

## Struktur folder yang disarankan

```
medical-ner-id/
├── data/
│   ├── raw/            # data mentah
│   ├── clean/          # data bersih
│   └── annotated/      # data BIO (train/val/test)
├── notebooks/          # eksplorasi & eksperimen
├── src/
│   ├── data_prep.py    # pembersihan & split data
│   ├── train.py        # fine-tuning IndoBERT
│   ├── evaluate.py     # evaluasi seqeval
│   └── predict.py      # inferensi
├── models/             # model terlatih (jangan commit file besar)
├── reports/            # metrik, grafik, confusion matrix
├── app/
│   └── demo.py         # aplikasi Streamlit/Gradio
├── requirements.txt
├── .gitignore
└── README.md
```

## requirements.txt (contоh awal)

```
transformers
torch
datasets
seqeval
scikit-learn
pandas
numpy
streamlit
```

## Setup lingkungan

```bash
# 1. Buat virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 2. Pasang dependensi
pip install -r requirements.txt

# 3. Jalankan training
python src/train.py

# 4. Jalankan demo
streamlit run app/demo.py
```

## .gitignore (poin penting)

```
venv/
__pycache__/
*.pyc
models/*.bin
data/raw/
.env
```

## Tips

- Jangan commit file model besar / data sensitif — gunakan `.gitignore` atau Git LFS.
- Simpan konfigurasi (learning rate, epoch) dalam satu file `config.yaml` agar mudah diatur.
- Tulis `README.md` seolah untuk orang yang belum tahu apa-apa tentang proyek.