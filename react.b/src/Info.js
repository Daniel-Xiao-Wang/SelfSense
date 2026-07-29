import { Link } from "react-router-dom";
import "./App.css";

function Info() {
  return (
    <div className="page info-page">
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
          <Link to="/">Back to diagnose</Link>
        </nav>
      </header>

      <main className="shell">
        <section className="hero">
          <p className="eyebrow">About the demo</p>
          <h1 className="brand">How it works</h1>
          <p className="lede">
            SelfSense turns a short symptom list into a consensus prediction
            from three classifiers, then keeps only conditions that actually
            co-occur with those symptoms in the training data.
          </p>
        </section>

        <section className="info-panel">
          <div className="info-head">
            <h2>Using the app</h2>
          </div>
          <ol className="info-steps">
            <li>Search for a symptom and select it from the suggestions.</li>
            <li>Add up to eight symptoms that best match what you feel.</li>
            <li>Remove any chip to refine the list before diagnosing.</li>
            <li>Click Diagnose to compare the model predictions.</li>
            <li>
              Percentages show how often the models agreed on each condition.
            </li>
          </ol>
        </section>

        <section className="info-panel">
          <div className="info-head">
            <h2>Under the hood</h2>
          </div>
          <p className="info-copy">
            Training data maps symptom patterns to prognoses. At request time,
            SelfSense fits three classifiers and returns both individual
            predictions and a combined view.
          </p>
          <div className="info-models">
            <div>
              <strong>Random Forest</strong>
              <span>Ensemble of decision trees for robust pattern matching.</span>
            </div>
            <div>
              <strong>Gaussian Naive Bayes</strong>
              <span>Probabilistic baseline that handles sparse symptom vectors.</span>
            </div>
            <div>
              <strong>Logistic Regression</strong>
              <span>
                Calibrated multi-class baseline that behaves better on sparse
                symptom vectors than the old SVM.
              </span>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

export default Info;
