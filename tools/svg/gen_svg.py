"""Generate SVG figures for KIV/UPS ex05 (helpers are reused by gen_svg06.py). Usage: python3 gen_svg.py <out_dir>"""
import math
import os
import sys

OUT = sys.argv[1]
FONT = 'font-family="Helvetica, Arial, sans-serif"'
INK, MUTED, BLUE, RED, GREEN = '#1f2328', '#656d76', '#0969da', '#cf222e', '#1a7f37'
KIND_FILL = {'idle': '#f6f8fa', 'start': '#ffebe9', 'data': '#ddf4ff', 'parity': '#fff8c5', 'stop': '#dafbe1'}


def save(name, w, h, body):
    with open(os.path.join(OUT, name), 'w', encoding='utf-8') as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" {FONT}>\n'
                f'<rect width="100%" height="100%" fill="#fff"/>\n{body}\n</svg>\n')


def text(x, y, s, size=14, fill=INK, anchor='middle', extra=''):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" {extra}>{s}</text>'


def polyline(pts, color=BLUE, width=3, extra=''):
    d = ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts)
    return f'<polyline points="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round" {extra}/>'


def step_wave(levels, x0, w, ymap):
    """levels: list of (level, width_in_units) -> polyline points of a step waveform."""
    pts, x = [], x0
    for lv, units in levels:
        y = ymap(lv)
        pts += [(x, y), (x + units * w, y)]
        x += units * w
    return pts


# ---------- UART frame ----------

def uart_segments(byte, data_bits=8, parity=None, stop=1):
    bits = [(byte >> i) & 1 for i in range(data_bits)]
    seg = [('klid', 1, 'idle', 1.5), ('START', 0, 'start', 1)]
    seg += [(f'D{i}', b, 'data', 1) for i, b in enumerate(bits)]
    if parity:
        p = sum(bits) % 2 if parity == 'E' else 1 - sum(bits) % 2
        seg.append(('P', p, 'parity', 1))
    seg += [('STOP' if stop == 1 else f'STOP ×{stop}', 1, 'stop', stop), ('klid', 1, 'idle', 1.5)]
    return seg


W_BIT, X0, Y_HI, Y_LO = 56, 50, 80, 150


def uart_base(seg, kinds=True, values=True, samples=True, grid=False):
    body, x = [], X0
    for label, v, kind, units in seg:
        wpx = units * W_BIT
        if kinds:
            body.append(f'<rect x="{x}" y="50" width="{wpx}" height="120" fill="{KIND_FILL[kind]}" stroke="#d0d7de"/>')
            body.append(text(x + wpx / 2, 40, label, 13, MUTED if kind == 'idle' else INK,
                             extra='font-weight="bold"' if kind != 'idle' else ''))
        if values and kind != 'idle':
            body.append(text(x + wpx / 2, 195, str(v), 16, INK, extra='font-family="monospace"'))
        if grid:
            body.append(f'<line x1="{x}" y1="55" x2="{x}" y2="170" stroke="#8c959f" stroke-dasharray="4 3"/>')
        x += wpx
    if grid:
        body.append(f'<line x1="{x}" y1="55" x2="{x}" y2="170" stroke="#8c959f" stroke-dasharray="4 3"/>')
    body.append(text(30, Y_HI + 5, '1', 14, MUTED))
    body.append(text(30, Y_LO + 5, '0', 14, MUTED))
    wave = polyline(step_wave([(v, u) for _, v, _, u in seg], X0, W_BIT, lambda v: Y_HI if v else Y_LO))
    sample_pts = []
    x = X0
    for label, v, kind, units in seg:
        if kind != 'idle':
            sample_pts.append((x + units * W_BIT / 2, Y_HI if v else Y_LO, label, v))
        x += units * W_BIT
    if samples:
        for sx, sy, _, _ in sample_pts:
            body.append(f'<line x1="{sx}" y1="55" x2="{sx}" y2="170" stroke="{RED}" stroke-dasharray="2 4"/>')
    return body, wave, sample_pts, x


def uart_static(name, byte, caption, **kw):
    seg = uart_segments(byte, **{k: kw.pop(k) for k in ('data_bits', 'parity', 'stop') if k in kw})
    baud = kw.pop('time_axis', None)
    body, wave, samples, xend = uart_base(seg, **kw)
    body.append(wave)
    if baud:
        edge = X0 + 1.5 * W_BIT
        body.append(f'<line x1="{X0}" y1="185" x2="{xend}" y2="185" stroke="{INK}"/>')
        for i in range(11):
            tx = edge + i * W_BIT
            body.append(f'<line x1="{tx}" y1="180" x2="{tx}" y2="190" stroke="{INK}"/>')
            body.append(text(tx, 206, f'{round(i * 1e6 / baud)}', 12, INK))
        body.append(text(xend, 225, 't [µs]', 12, MUTED, 'end'))
    if kw.get('samples', True):
        body += [f'<circle cx="{sx}" cy="{sy}" r="5" fill="{RED}"/>' for sx, sy, _, _ in samples]
    if kw.get('kinds', True):
        fs = X0 + 1.5 * W_BIT
        fe = xend - 1.5 * W_BIT
        body.append(f'<path d="M{fs},215 v8 H{fe} v-8" fill="none" stroke="{INK}"/>')
        nbits = round((fe - fs) / W_BIT)
        body.append(text((fs + fe) / 2, 242, f'1 rámec = {nbits} bitových intervalů', 14))
    body.append(text(X0, 272 if kw.get('kinds', True) else 245, caption, 14, MUTED, 'start'))
    save(name, xend + 30, 285 if kw.get('kinds', True) else 258, '\n'.join(body))


def uart_anim(name, byte, char):
    seg = uart_segments(byte)
    body, wave, samples, xend = uart_base(seg, samples=False)
    width = xend - X0
    total_units = sum(u for *_, u in seg)
    sec_per_bit = 0.7
    t_draw = total_units * sec_per_bit
    dur = t_draw + 3.0
    kt = lambda u: f'{u * sec_per_bit / dur:.4f}'
    body.append(f'<clipPath id="reveal"><rect x="{X0}" y="0" height="300" width="{width}">'
                f'<animate attributeName="width" values="0;{width};{width}" keyTimes="0;{kt(total_units)};1" '
                f'dur="{dur}s" repeatCount="indefinite"/></rect></clipPath>')
    body.append(f'<g clip-path="url(#reveal)">{wave}</g>')
    # moving cursor = current time
    body.append(f'<g><line x1="{X0}" y1="50" x2="{X0}" y2="170" stroke="{INK}" stroke-width="2"/>'
                f'<animateTransform attributeName="transform" type="translate" values="0 0;{width} 0;{width} 0" '
                f'keyTimes="0;{kt(total_units)};1" dur="{dur}s" repeatCount="indefinite"/></g>')

    def appear(u):  # visible from time u (bit units) until loop end
        return (f'<animate attributeName="opacity" values="0;1" keyTimes="0;{kt(u)}" calcMode="discrete" '
                f'dur="{dur}s" repeatCount="indefinite"/>')

    # samples + receive register (D7 left ... D0 right)
    reg_x, reg_y, box = X0 + 3 * W_BIT, 235, 40
    body.append(text(X0, reg_y + 26, 'přijímací registr:', 14, INK, 'start'))
    for i in range(8):
        bx = reg_x + (7 - i) * box
        body.append(f'<rect x="{bx}" y="{reg_y}" width="{box}" height="{box}" fill="#fff" stroke="{INK}"/>')
        body.append(text(bx + box / 2, reg_y + box + 16, f'D{i}', 12, MUTED))
    for sx, sy, label, v in samples:
        u = (sx - X0) / W_BIT
        body.append(f'<circle cx="{sx}" cy="{sy}" r="6" fill="{RED}">{appear(u)}</circle>')
        if label.startswith('D'):
            i = int(label[1:])
            bx = reg_x + (7 - i) * box
            body.append(f'<g><rect x="{bx + 2}" y="{reg_y + 2}" width="{box - 4}" height="{box - 4}" fill="#ddf4ff"/>'
                        f'{text(bx + box / 2, reg_y + 27, str(v), 20, BLUE, extra="font-family=\"monospace\" font-weight=\"bold\"")}'
                        f'{appear(u)}</g>')
    # status line
    phases = [(0, 1.5, 'klid: linka drží log. 1'),
              (1.5, 2.0, 'sestupná hrana 1→0: začátek START bitu, přijímač spouští časovač'),
              (2.0, 3.0, 'střed START bitu: stále 0 → platný start (ne zákmit)'),
              (3.0, 11.0, 'vzorkování dat uprostřed bitu, LSB (D0) jde první'),
              (11.0, None, f'STOP = 1 → rámec OK, přijato 0x{byte:02X} = \'{char}\'')]
    sy = 222
    for us, ue, s in phases:
        if ue is None:
            anim = (f'<animate attributeName="opacity" values="0;1" keyTimes="0;{kt(us)}" calcMode="discrete" '
                    f'dur="{dur}s" repeatCount="indefinite"/>')
            op = 1
        elif us == 0:
            anim = (f'<animate attributeName="opacity" values="1;0" keyTimes="0;{kt(ue)}" calcMode="discrete" '
                    f'dur="{dur}s" repeatCount="indefinite"/>')
            op = 0
        else:
            anim = (f'<animate attributeName="opacity" values="0;1;0" keyTimes="0;{kt(us)};{kt(ue)}" '
                    f'calcMode="discrete" dur="{dur}s" repeatCount="indefinite"/>')
            op = 0
        body.append(f'<g opacity="{op}">{text(X0, sy, s, 15, RED if ue is None else INK, "start", "font-weight=\"bold\"")}{anim}</g>')
    save(name, xend + 30, 300, '\n'.join(body))


# ---------- Fourier: square wave from harmonics ----------

def fourier():
    x0, x1, yc, amp = 60, 780, 140, 70
    n = 600
    stages = [1, 2, 3, 5, 10, 30]  # number of odd harmonics
    dur = len(stages) * 1.6
    body = [f'<line x1="{x0}" y1="{yc}" x2="{x1}" y2="{yc}" stroke="#d0d7de"/>']
    ideal = [(x0, yc - amp)]
    for k in range(4):
        xa, xb = x0 + k * (x1 - x0) / 4, x0 + (k + 1) * (x1 - x0) / 4
        y = yc - amp if k % 2 == 0 else yc + amp
        ideal += [(xa, y), (xb, y)]
    body.append(polyline(ideal, MUTED, 2, 'stroke-dasharray="6 5"'))
    for si, K in enumerate(stages):
        pts = []
        for j in range(n + 1):
            t = 2 * j / n  # two periods
            s = 4 / math.pi * sum(math.sin(2 * math.pi * (2 * h - 1) * t) / (2 * h - 1) for h in range(1, K + 1))
            pts.append((x0 + (x1 - x0) * j / n, yc - amp * s))
        vals = ';'.join('1' if i == si else '0' for i in range(len(stages)))
        kts = ';'.join(f'{i / len(stages):.4f}' for i in range(len(stages)))
        anim = (f'<animate attributeName="opacity" values="{vals}" keyTimes="{kts}" calcMode="discrete" '
                f'dur="{dur}s" repeatCount="indefinite"/>')
        op = 1 if si == len(stages) - 1 else 0
        top = 2 * K - 1
        label = '1. harmonická (jen základní frekvence f)' if K == 1 else f'harmonické 1, 3, ... {top} → potřebné pásmo ≈ {top}·f'
        body.append(f'<g opacity="{op}">{polyline(pts)}{text(x0, 262, label, 16, BLUE, "start", "font-weight=\"bold\"")}{anim}</g>')
    body.append(text(x0, 30, 'Obdélníkový signál = součet lichých harmonických (Fourier)', 17, INK, 'start', 'font-weight="bold"'))
    body.append(text(x1, 30, 'čárkovaně: ideální obdélník', 13, MUTED, 'end'))
    save('fourier.svg', 820, 280, '\n'.join(body))


# ---------- Transfer function / bandwidth ----------

def bandwidth():
    x0, x1, yb, yt = 70, 770, 230, 60
    fmax = 5000
    fx = lambda f: x0 + (x1 - x0) * f / fmax
    hy = lambda h: yb - (yb - yt) * h
    H = lambda f: 1 / math.sqrt(1 + ((f - 1850) / 1550) ** 10)
    body = [f'<rect x="{fx(300):.1f}" y="{yt - 10}" width="{fx(3400) - fx(300):.1f}" height="{yb - yt + 10}" fill="#ddf4ff"/>',
            f'<line x1="{x0}" y1="{yb}" x2="{x1 + 10}" y2="{yb}" stroke="{INK}"/>',
            f'<line x1="{x0}" y1="{yb}" x2="{x0}" y2="{yt - 25}" stroke="{INK}"/>',
            text(x1 + 5, yb + 35, 'f [Hz]', 13, MUTED, 'end'),
            text(x0 + 8, yt - 12, '|H(f)|', 13, MUTED, 'start'),
            text(x0 - 10, hy(1) + 5, '1', 13, MUTED, 'end'),
            text(x0 - 10, hy(0.707) + 5, '0,707', 13, MUTED, 'end'),
            f'<line x1="{x0}" y1="{hy(0.707):.1f}" x2="{x1}" y2="{hy(0.707):.1f}" stroke="{RED}" stroke-dasharray="5 4"/>',
            text(x1, hy(0.707) - 6, '−3 dB (poloviční výkon)', 13, RED, 'end')]
    pts = [(fx(f), hy(H(f))) for f in range(0, fmax + 1, 10)]
    body.append(polyline(pts))
    for f in (300, 3400):
        body.append(f'<line x1="{fx(f):.1f}" y1="{yb}" x2="{fx(f):.1f}" y2="{hy(0.707):.1f}" stroke="{INK}" stroke-dasharray="2 3"/>')
        body.append(text(fx(f), yb + 18, f'{f}', 13))
    body.append(text(fx(300), yb + 34, 'f_min', 13, MUTED))
    body.append(text(fx(3400), yb + 34, 'f_max', 13, MUTED))
    for f in (1000, 2000, 4000, 5000):
        body.append(text(fx(f), yb + 18, f'{f}', 12, MUTED))
    ya = hy(0.35)
    body.append(f'<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
                f'<path d="M0,0 L10,5 L0,10 z" fill="{INK}"/></marker></defs>')
    body.append(f'<line x1="{fx(300):.1f}" y1="{ya:.1f}" x2="{fx(3400):.1f}" y2="{ya:.1f}" stroke="{INK}" stroke-width="1.5" '
                f'marker-start="url(#a)" marker-end="url(#a)"/>')
    body.append(text((fx(300) + fx(3400)) / 2, ya - 8, 'B = f_max − f_min = 3100 Hz', 16, INK, extra='font-weight="bold"'))
    body.append(text(x0, 20, 'Přenosové pásmo telefonního kanálu (300–3400 Hz)', 17, INK, 'start', 'font-weight="bold"'))
    save('bandwidth.svg', 800, 280, '\n'.join(body))


# ---------- N=2 vs N=4 levels ----------

def levels():
    x0, sw = 110, 80
    body = []
    top_bits = '10110010'
    yt = lambda b: 60 if b == '1' else 120
    body.append(text(20, 25, 'N = 2 (NRZ): 1 bit / symbol', 15, INK, 'start', 'font-weight="bold"'))
    body.append(polyline(step_wave([(b, 1) for b in top_bits], x0, sw, yt)))
    for i, b in enumerate(top_bits):
        body.append(text(x0 + sw * i + sw / 2, 50, b, 15, INK, extra='font-family="monospace"'))
    body += [text(x0 - 15, 65, '1', 13, MUTED, 'end'), text(x0 - 15, 125, '0', 13, MUTED, 'end')]
    gray = {'10': 3, '11': 1, '01': -1, '00': -3}
    pairs = ['10', '11', '00', '10', '01', '11', '10', '00']
    yb = lambda p: 270 - gray[p] * 22
    body.append(text(20, 170, 'N = 4 (PAM-4, Grayův kód): 2 bity / symbol', 15, INK, 'start', 'font-weight="bold"'))
    for lv in (3, 1, -1, -3):
        y = 270 - lv * 22
        body.append(f'<line x1="{x0}" y1="{y}" x2="{x0 + 8 * sw}" y2="{y}" stroke="#d0d7de" stroke-dasharray="3 3"/>')
        lab = [k for k, v in gray.items() if v == lv][0]
        body.append(text(x0 - 15, y + 5, f'{lv:+d} = {lab}', 13, MUTED, 'end'))
    body.append(polyline(step_wave([(p, 1) for p in pairs], x0, sw, yb), GREEN))
    for i, p in enumerate(pairs):
        body.append(text(x0 + sw * i + sw / 2, 190, p, 15, INK, extra='font-family="monospace"'))
    for i in range(9):
        body.append(f'<line x1="{x0 + sw * i}" y1="345" x2="{x0 + sw * i}" y2="353" stroke="{INK}"/>')
    body.append(f'<line x1="{x0}" y1="349" x2="{x0 + 8 * sw}" y2="349" stroke="{INK}"/>')
    body.append(text(x0 + 4 * sw, 372, 'stejná modulační rychlost (8 symbolů) → N=4 přenese 2× víc bitů, ale úrovně jsou blíže u sebe → citlivější na šum', 13, MUTED))
    save('levels.svg', 800, 385, '\n'.join(body))


# ---------- Shannon curve ----------

def shannon():
    x0, x1, yb, yt = 80, 760, 300, 40
    sx = lambda d: x0 + (x1 - x0) * (d + 10) / 50
    sy = lambda c: yb - (yb - yt) * c / 14
    body = []
    for d in range(-10, 41, 10):
        body.append(f'<line x1="{sx(d)}" y1="{yt}" x2="{sx(d)}" y2="{yb}" stroke="#eaeef2"/>')
        body.append(text(sx(d), yb + 20, f'{d}', 13, MUTED))
    for c in range(0, 15, 2):
        body.append(f'<line x1="{x0}" y1="{sy(c)}" x2="{x1}" y2="{sy(c)}" stroke="#eaeef2"/>')
        body.append(text(x0 - 10, sy(c) + 5, f'{c}', 13, MUTED, 'end'))
    body.append(f'<rect x="{x0}" y="{yt}" width="{x1 - x0}" height="{yb - yt}" fill="none" stroke="{INK}"/>')
    body.append(text((x0 + x1) / 2, yb + 42, 'SNR [dB]', 14, INK))
    body.append(text(25, (yt + yb) / 2, 'C / B [b/s na 1 Hz pásma]', 14, INK, extra=f'transform="rotate(-90 25 {(yt + yb) / 2})"'))
    c = lambda d: math.log2(1 + 10 ** (d / 10))
    body.append(polyline([(sx(d / 10), sy(c(d / 10))) for d in range(-100, 401)]))
    body.append(polyline([(sx(d), sy(d / 3)) for d in (0, 40)], MUTED, 2, 'stroke-dasharray="6 5"'))
    body.append(text(sx(16), sy(0.5), 'čárkovaně: C/B ≈ SNR_dB / 3 (pro SNR ≫ 1)', 13, MUTED, 'start'))
    for d, lab in ((0, 'S = N → 1 b/s na Hz'), (10, '10× silnější → 3,46'), (20, '100× → 6,66'), (30, '1000× (telefon) → 9,97')):
        body.append(f'<circle cx="{sx(d)}" cy="{sy(c(d))}" r="5" fill="{RED}"/>')
        body.append(text(sx(d) - 12, sy(c(d)) - 12, lab, 13, RED, 'end') if d == 0 else text(sx(d) + 12, sy(c(d)) + 22, lab, 13, RED, 'start'))
    body.append(text(x0, 25, 'Kolik b/s unese 1 Hz pásma při daném SNR (Shannon)', 17, INK, 'start', 'font-weight="bold"'))
    save('shannon.svg', 800, 360, '\n'.join(body))


# ---------- Synchronous vs start-stop ----------

def sync_vs_async():
    body = [text(20, 25, 'Synchronní: hodiny vedou zvlášť (např. SPI, I2C)', 15, INK, 'start', 'font-weight="bold"')]
    x0, w = 90, 60
    bits = '1011001011'
    clk = []
    for i in range(len(bits)):
        clk += [(x0 + i * w, 85), (x0 + i * w + w / 2, 85), (x0 + i * w + w / 2, 45), (x0 + (i + 1) * w, 45)]
    body.append(text(x0 - 15, 70, 'CLK', 13, MUTED, 'end'))
    body.append(polyline(clk, MUTED, 2))
    body.append(text(x0 - 15, 130, 'DATA', 13, MUTED, 'end'))
    body.append(polyline(step_wave([(b, 1) for b in bits], x0, w, lambda b: 105 if b == '1' else 145)))
    for i, b in enumerate(bits):
        xs = x0 + i * w + w / 2
        body.append(f'<line x1="{xs}" y1="45" x2="{xs}" y2="150" stroke="{RED}" stroke-dasharray="2 4"/>')
        body.append(text(xs, 168, b, 13, INK, extra='font-family="monospace"'))
    body.append(text(x0 + len(bits) * w + 10, 70, 'vzorkuj na', 12, RED, 'start'))
    body.append(text(x0 + len(bits) * w + 10, 85, 'náběžné hraně', 12, RED, 'start'))

    body.append(text(20, 215, 'Arytmický (start-stop): hodiny nevedou, synchronizace na začátku každého znaku', 15, INK, 'start', 'font-weight="bold"'))
    w2, y1, y0 = 22, 250, 300
    levels_ = [(1, 1.5)]
    marks = []
    x = x0
    for i, (ch, gap) in enumerate((('H', 4), ('i', 1.5))):
        seg = uart_segments(ord(ch))[1:-1]
        fs = x0 + sum(u for _, u in levels_) * w2
        levels_ += [(v, u) for _, v, _, u in seg]
        fe = x0 + sum(u for _, u in levels_) * w2
        marks.append((fs, fe, ch))
        levels_.append((1, gap))
    for fs, fe, ch in marks:
        body.append(f'<rect x="{fs}" y="{y1 - 10}" width="{w2}" height="{y0 - y1 + 20}" fill="{KIND_FILL["start"]}"/>')
        body.append(f'<rect x="{fe - w2}" y="{y1 - 10}" width="{w2}" height="{y0 - y1 + 20}" fill="{KIND_FILL["stop"]}"/>')
        body.append(f'<path d="M{fs},322 v6 H{fe} v-6" fill="none" stroke="{INK}"/>')
        body.append(text((fs + fe) / 2, 345, f"znak '{ch}'", 13))
    body.append(polyline(step_wave(levels_, x0, w2, lambda v: y1 if v else y0)))
    gx = marks[0][1] + 2 * w2
    body.append(text(gx, 345, 'mezera libovolně dlouhá', 12, MUTED))
    body.append(text(x0 - 15, y1 + 5, '1', 13, MUTED, 'end'))
    body.append(text(x0 - 15, y0 + 5, '0', 13, MUTED, 'end'))
    save('sync-async.svg', 800, 360, '\n'.join(body))



# ---------- QAM-16 constellation + carrier ----------

GRAY2 = {-3: '00', -1: '01', 1: '11', 3: '10'}


def constellation():
    cx, cy, u = 230, 210, 40
    body = [f'<line x1="{cx - 170}" y1="{cy}" x2="{cx + 170}" y2="{cy}" stroke="{MUTED}"/>',
            f'<line x1="{cx}" y1="{cy + 170}" x2="{cx}" y2="{cy - 170}" stroke="{MUTED}"/>',
            text(cx + 175, cy + 5, 'I', 15, MUTED, 'start', 'font-style="italic"'),
            text(cx + 10, cy - 150, 'Q', 15, MUTED, 'start', 'font-style="italic"')]
    hi = (3, 1)
    for i in (-3, -1, 1, 3):
        for q in (-3, -1, 1, 3):
            x, y = cx + i * u, cy - q * u
            col = RED if (i, q) == hi else BLUE
            body.append(f'<circle cx="{x}" cy="{y}" r="7" fill="{col}"/>')
            body.append(text(x, y + 22, GRAY2[i] + GRAY2[q], 12, INK, extra='font-family="monospace"'))
    x, y = cx + hi[0] * u, cy - hi[1] * u
    phi = math.atan2(hi[1], hi[0])
    r = 45
    body.append(f'<line x1="{cx}" y1="{cy}" x2="{x - 6}" y2="{y + 2}" stroke="{RED}" stroke-width="2"/>')
    body.append(f'<path d="M{cx + r},{cy} A{r},{r} 0 0 0 {cx + r * math.cos(phi):.1f},{cy - r * math.sin(phi):.1f}" fill="none" stroke="{RED}"/>')
    body.append(text(cx + r + 8, cy - 6, 'φ', 15, RED, 'start'))
    body.append(text(x - 30, y - 12, 'A', 15, RED, extra='font-style="italic"'))
    body.append(text(20, 25, 'QAM-16: 16 stavů = 16 bodů = 4 bity / symbol', 16, INK, 'start', 'font-weight="bold"'))
    notes = ['symbol = úsek nosné (1/2400 s)', 'se zvolenou amplitudou A', 'a fází φ',
             '', 'červený bod: I = 3, Q = 1', '→ bity 1011', '',
             'Grayův kód: sousední body', 'se liší o 1 bit → chyba', 'o 1 bod = 1 chybný bit']
    for k, n in enumerate(notes):
        body.append(text(430, 90 + 22 * k, n, 14, RED if k in (4, 5) else INK, 'start'))
    save('qam16.svg', 680, 400, '\n'.join(body))


def qam_carrier():
    x0, sw, yc, amp_u = 60, 170, 130, 20
    syms = [(3, 1), (-1, 3), (1, -1), (-3, -3)]
    cycles = 2  # ponytail: 2 periody nosne na symbol jen pro citelnost, realne V.32 ma 0,75
    body = [f'<line x1="{x0}" y1="{yc}" x2="{x0 + sw * len(syms)}" y2="{yc}" stroke="#d0d7de"/>']
    pts = []
    for k, (i, q) in enumerate(syms):
        xs = x0 + k * sw
        body.append(f'<rect x="{xs}" y="40" width="{sw}" height="180" fill="{"#f6f8fa" if k % 2 else "#ffffff"}" stroke="#d0d7de"/>')
        for j in range(121):
            t = j / 120
            w = 2 * math.pi * cycles * t
            pts.append((xs + sw * t, yc - amp_u * (i * math.cos(w) - q * math.sin(w))))
        a = math.hypot(i, q)
        ph = math.degrees(math.atan2(q, i)) % 360
        body.append(text(xs + sw / 2, 34, f'I={i:+d} Q={q:+d} → {GRAY2[i]}{GRAY2[q]}', 13, INK, extra='font-family="monospace"'))
        body.append(text(xs + sw / 2, 240, f'A = {a:.2f}'.replace(".", ",") + f', φ = {ph:.0f}°', 13, MUTED))
    body.append(polyline(pts, BLUE, 2.5))
    body.append(text(x0, 270, 'Každý symbol = jiný úsek sinusovky (amplituda + fáze). 4 symboly × 4 bity = 16 bitů.', 14, INK, 'start'))
    body.append(text(x0, 290, 'Zjednodušeno: nakresleny 2 periody nosné na symbol (V.32: 1800 Hz / 2400 Bd = 0,75 periody).', 12, MUTED, 'start'))
    save('qam-carrier.svg', x0 + sw * len(syms) + 30, 305, '\n'.join(body))


# ---------- NRZI vs MLT-3 ----------

def mlt3():
    bits = '1111011001'
    x0, w = 110, 64
    body = []
    for i, b in enumerate(bits):
        body.append(f'<line x1="{x0 + i * w}" y1="40" x2="{x0 + i * w}" y2="330" stroke="#d0d7de" stroke-dasharray="3 3"/>')
        body.append(text(x0 + i * w + w / 2, 32, b, 15, INK, extra='font-family="monospace"'))
    body.append(f'<line x1="{x0 + len(bits) * w}" y1="40" x2="{x0 + len(bits) * w}" y2="330" stroke="#d0d7de" stroke-dasharray="3 3"/>')
    # NRZI: 1 = zmena, 0 = beze zmeny
    lv, nrzi = 0, []
    for b in bits:
        lv ^= int(b)
        nrzi.append((lv, 1))
    body.append(text(20, 70, 'NRZI', 14, INK, 'start', 'font-weight="bold"'))
    body.append(text(20, 88, '2 úrovně', 12, MUTED, 'start'))
    body.append(polyline(step_wave(nrzi, x0, w, lambda v: 60 if v else 120), MUTED))
    # MLT-3: 1 = dalsi uroven v cyklu 0, +, 0, -; 0 = beze zmeny
    cyc, k, mlt = [0, 1, 0, -1], 0, []
    for b in bits:
        k = (k + int(b)) % 4
        mlt.append((cyc[k], 1))
    ym = lambda v: 230 - 50 * v
    body.append(text(20, 220, 'MLT-3', 14, INK, 'start', 'font-weight="bold"'))
    body.append(text(20, 238, '3 úrovně', 12, MUTED, 'start'))
    for v, lab in ((1, '+'), (0, '0'), (-1, '−')):
        body.append(text(x0 - 12, ym(v) + 5, lab, 14, MUTED, 'end'))
    body.append(polyline(step_wave(mlt, x0, w, ym), BLUE))
    body.append(f'<path d="M{x0},300 v6 H{x0 + 4 * w} v-6" fill="none" stroke="{RED}"/>')
    body.append(text(x0 + 2 * w, 325, '4 bity = 1 perioda → 125 MBd / 4 = 31,25 MHz', 13, RED))
    body.append(text(x0 + 7 * w, 325, '(NRZI: 2 bity = perioda → 62,5 MHz)', 13, MUTED))
    body.append(text(20, 360, 'Pravidlo: bit 1 = posun na další úroveň (MLT-3: 0 → + → 0 → − → 0), bit 0 = beze změny', 13, INK, 'start'))
    save('mlt3.svg', x0 + len(bits) * w + 30, 375, '\n'.join(body))


# ---------- sync / async animations ----------

class Anim:
    """Shared SMIL timing: everything loops with the same dur so it stays in sync."""

    def __init__(self, units, spu, hold=3.0):
        self.units, self.spu = units, spu
        self.dur = units * spu + hold

    def kt(self, u):
        return f'{u * self.spu / self.dur:.4f}'

    def _a(self, values, times):
        return (f'<animate attributeName="opacity" values="{values}" keyTimes="{times}" calcMode="discrete" '
                f'dur="{self.dur}s" repeatCount="indefinite"/>')

    def appear(self, u):
        return self._a('0;1', f'0;{self.kt(u)}')

    def between(self, us, ue):
        if ue is None:
            return self.appear(us)
        if us == 0:
            return self._a('1;0', f'0;{self.kt(ue)}')
        return self._a('0;1;0', f'0;{self.kt(us)};{self.kt(ue)}')

    def reveal(self, cid, x0, width, content, y1, y2):
        k = self.kt(self.units)
        anim = f'dur="{self.dur}s" repeatCount="indefinite"'
        return (f'<clipPath id="{cid}"><rect x="{x0}" y="0" height="400" width="{width}">'
                f'<animate attributeName="width" values="0;{width};{width}" keyTimes="0;{k};1" {anim}/></rect></clipPath>'
                f'<g clip-path="url(#{cid})">{content}</g>'
                f'<g><line x1="{x0}" y1="{y1}" x2="{x0}" y2="{y2}" stroke="{INK}" stroke-width="2"/>'
                f'<animateTransform attributeName="transform" type="translate" values="0 0;{width} 0;{width} 0" keyTimes="0;{k};1" {anim}/></g>')

    def status(self, phases, x, y):
        out = []
        for us, ue, s_ in phases:
            op = 1 if ue is None else 0
            col = RED if ue is None else INK
            out.append(f'<g opacity="{op}">{text(x, y, s_, 15, col, "start", "font-weight=\"bold\"")}{self.between(us, ue)}</g>')
        return out


def sync_anim():
    bits = '110000000111'
    x0, w = 90, 56
    width = len(bits) * w
    A = Anim(len(bits), 0.8)
    body = [text(20, 25, 'Synchronní přenos: hodiny CLK vedou zvlášť vedle dat', 16, INK, 'start', 'font-weight="bold"'),
            text(x0 - 15, 70, 'CLK', 13, MUTED, 'end'), text(x0 - 15, 130, 'DATA', 13, MUTED, 'end')]
    clk = []
    for i in range(len(bits)):
        clk += [(x0 + i * w, 85), (x0 + i * w + w / 2, 85), (x0 + i * w + w / 2, 45), (x0 + (i + 1) * w, 45)]
    waves = polyline(clk, MUTED, 2) + polyline(step_wave([(b, 1) for b in bits], x0, w, lambda b: 105 if b == '1' else 145))
    body.append(f'<rect x="{x0 + 2 * w}" y="98" width="{7 * w}" height="54" fill="#fff8c5"/>')
    body.append(A.reveal('rs', x0, width, waves, 40, 155))
    body.append(text(x0 - 15, 200, 'přijato', 13, MUTED, 'end'))
    for i, b in enumerate(bits):
        xs = x0 + i * w + w / 2
        body.append(f'<g><line x1="{xs}" y1="45" x2="{xs}" y2="150" stroke="{RED}" stroke-dasharray="2 4"/>'
                    f'<circle cx="{xs}" cy="{105 if b == "1" else 145}" r="6" fill="{RED}"/>'
                    f'<rect x="{xs - w / 2 + 3}" y="178" width="{w - 6}" height="34" fill="#ddf4ff" stroke="{INK}"/>'
                    f'{text(xs, 202, b, 18, BLUE, extra="font-family=\"monospace\" font-weight=\"bold\"")}'
                    f'{A.appear(i + 0.5)}</g>')
    body += A.status([(0, 2, 'přijímač vzorkuje DATA na každé náběžné hraně CLK'),
                      (2, 9, '7 nul za sebou: bez CLK nelze poznat, kolik jich je – hodiny to říkají'),
                      (9, 12, 'žádná režie na start/stop: každý takt = 1 datový bit'),
                      (12, None, 'přijato 12 bitů: 1100 0000 0111')], x0, 250)
    save('sync-anim.svg', x0 + width + 40, 270, '\n'.join(body))


def async_anim():
    x0, w = 60, 28
    y1, y0 = 80, 140
    levels_, frames = [(1, 1.5)], []
    for ch, gap in (('H', 3), ('i', 1.5)):
        start = sum(u for _, u in levels_)
        levels_ += [(v, u) for _, v, _, u in uart_segments(ord(ch))[1:-1]]
        frames.append((start, ch))
        levels_.append((1, gap))
    units = sum(u for _, u in levels_)
    width = units * w
    A = Anim(units, 0.45)
    X = lambda u: x0 + u * w
    body = [text(20, 25, 'Arytmický přenos: hodiny přijímače se rozběhnou až hranou START bitu', 16, INK, 'start', 'font-weight="bold"'),
            text(x0 - 12, y1 + 5, '1', 13, MUTED, 'end'), text(x0 - 12, y0 + 5, '0', 13, MUTED, 'end')]
    for start, ch in frames:
        body.append(f'<rect x="{X(start)}" y="{y1 - 15}" width="{w}" height="{y0 - y1 + 30}" fill="{KIND_FILL["start"]}"/>')
        body.append(f'<rect x="{X(start + 9)}" y="{y1 - 15}" width="{w}" height="{y0 - y1 + 30}" fill="{KIND_FILL["stop"]}"/>')
        body.append(f'<path d="M{X(start)},165 v6 H{X(start + 10)} v-6" fill="none" stroke="{INK}"/>')
    body.append(A.reveal('ra', x0, width, polyline(step_wave(levels_, x0, w, lambda v: y1 if v else y0)), y1 - 20, y0 + 20))
    body.append(text(x0 - 12, 215, 'hodiny', 12, MUTED, 'end'))
    body.append(text(x0 - 12, 229, 'přijímače', 12, MUTED, 'end'))
    body.append(f'<line x1="{x0}" y1="220" x2="{x0 + width}" y2="220" stroke="#d0d7de"/>')
    for start, ch in frames:
        body.append(f'<g><line x1="{X(start)}" y1="{y1 - 20}" x2="{X(start)}" y2="235" stroke="{RED}" stroke-width="2"/>'
                    f'{text(X(start), 252, "sync", 12, RED)}{A.appear(start)}</g>')
        for k in range(10):
            u = start + k + 0.5
            body.append(f'<g><line x1="{X(u)}" y1="206" x2="{X(u)}" y2="234" stroke="{BLUE}" stroke-width="2"/>'
                        f'<circle cx="{X(u)}" cy="{y0 if k == 0 or (k < 9 and not (ord(ch) >> (k - 1)) & 1) else y1}" r="4" fill="{RED}"/>'
                        f'{A.appear(u)}</g>')
        body.append(f'<g>{text(X(start + 5), 190, f"znak {ch!r} = 0x{ord(ch):02X}", 14, RED, extra="font-weight=\"bold\"")}{A.appear(start + 9.5)}</g>')
    g0 = frames[0][0] + 10
    body.append(f'<g>{text(X(g0 + 1.5), 228, "stojí", 12, MUTED)}{A.appear(g0)}</g>')
    body += A.status([(0, 1.5, 'klid (1): přijímač nemá hodiny, jen hlídá sestupnou hranu'),
                      (1.5, 11.5, 'hrana 1→0 = sync: přijímač spustí své hodiny a vzorkuje střed každého bitu'),
                      (11.5, 14.5, 'mezera libovolně dlouhá: hodiny stojí, čeká se na další hranu'),
                      (14.5, 24.5, 'nová hrana: hodiny znovu od nuly → chyba se mezi znaky nesčítá'),
                      (24.5, None, "přijato 'H' a 'i' – každý znak má vlastní synchronizaci")], x0, 285)
    save('async-anim.svg', x0 + width + 30, 305, '\n'.join(body))

os.makedirs(OUT, exist_ok=True)
# ---------- Nyquist: why 2B ----------

def nyquist_2b():
    x0, w, n, yhi, ylo, yc, amp = 60, 78, 8, 70, 170, 120, 50
    body = [text(x0, 28, 'Proč 2B: nejrychlejší střídání symbolů = sinusovka s polovičním kmitočtem', 16, INK, 'start', 'font-weight="bold"')]
    bits = '10101010'
    for i, b in enumerate(bits):
        body.append(f'<line x1="{x0 + i * w}" y1="55" x2="{x0 + i * w}" y2="185" stroke="#eaeef2"/>')
        body.append(text(x0 + (i + 0.5) * w, 205, b, 14, INK, extra='font-family="monospace"'))
    body.append(polyline(step_wave([(b, 1) for b in bits], x0, w, lambda b: yhi if b == '1' else ylo), MUTED, 2))
    pts = [(x0 + t, yc - amp * math.cos(math.pi * (t - w / 2) / w)) for t in range(0, n * w + 1, 2)]
    body.append(polyline(pts, BLUE, 3))
    bx = x0 + 2 * w
    body.append(f'<path d="M{bx},225 v6 H{bx + 2 * w} v-6" fill="none" stroke="{RED}"/>')
    body.append(text(bx + w, 250, '1 perioda sinusovky = 2 symboly', 13, RED))
    body.append(text(x0 + n * w + 8, yhi + 4, 'symboly', 12, MUTED, 'start'))
    body.append(text(x0 + n * w + 8, yc + 4, 'f = v_m / 2', 12, BLUE, 'start'))
    body.append(text(x0, 285, 'Kanál s pásmem B propustí sinusovku nejvýš s kmitočtem B → v_m / 2 ≤ B → v_m ≤ 2B symbolů/s.', 14, INK, 'start'))
    body.append(text(x0, 307, 'Rychlejší střídání by kanál "uhladil" a sousední symboly by se slily (ISI).', 13, MUTED, 'start'))
    save('nyquist-2b.svg', 800, 320, '\n'.join(body))


# ---------- Sampling: aliasing ----------

def aliasing():
    x0, x1, f = 60, 760, 5
    sx = lambda t: x0 + (x1 - x0) * t
    body = []
    for row, (fs, ok, cap) in enumerate(((12, True, 'f_vz = 2,4 · f ✓ – vzorky (červeně) jednoznačně popíšou původní sinusovku'),
                                         (6, False, 'f_vz = 1,2 · f ✗ – stejné vzorky dá i pomalá sinusovka (alias, čárkovaně)'))):
        yc, amp = 85 + row * 165, 45
        body.append(text(x0, yc - 60, cap, 14, INK if ok else RED, 'start', 'font-weight="bold"'))
        body.append(f'<line x1="{x0}" y1="{yc}" x2="{x1}" y2="{yc}" stroke="#eaeef2"/>')
        body.append(polyline([(sx(t / 700), yc - amp * math.sin(2 * math.pi * f * t / 700)) for t in range(701)], BLUE, 2))
        if not ok:
            body.append(polyline([(sx(t / 700), yc + amp * math.sin(2 * math.pi * (fs - f) * t / 700)) for t in range(701)], RED, 2, 'stroke-dasharray="6 5"'))
        for k in range(fs + 1):
            t = k / fs
            body.append(f'<circle cx="{sx(t):.1f}" cy="{yc - amp * math.sin(2 * math.pi * f * t):.1f}" r="5" fill="{RED}"/>')
    body.append(text(x0, 345, 'Na 1 periodu jsou potřeba víc než 2 vzorky (vrchol a důl) → f_vz > 2 · f_max. Stejná dvojka jako u 2B.', 13, MUTED, 'start'))
    save('aliasing.svg', 800, 360, '\n'.join(body))


if __name__ == '__main__':  # ex06 figures (QAM, MLT-3) live in gen_svg06.py
    fourier()
    bandwidth()
    levels()
    shannon()
    sync_vs_async()
    # uart_static('uart-8n1.svg', 0x41, "Znak 'A' = 0x41 = 0100 0001b, 8N1, červeně = okamžiky vzorkování (střed bitu)")
    uart_static('uart-K-8n1.svg', 0x4B, "Řešení: 'K' = 0x4B = 0100 1011b, 8N1")
    uart_static('uart-K-7e1.svg', 0x4B, "Řešení: 'K' = 0x4B, 7E1 – 7 datových bitů, sudá parita (4 jedničky → P = 0)", data_bits=7, parity='E')
    uart_static('uart-k-8e2.svg', 0x6B, "Řešení: 'k' = 0x6B = 0110 1011b, 8E2 – sudá parita (5 jedniček → P = 1), 2 stop bity", parity='E', stop=2)
    uart_static('uart-decode.svg', 0x68, '9600 Bd, 8N1 – jaký znak byl přenesen?', kinds=False, values=False, samples=False, grid=True, time_axis=9600)
    uart_static('uart-decode-solution.svg', 0x68, "Řešení: D7..D0 = 0110 1000b = 0x68 = 'h'")
    uart_anim('uart-anim.svg', 0x41, 'A')
    sync_anim()
    async_anim()
    nyquist_2b()
    aliasing()
