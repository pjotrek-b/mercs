#!/usr/bin/python3

# @author: Peter Bubestinger-Steindl (p.bubestinger at ArkThis com)
# @date: 2024-11-22

# This program reads JSON input and applies it to a filesystem object as
# extended attributes (xattrs).

import argparse
import json
import sys
import os
import traceback
import time


# --- Commandline parameters:

def parse_args():
    parser = argparse.ArgumentParser(
            description='Write JSON data as xattrs to a file.'
            )
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
    parser.add_argument('-a', '--archive',
            type=bool,
            default=False,
            help='Preserve source as best as possible. Disables: value-strip, key-lowercase.'
            )
    parser.add_argument('-lk', '--lower_key',
            type=bool,
            default=False,
            help='Force lowercase on all key strings'
            )
    parser.add_argument('-lv', '--lower_value',
            type=bool,
            default=False,
            help='Force lowercase on all key strings'
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

def clean_key(key):
    global args

    out = str(key).strip()
    if (not args.archive and args.lower_key):
        out = out.lower()
    return out

def clean_value(value):
    out = str(value).strip()
    if (not args.archive and args.lower_value):
        out = out.lower()
    return out

def write_xattrs_list(target, data, prefix=None, archive=True):
    if not isinstance(data, list):
        raise ValueError("data must be a list")

    for key, value in data.items():
        try:
            written = write_xattr(target, key, value, prefix, archive)
        except Exception as e:
            print("ERROR: could not write '{} = {}'.".format(key, value))
            print(e)
            sleep(1)
            raise(e)
            break

def write_xattrs_dict(target, data, prefix=None, archive=True):
    if not isinstance(data, dict):
        raise ValueError("data must be a dictionary")

    total = {}
    total['keys'] = 0
    total['values'] = 0

    for key, value in data.items():
        try:
            written = write_xattr(target, key, value, prefix, archive)
            # Add byte sizes:
            total['keys'] += written['keys']
            total['values'] += written['values']
            #print("current: {} +{}".format(total['keys'], total['values']))    # verbose

        except Exception as e:
            print("ERROR: could not write '{} = {}'.".format(key, value))
            #traceback.print_exc()
            print(e)
            time.sleep(1)
            raise(e)

    total['sum'] = total['keys'] + total['values']
    print("wrote {} ({} +{}) / {} bytes as attributes.".format(
        convert_bytes(total['sum']),
        total['keys'], total['values'],
        convert_bytes(sys.getsizeof(data))
        ))

# Stores a list or dict of key/value pairs as xattrs to `target`.
def write_xattrs(target, data, prefix=None, archive=True):
    if isinstance(data, dict):
        write_xattrs_dict(target, data, prefix, archive)
    elif isinstance(data, list):
        write_xattrs_list(target, data, prefix, archive)
    else:
        raise ValueError("data must be a dictionary or a list.")

# Store a single xattr, but possibly preprocess/sanitize/normalize key/values
# before writing it.
def write_xattr(target, key, value, prefix=None, archive=True):
    # Count bytes written as attributes:
    written = {}
    written['keys'] = 0
    written['values'] = 0

    if archive:
        # preserve:
        strkey = key
        strval = value
    else:
        # clean/strip:
        strkey = clean_key(key)
        strval = clean_value(value)

    print("{} = {}".format(strkey.ljust(30), strval)) #debug

    # We may want to change that when binary data comes in?
    strval = str(strval).encode() # I have type-doubts and had issues already.
    strkey = (prefix + strkey).encode() # now it's offical ;P

    try:
        #print(".", end='')
        os.setxattr(target, strkey, strval, flags=os.XATTR_CREATE)
        """ verbose:
        print("current: {} +{} - '{}' = '{}'".format(
            len(strkey), len(strval), strkey.decode(), strval.decode()
            ))
        """
        written['keys'] += len(strkey)
        written['values'] += len(strval)
    except FileExistsError:
        print("x", end='')
    except Exception as e:
        print("ouch.")
        raise(e)

    # Brag how much we've made:
    return written

def read_xattrs(target):
    xattrs = os.listxattr(target)
    return xattrs

def clear_xattrs(target):
    xattrs = os.listxattr(target)
    for key in xattrs:
        os.removexattr(target, key)


def show_xattr_limits():
    # See: https://unix.stackexchange.com/questions/390274/what-are-costs-of-storing-xattrs-on-ext4-btrfs-filesystems
    print("Max. size of an extended attribute: {}".format(convert_bytes(os.XATTR_SIZE_MAX)))


# --- Main function:

def main():
    # Get commandline arguments/options:
    parser = parse_args()
    global args
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
    try:
        write_xattrs(target, metadata, prefix=prefix, archive=args.archive)
    except Exception as e:
        print("Failed.")
        raise(e)

    print("saved xattrs to: {}".format(
        convert_bytes(sys.getsizeof(metadata)),
        target)
        )

    #print("\nReading xattrs from target:")
    xattrs = read_xattrs(target)
    #print(xattrs)  # pretty verbose. But nice to see what's happening.

if __name__ == '__main__':
    main()

