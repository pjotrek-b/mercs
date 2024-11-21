#!/usr/bin/python3

# @author: Peter Bubestinger-Steindl (p.bubestinger at ArkThis com)
# @date: 2024-11-22

# This program reads JSON input and applies it to a filesystem object as
# extended attributes (xattrs).

import argparse
import json
import sys
import os

# --- handling JSON data:

def read_json_file(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

def read_json_stdin():
    data = None
    if sys.stdin.isatty():
        print("No JSON data provided in standard input. Exiting...")
        sys.exit(1)
    else:
        data = json.load(sys.stdin)
    return data

def show_json(json):
    for key, value in json[0].items():
        print("{} = {}".format(key, value))

# --- handling extended attributes:

def write_xattrs_list(target, data, prefix='user.'):
    for key, value in data.items():
        os.setxattr(target, prefix + key, value.encode())

def write_xattrs_dict(target, data, prefix='user.'):
    if isinstance(data, dict):
        for key, value in data.items():
            strvar = str(value)
            os.setxattr(target, prefix + key, strvar.encode())
    elif isinstance(data, list):
        write_xattrs_list(target, data, prefix)
        """
        for i, item in enumerate(data):
            os.setxattr(target, f"{i}", json.dumps(item).encode())
        """
    else:
        raise ValueError("JSON data must be a dictionary or a list.")

def read_xattrs(target):
    xattrs = os.listxattr(target)
    return xattrs

def parse_args():
    parser = argparse.ArgumentParser(description='Write JSON data as xattrs to a file.')
    parser.add_argument('-t', '--target',
            type=str,
            required=True,
            help='A filename to write xattrs to.'
            )
    parser.add_argument('-j', '--json',
            type=str,
            required=True,
            default='-',
            help='A filename containing JSON data to write as xattrs, or - to read JSON data from standard input.'
            )
    return parser


# --- Main function:

def main():
    # Get commandline arguments/options:
    parser = parse_args()
    args = parser.parse_args()

    print("parsed args.")

    if args.json == '-':
        json_data = read_json_stdin()
    else:
        json_data = read_json_file(args.json)

    print("read json.\n")
    #show_json(json_data)


    target = args.target
    write_xattrs_dict(target, json_data[0])
    print("wrote xattrs to: {}".format(target))

    print("\nReading xattrs from target:")
    xattrs = read_xattrs(target)
    print(xattrs)

if __name__ == '__main__':
    main()

