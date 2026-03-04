from datetime import datetime, timedelta
import os
import subprocess
from airflow import DAG
from airflow.operators.python import PythonOperator

def on_failure_callback(context):
    ti = context.get("task_instance")
    dag_id = context.get("dag").dag_id if context.get("dag") else "unknown_dag"
    task_id = ti.task_id if ti else "unknown_task"
    run_id = context.get("run_id", "unknown_run")
    print(f"[FAILURE] dag={dag_id} task={task_id} run_id={run_id}")

def preprocess_data():
    # Idempotent: always writes deterministic output to the same file (safe overwrite)
    os.makedirs("data", exist_ok=True)
    processed = "data/processed.txt"
    with open(processed, "w") as f:
        f.write("preprocess complete\n")

def train_model():
    # Idempotent: overwrites outputs/model.pkl and outputs/metrics.json safely
    subprocess.check_call(["python", "train.py"])

def register_model():
    # Placeholder “registration” step (idempotent check)
    if not os.path.exists("outputs/metrics.json"):
        raise FileNotFoundError("outputs/metrics.json not found; training may have failed.")
    print("Register step complete (placeholder).")

default_args = {
    "owner": "mlops",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "on_failure_callback": on_failure_callback,
}

with DAG(
    dag_id="train_pipeline",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
) as dag:

    preprocess = PythonOperator(
    task_id="preprocess_data",
    python_callable=preprocess_data
)

train = PythonOperator(
    task_id="train_model",
    python_callable=train_model
)

register = PythonOperator(
    task_id="register_model",
    python_callable=register_model
)
    preprocess >> train >> register