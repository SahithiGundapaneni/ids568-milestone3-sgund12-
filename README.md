# Milestone 3 – Workflow Automation + Experiment Tracking

## Setup Instructions

1. Create and activate a virtual environment.

Windows (PowerShell):

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Mac/Linux:

```
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```
pip install -r requirements.txt
```

---

# How to Run the Pipeline

### Run training locally (creates outputs + MLflow run)

```
python train.py
```

### Run validation (quality gate)

```
python model_validation.py
```

### Run Airflow DAG (manual trigger)

1. Ensure Airflow is installed via `requirements.txt`.

2. Start Airflow services:

```
airflow db init
airflow webserver --port 8080
airflow scheduler
```

3. Place `dags/train_pipeline.py` in your Airflow DAGs folder
   (or configure `AIRFLOW__CORE__DAGS_FOLDER`).

4. Open the Airflow UI and trigger the DAG:

```
train_pipeline
```

---

# Architecture Overview

This project implements an MLOps training pipeline that automates model training, validation, and experiment tracking.

Key components include:

* **Airflow DAG orchestration**: manages the pipeline workflow
* **MLflow experiment tracking**: logs parameters, metrics, and artifacts
* **GitHub Actions CI pipeline**: automates training and validation checks

The workflow structure is:

```
Preprocess → Train → Register
```

---

# Airflow DAG Tasks

The DAG **`train_pipeline`** contains three tasks:

### 1. preprocess_data

Generates deterministic processed data and writes it to a fixed file location.

### 2. train_model

Runs the `train.py` script to train the machine learning model and log experiment results using MLflow.

### 3. register_model

A placeholder step that verifies outputs exist and simulates model registration.

Task dependency:

```
preprocess_data → train_model → register_model
```

---

# Project Structure

```
milestone3/
│
├── train.py
│   Model training script with MLflow tracking
│
├── model_validation.py
│   Validation script acting as a quality gate
│
├── requirements.txt
│   Project dependencies
│
├── README.md
│   Project documentation
│
├── outputs/
│   Generated artifacts
│   ├── model.pkl
│   └── metrics.json
│
├── data/
│   └── processed.txt
│
├── dags/
│   └── train_pipeline.py
│   Airflow DAG definition
│
└── .github/workflows/
    └── train_and_validate.yml
    CI workflow for automated training and validation
```

---

# DAG Idempotency and Lineage Guarantees

Tasks are designed to be **idempotent**, meaning they can run multiple times safely without corrupting outputs.

Examples:

* **Preprocess step**

  * Writes deterministic outputs
  * Safely overwrites the same file each run

* **Training step**

  * Writes model and metrics to the `outputs/` directory
  * Files are overwritten safely if the pipeline is rerun

### Lineage Tracking

Experiment lineage is captured using **MLflow**:

* Hyperparameters are logged as MLflow **parameters**
* Performance metrics are logged as MLflow **metrics**
* The trained model is logged as an **artifact**

---

# CI-based Model Governance Approach

Model governance is implemented using **GitHub Actions**.

The CI workflow performs the following steps:

1. Checkout repository code
2. Install project dependencies
3. Run model training (`train.py`)
4. Execute validation (`model_validation.py`)

If the validation script fails (for example, accuracy below the threshold), the CI pipeline fails and prevents the model from being accepted.

This provides an automated **quality gate** for the machine learning workflow.

---

# Experiment Tracking Methodology (MLflow)

Each training execution logs the following information using MLflow:

### Parameters

Examples:

* C (regularization strength)
* max_iter
* random seed

### Metrics

* Model accuracy

### Artifacts

* Trained model file
* metrics.json file containing evaluation results

Minimum experiment requirement:

* At least **5 MLflow runs using different hyperparameters**.

---

# Viewing MLflow Runs

To view experiment tracking results locally:

```
mlflow ui
```

Then open the browser:

```
http://localhost:5000
```

The MLflow interface displays:

* parameters
* metrics
* experiment runs
* stored artifacts

---

# Operational Notes

## Retry Strategies and Failure Handling

The Airflow DAG defines retry behavior using `default_args`:

* `retries = 2`
* `retry_delay = 5 minutes`
* `on_failure_callback` captures failures and prints diagnostic information.

This allows transient failures to be retried automatically.

---

## Monitoring and Alerting Recommendations

Suggested monitoring strategies:

* Track validation accuracy trends over time
* Alert if model accuracy falls below the validation threshold
* Monitor repeated pipeline failures to detect system issues

---

## Rollback Procedures

If a deployed model performs poorly:

1. Identify the last successful MLflow run with acceptable metrics
2. Restore the corresponding model artifact
3. Re-run the pipeline with the previous hyperparameters if necessary

This allows the system to revert to a stable model version quickly.
