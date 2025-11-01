"""
Captures a baseline snapshot of the retrieval evaluation metrics.

This script runs the main evaluation and saves the resulting metrics to a
dedicated baseline file. This baseline can then be used in CI/CD or other
processes to detect regressions in retrieval performance.

Usage:
    python evaluation/capture_baseline.py
"""

import json
import subprocess
from pathlib import Path


def main():
    """Runs the evaluation and saves the metrics as the new baseline."""
    print("Capturing new evaluation baseline...")

    # Define paths
    evaluation_script_path = Path(__file__).parent / "run_evaluation.py"
    results_path = Path(__file__).parent / "results.json"
    baseline_path = Path(__file__).parent / "baseline_metrics.json"

    # Run the main evaluation script
    print(f"Running evaluation script: {evaluation_script_path}...")
    subprocess.run(["python", str(evaluation_script_path)], check=True)

    # Check if results were generated
    if not results_path.exists():
        print("Error: Evaluation did not produce a results.json file.")
        return

    # Load the metrics from the results file
    with open(results_path, "r") as f:
        results = json.load(f)
    
    metrics = results.get("metrics")
    if not metrics:
        print("Error: results.json does not contain a 'metrics' key.")
        return

    # Save the metrics as the new baseline
    print(f"Saving new baseline metrics to {baseline_path}...")
    with open(baseline_path, "w") as f:
        json.dump(metrics, f, indent=4)
    
    print("\nNew baseline captured successfully:")
    print(json.dumps(metrics, indent=4))


if __name__ == "__main__":
    main()
