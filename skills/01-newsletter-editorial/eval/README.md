# Newsletter editorial outcome eval

`bash skills/01-newsletter-editorial/eval/run-eval.sh` is the deterministic CI layer. It uses synthetic, held-out fixtures and the Python standard library only. Static contract mutation checks and outcome validation are deliberately separate: the outcome validator compares candidate decisions, reason codes, and next actions to frozen expected results rather than checking whether the skill text was loaded.

The manually dispatched harness runs `run_harness.py` with a repository-controlled runner and approved image. It creates a new temporary workspace for every condition and trial, exposing only the fixture, runner, and (when enabled) `SKILL.md`. Each Docker execution uses a read-only root filesystem and `--network none`, without mounting the checkout or providing credentials. The runner emits JSON records with `name`, `condition`, `trial`, and `outcome`.

Run three to six trials per case. The gate requires at least an 80% enabled pass rate and a positive enabled-versus-disabled delta. The manual GitHub Actions workflow retains the JSON comparison report; do not run this harness in pull-request CI.
