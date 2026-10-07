from PIL import Image, ImageEnhance, ImageFilter, ImageDraw

SRC="assets/profile-photo.jpg"
OUT="assets/profile-photo-face-first-reveal.gif"

img=Image.open(SRC).convert("RGB")
target_w=428
target_h=round(img.height*target_w/img.width)
img=img.resize((target_w,target_h), Image.Resampling.LANCZOS)
w,h=img.size

base=ImageEnhance.Brightness(img).enhance(0.04)
base=ImageEnhance.Contrast(base).enhance(0.88)
base=base.filter(ImageFilter.GaussianBlur(0.4))

center_y=int(h*0.33)
start_half=int(h*0.018)
reveal_frames=18
feather=12
frames=[]
durations=[]

def smoothstep(t):
    return t*t*(3-2*t)

for i in range(reveal_frames):
    t=smoothstep(i/(reveal_frames-1))
    top=int(center_y-(start_half+t*(center_y+10)))
    bottom=int(center_y+(start_half+t*((h-center_y)+10)))

    mask=Image.new("L",(w,h),0)
    d=ImageDraw.Draw(mask)
    d.rectangle((0,max(0,top),w,min(h,bottom)),fill=255)
    mask=mask.filter(ImageFilter.GaussianBlur(feather))

    frame=Image.composite(img,base,mask).convert("RGBA")

    glow=Image.new("RGBA",(w,h),(0,0,0,0))
    gd=ImageDraw.Draw(glow)
    for edge_y in (top,bottom):
        if 0<=edge_y<h:
            gd.rectangle((0,edge_y-1,w,edge_y+1),fill=(255,115,45,24))
    glow=glow.filter(ImageFilter.GaussianBlur(8))
    frame=Image.alpha_composite(frame,glow).convert("RGB")

    frames.append(frame)
    durations.append(70 if i<3 else 55)

frames.append(img.copy())
durations.append(1600)

frames[0].save(
    OUT,
    save_all=True,
    append_images=frames[1:],
    duration=durations,
    disposal=2
)
print("created", OUT)
