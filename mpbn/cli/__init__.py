
import mpbn

import sys
from argparse import ArgumentParser

def main():
    ap = ArgumentParser(prog=sys.argv[0])
    ap.add_argument("bnet_file")
    ap.add_argument("method", choices=["attractors", "fixedpoints", "bn2asp"])
    ap.add_argument("--limit", type=int, default=0,
                    help="limit the number of results")
    ap.add_argument("--encoding", default=mpbn.DEFAULT_ENCODING,
                    choices=mpbn.MPBooleanNetwork.supported_encodings,
                    help=f"Encoding method (default: {mpbn.DEFAULT_ENCODING})")
    ap.add_argument("--simplify", action="store_true", default=False,
                    help="Try costly Boolean function simplifications to improve encoding")
    ap.add_argument("--try-unate-hard", action="store_true", default=False,
                    help="Try even more costly Boolean function simplifications")
    args = ap.parse_args()
    mbn = mpbn.MPBooleanNetwork(args.bnet_file, encoding=args.encoding,
                    simplify=args.simplify,
                    try_unate_hard=args.try_unate_hard)
    if args.method == "attractors":
        for attractor in mbn.attractors(limit=args.limit):
            print(attractor)
    elif args.method == "fixedpoints":
        for attractor in mbn.fixedpoints(limit=args.limit):
            print(attractor)
    elif args.method == "bn2asp":
        print(mbn.asp_of_bn())
