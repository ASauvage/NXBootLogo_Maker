#!/usr/bin/env python3

import io
import os
import ips
import argparse
import json
from pathlib import Path
from PIL import Image

# Build Id: offset

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--patches_dir", help="The directory where the generated patches will be dumped", type=Path, default=None)
    parser.add_argument("-n", "--new_logo", help="The new logo image", type=Path, default=None)
    parser.add_argument("-o", "--old_logo", help="The original logo image", type=Path, default=None)
    parser.add_argument("-j", "--patch_info", help="The patch_info.json file path", type=Path, default="./patch_info.json")
    args = parser.parse_args()

    if args.patches_dir is None:
        patches_dir_args = Path(input("Name of the output folder: "))
    else:
        patches_dir_args = args.patches_dir

    if args.new_logo is None:
        new_logo_args = Path(input("Name of the image(jpg/dds): "))
    else:
        new_logo_args = args.new_logo

    patch_info_file = args.patch_info
    old_logo_args = args.old_logo

    try:
        f = open(patch_info_file, )
        data = json.load(f)
        patch_info = data['patch_info'][0]
    except FileNotFoundError:
        print("patch_info.json not found")
        quit()

    if old_logo_args is None:
        new_logo = Image.open(new_logo_args).convert("RGBA")
        if new_logo.size != (308, 350):
            raise ValueError("Invalid size for the logo")

        new_f = io.BytesIO(new_logo.tobytes())
        new_f.seek(0, 2)
        new_len = new_f.tell()
        new_f.seek(0)

        base_patch = ips.Patch()
        while new_f.tell() < new_len:
            base_patch.add_record(new_f.tell(), new_f.read(0xFFFF))
    else:
        old_logo = Image.open(old_logo_args).convert("RGBA")
        new_logo = Image.open(new_logo_args).convert("RGBA")
        if old_logo.size != (308, 350) or new_logo.size != (308, 350):
            raise ValueError("Invalid size for the logo")

        base_patch = ips.Patch.create(old_logo.tobytes(), new_logo.tobytes())

    if not patches_dir_args.exists():
        patches_dir_args.mkdir(parents=True)

    path = os.path.join(f"{patches_dir_args}/atmosphere/exefs_patches", "boot_logo")
    os.makedirs(path)

    patches_dir_args = Path(f"{patches_dir_args}/atmosphere/exefs_patches/boot_logo")

    for build_id, offset in patch_info.items():
        tmp_p = ips.Patch()

        for r in base_patch.records:
            tmp_p.add_record(r.offset + offset, r.content, r.rle_size)

        with Path(patches_dir_args, f"{build_id}.ips").open("wb") as f:
            f.write(bytes(tmp_p))
