"""Retrain and persist the SelfSense diagnosis models."""

from diagnose import Diagnosor


if __name__ == "__main__":
    Diagnosor(force_retrain=True)
    print("Retrain complete.")
