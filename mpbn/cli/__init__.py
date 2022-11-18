
import mpbn

import sys
from argparse import ArgumentParser

def main():
    ap = ArgumentParser(prog=sys.argv[0])
    ap.add_argument("bnet_file")
    ap.add_argument("method", choices=["attractors", "fixedpoints", "bn2asp"])
    ap.add_argument("--limit", type=int, default=0,
                    help="limit the number of results")
    args = ap.parse_args()
    mbn = mpbn.MPBooleanNetwork(args.bnet_file)
    if args.method == "attractors":
        for attractor in mbn.attractors(limit=args.limit):
            print(attractor)
    elif args.method == "fixedpoints":
        for attractor in mbn.fixedpoints(limit=args.limit):
            print(attractor)
    elif args.method == "bn2asp":
        print(mbn.asp_of_bn())
