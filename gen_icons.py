#!/home/ttolmany/scripts/tide-alert/venv/bin/python3
"""내 선사 바로가기(hojak-boats) 패밀리 룩 PWA/파비콘 생성 스크립트.
디자인: 다크 네이비 배경 + 원형 림 + 파도 위 낚싯배(선박) + 닻(Anchor) + 안테나.
초고해상도(1024x1024)에서 2배 슈퍼샘플링(2048x2048) 렌더링 후 리사이즈.
"""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

SIZE = 1024
OUT_DIR = Path(__file__).resolve().parent

BG_COLOR = (18, 22, 28)        # --ink #12161c
BG_RIM = (35, 43, 53)          # --surface-2 #232b35
LINE_COLOR = (46, 55, 66)      # --line #2e3742
ACCENT = (255, 122, 61)        # 세이프티 오렌지 --accent #ff7a3d
ACCENT_LIGHT = (255, 160, 110)
ACCENT_DARK = (210, 80, 30)
BOAT_HULL = (235, 240, 246)    # 선체 화이트
BOAT_CABIN = (210, 220, 230)   # 조타실 실버그레이
SEA_BLUE = (56, 189, 248)      # 파도 블루 #38bdf8
SEA_DEEP = (30, 100, 160)
WHITE = (255, 255, 255)


def draw_icon():
    scale = 2
    W = SIZE * scale
    H = SIZE * scale
    img = Image.new("RGBA", (W, H), BG_COLOR + (255,))
    draw = ImageDraw.Draw(img)

    cx, cy = W // 2, H // 2
    r_rim = int(W * 0.44)

    # 1. 은은한 배경 원형 림 (뱃지)
    draw.ellipse(
        [cx - r_rim, cy - r_rim, cx + r_rim, cy + r_rim],
        fill=(27, 33, 41, 255),
        outline=(46, 55, 66, 255),
        width=8 * scale
    )

    # 그림자 레이어
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)

    # 2. 파도 (Sea Waves) - 하단 2겹
    wave_y1 = int(H * 0.68)
    wave_y2 = int(H * 0.74)

    # 3. 낚싯배 (Fishing Boat) 기하 좌표
    # 선체 중심 x, y
    bx = cx
    by = int(H * 0.54)

    # 선체 (Hull)
    # 우측이 뱃머리(Bow), 좌측이 선미(Stern)
    hull_pts = [
        (bx - 260 * scale, by + 10 * scale),   # 선미 상단
        (bx + 180 * scale, by + 15 * scale),   # 뱃머리 꺾임
        (bx + 280 * scale, by - 30 * scale),   # 뱃머리 팁 (위로 치켜올라감)
        (bx + 230 * scale, by + 85 * scale),   # 뱃머리 하단
        (bx - 220 * scale, by + 95 * scale),   # 선미 하단
        (bx - 260 * scale, by + 30 * scale),   # 선미 뒤
    ]

    # 선체 그림자
    hull_shadow = [(p[0] + 10 * scale, p[1] + 18 * scale) for p in hull_pts]
    sdraw.polygon(hull_shadow, fill=(0, 0, 0, 140))
    shadow = shadow.filter(ImageFilter.GaussianBlur(16 * scale))
    img = Image.alpha_composite(img, shadow)
    draw = ImageDraw.Draw(img)

    # 조타실 (Cabin / Pilothouse)
    cabin_pts = [
        (bx - 140 * scale, by + 10 * scale),
        (bx - 140 * scale, by - 95 * scale),
        (bx + 60 * scale, by - 95 * scale),
        (bx + 105 * scale, by + 10 * scale),
    ]
    draw.polygon(cabin_pts, fill=BOAT_CABIN + (255,), outline=(160, 175, 195, 255), width=3 * scale)

    # 조타실 지붕 (Roof / Canopy)
    roof_pts = [
        (bx - 155 * scale, by - 95 * scale),
        (bx + 85 * scale, by - 95 * scale),
        (bx + 75 * scale, by - 110 * scale),
        (bx - 155 * scale, by - 110 * scale),
    ]
    draw.polygon(roof_pts, fill=ACCENT + (255,))

    # 조타실 창문 (2개)
    win1 = [
        (bx - 115 * scale, by - 20 * scale),
        (bx - 115 * scale, by - 75 * scale),
        (bx - 35 * scale, by - 75 * scale),
        (bx - 35 * scale, by - 20 * scale),
    ]
    win2 = [
        (bx - 15 * scale, by - 20 * scale),
        (bx - 15 * scale, by - 75 * scale),
        (bx + 65 * scale, by - 75 * scale),
        (bx + 50 * scale, by - 20 * scale),
    ]
    draw.polygon(win1, fill=(24, 32, 45, 255), outline=(100, 115, 135, 255), width=2 * scale)
    draw.polygon(win2, fill=(24, 32, 45, 255), outline=(100, 115, 135, 255), width=2 * scale)

    # 선박 레이더 돔 & 안테나 마스트
    mast_x = bx - 40 * scale
    draw.line([(mast_x, by - 110 * scale), (mast_x, by - 180 * scale)], fill=(180, 190, 205, 255), width=4 * scale)
    # 레이더 바
    draw.line([(mast_x - 30 * scale, by - 165 * scale), (mast_x + 30 * scale, by - 165 * scale)], fill=ACCENT_LIGHT + (255,), width=5 * scale)
    # 깃발 (선미 플래그)
    flag_pole_x = bx - 250 * scale
    draw.line([(flag_pole_x, by + 10 * scale), (flag_pole_x, by - 70 * scale)], fill=(180, 190, 205, 255), width=3 * scale)
    draw.polygon([
        (flag_pole_x, by - 68 * scale),
        (flag_pole_x - 45 * scale, by - 53 * scale),
        (flag_pole_x, by - 38 * scale),
    ], fill=ACCENT + (255,))

    # 선체 본체 (Hull) 렌더링
    draw.polygon(hull_pts, fill=BOAT_HULL + (255,), outline=(180, 195, 210, 255), width=3 * scale)

    # 선체 사이드 오렌지 액센트 라인 (뱃길 띠)
    stripe_pts = [
        (bx - 258 * scale, by + 28 * scale),
        (bx + 185 * scale, by + 32 * scale),
        (bx + 265 * scale, by - 8 * scale),
        (bx + 260 * scale, by + 4 * scale),
        (bx + 185 * scale, by + 45 * scale),
        (bx - 255 * scale, by + 40 * scale),
    ]
    draw.polygon(stripe_pts, fill=ACCENT + (255,))

    # 4. 닻 심볼 (Anchor) - 선체 우측 앞면에 양각
    ax = bx + 160 * scale
    ay = by + 50 * scale
    s_anc = 0.55 * scale
    # 닻 링
    draw.ellipse([ax - 12 * s_anc, ay - 38 * s_anc, ax + 12 * s_anc, ay - 14 * s_anc], outline=WHITE + (255,), width=int(5 * s_anc))
    # 닻 생크(기둥)
    draw.line([(ax, ay - 16 * s_anc), (ax, ay + 34 * s_anc)], fill=WHITE + (255,), width=int(6 * s_anc))
    # 닻 가로대
    draw.line([(ax - 20 * s_anc, ay - 2 * s_anc), (ax + 20 * s_anc, ay - 2 * s_anc)], fill=WHITE + (255,), width=int(5 * s_anc))
    # 닻 갈고리 (원호)
    draw.arc([ax - 30 * s_anc, ay + 6 * s_anc, ax + 30 * s_anc, ay + 42 * s_anc], start=20, end=160, fill=WHITE + (255,), width=int(6 * s_anc))

    # 5. 파도 웨이브 곡선 렌더링 (하단)
    # 1번째 파도 (밝은 블루)
    wave1_pts = []
    for x in range(int(W * 0.16), int(W * 0.84), 4 * scale):
        y = wave_y1 + math.sin((x - cx) * 0.008) * 16 * scale + math.cos((x - cx) * 0.015) * 8 * scale
        wave1_pts.append((x, y))
    for i in range(len(wave1_pts) - 1):
        draw.line([wave1_pts[i], wave1_pts[i + 1]], fill=SEA_BLUE + (230,), width=6 * scale)

    # 2번째 파도 (앞쪽 딥 블루)
    wave2_pts = []
    for x in range(int(W * 0.22), int(W * 0.78), 4 * scale):
        y = wave_y2 + math.sin((x - cx) * 0.01 + 1.2) * 14 * scale
        wave2_pts.append((x, y))
    for i in range(len(wave2_pts) - 1):
        draw.line([wave2_pts[i], wave2_pts[i + 1]], fill=SEA_BLUE + (180,), width=4 * scale)

    # 리사이즈
    final_512 = img.resize((512, 512), Image.Resampling.LANCZOS)
    final_192 = img.resize((192, 192), Image.Resampling.LANCZOS)
    final_180 = img.resize((180, 180), Image.Resampling.LANCZOS)
    final_32 = img.resize((32, 32), Image.Resampling.LANCZOS)

    target_dirs = [OUT_DIR, Path.home() / "projects/hojak-boats"]
    for td in target_dirs:
        td.mkdir(parents=True, exist_ok=True)
        final_512.save(td / "icon-512.png", "PNG")
        final_192.save(td / "icon-192.png", "PNG")
        final_180.save(td / "favicon-180.png", "PNG")
        final_32.save(td / "favicon-32.png", "PNG")
        print(f"[gen_icons] wrote {td}/(icon-512, icon-192, favicon-180, favicon-32).png")


if __name__ == "__main__":
    draw_icon()
