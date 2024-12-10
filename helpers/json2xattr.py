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
    parser.add_argument('-v', '--verbose',
            action='count',
            default=0,
            help='Increase verbosity level.'
            )
    parser.add_argument('-q', '--quiet',
            action='store_true',
            default=False,
            help='Be as quiet as possible with text output.'
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
            default=False,
            action='store_true',
            help='Preserve source as best as possible. Disables: value-strip, key-lowercase.'
            )
    parser.add_argument('-lk', '--lower_key',
            default=False,
            action='store_true',
            help='Force lowercase on all key strings'
            )
    parser.add_argument('-lv', '--lower_value',
            default=False,
            action='store_true',
            help='Force lowercase on all key strings'
            )
    parser.add_argument('-c', '--clear_first',
            default=False,
            action='store_true',
            help='Clear (=remove) existing xattrs before writing new ones. Nice to clean dirty leftovers. May come with performance penalty though.'
            )
    parser.add_argument('-ev', '--empty_values',
            default=False,
            action='store_true',
            help='By default, empty values will NOT be written to target. Use this to write empty values.'
            )

    return parser

def handle_args(args):
    # TODO: args.json: check if file exists.
    if (args.verbose > 0):
        print("\nVerbosity: {}".format(args.verbose))

        if (args.verbose > 1):
            print("Used configuration:")
            print("------------------------")
            print("Target:          {}".format(args.target))
            print("Default prefix:  {}".format(args.prefix))
            print("Lowercase key:   {}".format(args.lower_key))
            print("Lowercase value: {}".format(args.lower_value))
            print("Clear first:     {}".format(args.clear_first))
            print("Empty values:    {}".format(args.empty_values))
            print("------------------------")

        print("\n")

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

    return written

def write_xattrs_dict(target, data, prefix=None, archive=True):
    global args

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

            if (args.verbose > 1):
                #print("current: {} +{}".format(total['keys'], total['values']))
                pass

        except Exception as e:
            print("ERROR: could not write '{} = {}'.".format(key, value))
            #traceback.print_exc()
            print(e)
            time.sleep(1)
            raise(e)

    total['sum'] = total['keys'] + total['values']

    if (args.verbose > 0):
        print() # linebreak if verbose

    if (not args.quiet):
        print("wrote {} ({} +{}) / {} as attributes on '{}'.".format(
            convert_bytes(total['sum']),
            total['keys'], total['values'],
            convert_bytes(sys.getsizeof(data)),
            target
            ))

    return written

# Stores a list or dict of key/value pairs as xattrs to `target`.
def write_xattrs(target, data, prefix=None, archive=True):
    written = {}
    if isinstance(data, dict):
        written = write_xattrs_dict(target, data, prefix, archive)
    elif isinstance(data, list):
        written = write_xattrs_list(target, data, prefix, archive)
    else:
        raise ValueError("data must be a dictionary or a list.")

    return written

# Store a single xattr, but possibly preprocess/sanitize/normalize key/values
# before writing it.
def write_xattr(target, key, value, prefix=None, archive=True):
    global args

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

    # Skip empty values (unless allowed).
    if (not strval) and (not args.empty_values):
        return written

    if (args.verbose > 2):
        print("{} = '{}'".format(strkey.ljust(30), strval)) #debug

    # We may want to change that when binary data comes in?
    strval = str(strval).encode() # I have type-doubts and had issues already.
    strkey = (prefix + strkey).encode() # now it's offical ;P

    try:
        #print(".", end='')
        # This is where things get written for real:
        os.setxattr(target, strkey, strval, flags=os.XATTR_CREATE)

        if (args.verbose > 3):
            # Show information about current key/value set:
            print("current: {} +{} - '{}' = '{}'".format(
                len(strkey),
                len(strval),
                strkey.decode(),
                strval.decode()
                ))

            print("blip!")
        written['keys'] += len(strkey)
        written['values'] += len(strval)
    except FileExistsError:
        if (args.verbose == 1):
            print('*', end='')
        if (args.verbose > 4):
            print("exists: {} = '{}'".format(strkey.ljust(30), strval))

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

    # Shortcut variables for popular options:
    prefix = args.prefix
    target = args.target

    if args.json == '-':
        json_data = read_json_stdin()
    else:
        json_data = read_json_file(args.json)

    if (args.verbose > 4):
        # Very noisy, but useful for debugging:
        #print("read json.\n")
        show_json(json_data)


    if (args.verbose > 3):
        show_xattr_limits()    # nice, but verbose

    if (args.clear_first):
        if (args.verbose > 0):
            print("Removing existing xattrs from {}...".format(target))
        clear_xattrs(target)

    # Use the JSON input as metadata to write:
    metadata = json_data[0]
    try:
        written = write_xattrs(target, metadata, prefix=prefix, archive=args.archive)
    except Exception as e:
        print("Failed.")
        raise(e)

    xattrs = read_xattrs(target)
    if (args.verbose > 3):
        print("\nRead xattrs keys from target:")
        print(xattrs)  # pretty verbose. But nice to see what's happening.

if __name__ == '__main__':
    main()

