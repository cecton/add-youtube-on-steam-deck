#!/usr/bin/env python3

import argparse
import binascii
import os
import shutil

parser = argparse.ArgumentParser(description="Add URL shortcuts to Steam")

parser.add_argument("-n", "--name", type=str, help="Shortcut name", required=True)
parser.add_argument("-u", "--url", type=str, help="Shortcut URL target", required=True)
parser.add_argument("-s", "--shortcuts", type=str, help="Path to the shortcuts.vdf file", required=True)

args = parser.parse_args()

appname = args.name
exe = "/usr/bin/flatpak"
start_dir = "/usr/bin"
launch_options = 'run --branch=stable --arch=x86_64 --command=/app/bin/chrome --file-forwarding com.google.Chrome @@u @@ --window-size=1024,640 --force-device-scale-factor=1.25 --device-scale-factor=1.25 --start-fullscreen --user-agent="SMART-TV; Tizen 4.0" %s' % args.url

header = b"\0shortcuts\0"

if os.path.exists(args.shortcuts):
    with open(args.shortcuts, "rb") as f:
        content = f.read()

    assert content.startswith(header), "expected %r" % header
    content = content[len(header):]

    entries = content.split(b"\x08\x08")
    entries = entries[:len(entries) - 2]
else:
    entries = []

i = len(entries)
kv = {
    b"\x02appid": binascii.crc32(appname.encode("utf-8")).to_bytes(4, "little"),
    b"\x01AppName": appname.encode("utf-8") + b"\0",
    b"\x01Exe": exe.encode("utf-8") + b"\0",
    b"\x01StartDir": start_dir.encode("utf-8") + b"\0",
    b"\x01LaunchOptions": launch_options.encode("utf-8") + b"\0",
}

if any([b"\x02appid\0%s" % kv[b"\x02appid"] in entry for entry in entries]):
    print("Duplicated entry detected")
    exit(1)

entries.append(b"\0%d\0%s" % (i, b"".join([b"%s\0%s" % (k, v) for (k, v) in kv.items()])))

if os.path.exists(args.shortcuts):
    shutil.copy2(args.shortcuts, args.shortcuts + ".bak")
with open(args.shortcuts, "wb") as f:
    f.write(header + b"\x08\x08".join(entries) + b"\x08\x08\x08\x08")
