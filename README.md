# CodePro Lead Scoring — End-to-End MLOps Pipeline

A production-grade MLOps system that predicts the likelihood of a lead converting to a paid course purchase on CodePro's ed-tech platform. The project implements three fully orchestrated pipelines — data, training, and inference — using Apache Airflow for scheduling and MLflow for experiment tracking, model versioning, and production promotion.

---

## Table of Contents

- [Overview](#overview)
- [Background](#background)
- [System Architecture](#system-architecture)
- [Pipeline Components](#pipeline-components)
- [Performance Targets](#performance-targets)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)
- [Setup and Installation](#setup-and-installation)
- [Running the Pipelines](#running-the-pipelines)
- [MLflow Experiment Tracking](#mlflow-experiment-tracking)
- [Results](#results)
- [Contact](#contact)

---

## Overview

CodePro's sales team receives a high volume of leads, many of which are unlikely to convert. Manually qualifying every lead is inefficient and diverts sales effort away from high-intent prospects. This project builds an automated lead scoring system — a binary classifier that assigns each lead a conversion probability — enabling the sales team to prioritise outreach and improve revenue efficiency.

The project is structured as a full MLOps system rather than a standalone notebook, reflecting real-world production deployment patterns: separate, independently schedulable pipelines for data ingestion, model training, and batch inference, with full experiment tracking and model lifecycle management.

---

## Background

Lead scoring is a supervised classification problem. The system learns from historical lead data — demographic attributes, engagement signals, source channel, and prior interactions — to predict whether a new lead will convert to a paid enrolment. The class imbalance inherent in lead data (most leads do not convert) is addressed through appropriate metric selection (AUC, Precision, Recall) rather than raw accuracy.

This project also demonstrates a core MLOps principle: **separating the concerns of data processing, model training, and inference** into independently testable, schedulable, and maintainable components.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Apache Airflow DAGs                      │
├───────────────┬──────────────────┬──────────────────────────┤
│  Data Pipeline │ Training Pipeline │   Inference Pipeline    │
│               │                  │                          │
│  • Ingest raw │ • Feature eng.   │ • Load production model  │
│    lead data  │ • Train model    │ • Score new leads        │
│  • Clean &    │ • Log to MLflow  │ • Write predictions      │
│    validate   │ • Register model │ • Trigger on schedule    │
│  • Feature    │ • Promote to     │                          │
│    encoding   │   Production     │                          │
└───────────────┴──────────────────┴──────────────────────────┘
                          │
                    ┌─────▼──────┐
                    │   MLflow   │
                    │  Registry  │
                    │            │
                    │ Staging →  │
                    │ Production │
                    └────────────┘
```

---

## Pipeline Components

### 1. Data Pipeline — `lead_scoring_data_pipeline/`
Responsible for ingesting, cleaning, and preparing raw lead data for model training and inference.

- Ingests raw lead records from source
- Handles missing values, duplicates, and outliers
- Encodes categorical features and scales continuous variables
- Outputs clean, model-ready feature sets
- Validates data schema and completeness before downstream use

### 2. Training Pipeline — `lead_scoring_training_pipeline/`
Trains the lead scoring classifier and manages model lifecycle via MLflow.

- Consumes processed data from the data pipeline
- Trains a classification model (targeting AUC > 75%, Precision > 65%, Recall > 75%)
- Logs hyperparameters, metrics, and artefacts to MLflow
- Registers the trained model in the MLflow Model Registry
- Promotes model from Staging → Production upon meeting performance thresholds

### 3. Inference Pipeline — `lead_scoring_inference_pipeline/`
Loads the production-registered model and scores incoming leads in batch.

- Fetches the current Production model from MLflow Registry
- Applies the same feature engineering as the training pipeline
- Generates conversion probability scores for new leads
- Orchestrated via Airflow DAG on a defined schedule

### 4. Unit Tests — `unit_test/`
Test coverage for data pipeline transformations, feature encoding logic, and model loading utilities, ensuring correctness of individual components in isolation.

---

## Performance Targets

| Metric | Target |
|---|---|
| AUC (ROC) | > 75% |
| Precision | > 65% |
| Recall | > 75% |

Recall is weighted alongside Precision to ensure that high-intent leads are captured even at the cost of some false positives — missing a likely converter is more costly than incorrectly flagging a non-converter for follow-up.

---

## Project Structure

```
CodeProMLOPS/
├── lead_scoring_data_pipeline/       # Data ingestion, cleaning, feature engineering
├── lead_scoring_training_pipeline/   # Model training, MLflow logging, model registration
├── lead_scoring_inference_pipeline/  # Batch scoring using production model
├── notebooks/                        # Exploratory analysis and prototyping
├── unit_test/                        # Unit tests for pipeline components
├── MLOps_Lead_Conversion             # Lead conversion analysis and model artefacts
├── airflow_ui_inference_pipeline.png         # Airflow DAG — inference pipeline view
├── airflow_ui_inference_pipeline_ran.png     # Airflow DAG — successful run
├── mlflow_artifact.png               # MLflow artefact tracking screenshot
├── mlflow_model_promoted.png         # Model promoted from Staging to Production
├── mlflow_prod.png                   # Production model registry view
└── README.md
```

---

## Technologies Used

| Tool / Library | Purpose |
|---|---|
| `Apache Airflow` | Pipeline orchestration and DAG scheduling |
| `MLflow` | Experiment tracking, model registry, production promotion |
| `scikit-learn` | Classification model training and evaluation |
| `pandas` / `numpy` | Data manipulation and feature engineering |
| `pytest` | Unit testing of pipeline components |
| `Python 3.10+` | Runtime environment |
| `Docker` | Containerised environment for Airflow and MLflow services |

---

## Setup and Installation

### Prerequisites
- Docker and Docker Compose installed
- Python 3.10+

### Clone the repository

```bash
git clone https://github.com/chetnapriyadarshini/CodeProMLOPS.git
cd CodeProMLOPS
```

### Start Airflow and MLflow services

```bash
docker-compose up -d
```

### Install Python dependencies

```bash
pip install apache-airflow mlflow scikit-learn pandas numpy pytest
```

### Access the UIs

| Service | URL |
|---|---|
| Apache Airflow | http://localhost:8080 |
| MLflow Tracking | http://localhost:5000 |

---

## Running the Pipelines

Pipelines are triggered via the Airflow UI or CLI:

```bash
# Trigger the data pipeline
airflow dags trigger lead_scoring_data_pipeline

# Trigger the training pipeline
airflow dags trigger lead_scoring_training_pipeline

# Trigger the inference pipeline
airflow dags trigger lead_scoring_inference_pipeline
```

Run unit tests:

```bash
pytest unit_test/
```

---

## MLflow Experiment Tracking

All training runs are logged to MLflow, including:
- Hyperparameters (model type, regularisation, threshold)
- Metrics (AUC, Precision, Recall, F1)
- Artefacts (trained model, feature encoders, confusion matrix)
- Model registration with versioned Staging → Production promotion

Screenshots of the MLflow tracking UI, model registry, and production promotion are included in the repository root.

---

## Results

The trained model meets all defined performance thresholds (AUC > 75%, Precision > 65%, Recall > 75%) on the held-out test set and is registered and promoted to Production in the MLflow Model Registry. The inference pipeline successfully retrieves and applies the production model to score new leads on schedule, as shown in the Airflow DAG run screenshots.

---

## Contact

Created by [@chetnapriyadarshini](https://github.com/chetnapriyadarshini) — feel free to reach out with questions or suggestions.
