from __future__ import annotations

import base64
import math
import os
import pathlib
import string
import subprocess

from django.conf import settings
from django.template.defaultfilters import slugify


def guid(length: int = 15) -> str:
    """
    Generate a random string of length `length` using base62 encoding.

    - length: int - the length of the string to generate
    """
    # We generate a random number in a space at least as big as 62^length,
    # and if it's too big, we just retry. This is still statistically O(1)
    # since repeated probabilities less than one converge to zero. Hat-tip to
    # a Google interview for teaching me this technique! ;)
    max_num = 62**length
    num_bytes = math.ceil(math.log(max_num) / math.log(256))

    while True:
        bytes = os.urandom(num_bytes)
        num = 0
        for i in range(len(bytes)):
            num += 256**i * bytes[i]
        if num < max_num:
            return base62_encode(num)


def base62_encode(num) -> str:
    chars = string.digits + string.ascii_letters
    encoded = []
    while num > 0:
        num, remainder = divmod(num, 62)
        encoded.insert(0, chars[remainder])
    return "".join(encoded)


def blob_to_file(media, blob) -> str:
    blob_data = blob.split("data:")[1]

    # Split the data into the MIME type and the base64-encoded content
    _mime_type, base64_data = blob_data.split(";base64,", 1)
    ext = media.filename.split(".")[-1]
    filename = media.filename.split(".")[:-1]
    filename = slugify("".join(filename))
    filename = f"{filename}-{media.id}"

    filename_with_ext = f"{filename}.{ext}"

    # Decode the base64 data
    file_data = base64.b64decode(base64_data)

    # create path and parents if necessary
    path = os.path.join(settings.MEDIA_ROOT, "bids", media.bid.id)
    file_path = os.path.join(path, filename_with_ext)

    # Write the decoded data to a file
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)
    with open(file_path, "wb") as file:
        file.write(file_data)
        file.close()

    return filename_with_ext


def delete_media_file(media) -> None:
    file_path = os.path.join(settings.MEDIA_ROOT, "bids", media.bid.id, media.filename)

    file_to_rem = pathlib.Path(file_path, missing_ok=True)
    file_to_rem.unlink(missing_ok=True)

    return None


def get_image_metadata(media) -> dict:
    file_path = os.path.join(settings.MEDIA_ROOT, "bids", media.bid.id, media.filename)

    metadata = subprocess.run(
        [
            settings.CONVERT_BIN,
            file_path,
            "-identify",
            file_path,
        ],
        capture_output=True,
        text=True,
    )
    metadata_list = metadata.stdout.strip().split(" ")[1:]
    metadata_str = " ".join(metadata_list)
    return metadata_str


def create_image_thumbnail(media) -> None:
    ext = media.filename.split(".")[-1]
    filename = media.filename.split(".")[:-1]
    filename = "".join(filename)
    filename = f"{filename}_small.{ext}"
    file_path = os.path.join(settings.MEDIA_ROOT, "bids", media.bid.id, media.filename)
    thumbnail_path = os.path.join(settings.MEDIA_ROOT, "bids", media.bid.id, filename)

    resize = subprocess.run(
        [
            settings.CONVERT_BIN,
            file_path,
            "-resize",
            "200^>",
            thumbnail_path,
        ],
        capture_output=True,
        text=True,
    )

    return None


def encode_mp3_file(media):
    path = os.path.join(settings.MEDIA_ROOT, "bids", media.bid.id)
    file_path = os.path.join(path, media.filename)
    filename = os.path.join(path, media.filename)
    filename_list = media.filename.split(".")[:-1]
    filename_join = "".join(filename_list)
    filename_ext = f"{filename_join}_conv.mp3"
    filename_mp3 = os.path.join(path, filename_ext)

    print(path, filename, filename_list, filename_join, filename_ext, filename_mp3)

    encode = subprocess.run(
        f"{settings.FFMPEG_BIN} \
            -nostdin \
            -hide_banner \
            -y \
            -i \
            {file_path} \
            -codec:a \
            libmp3lame \
            -aq 2 \
            -ar 48000 \
            -b:a 192k \
            -f mp3 \
            {filename_mp3}",
        capture_output=True,
        text=True,
    )

    if encode.returncode == 0:
        media.filename = filename_ext
        media.save()
        return media
