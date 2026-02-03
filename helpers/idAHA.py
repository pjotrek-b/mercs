#!/usr/bin/python3
# @author: Peter Bubestinger-Steindl (aha at ArkThis com)
# @date: 2024-11-22
# Program to generate CFIDs for existing files/data.

import os
import datetime
import random
import string
import argparse

def get_creation_timestamp(file_path):
    """
    Get the creation timestamp of a file using st_birthtime.
    This function is designed for ZFS on Linux.
    """
    stat = os.stat(file_path)
    try:
        return stat.st_birthtime
    except AttributeError:
        # Fallback to modification time if st_birthtime is not available
        return stat.st_mtime

def generate_random_string(max_chars, charset):
    """
    Generate a random string of a specified length and character set.

    :param max_chars: Maximum number of characters in the random string
    :param charset: Character set to use for the random string
    :return: Generated random string
    """
    return ''.join(random.choices(charset, k=max_chars))

def format_timestamp(timestamp, precision):
    """
    Format the timestamp based on the specified precision.

    :param timestamp: The timestamp to format
    :param precision: The precision level (1=year, 2=year+month, 3=year+month+day, etc.)
    :return: Formatted timestamp string
    """
    if precision == 1:
        return datetime.datetime.fromtimestamp(timestamp).strftime('%Y')
    elif precision == 2:
        return datetime.datetime.fromtimestamp(timestamp).strftime('%Y%m')
    elif precision == 3:
        return datetime.datetime.fromtimestamp(timestamp).strftime('%Y%m%d')
    elif precision == 4:
        return datetime.datetime.fromtimestamp(timestamp).strftime('%Y%m%dT%H')
    elif precision == 5:
        return datetime.datetime.fromtimestamp(timestamp).strftime('%Y%m%dT%H%M')
    elif precision == 6:
        return datetime.datetime.fromtimestamp(timestamp).strftime('%Y%m%dT%H%M%S')
    else:
        return datetime.datetime.fromtimestamp(timestamp).strftime('%Y%m%dT%H%M%S')

def trim_string(s, max_length):
    """
    Trim a string to a maximum length.

    :param s: The string to trim
    :param max_length: The maximum length of the string
    :return: Trimmed string
    """
    return s[:max_length]

def mkCFID(file_path, precision, context_length, random_length, max_total_length, charset, replace_whitespace):
    """
    Generate an ID for a given file based on its creation timestamp, context, and optional random string.

    :param file_path: Path to the file
    :param precision: Precision level for the timestamp
    :param context_length: Maximum length of the context
    :param random_length: Length of the random string
    :param max_total_length: Maximum total length of the ID
    :param charset: Character set to use for the random string
    :return: Generated ID in the format ⭐️$TIMESTAMP-$CONTEXT-$RANDOM❤️
    """
    # Get the creation timestamp
    timestamp = get_creation_timestamp(file_path)
    timestamp_str = format_timestamp(timestamp, precision)

    # Get the context (parent folder and filename)
    context = os.path.relpath(file_path, start=os.path.dirname(file_path))
    context = trim_string(context, context_length)
    if replace_whitespace:
        context = context.replace(' ', '_')

    # Generate the random string if random_length is greater than 0
    random_str = generate_random_string(random_length, charset) if random_length > 0 else ""

    # Initial ID construction
    cfid_parts = [f"⭐️{timestamp_str}"]
    if context:
        cfid_parts.append(context)
    if random_str:
        cfid_parts.append(random_str)
    cfid = "-".join(cfid_parts) + "❤️"

    # Trim the ID to fit within the maximum total length
    while len(cfid) > max_total_length:
        if len(timestamp_str) > 0:
            timestamp_str = trim_string(timestamp_str, len(timestamp_str) - 1)
        elif context and len(context) > 0:
            context = trim_string(context, len(context) - 1)
        elif random_str and len(random_str) > 0:
            random_str = trim_string(random_str, len(random_str) - 1)
        cfid_parts = [f"⭐️{timestamp_str}"]
        if context:
            cfid_parts.append(context)
        if random_str:
            cfid_parts.append(random_str)
        cfid = "-".join(cfid_parts) + "❤️"

    return cfid

def main():
    parser = argparse.ArgumentParser(
        description="Generate a CFID for a file. The CFID is constructed using the file's creation timestamp, context (parent folder and filename), and an optional random string. The ID is wrapped in ⭐️ and ❤️ and can be configured to fit within a maximum total length."
        )

    parser.add_argument("file_path", help="Path to the file")
    parser.add_argument("-t", type=int, choices=range(1, 7), default=6, help="Precision level for the timestamp (1=year, 2=year+month, 3=year+month+day, etc.)")
    parser.add_argument("-c", type=int, default=100, help="Maximum length of the context")
    parser.add_argument("-r", type=int, default=0, help="Length of the random string")
    parser.add_argument("-m", type=int, default=127, help="Maximum total length of the ID")
    parser.add_argument("-s", type=str, default=string.ascii_letters + string.digits, help="Character set to use for the random string")
    parser.add_argument("-w", action="store_true", help="Replace whitespace with underscore characters in the context")
    parser.add_argument("-j", action="store_true", help="Format the output as key/value JSON")


    args = parser.parse_args()

    cfid = mkCFID(args.file_path, args.t, args.c, args.r, args.m, args.s, args.w)

    if args.j:
        print(f'{{"aha.id":"{cfid}"}}')
    else:
        print(f"Generated ID: {cfid}")


if __name__ == "__main__":
    main()

