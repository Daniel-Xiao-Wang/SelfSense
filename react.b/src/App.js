import { useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import "./App.css";

const backendBaseUrl = "http://127.0.0.1:5000";
const MAX_SYMPTOMS_COUNT = 8;

function App() {
  const [allSymptoms, setAllSymptoms] = useState([]);
  const [selected, setSelected] = useState([]);
  const [query, setQuery] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [highlight, setHighlight] = useState(0);
  const [results, setResults] = useState(null);
  const [rawResult, setRawResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [listLoading, setListLoading] = useState(true);
  const [error, setError] = useState("");
  const searchRef = useRef(null);
  const listRef = useRef(null);

  useEffect(() => {
    setListLoading(true);
    fetch(`${backendBaseUrl}/symptoms`)
      .then((response) => {
        if (!response.ok) throw new Error("Could not load symptoms");
        return response.json();
      })
      .then((data) => {
        setAllSymptoms(Array.isArray(data) ? data : []);
        setError("");
      })
      .catch(() => {
        setError(
          "Could not reach the backend. Make sure Flask is running on port 5000."
        );
      })
      .finally(() => setListLoading(false));
  }, []);

  useEffect(() => {
    const onClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, []);

  const suggestions = useMemo(() => {
    const q = query.trim().toLowerCase();
    return allSymptoms
      .filter((symptom) => !selected.includes(symptom))
      .filter((symptom) => (q ? symptom.toLowerCase().includes(q) : true))
      .slice(0, 8);
  }, [allSymptoms, selected, query]);

  useEffect(() => {
    setHighlight(0);
  }, [query, isOpen]);

  const addSymptom = (symptom) => {
    if (!symptom || selected.includes(symptom)) return;
    if (selected.length >= MAX_SYMPTOMS_COUNT) {
      setError(`You can select up to ${MAX_SYMPTOMS_COUNT} symptoms.`);
      return;
    }
    setSelected((prev) => [...prev, symptom]);
    setQuery("");
    setIsOpen(false);
    setResults(null);
    setRawResult(null);
    setError("");
  };

  const removeSymptom = (symptom) => {
    setSelected((prev) => prev.filter((item) => item !== symptom));
    setResults(null);
    setRawResult(null);
    setError("");
  };

  const clearAll = () => {
    setSelected([]);
    setResults(null);
    setRawResult(null);
    setError("");
    setQuery("");
  };

  const onKeyDown = (event) => {
    if (!isOpen && (event.key === "ArrowDown" || event.key === "Enter")) {
      setIsOpen(true);
      return;
    }

    if (event.key === "ArrowDown") {
      event.preventDefault();
      setHighlight((prev) =>
        suggestions.length ? (prev + 1) % suggestions.length : 0
      );
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      setHighlight((prev) =>
        suggestions.length
          ? (prev - 1 + suggestions.length) % suggestions.length
          : 0
      );
    } else if (event.key === "Enter") {
      event.preventDefault();
      if (suggestions[highlight]) addSymptom(suggestions[highlight]);
    } else if (event.key === "Escape") {
      setIsOpen(false);
    } else if (event.key === "Backspace" && !query && selected.length) {
      removeSymptom(selected[selected.length - 1]);
    }
  };

  const diagnose = async () => {
    if (!selected.length) {
      setError("Add at least one symptom to run a diagnosis.");
      return;
    }

    setLoading(true);
    setError("");
    setResults(null);
    setRawResult(null);

    try {
      const path = selected.map(encodeURIComponent).join(",");
      const response = await fetch(`${backendBaseUrl}/generate/${path}`);
      if (!response.ok) throw new Error("Diagnosis request failed");
      const data = await response.json();

      let ranked;
      if (Array.isArray(data.ranked) && data.ranked.length) {
        ranked = data.ranked.map(({ name, score }) => ({
          name,
          score: Number(score),
        }));
      } else {
        const votes = [
          data.rf_model_prediction,
          data.naive_bayes_prediction,
          data.svm_model_prediction,
        ].filter(Boolean);
        const tallies = {};
        votes.forEach((name) => {
          tallies[name] = (tallies[name] || 0) + 1 / votes.length;
        });
        ranked = Object.entries(tallies)
          .map(([name, score]) => ({ name, score }))
          .sort((a, b) => b.score - a.score);
      }

      setResults(ranked);
      setRawResult(data);
    } catch {
      setError("Something went wrong while generating a diagnosis.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="atmosphere" aria-hidden="true">
        <span className="orb orb-a" />
        <span className="orb orb-b" />
        <span className="grid-wash" />
      </div>

      <header className="topbar">
        <Link to="/" className="brand-mark">
          SelfSense
        </Link>
        <nav className="nav">
          <Link to="/info">How it works</Link>
        </nav>
      </header>

      <main className="shell">
        <section className="hero">
          <p className="eyebrow">Symptom-guided screening</p>
          <h1 className="brand">SelfSense</h1>
          <p className="lede">
            Search what you feel, build a short symptom list, and get a
            model-backed read of likely conditions.
          </p>
        </section>

        <section className="workspace" aria-label="Symptom search">
          <div className="workspace-head">
            <div>
              <h2>Your symptoms</h2>
              <p>
                {selected.length}/{MAX_SYMPTOMS_COUNT} selected
                {listLoading ? " · loading catalog…" : ""}
              </p>
            </div>
            {selected.length > 0 && (
              <button type="button" className="text-btn" onClick={clearAll}>
                Clear all
              </button>
            )}
          </div>

          <div className="search-block" ref={searchRef}>
            <label className="search-label" htmlFor="symptom-search">
              Search symptoms
            </label>
            <div className={`search-field ${isOpen ? "is-open" : ""}`}>
              <svg
                className="search-icon"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <circle cx="11" cy="11" r="7" />
                <path d="M20 20l-3.5-3.5" />
              </svg>
              <input
                id="symptom-search"
                type="search"
                autoComplete="off"
                placeholder={
                  selected.length >= MAX_SYMPTOMS_COUNT
                    ? "Maximum symptoms reached"
                    : "Try fever, cough, itching…"
                }
                value={query}
                disabled={
                  listLoading || selected.length >= MAX_SYMPTOMS_COUNT
                }
                onChange={(event) => {
                  setQuery(event.target.value);
                  setIsOpen(true);
                }}
                onFocus={() => setIsOpen(true)}
                onKeyDown={onKeyDown}
              />
            </div>

            {isOpen && suggestions.length > 0 && (
              <ul className="suggestions" role="listbox" ref={listRef}>
                {suggestions.map((symptom, index) => (
                  <li key={symptom}>
                    <button
                      type="button"
                      role="option"
                      aria-selected={index === highlight}
                      className={index === highlight ? "is-active" : ""}
                      onMouseEnter={() => setHighlight(index)}
                      onClick={() => addSymptom(symptom)}
                    >
                      <span>{symptom}</span>
                      <em>Add</em>
                    </button>
                  </li>
                ))}
              </ul>
            )}

            {isOpen && query && suggestions.length === 0 && (
              <div className="empty-search">No matching symptoms.</div>
            )}
          </div>

          <div className="chip-row" aria-live="polite">
            {selected.length === 0 ? (
              <p className="chip-empty">
                No symptoms yet. Start typing above to add one.
              </p>
            ) : (
              selected.map((symptom, index) => (
                <button
                  key={symptom}
                  type="button"
                  className="chip"
                  style={{ animationDelay: `${index * 40}ms` }}
                  onClick={() => removeSymptom(symptom)}
                  aria-label={`Remove ${symptom}`}
                >
                  {symptom}
                  <span aria-hidden="true">×</span>
                </button>
              ))
            )}
          </div>

          <div className="actions">
            <button
              type="button"
              className="primary-btn"
              onClick={diagnose}
              disabled={loading || !selected.length}
            >
              {loading ? "Diagnosing…" : "Diagnose"}
            </button>
            <p className="hint">
              Ensemble of Random Forest, Naive Bayes, and Logistic Regression.
            </p>
          </div>

          {error && (
            <div className="banner banner-error" role="alert">
              {error}
            </div>
          )}
        </section>

        {results && (
          <section className="results" aria-live="polite">
            <div className="results-head">
              <h2>Likely conditions</h2>
              <p>
                Agreement across the three models for your selected symptoms.
              </p>
            </div>

            <ol className="result-list">
              {results.map(({ name, score }, index) => (
                <li
                  key={name}
                  className="result-item"
                  style={{ animationDelay: `${index * 80}ms` }}
                >
                  <div className="result-meta">
                    <strong>{name}</strong>
                    <span>{(score * 100).toFixed(0)}%</span>
                  </div>
                  <div className="meter" aria-hidden="true">
                    <span style={{ width: `${Math.max(score * 100, 8)}%` }} />
                  </div>
                </li>
              ))}
            </ol>

            {rawResult && (
              <details className="model-breakdown">
                <summary>Model breakdown</summary>
                <ul>
                  <li>
                    <span>Random Forest</span>
                    <strong>{rawResult.rf_model_prediction}</strong>
                  </li>
                  <li>
                    <span>Naive Bayes</span>
                    <strong>{rawResult.naive_bayes_prediction}</strong>
                  </li>
                  <li>
                    <span>Logistic Regression</span>
                    <strong>
                      {rawResult.logistic_regression_prediction ||
                        rawResult.svm_model_prediction}
                    </strong>
                  </li>
                </ul>
              </details>
            )}
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
