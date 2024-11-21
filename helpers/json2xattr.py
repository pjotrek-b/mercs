#!/usr/bin/python3

# @author: Peter Bubestinger-Steindl (p.bubestinger at ArkThis com)
# @date: 2024-11-22

# This program reads JSON input and applies it to a filesystem object as
# extended attributes (xattrs).

import argparse
import json
import sys
import os


# --- Commandline parameters:

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
    parser.add_argument('-p', '--prefix',
            type=str,
            default='user.',
            help='Attribute namespace prefix: defaults to "user." (POSIX)'
            )
    return parser

def handle_args(args):
    # TODO: args.json: check if file exists.
    #print("Default prefix: '{}'".format(args.prefix)) # verbose
    pass

# This function will convert bytes to MB.... GB... etc
# use "step_unit=1024.0" for KiB, etc.
# use "step_unit=1000.0" for kilo (=1000), etc.
def convert_bytes(num, step_unit=1024.0):
    for x in ['bytes', 'kB', 'MB', 'GB', 'TB']:
        if num < step_unit:
            return "%3.1f %s" % (num, x)
        num /= step_unit


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

def write_xattrs_list(target, data, prefix=None):
    for key, value in data.items():
        os.setxattr(target, prefix + key, value.encode())

def write_xattrs_dict(target, data, prefix=None):
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

def clear_xattrs(target):
    xattrs = os.listxattr(target)
    for key in xattrs:
        os.removexattr(target, key)


def show_xattr_limits():
    print("Max. size of an extended attribute: {}".format(convert_bytes(os.XATTR_SIZE_MAX)))


# --- Main function:

def main():
    # Get commandline arguments/options:
    parser = parse_args()
    args = parser.parse_args()
    handle_args(args)

    #print("parsed args.")

    # Use prefix from args (or default):
    prefix = args.prefix

    if args.json == '-':
        json_data = read_json_stdin()
    else:
        json_data = read_json_file(args.json)

    #print("read json.\n")
    #show_json(json_data)


    target = args.target
    #show_xattr_limits()    # nice, but verbose

    #print("Removing existing xattrs from {}...".format(target))
    clear_xattrs(target)
    metadata = json_data[0]
    write_xattrs_dict(target, metadata, prefix=prefix)
    print("wrote {} xattrs to: {}".format(
        convert_bytes(sys.getsizeof(metadata)),
        target)
        )

    #print("\nReading xattrs from target:")
    xattrs = read_xattrs(target)
    #print(xattrs)  # pretty verbose. But nice to see what's happening.

if __name__ == '__main__':
    main()

