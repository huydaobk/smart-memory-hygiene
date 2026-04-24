# Smart Memory Hygiene Framework

> **Version:** 0.1.0-alpha  
> **Author:** Đệ (AI Assistant)  
> **Location:** `/mnt/toshiba/projects/smart-memory-hygiene/`

AI-powered memory management for OpenClaw agents. Automatically optimizes MEMORY.md and other memory files using semantic analysis, importance scoring, and predictive cleanup.

---

## 🎯 Vision

Transform memory management from **manual maintenance** to **intelligent self-healing**:

```
Before: Human reviews → Manual cleanup → Risk of data loss
After:  AI analyzes  → Smart pruning → Zero data loss
```

**Multi-agent support:** Works with any OpenClaw agent instance.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│  INPUT LAYER                                            │
│  • MEMORY.md parser                                     │
│  • Daily notes scanner                                  │
│  • Project files indexer                                │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  ANALYSIS ENGINE                                        │
│  • Semantic deduplication                               │
│  • Importance scoring (recency × frequency × relevance) │
│  • Cross-reference validation                             │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  ACTION LAYER                                           │
│  • Smart merge (consolidate related entries)            │
│  • Predictive archive (low-importance → cold storage)   │
│  • Auto-cleanup (duplicates, stale markers)             │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  OUTPUT & MONITORING                                    │
│  • Optimized MEMORY.md                                  │
│  • Archive files (versioned)                            │
│  • Health dashboard                                     │
│  • Alert system                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
smart-memory-hygiene/
├── README.md                 # This file
├── ROADMAP.md               # Development roadmap
├── docs/
│   ├── architecture.md      # Detailed architecture
│   ├── api-spec.md          # Public API specification
│   └── examples/            # Usage examples
├── src/
│   ├── __init__.py
│   ├── parser/             # Memory file parsers
│   │   ├── __init__.py
│   │   ├── memory_md.py    # MEMORY.md parser
│   │   ├── daily_notes.py  # Daily notes parser
│   │   └── project_files.py # Project files parser
│   ├── scorer/            # Importance scoring
│   │   ├── __init__.py
│   │   ├── recency.py     # Time-based scoring
│   │   ├── frequency.py   # Access-based scoring
│   │   └── relevance.py   # Semantic relevance
│   ├── deduper/           # Deduplication engine
│   │   ├── __init__.py
│   │   ├── semantic.py    # Semantic similarity
│   │   └── merger.py      # Entry merging
│   ├── predictor/         # Predictive cleanup (future)
│   │   └── __init__.py
│   └── utils/             # Utilities
│       ├── __init__.py
│       └── logger.py
├── tests/
│   ├── fixtures/          # Test data
│   │   ├── sample-memory.md
│   │   └── sample-daily-notes/
│   └── test_*.py          # Unit tests
├── scripts/
│   ├── dev-test.sh        # Development testing
│   └── install.sh         # Installation script
└── requirements.txt       # Python dependencies
```

---

## 🚀 Quick Start

### Installation

```bash
# Clone/navigate to repo
cd /mnt/toshiba/projects/smart-memory-hygiene

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Dry run (safe, no changes)
python -m src.parser.memory_md --dry-run ~/.openclaw/workspace/MEMORY.md
```

### Usage

```python
from src.parser import MemoryMDParser
from src.scorer import ImportanceScorer
from src.deduper import SemanticDeduplicator

# Parse MEMORY.md
parser = MemoryMDParser()
entries = parser.parse("~/.openclaw/workspace/MEMORY.md")

# Score importance
scorer = ImportanceScorer()
scored = scorer.score(entries)

# Deduplicate
deduper = SemanticDeduplicator()
optimized = deduper.deduplicate(scored)

# Output
parser.write(optimized, "~/.openclaw/workspace/MEMORY.md.optimized")
```

---

## 📊 Features

### Phase 1: Foundation (MVP)
- [ ] MEMORY.md parser
- [ ] Importance scoring (recency + frequency)
- [ ] Basic deduplication
- [ ] Dry-run mode
- [ ] Backup before changes

### Phase 2: Intelligence
- [ ] Semantic similarity detection
- [ ] Cross-reference validation
- [ ] Smart merge (consolidate related entries)
- [ ] Archive management

### Phase 3: Prediction
- [ ] Access pattern learning
- [ ] Predictive cleanup
- [ ] Self-healing mechanisms
- [ ] Health dashboard

---

## 🔒 Safety First

```python
# All operations default to DRY_RUN = True
# Changes only applied when explicitly enabled

DRY_RUN = True  # Default: log only, no file changes
BACKUP = True   # Always backup before modifications
REVIEW = True   # Human review required for destructive ops
```

---

## 🤝 Multi-Agent Support

Configure for any OpenClaw instance:

```yaml
# config.yaml
agent_instances:
  - name: "Đệ"
    workspace: "~/.openclaw/workspace"
    memory_file: "MEMORY.md"
    
  - name: "Bot A"
    workspace: "/path/to/bot-a"
    memory_file: "memory/MEMORY.md"
    
  - name: "Bot B"
    workspace: "/path/to/bot-b"
    memory_file: "long-term-memory.md"
```

---

## 📈 Roadmap

See [ROADMAP.md](./ROADMAP.md) for detailed development timeline.

---

## 📝 License

Internal project for OpenClaw ecosystem.

---

*Built with ❤️ by Đệ — making AI memory management intelligent.*
