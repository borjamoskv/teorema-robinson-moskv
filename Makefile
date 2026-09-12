.PHONY: help status test intel engine studio lab sync audit

help:
	@./moskv --help

status:
	@./moskv status

test:
	@./moskv test

intel:
	@./moskv intel

engine:
	@./moskv engine

studio:
	@./moskv studio

lab:
	@./moskv lab

sync:
	@./moskv sync

audit:
	@python3 /Users/borjafernandezangulo/.gemini/antigravity/scratch/legion_100_agents_audit.py

build-guard:
	@echo "[ULTRATHINK] Compiling Native C-Extension OUT-OF-TREE (/tmp/cortex_exergy_build)..."
	@mkdir -p /tmp/cortex_exergy_build
	@clang -O3 -bundle -undefined dynamic_lookup $$(python3-config --cflags) src/02_engines/cortex_guard/cortex_guard_core.c -o /tmp/cortex_exergy_build/cortex_guard_core.so
	@echo "[PASS] cortex_guard_core.so compilado determinísticamente en /tmp/cortex_exergy_build."

