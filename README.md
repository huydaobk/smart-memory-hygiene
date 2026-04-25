# Smart Memory Hygiene Framework

> **Version:** 1.0.0  
> **Author:** Đệ (AI Assistant) for Sếp Huy  
> **GitHub:** https://github.com/huydaobk/smart-memory-hygiene

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
├── ROADMAP.md               # Development roadmap ✅ COMPLETED
├── .github/workflows/       # CI/CD
│   └── tests.yml            # Auto-test on push
├── src/
│   ├── __init__.py
│   ├── parser/             # Week 1 ✅
│   │   ├── memory_md.py    # MEMORY.md parser (5 entry types)
│   │   └── __init__.py
│   ├── scorer/            # Week 2 ✅
│   │   ├── recency.py      # Time-based scoring
│   │   ├── frequency.py    # Access-based scoring
│   │   ├── composite.py    # Combined importance
│   │   └── __init__.py
│   ├── deduper/           # Week 3 ✅
│   │   ├── semantic.py     # Semantic similarity + Union-Find
│   │   └── __init__.py
│   ├── archiver/          # Week 4 ✅
│   │   ├── manager.py      # Archive with JSON index
│   │   └── __init__.py
│   ├── intelligence/      # Weeks 5-6 ✅
│   │   ├── semantic_analyzer.py  # Embedding-based similarity
│   │   ├── topic_extractor.py    # Keyword + clustering
│   │   └── __init__.py
│   ├── prediction/        # Week 7 ✅
│   │   ├── engine.py       # Access tracking + relevance prediction
│   │   └── __init__.py
│   └── dashboard/         # Week 7 ✅
│       ├── health.py       # Health score + alerts
│       └── __init__.py
├── tests/                  # All phases ✅
│   ├── test_parser_memory_md.py
│   ├── test_scorer_*.py
│   ├── test_deduper_*.py
│   ├── test_archiver_*.py
│   ├── test_semantic_analyzer.py
│   ├── test_topic_extractor.py
│   ├── test_prediction.py
│   └── fixtures/
├── scripts/
│   ├── full_pipeline.py    # End-to-end pipeline
│   └── run_tests.py        # Test runner
└── requirements.txt        # Python dependencies
```

---

## 🚀 Quick Start

### Installation

#### Method 1: Clone from GitHub
```bash
# Clone repo
git clone https://github.com/YOUR_USERNAME/smart-memory-hygiene.git
cd smart-memory-hygiene

# Install dependencies
pip install -r requirements.txt
```

#### Method 2: Direct Download
```bash
# Download and extract
curl -L https://github.com/YOUR_USERNAME/smart-memory-hygiene/archive/main.tar.gz | tar xz
cd smart-memory-hygiene-main

# Install dependencies
pip install -r requirements.txt
```

#### Method 3: For OpenClaw Users
```bash
# Navigate to your OpenClaw workspace
cd ~/.openclaw/workspace

# Clone into projects folder
git clone https://github.com/YOUR_USERNAME/smart-memory-hygiene.git projects/smart-memory-hygiene
cd projects/smart-memory-hygiene

# Install dependencies
pip install -r requirements.txt
```

### Verify Installation
```bash
# Run all tests
python run_phase2_tests.py
python run_phase3_tests.py

# Or run individual test suites
python run_tests.py          # Week 1: Parser
python run_week2_tests.py    # Week 2: Scorer
python run_week3_tests.py    # Week 3: Deduplicator
python run_week4_tests.py    # Week 4: Archiver
```

### Usage Examples

#### Example 1: Basic Memory Analysis
```python
#!/usr/bin/env python3
"""Basic analysis of MEMORY.md"""
import sys
sys.path.insert(0, '/path/to/smart-memory-hygiene')

from src.parser.memory_md import MemoryMDParser
from src.scorer.composite import ImportanceScorer
from src.dashboard.health import HealthDashboard

# Parse your MEMORY.md
parser = MemoryMDParser(dry_run=True)
entries = parser.parse("~/.openclaw/workspace/MEMORY.md")

print(f"Found {len(entries)} entries")

# Score all entries
scorer = ImportanceScorer()
for entry in entries:
    entry.importance = scorer.score(entry)

# Sort by importance
entries.sort(key=lambda e: e.importance, reverse=True)

print("\nTop 5 most important:")
for i, e in enumerate(entries[:5]):
    print(f"{i+1}. [{e.type}] {e.importance:.3f} - {e.content[:50]}...")

# Health check
dashboard = HealthDashboard()
metrics = dashboard.get_metrics(
    total_entries=len(entries),
    duplicate_entries=0,
    archived_entries=0,
    fragmented_sections=5,
    total_sections=15
)
score = dashboard.get_health_score(metrics)
print(f"\nHealth Score: {score:.3f}")
```

#### Example 2: Full Pipeline (Parse → Score → Deduplicate → Archive)
```python
#!/usr/bin/env python3
"""Full memory hygiene pipeline"""
import sys
sys.path.insert(0, '/path/to/smart-memory-hygiene')

from src.parser.memory_md import MemoryMDParser
from src.scorer.composite import ImportanceScorer
from src.deduper.semantic import SemanticDeduplicator
from src.archiver.manager import ArchiveManager
from src.prediction.engine import PredictionEngine

MEMORY_FILE = "~/.openclaw/workspace/MEMORY.md"
ARCHIVE_DIR = "~/.openclaw/workspace/memory/archive"

# Step 1: Parse
parser = MemoryMDParser(dry_run=True)
entries = parser.parse(MEMORY_FILE)
print(f"Parsed {len(entries)} entries")

# Step 2: Score
scorer = ImportanceScorer()
for entry in entries:
    entry.importance = scorer.score(entry)

# Step 3: Deduplicate
deduper = SemanticDeduplicator(similarity_threshold=0.8)
entries = deduper.deduplicate(entries, importance_scorer=scorer)
print(f"After dedup: {len(entries)} entries")

# Step 4: Archive low-importance (dry-run by default)
archiver = ArchiveManager(archive_dir=ARCHIVE_DIR, importance_threshold=0.3)
archived = archiver.archive_entries([e for e in entries if hasattr(e, 'importance') and e.importance < 0.3])
print(f"Archived {len(archived)} entries")

# Step 5: Predict trends
predictor = PredictionEngine()
for i, entry in enumerate(entries[:10]):
    entry_id = f"entry-{i}"
    predictor.track_access(entry_id)

trends = predictor.get_trends(top_n=5)
print(f"Top trends: {len(trends)}")
```

#### Example 3: Semantic Search
```python
#!/usr/bin/env python3
"""Search memory by semantic similarity"""
import sys
sys.path.insert(0, '/path/to/smart-memory-hygiene')

from src.parser.memory_md import MemoryMDParser
from src.intelligence.semantic_analyzer import SemanticAnalyzer

parser = MemoryMDParser()
entries = parser.parse("~/.openclaw/workspace/MEMORY.md")

analyzer = SemanticAnalyzer(use_embeddings=False)  # Use text similarity

query = "How to sync files with Google Drive"
results = analyzer.find_most_similar(query, entries, top_k=5)

print(f"Results for: '{query}'")
for idx, score in results:
    print(f"  [{idx}] {score:.3f}: {entries[idx].content[:60]}...")
```

#### Example 4: Command Line Usage
```bash
# Run full pipeline on your MEMORY.md
cd /path/to/smart-memory-hygiene
python scripts/full_pipeline.py ~/.openclaw/workspace/MEMORY.md

# With actual archival (default is dry-run)
python scripts/full_pipeline.py ~/.openclaw/workspace/MEMORY.md --apply

# Run health check only
python -c "
import sys
sys.path.insert(0, '.')
from run_phase2_tests import *
# ... health check code
"
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

## 📋 Requirements

### System Requirements
- **Python**: 3.8 or higher
- **OS**: Linux, macOS, or Windows (WSL recommended)
- **RAM**: 4GB minimum (8GB recommended for ML features)
- **Disk**: 500MB free space

### Python Dependencies
```
# Core (required)
python-dateutil>=2.8.0
pyyaml>=6.0

# NLP & Semantic Analysis (optional but recommended)
sentence-transformers>=2.2.0
scikit-learn>=1.3.0
numpy>=1.24.0

# Testing
pytest>=7.4.0

# Logging
structlog>=23.0.0
```

### Optional: GPU Support
For faster embedding generation with sentence-transformers:
```bash
# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## 🔧 Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'sentence_transformers'`
**Solution**: Install optional dependencies
```bash
pip install sentence-transformers
```
Or run without embeddings (fallback mode):
```python
analyzer = SemanticAnalyzer(use_embeddings=False)
```

### Issue: `ImportError: numpy` not found
**Solution**: Install numpy
```bash
pip install numpy
```

### Issue: Tests fail with `pytest` not found
**Solution**: Install test dependencies
```bash
pip install pytest pytest-cov
```

### Issue: Memory file not found
**Solution**: Check path and permissions
```python
from pathlib import Path
memory_file = Path.home() / ".openclaw" / "workspace" / "MEMORY.md"
assert memory_file.exists(), f"File not found: {memory_file}"
```

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
