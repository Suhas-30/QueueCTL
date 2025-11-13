# 🧩 QueueCTL — Lightweight Job Queue & Worker System

`QueueCTL` is a **modular command-line job queue manager** built with **Python, Typer, SQLite, and Docker**.  
It provides a lightweight yet powerful framework to enqueue shell commands, manage workers, handle retries, and inspect a Dead Letter Queue (DLQ) — all from the CLI.

---

## 🎬 Demo of QueueCTL

📹 **Watch Demo:** [Demo of QueueCTL](https://drive.google.com/file/d/1azycxCbUBw0bMBSMxxoQDU0uZ-sOVv5l/view?usp=sharing)


---

## 📋 Table of Contents

- [Features](#-features)
- [Setup Instructions](#%EF%B8%8F-setup-instructions)
- [Usage Examples](#-usage-examples)
- [Architecture Overview](#-architecture-overview)
- [Assumptions & Trade-offs](#%EF%B8%8F-assumptions--trade-offs)
- [Testing Instructions](#-testing-instructions)
- [Project Structure](#-project-structure)
- [License](#-license)
- [Author](#-author)

---

## ✨ Features

- 🚀 **CLI-based job queue management** with Typer
- 📊 **SQLite database** for lightweight persistence
- 🔄 **Automatic retry logic** with exponential backoff
- 💀 **Dead Letter Queue (DLQ)** for failed jobs
- ⚙️ **Configurable settings** (max retries, worker count, etc.)
- 🐳 **Docker support** with persistent volumes
- 👷 **Multi-worker architecture** for concurrent job processing
- 🛡️ **Graceful shutdown** handling
- 🎨 **Rich CLI output** with tables and status indicators

---

## ⚙️ Setup Instructions

### 🧠 Requirements

- Python **3.11+**
- Docker & Docker Compose (for containerized setup)
- `pip` (Python package manager)

---

### 🧰 Local Setup

```bash
# Clone the repository
git clone https://github.com/<your-username>/queuectl.git
cd queuectl

# Create a virtual environment
python -m venv venv
source venv/bin/activate       # (Linux/Mac)
venv\Scripts\activate          # (Windows)

# Install dependencies
pip install -e .

# Initialize database (automatically happens on first command)
queuectl list
```

---

### 🐳 Docker Setup

```bash
# Build the Docker image
docker build -t queuectl .

# Run interactively
docker run -it queuectl bash

# Inside container, run commands
queuectl enqueue "echo 'Hello from Docker!'"
queuectl list --state pending
```

**✅ Persistent Data:**  
A Docker volume `queuectl-data` ensures your SQLite database persists between container runs.

```bash
# Using Docker Compose (if available)
docker-compose up -d
docker-compose exec queuectl queuectl list
```

---

## 💡 Usage Examples

### 🧱 Enqueue a Job

```bash
queuectl enqueue "echo 'Test Job'" --max-retries 3
```

**Output:**
```
Job added with ID: 5f07c123-45ef-42b8-88cd-8e6e33bd4e5d
```

---

### 📋 List Jobs

```bash
# List all jobs
queuectl list

# Filter by state
queuectl list --state pending
queuectl list --state completed
queuectl list --state failed
```

**Output:**
```
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ ID         ┃ Command            ┃ State     ┃ Retries   ┃ Created At   ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ 5f07c123   │ echo 'Test Job'    │ pending   │ 0/3       │ 2025-01-15   │
└────────────┴────────────────────┴───────────┴───────────┴──────────────┘
```

---

### ⚙️ Start Workers

```bash
# Start 2 worker processes
queuectl worker start --count 2
```

**Output:**
```
[Manager PID 1234] Starting 2 workers...
[Worker PID 5678] Loop started
[Executor] Running job 5f07c123...
[Executor] Job completed successfully.
```

**Stop Workers:**
```bash
# Graceful shutdown (Ctrl+C or send SIGTERM)
^C
[Worker PID 5678] Received shutdown signal, finishing current job...
[Worker PID 5678] Shutdown complete.
```

---

### 💀 Dead Letter Queue (DLQ)

```bash
# View all failed jobs in DLQ
queuectl dlq list

# Retry a specific job from DLQ
queuectl dlq retry <job_id>

# Clear all jobs from DLQ
queuectl dlq clear
```

---

### 🧩 Configuration Management

```bash
# Set configuration values
queuectl config set max-retries 5
queuectl config set worker-count 4

# Get a specific config value
queuectl config get max-retries

# List all configuration
queuectl config list
```

**Output:**
```
Current configuration:
  max-retries: 5
  worker-count: 4
```

---

## 🧠 Architecture Overview

### 🏗️ System Architecture Diagram

```
                    ┌──────────────────────────────┐
                    │          CLI Layer           │
                    │ (Typer + Rich interface)     │
                    │------------------------------│
                    │ • queuectl enqueue/list      │
                    │ • queuectl worker start      │
                    │ • queuectl dlq/config        │
                    └──────────────┬───────────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          │                        │                        │
          ▼                        ▼                        ▼
┌────────────────────┐   ┌───────────────────────┐   ┌──────────────────────┐
│  Repository Layer  │   │ Worker Management     │   │   Config Layer       │
│ (JobRepository,    │   │ (manager.py)          │   │ (config.py)          │
│  ConfigRepo)       │   │-----------------------│   │----------------------│
│--------------------│   │ • Spawns processes    │   │ • Key-value config   │
│ • SQLite queries   │   │ • Graceful shutdown   │   │ • CLI-based updates  │
│ • Job persistence  │   │ • Process isolation   │   │ • Persists to DB     │
└──────────┬─────────┘   └────────────┬──────────┘   └──────────┬──────────┘
           │                          │                         │
           │                          │                         │
           ▼                          ▼                         ▼
┌────────────────────┐     ┌────────────────────┐     ┌────────────────────┐
│ Worker Execution   │     │ Retry & DLQ Logic  │     │ Database Layer     │
│ (workLoop, executor│     │ (retry.py)         │     │ (SQLite + Volume)  │
│  jobLifeCycle)     │     │--------------------│     │--------------------│
│--------------------│     │ • Exponential back │     │ • jobs table       │
│ • Runs shell cmds  │     │ • DLQ transition   │     │ • config table     │
│ • Updates job state│     │ • Attempts tracking│     │ • Persistent volume│
│ • Manages retries  │     └────────────────────┘     └────────────────────┘
└────────────────────┘
```

### 🧩 Component Descriptions

| Component | Description |
|-----------|-------------|
| **CLI Layer** | Command interface for managing jobs, workers, config, and DLQ using Typer and Rich |
| **Repository Layer** | Handles job creation, listing, and database operations through JobRepository |
| **Worker Management** | Spawns and manages worker processes with graceful shutdown capabilities |
| **Config Layer** | Key-value configuration system with CLI-based updates persisted to database |
| **Worker Execution** | Runs shell commands, updates job states, and manages the execution lifecycle |
| **Retry & DLQ Logic** | Implements exponential backoff and transitions failed jobs to Dead Letter Queue |
| **Database Layer** | SQLite-based persistence for jobs and config with Docker volume support |

---

### 🔄 Job Lifecycle

```
pending  →  processing  →  completed
   ↓             ↓
   ↓         failed → retry (pending)
   ↓
   └──> dead (DLQ after max retries)
```

Each job moves through these states based on worker execution results.

---

### 📦 Data Persistence

- Jobs are stored in `queuectl.db` (SQLite)
- In Docker, this file lives inside `/app/data` (mounted via `queuectl-data` volume)
- Configuration settings are persisted in the same database
- Ensures your queue survives application and container restarts

---

## ⚖️ Assumptions & Trade-offs

| Design Decision | Rationale |
|----------------|-----------|
| ✅ **SQLite** | Simple, embedded database — ideal for local or small-scale deployments |
| ⚙️ **One command per job** | Designed for shell-style tasks; keeps job model simple |
| 🔁 **Exponential backoff** | Prevents overwhelming systems during transient failures |
| 🧠 **Single-node design** | No distributed locking (but could be extended with PostgreSQL or Redis) |
| 🧩 **Multiprocess workers** | Scalable on one machine; not yet distributed/clustered |
| 💾 **Minimal dependencies** | Pure Python standard libs + Typer + Rich for portability |

---

## 🧪 Testing Instructions

### 🔬 Run Unit Tests

```bash
# Install test dependencies
pip install pytest

# Run all tests
pytest -v

# Run specific test file
pytest tests/test_jobs.py -v

# Run with coverage
pytest --cov=queuectl tests/
```

**Expected Output:**
```
tests/test_config.py::test_set_and_get_config PASSED
tests/test_dlq.py::test_dlq_job_state PASSED
tests/test_jobs.py::test_enqueue_and_list_jobs PASSED
tests/test_workers.py::test_run_valid_job PASSED
```

---

### 🧱 Test Coverage

| Test File | Purpose |
|-----------|---------|
| `test_jobs.py` | Verifies enqueue & listing of jobs |
| `test_workers.py` | Ensures workers execute commands correctly |
| `test_dlq.py` | Confirms failed jobs move to DLQ |
| `test_config.py` | Validates configuration persistence |

---

## 📂 Project Structure

```
queuectl/
├── cli/
│   ├── main.py           # Main CLI entry point
│   ├── job_cli.py        # Job management commands
│   ├── worker_cli.py     # Worker control commands
│   ├── dlq_cli.py        # Dead Letter Queue commands
│   └── config_cli.py     # Configuration commands
├── worker/
│   ├── manager.py        # Worker process manager
│   ├── jobExecutor.py    # Job execution logic
│   ├── jobLifeCycle.py   # State transitions
│   ├── retry.py          # Retry logic & backoff
│   ├── workLoop.py       # Main worker loop
│   └── shutdown.py       # Graceful shutdown handler
├── repository.py         # Database operations
├── config.py             # Configuration management
├── dbConnection.py       # SQLite connection handler
├── tests/
│   ├── test_config.py
│   ├── test_dlq.py
│   ├── test_jobs.py
│   └── test_workers.py
├── Dockerfile
├── docker-compose.yml
├── setup.py
├── requirements.txt
└── README.md
```

---

## 🧾 License

MIT License © 2025 — QueueCTL Project

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## ✉️ Author

**Developed by Suhas**

📧 *3suhashs@gamil.com*  
🐙 GitHub: [Suhas-30](https://github.com/Suhas-30)  


---

## 🎥 Video Submission

📹 **Demo of QueueCTL:** [Click here to watch](https://drive.google.com/file/d/1azycxCbUBw0bMBSMxxoQDU0uZ-sOVv5l/view?usp=sharing)


---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 Roadmap

- [ ] Add support for job priorities
- [ ] Implement job dependencies (DAG execution)
- [ ] Add web UI for queue monitoring
- [ ] Support for PostgreSQL backend
- [ ] Distributed worker support with Redis
- [ ] Webhook notifications for job completion
- [ ] Scheduled/cron-style job execution

---

## 🙏 Acknowledgments

- Built with [Typer](https://typer.tiangolo.com/) for CLI
- Styled with [Rich](https://rich.readthedocs.io/) for beautiful terminal output


---

**⭐ If you find this project useful, please consider giving it a star on GitHub!**