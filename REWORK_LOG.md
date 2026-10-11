# Rework log

This file explains, step by step, what was changed during the big rework of
Terminal Academy, **why** each decision was made, and what is still open for
discussion. It is written in simple English on purpose.

---

## Stage 0 — Preparation

**What was done**
- Created the branch `rework` from `main`. All work happens there; one PR
  goes from `rework` into `main` at the end.

**Decisions**
- Every stage is a separate commit (or a few commits), so you can read the
  history stage by stage with `git log --oneline main..rework`.
- Wave 1 tasks (audit, sites, lessons plan, open-source docs) touch
  different files, so they ran in parallel. Wave 2 tasks change the same
  code, so they ran one after another.

