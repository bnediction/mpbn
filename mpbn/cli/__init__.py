
import mpbn

import os
import sys
from argparse import ArgumentParser

def main():
    if "CLINGO_OPTS" in os.environ:
        mpbn.clingo_options += os.environ["CLINGO_OPTS"].split(" ")

    ap = ArgumentParser(prog=sys.argv[0])
    ap.add_argument("bnet_file")
    ap.add_argument("method", choices=["attractors", "fixedpoints", "bn2asp"])
    ap.add_argument("--limit", type=int, default=0,
                    help="limit the number of results")
    ap.add_argument("--encoding", default=mpbn.DEFAULT_ENCODING,
                    choices=mpbn.MPBooleanNetwork.supported_encodings,
                    help=f"Encoding method (default: {mpbn.DEFAULT_ENCODING})")
    ap.add_argument("--boolfunclib", default="aeon",
                    choices=mpbn.SUPPORTED_BOOLFUNCLIBS,
                    help=f"Backend lib for Boolean functions (default: {mpbn.DEFAULT_BOOLFUNCLIB})")
    ap.add_argument("--input-is-dnf", action="store_true", default=False,
                    help="Functions are already in DNF form")
    ap.add_argument("--simplify", action="store_true", default=False,
                    help="Try costly Boolean function simplifications to improve encoding")
    ap.add_argument("--try-unate-hard", action="store_true", default=False,
                    help="Try even more costly Boolean function simplifications")
    ap.add_argument("--count", action="store_true",
                    help="Returns only the number of solutions")
    args = ap.parse_args()
    mbn = mpbn.MPBooleanNetwork(args.bnet_file, encoding=args.encoding,
                    boolfunclib=args.boolfunclib,
                    auto_dnf=not args.input_is_dnf,
                    simplify=args.simplify,
                    try_unate_hard=args.try_unate_hard)
    if args.method in ["attractors", "fixedpoints"]:
        if args.count:
            func = getattr(mbn, f"count_{args.method}")
            print(func(limit=args.limit))
        else:
            func = getattr(mbn, args.method)
            for obj in func(limit=args.limit):
                print(obj)
    elif args.method == "bn2asp":
        print(mbn.asp_of_bn())
