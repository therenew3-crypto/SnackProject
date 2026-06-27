# -*- coding: utf-8 -*-
"""카카오톡/SNS 공유용 OG 썸네일(1200x630) 생성. 앱 결과 카드 느낌으로 클릭 유발."""
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
GOLD = (255, 215, 0)
WHITE = (242, 244, 248)
GRAY = (150, 160, 175)
RED = (255, 90, 95)
CARD = (26, 31, 42)

BOLD = "C:/Windows/Fonts/malgunbd.ttf"
REG = "C:/Windows/Fonts/malgun.ttf"
def f(path, size): return ImageFont.truetype(path, size)

img = Image.new("RGB", (W, H))
px = img.load()
# 세로 그라데이션 (위 진남색 → 아래 더 어둡게)
top, bot = (20, 26, 40), (6, 8, 13)
for y in range(H):
    t = y / H
    row = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
    for x in range(W):
        px[x, y] = row

d = ImageDraw.Draw(img)

def center(text, font, y, fill):
    w = d.textlength(text, font=font)
    d.text(((W - w) / 2, y), text, font=font, fill=fill)
    return w

# 상단 라벨
center("타임머신  ·  IF 계좌 계산기", f(BOLD, 34), 62, GOLD)
# 메인 헤드라인
center("내가 과거로 돌아갔다면?", f(BOLD, 74), 120, WHITE)

# 결과 카드
cx0, cy0, cx1, cy1 = 170, 250, 1030, 540
d.rounded_rectangle([cx0, cy0, cx1, cy1], radius=34, fill=CARD,
                    outline=(255, 215, 0), width=2)
center("비트코인을 2015년에 1,000만원 샀다면?", f(REG, 32), cy0 + 36, GRAY)
center("12억 7,631만원", f(BOLD, 104), cy0 + 92, GOLD)
# 수익률 배지
badge = "▲  수익률 +12,663%"
bw = d.textlength(badge, font=f(BOLD, 38))
bx = (W - bw) / 2
d.rounded_rectangle([bx - 26, cy0 + 222, bx + bw + 26, cy0 + 282], radius=30,
                    fill=(60, 24, 26))
d.text((bx, cy0 + 230), badge, font=f(BOLD, 38), fill=RED)

# 하단 도메인
center("if-ggeolmusae.netlify.app", f(REG, 28), H - 58, GRAY)

img.save("og-image.png", "PNG")
print("saved og-image.png", img.size)
