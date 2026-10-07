from PIL import Image, ImageEnhance, ImageFilter, ImageDraw
import math

SRC = "assets/profile-photo.jpg"
OUT = "assets/profile-photo-cinematic-reveal.gif"

img = Image.open(SRC).convert("RGB")

# GitHub displays the portrait at ~220px wide. 360px keeps it crisp without a huge GIF.
target_w = 360
target_h = round(img.height * target_w / img.width)
img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)

# Nearly-hidden opening state: preserve a faint silhouette instead of a flat black rectangle.
dark = ImageEnhance.Brightness(img).enhance(0.055)
dark = ImageEnhance.Contrast(dark).enhance(0.82)
dark = dark.filter(ImageFilter.GaussianBlur(0.7))

w, h = img.size
frames = []
durations = []

reveal_frames = 30
feather = max(22, int(h * 0.055))

def smoothstep(t):
    return t * t * (3.0 - 2.0 * t)

for i in range(reveal_frames):
    t = i / (reveal_frames - 1)
    p = smoothstep(t)
    edge_y = int((-feather * 0.9) + p * (h + feather * 1.35))

    # Feathered reveal mask.
    mask = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(mask)
    md.rectangle((0, 0, w, max(0, edge_y)), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(feather))

    frame = Image.composite(img, dark, mask).convert("RGBA")

    # Very subtle warm edge; enough to tie into the orange README accent.
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    band = max(10, feather // 2)
    for off in range(-band, band + 1):
        y = edge_y + off
        if 0 <= y < h:
            strength = 1.0 - abs(off) / (band + 1)
            alpha = int(18 * strength)
            gd.line((0, y, w, y), fill=(255, 122, 24, alpha), width=1)
    glow = glow.filter(ImageFilter.GaussianBlur(max(5, feather // 4)))
    frame = Image.alpha_composite(frame, glow).convert("RGB")

    # Adaptive palette keeps file size reasonable while preserving the portrait.
    frame = frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=160)
    frames.append(frame)
    durations.append(48)

# End on the untouched clean portrait. With no loop extension, browsers hold this frame.
final_frame = img.convert("P", palette=Image.Palette.ADAPTIVE, colors=192)
frames.append(final_frame)
durations.append(500)

frames[0].save(
    OUT,
    save_all=True,
    append_images=frames[1:],
    duration=durations,
    optimize=True,
    disposal=1
)

print(f"Created {OUT} at {w}x{h}, {len(frames)} frames")
