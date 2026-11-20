"""把品牌图切成 Android / PWA 需要的所有尺寸。

用法（CI 里）：icon-source.png 放在 app/ 目录，脚本从 app/icon-source.png 读；
本地没有那张图时回退到 assets/app-icon.png；都没有就画三根柱。
"""
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)            # 仓库根（CI 里是 workspace，本地是 capacitor-app）
OUT = os.path.join(ROOT, 'resources')

CANDIDATES = [
    os.path.join(ROOT, 'app', 'icon-source.png'),
    os.path.join(ROOT, 'icon-source.png'),
    os.path.join(ROOT, '..', 'assets', 'app-icon.png'),
]

BG = (9, 11, 16)
COLORS = [(74, 158, 255), (95, 211, 243), (255, 122, 60)]


def find_source():
    for p in CANDIDATES:
        p = os.path.abspath(p)
        if os.path.isfile(p):
            return p
    return None


def fallback(size):
    """没有品牌图时，画三根柱（原来的图标）。"""
    img = Image.new('RGB', (size, size), BG)
    d = ImageDraw.Draw(img)
    pad = size * 0.18
    inner = size - pad * 2
    bar_w = inner * 0.19
    gap = inner * 0.13
    heights = [0.52, 0.72, 0.94]
    base = (size + inner * 0.80) / 2
    for i, h in enumerate(heights):
        x = pad + i * (bar_w + gap)
        top = base - inner * h * 0.80
        d.rounded_rectangle([x, top, x + bar_w, base], radius=bar_w * 0.32, fill=COLORS[i])
    return img


def stat_icon(size):
    """通知栏小图标：白色剪影 + 透明底（系统会给它上色）。"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size
    w = max(1.4, s * 0.075)
    # 一页纸 + 两条横线
    d.rounded_rectangle([s * 0.26, s * 0.16, s * 0.74, s * 0.84],
                        radius=s * 0.10, outline=(255, 255, 255, 255), width=int(round(w)))
    d.rounded_rectangle([s * 0.38, s * 0.40, s * 0.62, s * 0.40 + max(1, s * 0.07)],
                        radius=s * 0.03, fill=(255, 255, 255, 255))
    d.rounded_rectangle([s * 0.38, s * 0.58, s * 0.55, s * 0.58 + max(1, s * 0.07)],
                        radius=s * 0.03, fill=(255, 255, 255, 255))
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    src = find_source()
    if src:
        base = Image.open(src).convert('RGB')
        print('品牌图：', src, base.size)
    else:
        base = None
        print('没找到品牌图，用三根柱兜底')

    for s in (48, 72, 96, 144, 192, 512):
        img = base.resize((s, s), Image.LANCZOS) if base else fallback(s)
        img.save(os.path.join(OUT, 'icon-%d.png' % s), 'PNG')

    # Android 自适应图标的前景层：整图铺满，靠系统遮罩裁圆
    for s in (108, 162, 216, 324, 432):
        img = base.resize((s, s), Image.LANCZOS) if base else fallback(s)
        img.save(os.path.join(OUT, 'ic_launcher_foreground-%d.png' % s), 'PNG')

    for s in (24, 36, 48, 72, 96):
        stat_icon(s).save(os.path.join(OUT, 'ic_stat_icon-%d.png' % s), 'PNG')

    names = sorted(os.listdir(OUT))
    print('写了 %d 个文件：%s' % (len(names), ', '.join(names[:6]) + ' ...'))


if __name__ == '__main__':
    sys.exit(main())
