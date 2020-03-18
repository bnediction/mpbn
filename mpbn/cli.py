
import mpbn

import sys
from argparse import ArgumentParser

def main():
    ap = ArgumentParser(prog=sys.argv[0])
    ap.add_argument("bnet_file")
    ap.add_argument("method", choices=["attractors", "bn2asp"])
    args = ap.parse_args()
    mbn = mpbn.MPBooleanNetwork(args.bnet_file)
    if args.method == "attractors":
        for attractor in mbn.attractors(yield_=True):
            print(attractor)
    elif args.method == "bn2asp":
        print(mbn.asp_of_bn())
