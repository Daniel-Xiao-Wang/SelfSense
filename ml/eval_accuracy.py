import pandas as pd
from diagnose import Diagnosor

df = pd.read_csv("DataSet/Training.csv").dropna(axis=1)
if "fluid_overload.1" in df.columns:
    df = df.drop(columns=["fluid_overload.1"])

profiles = {}
for disease, group in df.groupby("prognosis"):
    rates = group.drop(columns="prognosis").mean()
    core = rates[rates >= 0.8].sort_values(ascending=False)
    profiles[disease] = list(core.index)

d = Diagnosor()


def to_display(cols):
    return [" ".join(p.capitalize() for p in c.split("_")) for c in cols]


results = []
for disease, cols in profiles.items():
    if not cols:
        continue
    rates = df[df["prognosis"] == disease].drop(columns="prognosis").mean()
    cols_sorted = sorted(cols, key=lambda c: -rates[c])[:8]
    pred = d.generate(to_display(cols_sorted))
    top = pred["ranked"][0]["name"] if pred["ranked"] else None
    top3 = [r["name"] for r in pred["ranked"][:3]]
    results.append(
        {
            "case": "full_core",
            "truth": disease,
            "n_symptoms": len(cols_sorted),
            "symptoms": cols_sorted,
            "top": top,
            "top3": top3,
            "hit@1": top == disease,
            "hit@3": disease in top3,
            "score": pred["ranked"][0]["score"] if pred["ranked"] else 0,
        }
    )

for disease, cols in profiles.items():
    rates = df[df["prognosis"] == disease].drop(columns="prognosis").mean()
    cols_sorted = sorted(cols, key=lambda c: -rates[c])[:3]
    if len(cols_sorted) < 2:
        continue
    pred = d.generate(to_display(cols_sorted))
    top = pred["ranked"][0]["name"] if pred["ranked"] else None
    top3 = [r["name"] for r in pred["ranked"][:3]]
    results.append(
        {
            "case": "partial_3",
            "truth": disease,
            "n_symptoms": len(cols_sorted),
            "symptoms": cols_sorted,
            "top": top,
            "top3": top3,
            "hit@1": top == disease,
            "hit@3": disease in top3,
            "score": pred["ranked"][0]["score"] if pred["ranked"] else 0,
        }
    )

single_cases = {
    "cough": "Cough",
    "itching": "Itching",
    "continuous_sneezing": "Continuous Sneezing",
    "chest_pain": "Chest Pain",
    "joint_pain": "Joint Pain",
    "burning_micturition": "Burning Micturition",
}
single_results = []
for col, label in single_cases.items():
    truth_top = df[df[col] == 1]["prognosis"].value_counts().head(5)
    pred = d.generate([label])
    ranked = pred["ranked"][:5]
    valid = set(df[df[col] == 1]["prognosis"].unique())
    single_results.append(
        {
            "symptom": label,
            "top": ranked[0]["name"] if ranked else None,
            "score": ranked[0]["score"] if ranked else 0,
            "valid_top": ranked[0]["name"] in valid if ranked else False,
            "data_top5": list(truth_top.index),
        }
    )

combos = [
    ("Fungal infection", ["Itching", "Skin Rash", "Nodal Skin Eruptions"]),
    ("Common Cold", ["Continuous Sneezing", "Runny Nose", "Cough", "High Fever"]),
    ("Malaria", ["Chills", "High Fever", "Sweating", "Headache"]),
    (
        "AIDS",
        [
            "High Fever",
            "Muscle Wasting",
            "Patches In Throat",
            "Extra Marital Contacts",
        ],
    ),
    (
        "GERD",
        ["Stomach Pain", "Acidity", "Ulcers On Tongue", "Vomiting", "Cough"],
    ),
    (
        "Pneumonia",
        [
            "Chills",
            "Fatigue",
            "Cough",
            "High Fever",
            "Breathlessness",
            "Sweating",
            "Chest Pain",
        ],
    ),
    (
        "Migraine",
        ["Acidity", "Indigestion", "Headache", "Blurred And Distorted Vision"],
    ),
    ("Heart attack", ["Chest Pain", "Breathlessness", "Sweating"]),
    (
        "Urinary tract infection",
        ["Burning Micturition", "Bladder Discomfort", "Foul Smell Of Urine"],
    ),
    (
        "Chicken pox",
        [
            "Itching",
            "Skin Rash",
            "Fatigue",
            "High Fever",
            "Loss Of Appetite",
            "Mild Fever",
        ],
    ),
]

combo_results = []
for truth, symptoms in combos:
    pred = d.generate(symptoms)
    top = pred["ranked"][0]["name"] if pred["ranked"] else None
    top3 = [r["name"] for r in pred["ranked"][:3]]
    combo_results.append(
        {
            "truth": truth,
            "symptoms": symptoms,
            "top": top,
            "score": round(pred["ranked"][0]["score"], 3) if pred["ranked"] else 0,
            "top3": top3,
            "hit@1": top == truth,
            "hit@3": truth in top3,
        }
    )

full = [r for r in results if r["case"] == "full_core"]
partial = [r for r in results if r["case"] == "partial_3"]

print("=== FULL CORE PROFILE (up to 8 symptoms, >=80% frequency) ===")
print(f"diseases tested: {len(full)}")
print(
    f"hit@1: {sum(r['hit@1'] for r in full)}/{len(full)} = {sum(r['hit@1'] for r in full)/len(full):.1%}"
)
print(
    f"hit@3: {sum(r['hit@3'] for r in full)}/{len(full)} = {sum(r['hit@3'] for r in full)/len(full):.1%}"
)
misses = [r for r in full if not r["hit@1"]]
if misses:
    print("misses:")
    for r in misses:
        print(
            f"  truth={r['truth']} -> top={r['top']} top3={r['top3']} n={r['n_symptoms']}"
        )

print("\n=== PARTIAL (top 3 core symptoms) ===")
print(f"diseases tested: {len(partial)}")
print(
    f"hit@1: {sum(r['hit@1'] for r in partial)}/{len(partial)} = {sum(r['hit@1'] for r in partial)/len(partial):.1%}"
)
print(
    f"hit@3: {sum(r['hit@3'] for r in partial)}/{len(partial)} = {sum(r['hit@3'] for r in partial)/len(partial):.1%}"
)
misses = [r for r in partial if not r["hit@1"]]
if misses:
    print("misses:")
    for r in misses:
        print(
            f"  truth={r['truth']} symptoms={r['symptoms']} -> top={r['top']} top3={r['top3']}"
        )

print("\n=== SINGLE SYMPTOM SANITY (top must be a disease that has the symptom) ===")
ok = sum(r["valid_top"] for r in single_results)
print(f"valid tops: {ok}/{len(single_results)}")
for r in single_results:
    print(
        f"  {r['symptom']}: top={r['top']} ({r['score']:.2f}) valid={r['valid_top']} data_common={r['data_top5'][:3]}"
    )

print("\n=== HAND-PICKED COMBOS ===")
print(f"hit@1: {sum(r['hit@1'] for r in combo_results)}/{len(combo_results)}")
print(f"hit@3: {sum(r['hit@3'] for r in combo_results)}/{len(combo_results)}")
for r in combo_results:
    mark = "OK" if r["hit@1"] else ("TOP3" if r["hit@3"] else "MISS")
    print(f"  [{mark}] {r['truth']} -> {r['top']} ({r['score']}) | {r['symptoms']}")
