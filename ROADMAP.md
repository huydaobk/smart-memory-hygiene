# Smart Memory Hygiene - Roadmap

> **Last updated:** 2026-04-24  
> **Status:** Phase 1 - Foundation

---

## 🗓️ Timeline

```
Month 1 (Apr-May)    Month 2 (May-Jun)     Month 3 (Jun-Jul)
├─ Phase 1: MVP      ├─ Phase 2: Intel     ├─ Phase 3: Predict
│  ├─ Parser         │  ├─ Semantic        │  ├─ ML Model
│  ├─ Scorer         │  ├─ Cross-ref       │  ├─ Dashboard
│  └─ Tests          │  └─ Merge           │  └─ Self-heal
└─ Integration test  └─ Beta with Đệ      └─ Multi-agent
```

---

## Phase 1: Foundation (Weeks 1-4)

### Week 1: Setup & Parser
- [x] Create repo structure
- [ ] MEMORY.md parser (sections, entries, metadata)
- [ ] Daily notes parser
- [ ] Test fixtures (sample files)
- [ ] Unit tests for parsers

**Deliverable:** Can parse and reconstruct MEMORY.md without data loss.

### Week 2: Scoring Engine
- [ ] Recency scorer (time since last update)
- [ ] Frequency scorer (access count tracking)
- [ ] Composite importance score
- [ ] Scorer unit tests

**Deliverable:** Can score all entries in MEMORY.md by importance.

### Week 3: Deduplication MVP
- [ ] Exact duplicate detection
- [ ] Section-based dedup (promoted blocks)
- [ ] Raw marker cleanup
- [ ] Deduplicator unit tests

**Deliverable:** Can clean MEMORY.md, remove duplicates and markers.

### Week 4: Safety & Integration
- [ ] Backup system (pre-change snapshots)
- [ ] Dry-run mode (default)
- [ ] Logging & audit trail
- [ ] Integration test with Option 2

**Deliverable:** Safe to run alongside existing hygiene system.

---

## Phase 2: Intelligence (Weeks 5-8)

### Week 5: Semantic Analysis
- [ ] Embedding-based similarity (sentence-transformers)
- [ ] Cluster related entries
- [ ] Topic extraction
- [ ] Semantic tests

**Deliverable:** Can identify semantically similar entries.

### Week 6: Smart Merge
- [ ] Merge related entries (consolidate)
- [ ] Timeline reconstruction (e.g., 3 "Gateway crash" → 1 timeline)
- [ ] Preserve root cause + fix
- [ ] Merge tests

**Deliverable:** Can consolidate related memories intelligently.

### Week 7: Cross-Reference
- [ ] Validate against daily notes
- [ ] Check project file consistency
- [ ] Suggest missing updates
- [ ] Cross-ref tests

**Deliverable:** Can detect inconsistencies across memory layers.

### Week 8: Archive Management
- [ ] Smart archive (low-importance → cold storage)
- [ ] Archive search/retrieval
- [ ] Versioned archives
- [ ] Archive tests

**Deliverable:** Automatic archiving with full search capability.

---

## Phase 3: Prediction (Weeks 9-12)

### Week 9: Access Pattern Learning
- [ ] Track entry access patterns
- [ ] Build usage model
- [ ] Predict future relevance
- [ ] Pattern tests

**Deliverable:** Can predict which entries will be needed.

### Week 10: Predictive Cleanup
- [ ] Auto-archive low-priority predictions
- [ ] Boost high-priority predictions
- [ ] Confidence thresholds
- [ ] Predictive tests

**Deliverable:** Proactive memory management.

### Week 11: Health Dashboard
- [ ] Memory health metrics
- [ ] Size trends
- [ ] Cleanup effectiveness
- [ ] Alert system

**Deliverable:** Visual dashboard for memory health.

### Week 12: Self-Healing & Multi-Agent
- [ ] Self-healing mechanisms
- [ ] Multi-agent configuration
- [ ] Agent-specific tuning
- [ ] Full system tests

**Deliverable:** Production-ready for multiple agents.

---

## 🎯 Milestones

| Milestone | Date | Criteria |
|-----------|------|----------|
| **MVP Ready** | Week 4 | Parser + Scorer + Deduplication working |
| **Beta Test** | Week 8 | Running alongside Option 2, no data loss |
| **Production** | Week 12 | Multi-agent support, dashboard, self-healing |

---

## 📝 Notes

- **Safety first:** All phases have dry-run default
- **Test coverage:** Target >90% for each phase
- **Documentation:** Update docs with each feature
- **Sếp review:** Checkpoint at end of each phase

---

*Roadmap subject to change based on Sếp Huy's feedback.*
