## Testing DNF encoding against currently published version

The `dnf-bench.py` script builds the DNF encoding and uses it to compute *one* minimal
trap space. It's not the best test of correctness, but it should work as a simple
comparative benchmark. For each model, it reports the total number of DNF clauses
in the model encoding, the number of unate functions, and the total number of functions.

You should run this in the `benchmark` folder, not in the repository root:

```
./baseline.sh > baseline.out.txt
./current.sh > current.out.txt
```