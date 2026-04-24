# MEMORY.md (Long-term)

> Curated, long-term memory. Keep it short and high-signal.
> Updated: 2026-04-20

## Workflow - Google Drive Bridge (2026-04-13)
- **Pattern:** Laptop nhà (OpenClaw) → Google Drive (rclone mount) → Máy công ty (xem)
- **Tools:** openpyxl, pandas, rclone mount gdrive_sa:
- **Path:** ~/gdrive/OpenClaw/
- **Why:** Windows node lỗi escape, Google Sheets API cần share quyền
- **Status:** ✅ Chính thức, không dùng Windows node cho Excel phức tạp

## Critical Rules - ABSOLUTE

### Completion Reporting Discipline - MANDATORY

- **CONSEQUENCE**: User asks again = broken trust = operational failure
- **PRIORITY**: Completion reporting > ALL other tasks, no exceptions
- REL: CAUSED_BY 2026-03-31 incident (subagent done, main silent → Sếp phải hỏi lại)

### Subagent Anti-Spam Rule
→ See AGENTS.md `🚫 Subagent Anti-Spam Rule`

## Empty Promises Rule
- **NEVER** say "sẽ báo lại sau X phút" nếu chưa tạo subagent/cron
- **ALWAYS** set up mechanism (subagent, cron, callback) BEFORE promising follow-up
- **RULE**: Task >30s → progress update ngay trong turn; việc nền → subagent + announce

---

## Identity & working style

- User: **nontech**, assistant acts as **production dev**.
- [preference] 2026-03-05: Bản tin chiến sự Trung Đông: tóm tắt theo từng mặt trận (Iran, Gaza, Lebanon, Syria, Yemen) 24h gần nhất; tự chốt format.
- [workflow] Blocker escalation protocol (nếu bị block >2 phút): BLOCKER: <what> / CẦN SẾP: 1–2 actions / ETA: <time>. Ghi rõ làm được trực tiếp hay cần copy/paste.

## NotebookLM automation stack (2026-04-14)
- [workflow] **NotebookLM MCP HTTP Server** — `localhost:3000` (PM2), code at `/mnt/toshiba/tools/notebooklm-mcp/`, uses Google cookies. Skill: `notebooklm-query` (`health|list|ask`). Auto-restart + auto-start. RAM ~20MB.
- [decision] 2026-04-14: **NotebookLM Auto skill v2 hoàn tất** (40+ commands CRUD notebooks/sources/exports) chạy trên laptop. REL: MCP Server <-ENABLES-> Auto skill.

## Canonical memory recall (2026-04-16)
- [workflow] Quy tắc **canonical slug / query expansion**: query mơ hồ phải map về slug chuẩn (vd `finance app status` → `finance-suite status/roadmap`).
- [insight] Token quá ngắn (vd `A1`) recall kém → ưu tiên query theo **thành phần canonical** + cross-check `memory/projects/personal-finance.md` (không spam thêm memory).
- REL: CAUSED_BY recall drift vào các context khác (Bé Thỏ/Camoufox) khi dùng query mơ hồ.

## Durable operating rules

- [instruction] 2026-03-13: **Memory triage bắt buộc**: (1) `nmem recall "<query>"` → (2) search `MEMORY.md` + `memory/*.md` → (3) `memory/projects/INDEX.md` → rồi mới kết luận không có.
- [preference] 2026-03-14: Khi kiểm tra trí nhớ → phải có 3 phần: (1) status hiện tại, (2) project memory, (3) daily notes + đề xuất.
- [instruction] 2026-03-11: VPS `14.225.222.53` → mặc định SSH trực tiếp user `openclaw` + key `_runtime/vps_moltbot_ssh_ed25519*`; không dùng `nodes.run` trừ khi được yêu cầu.

## Memory system

- [workflow] 2026-03-26: **Không dùng `nmem cleanup`** trong vận hành thường; chỉ dùng sau khi có backup rõ ràng.
- [workflow] 2026-03-30: nmem hygiene → `systemd` user timer `nmem-hygiene` chạy 2 lần/ngày (09:20, 21:20).

## Multi-agent & routing

- [workflow] 2026-03-31: **Root cause investigation pattern** — hướng vá tận gốc nằm ở normalize/outbound layer (`auth-profiles-B5ypC5S-.js`), không chỉ symptom-fix.
- [decision] 2026-03-30: **Fireworks lane fallback chính thức** — thứ tự: Kimi K2.5 Turbo → DeepSeek V3.1 → gpt-oss-120b (main/coder/researcher); `ops` giữ `gpt-oss-120b`.
- [error→workflow] 2026-03-31: **Completion reporting discipline** — subagent done nhưng main không báo ngay → Sếp phải hỏi lại. Rule 5 bước: giao việc → agent xong → main kiểm tra → main báo ngay → ghi memory. Thiếu bước (4) = chưa done.

## Promoted From Short-Term Memory (2026-04-24)

<!-- openclaw-memory-promotion:memory:memory/2026-03-26.md:1:4 -->
- [workflow] Finance-suite hôm nay đã được đẩy thêm nhiều nhánh user-facing trước khi phát bản test: fix Telegram sync logout; refresh BACKLOG/SPEC/ARCHITECTURE; fix A1 reference price sync test; Bills có mark-paid + actual amount + undo; Budgets có progress cards + summary card; verify trọng yếu pass; build release APK split-per-ABI pass; bản ARM64 đã upload lên Drive output theo đúng pipeline phát hành. [synced]

## Test edge cases

- [workflow] Short entry [synced]
- [decision] Entry with REL: test-rel-value and CAUSED_BY test-cause
- [error→workflow] Complex entry with multiple tags REL: tag1 CAUSED_BY tag2 [synced]
