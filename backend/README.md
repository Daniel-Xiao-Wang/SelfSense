# Backend

Flask API for SelfSense. Serves the symptom catalog and diagnosis endpoints, and loads the trained ensemble from `ml/`.

## Run

From the **repo root**:

```bash
pip install flask flask-cors pandas scikit-learn joblib
python -m flask --app backend run
```

Windows helper:

```bash
.\start-backend.bat
```

Listens on [http://127.0.0.1:5000](http://127.0.0.1:5000).
