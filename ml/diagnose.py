import os
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import BernoulliNB
from sklearn.preprocessing import LabelEncoder


class Diagnosor:
    """Symptom-to-disease ensemble trained on the local dataset."""

    DATA_PATH = "DataSet/Training.csv"
    MODEL_PATH = "model_bundle.joblib"

    def __init__(self, force_retrain: bool = False):
        dir_path = Path(os.path.dirname(os.path.realpath(__file__)))
        self.csv_path = dir_path / self.DATA_PATH
        self.model_path = dir_path / self.MODEL_PATH

        if force_retrain or not self.model_path.exists():
            self._train_and_save()
        else:
            self._load()

    def _load_frame(self) -> pd.DataFrame:
        data = pd.read_csv(self.csv_path).dropna(axis=1)
        # pandas may rename a duplicated fluid_overload column
        drop_cols = [c for c in data.columns if c.startswith("fluid_overload.")]
        if drop_cols:
            data = data.drop(columns=drop_cols)
        return data

    def _build_symptom_index(self, columns) -> dict:
        symptom_index = {}
        for index, value in enumerate(columns):
            symptom = " ".join(part.capitalize() for part in value.split("_"))
            symptom_index[symptom] = index
        return symptom_index

    def _make_ensemble(self) -> VotingClassifier:
        rf = RandomForestClassifier(
            n_estimators=300,
            class_weight="balanced_subsample",
            random_state=18,
            n_jobs=-1,
        )
        bnb = BernoulliNB(alpha=0.3)
        lr = LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            solver="lbfgs",
        )
        return VotingClassifier(
            estimators=[("rf", rf), ("bnb", bnb), ("lr", lr)],
            voting="soft",
            weights=[2, 1, 1],
        )

    def _train_and_save(self):
        print("Training models from:", self.csv_path)
        data = self._load_frame()
        encoder = LabelEncoder()
        y = encoder.fit_transform(data["prognosis"])
        X = data.drop(columns=["prognosis"])

        ensemble = self._make_ensemble()
        ensemble.fit(X, y)

        # Keep named estimators available for breakdown views.
        rf = ensemble.named_estimators_["rf"]
        bnb = ensemble.named_estimators_["bnb"]
        lr = ensemble.named_estimators_["lr"]

        symptom_index = self._build_symptom_index(X.columns)
        bundle = {
            "ensemble": ensemble,
            "rf": rf,
            "bnb": bnb,
            "lr": lr,
            "encoder": encoder,
            "feature_columns": list(X.columns),
            "symptom_index": symptom_index,
            "training_X": X.astype("int8"),
            "training_y": y.astype("int32"),
        }
        joblib.dump(bundle, self.model_path)
        print("Saved model bundle to:", self.model_path)
        self._apply_bundle(bundle)

    def _load(self):
        print("Loading model bundle from:", self.model_path)
        bundle = joblib.load(self.model_path)
        self._apply_bundle(bundle)

    def _apply_bundle(self, bundle):
        self.ensemble = bundle["ensemble"]
        self.rf = bundle["rf"]
        self.bnb = bundle["bnb"]
        self.lr = bundle["lr"]
        self.encoder = bundle["encoder"]
        self.feature_columns = bundle["feature_columns"]
        self.symptom_index = bundle["symptom_index"]
        self.training_X = bundle["training_X"]
        self.training_y = bundle["training_y"]
        self.data_dict = {
            "symptom_index": self.symptom_index,
            "predictions_classes": self.encoder.classes_,
        }

    def getSymptoms(self):
        return list(self.symptom_index.keys())

    def _vectorize(self, inputed_symptoms):
        values = [0] * len(self.feature_columns)
        selected_cols = []
        for symptom in inputed_symptoms:
            if symptom not in self.symptom_index:
                raise KeyError(f"Unknown symptom: {symptom}")
            idx = self.symptom_index[symptom]
            values[idx] = 1
            selected_cols.append(self.feature_columns[idx])
        frame = pd.DataFrame([values], columns=self.feature_columns)
        return frame, selected_cols

    def _compatible_class_indices(self, selected_cols):
        """Diseases that appear in training with all selected symptoms present."""
        if not selected_cols:
            return np.array([], dtype=int)

        mask = np.ones(len(self.training_X), dtype=bool)
        for col in selected_cols:
            mask &= self.training_X[col].to_numpy() == 1

        if not mask.any():
            return np.array([], dtype=int)
        return np.unique(self.training_y[mask])

    def _top_label(self, estimator, frame, allowed):
        proba = estimator.predict_proba(frame)[0]
        if allowed.size:
            filtered = np.full_like(proba, -1.0)
            filtered[allowed] = proba[allowed]
            idx = int(np.argmax(filtered))
        else:
            idx = int(np.argmax(proba))
        return self.encoder.classes_[idx]

    def generate(self, inputed_symptoms):
        frame, selected_cols = self._vectorize(inputed_symptoms)
        allowed = self._compatible_class_indices(selected_cols)

        ensemble_proba = self.ensemble.predict_proba(frame)[0]
        if allowed.size:
            scores = np.zeros_like(ensemble_proba)
            scores[allowed] = ensemble_proba[allowed]
            total = scores.sum()
            if total > 0:
                scores = scores / total
            else:
                scores = ensemble_proba
        else:
            scores = ensemble_proba

        order = np.argsort(scores)[::-1]
        ranked = []
        diseases = []
        for idx in order:
            score = float(scores[idx])
            if score <= 0:
                break
            name = self.encoder.classes_[idx]
            ranked.append({"name": name, "score": score})
            diseases.append(name)
            if len(ranked) >= 5:
                break

        rf_prediction = self._top_label(self.rf, frame, allowed)
        nb_prediction = self._top_label(self.bnb, frame, allowed)
        lr_prediction = self._top_label(self.lr, frame, allowed)

        return {
            "rf_model_prediction": rf_prediction,
            "naive_bayes_prediction": nb_prediction,
            "svm_model_prediction": lr_prediction,  # kept for frontend compatibility
            "logistic_regression_prediction": lr_prediction,
            "final_prediction": diseases[:1],
            "diseases": diseases,
            "ranked": ranked,
        }
