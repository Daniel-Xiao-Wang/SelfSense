# SelfSense

Symptom-guided screening demo. Search what you feel, build a short symptom list, and get ranked condition suggestions from an ensemble of machine-learning classifiers.

## Stack

| Layer | Path | Tech |
|-------|------|------|
| Frontend | `react.b/` | React (Create React App) |
| Backend | `backend/` | Flask + CORS |
| Models | `ml/` | Random Forest, Bernoulli NB, Logistic Regression |

The API trains (or loads) a soft-voting ensemble on `ml/DataSet/Training.csv`, then ranks only conditions that actually co-occur with the selected symptoms in that data.

## Prerequisites

- Python 3.10+ (3.12 works)
- Node.js + npm

## Setup

### Backend

From the repo root:

```bash
pip install flask flask-cors pandas scikit-learn joblib
python -m flask --app backend run
```

Or on Windows:

```bash
.\start-backend.bat
```

API: [http://127.0.0.1:5000](http://127.0.0.1:5000)

Useful endpoints:

- `GET /symptoms` — symptom catalog
- `GET /generate/<symptoms>` — comma-separated symptom names (URL-encoded)
- `GET /info` — service metadata

Retrain and save the model bundle:

```bash
python ml/retrain.py
```

Optional accuracy checks:

```bash
python ml/eval_accuracy.py
```

### Frontend

```bash
cd react.b
npm install
npm start
```

App: [http://localhost:3000](http://localhost:3000)

The UI expects the backend at `http://127.0.0.1:5000`.

## How it works

1. Search and select up to 8 symptoms.
2. Click **Diagnose**.
3. SelfSense returns ranked conditions with confidence scores, plus a per-model breakdown.

**Note:** This is a demo trained on a public symptom–disease dataset. It is not medical advice.

## License

See [LICENSE](LICENSE).
