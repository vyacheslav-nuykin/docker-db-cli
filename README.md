# 🐘 Docker Database CLI (`core.py`)

> **Fast, secure, scriptable CLI to launch PostgreSQL, MySQL, Redis, MongoDB, and custom containers via Docker.**  
> Designed for developers who value speed, automation, and clean infrastructure.

> **Note**: This tool was developed with AI assistance. The architecture, requirements, validation logic, and testing were defined and verified by [Vyacheslav Nuykin](https://github.com/vyacheslav-nuykin). The implementation was generated and refined with AI, then thoroughly tested and adapted for production use.

---

## ✨ Features

- **5 database types**: PostgreSQL, MySQL, Redis, MongoDB, Custom
- **Idempotent**: safely re-run — existing containers are replaced
- **Pure CLI**: no GUI, no config files required (YAML optional via GUI wrapper)
- **Cross-platform**: Windows (`.bat`), Linux, macOS
- **Safe**: no shell injection, explicit argument passing
- **Script-friendly**: perfect for `Makefile`, CI, dev workflows

---

## 🚀 Quick Start

### 1. Requirements
- [Docker](https://www.docker.com/) installed and running
- Python 3.10+

### 2. Clone & Run
```bash
git clone https://github.com/vyacheslav-nuykin/docker-db-cli.git
cd docker-db-cli
```

Launch a PostgreSQL dev instance:
```bash
python core.py postgres \
  --name postgres-dev \
  --user devuser \
  --password devpassword \
  --db dev-app \
  --port 5432
```

Stop it:
```bash
python core.py stop --name postgres-dev
```

---

## 📂 Predefined Scripts (Windows)

For maximum speed, use the included batch scripts:

| Script | Action |
|--------|--------|
| `run-postgre-dev.bat` | Starts PostgreSQL dev container |
| `stop-and-remove-postgre-dev.bat` | Stops and removes it |
| `run-postgre-dev.sh` | Starts PostgreSQL dev container |
| `stop-and-remove-postgre-dev.sh` | Stops and removes it |

> 💡 Edit these files to match your preferred credentials.

---

## 🧪 Examples

### PostgreSQL
```bash
python core.py postgres \
  --name mypg \
  --user admin \
  --password s3cr3t \
  --db myapp \
  --port 5432 \
  --image postgres:16
```

### Redis
```bash
python core.py redis \
  --name mycache \
  --port 6380 \
  --image redis:7
```

### Custom (e.g., Nginx)
```bash
python core.py custom \
  --name myweb \
  --image nginx:alpine \
  --port 8080
```

### With Environment Variables
```bash
python core.py custom \
  --name myapp \
  --image myapp:latest \
  --port 3000 \
  --env "DEBUG=true" "ENV=staging"
```

---

## 🛠️ Build (Optional)

You can create a standalone executable (no Python required):

```bash
pip install pyinstaller
pyinstaller --onefile core.py
```

→ Output: `dist/core` (Linux/macOS) or `dist/core.exe` (Windows)

---

## 📁 Project Structure

```
.
├── core.py                            # CLI entrypoint (pure, no GUI)
├── gui.py                             # Optional PyQt6 GUI (profiles via YAML)
├── run-postgre-dev.bat                # Example dev script (Windows)
├── stop-and-remove-postgre-dev.bat    # Stop script
└── README.md                          # This file
```

> The GUI stores profiles in `~/.docker-db/profiles/*.yaml` (optional).

---

## 📜 License

Apache License 2.0 — see [LICENSE](LICENSE).

---

## 🙏 Acknowledgements

- **Author & Maintainer**: Vyacheslav Nuykin ([@vyacheslav-nuykin](https://github.com/vyacheslav-nuykin))
- **Implementation**: Generated with AI assistance, then rigorously tested, refined, and validated for correctness, security, and usability.
- **Inspired by**: Infrastructure-as-Code principles and Google’s engineering practices.

> This tool reflects the author’s philosophy: **"Speed through simplicity, reliability through automation."**
