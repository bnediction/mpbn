
import mpbn
from colomoto import minibn

import sys
from argparse import ArgumentParser

def main():
    ap = ArgumentParser(prog=sys.argv[0])
    ap.add_argument("bnet_file")
    ap.add_argument("method", choices=["attractors", "bn2asp"])
    args = ap.parse_args()
    bn = minibn.BooleanNetwork.load(args.bnet_file)
    mbn = mpbn.load(bn)
    if args.method == "attractors":
        for attractor in mbn.attractors(yield_=True):
            print(attractor)
    elif args.method == "bn2asp":
        print(mbn.asp_of_bn())


