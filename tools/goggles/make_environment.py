#!/usr/bin/env python3
"""Builds assets-source/goggles-home.glb, the Goggles Link lobby environment: the Goggles OS
"night" 360-degree picture (the same one the GogglesXR dashboard shows) on the inside of a big
sphere centred at eye height. The picture is used as the emissive colour with a black base
colour, so it looks the same whatever the lobby's lighting.

  python3 make_environment.py PICTURE.jpg OUT.glb [THUMBNAIL.png]

PICTURE.jpg is gogglesxr/dashboard/environments/goggles-home.jpg from the gogglesos repository
(drawn by make_goggles_home.py there). Needs Pillow only for the thumbnail.
"""

import json
import math
import struct
import sys

RADIUS = 60.0  # metres; the lobby camera has no far plane
EYE = 1.6  # the picture was drawn from this height above the floor
SEGMENTS, RINGS = 64, 32


def build(picture_path, out_path):
    positions, uvs, indices = [], [], []
    for r in range(RINGS + 1):
        lat = math.pi / 2 - math.pi * r / RINGS  # +90 (up) to -90
        for s in range(SEGMENTS + 1):
            lon = -math.pi + 2 * math.pi * s / SEGMENTS  # 0 = straight ahead (-Z)
            x = RADIUS * math.cos(lat) * math.sin(lon)
            y = RADIUS * math.sin(lat) + EYE
            z = -RADIUS * math.cos(lat) * math.cos(lon)
            positions.append((x, y, z))
            uvs.append((s / SEGMENTS, r / RINGS))
    row = SEGMENTS + 1
    for r in range(RINGS):
        for s in range(SEGMENTS):
            a, b = r * row + s, r * row + s + 1
            c, d = (r + 1) * row + s, (r + 1) * row + s + 1
            # counter-clockwise when seen from inside the sphere (glTF front faces)
            indices += [a, c, b, b, c, d]
    with open(picture_path, "rb") as f:
        image = f.read()

    def pad(data, fill=b"\0"):
        return data + fill * (-len(data) % 4)

    pos_bin = pad(b"".join(struct.pack("<3f", *p) for p in positions))
    uv_bin = pad(b"".join(struct.pack("<2f", *t) for t in uvs))
    idx_bin = pad(struct.pack(f"<{len(indices)}H", *indices))
    img_bin = pad(image)
    views, offset = [], 0
    for data, target in ((pos_bin, 34962), (uv_bin, 34962), (idx_bin, 34963), (img_bin, None)):
        view = {"buffer": 0, "byteOffset": offset, "byteLength": len(data)}
        if target:
            view["target"] = target
        views.append(view)
        offset += len(data)
    views[3]["byteLength"] = len(image)
    xs, ys, zs = zip(*positions)
    gltf = {
        "asset": {"version": "2.0", "generator": "Goggles Link make_environment.py"},
        "scene": 0,
        "scenes": [{"name": "Goggles night", "nodes": [0]}],
        "nodes": [{"name": "sky", "mesh": 0}],
        "meshes": [
            {
                "name": "sky",
                "primitives": [
                    {"attributes": {"POSITION": 0, "TEXCOORD_0": 1}, "indices": 2, "material": 0}
                ],
            }
        ],
        "materials": [
            {
                "name": "sky",
                "pbrMetallicRoughness": {
                    "baseColorFactor": [0, 0, 0, 1],
                    "metallicFactor": 0,
                    "roughnessFactor": 1,
                },
                "emissiveTexture": {"index": 0},
                "emissiveFactor": [1, 1, 1],
            }
        ],
        "textures": [{"sampler": 0, "source": 0}],
        "samplers": [{"magFilter": 9729, "minFilter": 9987, "wrapS": 10497, "wrapT": 33071}],
        "images": [{"bufferView": 3, "mimeType": "image/jpeg"}],
        "accessors": [
            {
                "bufferView": 0,
                "componentType": 5126,
                "count": len(positions),
                "type": "VEC3",
                "min": [min(xs), min(ys), min(zs)],
                "max": [max(xs), max(ys), max(zs)],
            },
            {"bufferView": 1, "componentType": 5126, "count": len(uvs), "type": "VEC2"},
            {"bufferView": 2, "componentType": 5123, "count": len(indices), "type": "SCALAR"},
        ],
        "bufferViews": views,
        "buffers": [{"byteLength": offset}],
    }
    text = pad(json.dumps(gltf, separators=(",", ":")).encode(), b" ")
    binary = pos_bin + uv_bin + idx_bin + img_bin
    with open(out_path, "wb") as f:
        f.write(struct.pack("<4sII", b"glTF", 2, 12 + 8 + len(text) + 8 + len(binary)))
        f.write(struct.pack("<I4s", len(text), b"JSON") + text)
        f.write(struct.pack("<I4s", len(binary), b"BIN\0") + binary)


def thumbnail(picture_path, out_path):
    from PIL import Image

    picture = Image.open(picture_path)
    w, h = picture.size
    side = h // 2  # the view straight ahead, around the horizon
    left, top = w // 2 - side // 2, h // 2 - int(side * 0.62)
    picture.crop((left, top, left + side, top + side)).resize((256, 256), Image.LANCZOS).save(
        out_path
    )


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    build(sys.argv[1], sys.argv[2])
    if len(sys.argv) > 3:
        thumbnail(sys.argv[1], sys.argv[3])
