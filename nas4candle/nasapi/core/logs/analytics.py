import argparse
import sys

from nas4candle.nasapi.core.logs import parsing, json

def create_parser():
    parser = argparse.ArgumentParser(description='Run some analytics for nas4candle.nasapi.')

    subparsers = parser.add_subparsers(help='Kind of analytics.')

    mapping = dict()

    # parsing
    name, func = parsing.add_subparser(subparsers)
    mapping[name] = func

    # json
    name, func = json.add_subparser(subparsers)
    mapping[name] = func

    return parser, mapping


def main():
    parser, mapping = create_parser()

    args = parser.parse_args()

    mapping[sys.argv[1]](**vars(args))

