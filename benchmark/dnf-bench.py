import mpbn
import sys

mbn = mpbn.load(sys.argv[1])

# The test is only relevant if we enforce automatic DNF conversion.
assert(mbn.auto_dnf)

unate_functions = 0
total_functions = 0
total_complexity = 0
for (n,f) in mbn.items():
    # Constants are ignored.
    if type(f) is mbn.ba.AND:
        total_complexity += 1
    if type(f) is mbn.ba.OR:
        total_complexity += len(f.args)
    if mbn._is_unate[n]:
        unate_functions += 1        
    total_functions += 1

print(f"{total_complexity},{unate_functions},{total_functions},{unate_functions==total_functions}")
sys.stdout.flush()

# Compute the first trap space to check if there are any issues
# with the ASP encoding.
first_trap = next(mbn.attractors())