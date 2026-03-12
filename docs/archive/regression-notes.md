# Regression Notes

As the project evolves, keep an eye on:
- output shape consistency
- risk visibility
- heuristic behavior drift
- mock/live contract compatibility

## Simple regression habit
Whenever a meaningful change lands:
1. run `make check`
2. run `make test`
3. run `scripts/demo_capture.sh`
4. compare output structure against examples/
