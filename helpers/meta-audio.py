#!/usr/bin/env python

from minio import Minio
from minio.error import S3Error
from minio.commonconfig import Tags
import os
import string
import random
import exiftool
import subprocess
import base64
from io import BytesIO


def keyvalue_to_dict(metadata):
    Lines = metadata.splitlines()
    count = 0
    out = {}
    for line in Lines:
        count += 1
        kv = line.strip().split(':')
        key = kv[0].strip()
        value = kv[1].strip()
        # Enable uuencoding: (looks encrypt-ish) hihii 🌟️:
        key = uuencode(key)
        value = uuencode(value)
        #print("Line {}: {} = {}".format(count, key, value)) # DEBUG

        # Here is where the magic happens:
        out[key] = value

    return out

def uuencode(text):
    return base64.b64encode(bytes(text, 'utf-8')).decode('ascii').replace('\n', '')



def read_metadata(filename):
    # ExitTool version issue (11.88 vs 12.15)
    #with exiftool.ExifTool() as e:
    #    metadata = e.execute_json(str(e.get_tags_batch(tags, filename)))

    metadata = subprocess.run(['exiftool', filename], stdout=subprocess.PIPE).stdout.decode('utf-8')
    # Convert key:value string to dictionary: Lib-fu! ha.
    metadata_kv = keyvalue_to_dict(metadata)

    return metadata_kv


# Define "allowed characters for key/value" in metadata/tags:
charset_key = string.ascii_lowercase + string.ascii_uppercase + string.digits + '_'
charset_value = charset_key + ' '

# Simple random generator for bogus key/value pairs in a dictionary:
# Used to generate dummy-test-data.

def generate_random_dict(num_items, chars_key, chars_value, key_max=10, value_max=256):
    dict = {}
    for i in range(num_items):
        key_len = random.randint(3, key_max)
        value_len = random.randint(3, value_max)

        key = ''.join(random.choice(chars_key) for _ in range(key_len))
        value = ''.join(random.choice(chars_value) for _ in range(value_len))
        dict[key] = value
    return dict



# =============================================
#   MAIN
# =============================================

def main():
    data_folder = "data"
    bucket_name = "pbtest1"
    prefix = "music"
    default_md = {}
    default_tags = {}

    # Create client to access server:
    client = Minio(
        "vm-aha.allhau.av-rd.com:9000",
        access_key="nhiYe9DFy9f4aplXw5iz",
        secret_key="oWUY3weE4gVWFP0ICXHEqPzbN6RIOWXbMMSYVmFd",
        secure=False,
        )

    # Default metadata for all Objects here:
    default_md = {
            "title": "This is a Title",
            "creator": "Peter B.",
            "date": "2024-01-03" 
            }

    default_tags = Tags.new_object_tags()
    default_tags["keywords"] = "one two three"
    default_tags["title"] = "This time as tag"


    # Show existing buckets, just to see that connection works and we're on the right storage:
    buckets = client.list_buckets()
    for bucket in buckets:
        print(bucket.name, bucket.creation_date)

    print("------------------------------------")

    # Create bucket if not exist:
    found = client.bucket_exists(bucket_name)
    if not found:
        client.make_bucket(bucket_name)
    else:
        print("Bucket '{}' already exists".format(bucket_name))

    # Upload a few demo files, and set metadata + tags:
    for filename in os.listdir(data_folder):
        print("\nFile: {}\n--------------------------".format(filename))
        f = os.path.join(data_folder, filename)

        exifdata = read_metadata(f)
        exif = dict(list(exifdata.items())[1:3])
        count = 0

        """
        for key, value in exifdata.items():
            exif[key] = value
            if (count > 5):
                break
            #print("file: {}\nMeta: {} = {}\n------\n\n".format(f, key, value))
            # JOKE: You code like a librarian! That's awesome annotated+ style. Oldschool-stable.
            """


        dummy_md = generate_random_dict(10,
                                     charset_key,
                                     charset_value, 
                                     key_max= 20,      # key length
                                     value_max= 40)   # value length
        # Dummy + fixed metadata:
        #metadata = {**default_md, **dummy_md}
        # Just fixed metadata:
        #metadata = default_md
        #metadata = exifdata
        metadata = exif
        tags = default_tags

        #print(default_md)
        #print(dummy_md)
        print(metadata)
        #print(tags)

        if os.path.isfile(f):
            # Upload 'test.py' as object name
            print("Uploading '{file}' to '{bucket}'...".format(file=filename, bucket=bucket_name))
            try:
                client.fput_object(
                    bucket_name,
                    object_name = "{}/{}".format(prefix, filename),
                    file_path = f, 
                    metadata = metadata,
                    tags = tags
                )
            except S3Error as exception:
                print("error occurred.", exception)



if __name__ == "__main__":
    try:
        main()
    except S3Error as exception:
        print("error occurred.", exception)
