# ⚡ PulseGrid

### AI-Assisted IoT Operations & Data Platform

PulseGrid is a production-inspired IoT data platform for simulating, processing, and analyzing telemetry from connected devices across smart buildings.

The platform uses a **Bronze → Silver → Gold** data architecture to transform raw IoT events into validated, analytics-ready datasets for operational monitoring, data visualization, and future machine-learning workloads.

PulseGrid is being designed as more than an ETL pipeline. The long-term goal is an **AI-assisted operations center** capable of detecting anomalies, predicting equipment failures, analyzing energy consumption, and providing actionable recommendations to facility operators.

> **Project Status:** 🚧 Active development — the core telemetry pipeline, configuration system, structured logging, and analytics layers are operational. Cloud, dashboard, and AI capabilities are planned.

---

## Why PulseGrid?

Modern smart buildings can generate enormous amounts of telemetry from temperature, humidity, occupancy, air-quality, and energy sensors. Raw sensor readings alone provide limited operational value.

PulseGrid is designed to turn that telemetry into useful information through an end-to-end data pipeline:

**Raw telemetry → Data validation → Analytics → Operational insights → Predictive intelligence**

The project is also designed to explore how IoT, data engineering, cloud computing, visualization, and machine learning can work together within a single scalable system.

---

## ✨ Current Features

- Configuration-driven IoT device simulation
- Multi-floor smart-building model
- Realistic temperature, humidity, energy, air-quality, and occupancy telemetry
- Unique event IDs and timestamps
- Bronze raw telemetry ingestion using JSONL
- Silver data validation and cleaning
- Invalid-event quarantine
- Duplicate-event detection and removal
- Parquet-based Silver and Gold storage
- Room-level analytics and aggregations
- Device-health monitoring
- Bronze → Silver → Gold pipeline runner
- Centralized structured logging
- Console and persistent file logging
- Git feature-branch and pull-request workflow

---

---

## 🏗️ Architecture

PulseGrid currently follows a Medallion-style data architecture with separate Bronze, Silver, and Gold layers.


Configuration
     │
     ▼
IoT Device Simulator
     │
     │ JSON telemetry
     ▼
┌─────────────────────┐
│       BRONZE        │
│     Raw JSONL       │
└──────────┬──────────┘
           │
           │ Validation
           │ Deduplication
           │ Data quality checks
           ▼
┌─────────────────────┐
│       SILVER        │
│  Validated Parquet  │
└──────────┬──────────┘
           │
           │ Aggregation
           │ Device health
           │ Operational metrics
           ▼
┌─────────────────────┐
│        GOLD         │
│ Analytics Parquet   │
└──────────┬──────────┘
           │
           ▼
     Analytics Layer
           │
     ┌─────┴─────┐
     ▼           ▼
 Dashboards      ML
 (planned)    (planned)
                   │
                   ▼
          AI Operations Assistant
                (planned)


Data Layers

Bronze — Raw Telemetry

Stores telemetry exactly as it arrives from simulated IoT devices. JSONL preserves individual events before downstream transformations occur.

Silver — Validated Telemetry

Validates required fields and acceptable sensor ranges, quarantines invalid records, removes duplicate events, and produces clean Parquet datasets.

Gold — Analytics

Transforms validated telemetry into business-oriented datasets including room-level metrics, hourly metrics, and device-health information.

---

### Motivation

I chose to build PulseGrid because I wanted to explore how machine learning can be combined with IoT telemetry to make useful predictions from real-world sensor data.

Rather than simply collecting and displaying sensor readings, my goal is to build a platform that can eventually use those readings to identify patterns, anticipate potential problems, and help operators make better-informed decisions.

Building the project end-to-end also allows me to explore the engineering required before machine learning can be useful — from telemetry generation and data quality to scalable processing, analytics, visualization, and eventually predictive models.

---

## 🛠️ Technology Stack

### Currently Implemented

- **Python** — simulation, ETL, configuration, and application logic

- **Pandas** — telemetry transformation and aggregation

- **PyArrow / Parquet** — efficient columnar data storage

- **JSON / JSONL** — configuration and raw telemetry

- **Python Logging** — structured application logging

- **Git & GitHub** — version control, feature branches, and pull requests

### Planned

- **Pytest** — automated unit and integration testing

- **Apache Spark** — distributed telemetry processing

- **Azure IoT Hub** — cloud IoT ingestion

- **Azure Data Lake Storage** — cloud-based Bronze/Silver/Gold storage

- **Power BI** — operational analytics and visualization

- **Docker** — containerized deployment

- **GitHub Actions** — CI/CD and automated testing

- **Machine Learning** — anomaly detection and predictive maintenance

- **AI Operations Assistant** — natural-language operational insights and recommendations

---

## 📁 Project Structure

PulseGrid/
├── config/
│   ├── buildings.json
│   ├── device_templates.json
│   └── simulation.json
│
├── data/
│   ├── bronze/          # Raw telemetry
│   ├── silver/          # Validated telemetry
│   └── gold/            # Analytics-ready datasets
│
├── logs/
│   └── pulsegrid.log
│
├── src/
│   ├── analytics/       # Gold-layer aggregations
│   ├── core/            # Configuration, logging, pipeline runner
│   ├── generator/       # IoT device simulation
│   └── processing/      # Silver-layer validation and cleaning
│
├── tests/               # Automated tests (planned)
│
├── .gitignore
├── README.md
└── requirements.txt

The codebase separates simulation, processing, analytics, and shared application services so that each component has a focused responsibility.

---

## 📊 Telemetry Schema

Each simulated IoT event contains operational and location information such as:

| Field | Description |
|---|---|
| `event_id` | Unique identifier for the telemetry event |
| `device_id` | Unique sensor identifier |
| `building_id` | Building identifier |
| `building` | Human-readable building name |
| `floor` | Floor number |
| `room_id` | Unique room identifier |
| `room` | Human-readable room name |
| `room_type` | Type of monitored space |
| `timestamp` | UTC event timestamp |
| `temperature` | Temperature reading |
| `humidity` | Relative humidity reading |
| `energy_usage` | Simulated energy consumption |
| `air_quality` | Air-quality reading |
| `occupancy` | Number of occupants detected |

The simulator can intentionally introduce invalid values and duplicate events, allowing the Silver layer to exercise realistic data-quality and deduplication workflows.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.13+
- Git

### Clone the Repository

```bash
git clone git@github.com:JamalB3/PulseGrid.git
cd PulseGrid
```

### Create a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Generate IoT Telemetry

```bash
PYTHONPATH=src python -m generator.device_simulator
```

Press `Control + C` when enough telemetry has been generated.

Raw events are written to the Bronze layer.

### Run the Data Pipeline

```bash
PYTHONPATH=src python -m core.pipeline_runner
```

The runner processes existing Bronze telemetry through:

```text
Bronze
   ↓
Validation & Deduplication
   ↓
Silver
   ↓
Aggregation & Device Health
   ↓
Gold
```

Application activity is written to both the console and:

```text
logs/pulsegrid.log
```

---

## 🧠 Engineering Decisions

### Configuration-Driven Architecture

Building layouts, room behavior, and simulation settings are stored outside the application logic. This allows the simulated environment to change without modifying the core Python code.

### Medallion Data Architecture

PulseGrid separates raw, validated, and analytics-ready data into Bronze, Silver, and Gold layers. This preserves raw telemetry while allowing downstream consumers to work with increasingly refined datasets.

### Parquet for Processed Data

Silver and Gold datasets use Parquet rather than JSONL because columnar storage is better suited to analytical workloads and provides a natural path toward larger-scale processing with tools such as Apache Spark.

### Centralized Logging

Application components share a centralized logging configuration that writes to both the console and persistent log files. Log levels distinguish routine application behavior from warnings and failures.

### Modular Pipeline

Simulation, validation, analytics, configuration, and logging are separated into focused modules. This makes individual components easier to test, maintain, and eventually replace with cloud-based implementations.

---

## 🗺️ Roadmap

### Phase 1 — Data Engineering Foundation
- [x] IoT telemetry simulator
- [x] Bronze raw-data layer
- [x] Silver validation and deduplication
- [x] Gold analytics layer
- [x] Configuration-driven device generation
- [x] Structured logging
- [x] Pipeline runner
- [ ] Automated testing

### Phase 2 — Platform Engineering
- [ ] Docker containerization
- [ ] GitHub Actions CI/CD
- [ ] Improved command-line interface
- [ ] Data-quality reporting

### Phase 3 — Scale & Cloud
- [ ] Multi-building simulation
- [ ] Large-scale device generation
- [ ] Apache Spark processing
- [ ] Azure IoT Hub ingestion
- [ ] Azure Data Lake Storage

### Phase 4 — Visualization
- [ ] Operations dashboard
- [ ] Building and room drill-down
- [ ] Energy-consumption analysis
- [ ] Device-health visualization
- [ ] Alert monitoring

### Phase 5 — Machine Learning & AI
- [ ] Anomaly detection
- [ ] Energy forecasting
- [ ] Predictive maintenance
- [ ] Explainable predictions
- [ ] AI-assisted operational recommendations
- [ ] Natural-language PulseGrid assistant
