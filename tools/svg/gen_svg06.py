"""Generate SVG figures for KIV/UPS ex06 (line codes, modulation, multiplex). Usage: python3 gen_svg06.py <out_dir>"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_svg as g  # noqa: E402
from gen_svg import text, polyline, step_wave, INK, MUTED, BLUE, RED, GREEN  # noqa: E402

g.OUT = sys.argv[1]
save = g.save
GRID = '#d0d7de'


# ---------- line codes ----------

def code_levels(bits, code):
    """-> list of (level, units); levels 0/1, RZ and MLT-3 use -1/0/+1. Previous level before the first bit is LOW (0)."""
    out, lv, k = [], 0, 0
    for b in bits:
        one = b == '1'
        if code == 'nrzl':
            out.append((int(one), 1))
        elif code in ('nrzm', 'nrzs'):
            if one == (code == 'nrzm'):
                lv ^= 1
            out.append((lv, 1))
        elif code == 'rz':
            out += [(1 if one else -1, .5), (0, .5)]
        elif code == 'man':  # IEEE 802.3: 1 = L->H, 0 = H->L
            out += [(0, .5), (1, .5)] if one else [(1, .5), (0, .5)]
        elif code == 'dman':  # 0 = zmena na zacatku intervalu, 1 = bez zmeny; uprostred vzdy zmena
            if not one:
                lv ^= 1
            out += [(lv, .5), (lv ^ 1, .5)]
            lv ^= 1
        elif code == 'mlt3':
            k = (k + one) % 4
            out.append(([0, 1, 0, -1][k], 1))
    return out


THREE = ('rz', 'mlt3')


def linefig(name, bits, rows, title=None, labels=True, note=None, w=60):
    """rows: list of (label, sublabel, code or None=prazdny radek k nakresleni)."""
    x0, rh, top = 190, 96, 68 if title else 34
    n = len(bits)
    h = top + rh * len(rows) + (34 if note else 12)
    body = []
    if title:
        body.append(text(20, 26, title, 16, INK, 'start', 'font-weight="bold"'))
    for i in range(n + 1):
        x = x0 + i * w
        body.append(f'<line x1="{x}" y1="{top - 6}" x2="{x}" y2="{top + rh * len(rows)}" stroke="{GRID}" stroke-dasharray="4 3"/>')
        if i < n:
            body.append(f'<line x1="{x + w / 2}" y1="{top}" x2="{x + w / 2}" y2="{top + rh * len(rows)}" stroke="#eef1f4"/>')
            body.append(text(x + w / 2, top - 12, bits[i] if labels else '?', 16, INK if labels else MUTED, extra='font-family="monospace"'))
    for r, (lab, sub, code) in enumerate(rows):
        yt = top + r * rh + 14
        body.append(text(20, yt + 30, lab, 15, INK, 'start', 'font-weight="bold"'))
        body.append(text(20, yt + 50, sub, 12, MUTED, 'start'))
        three = code in THREE or (code is None and 'RZ' == lab)
        if three:
            ymap = lambda v, yt=yt: yt + 34 - 30 * v
            for v, s_ in ((1, '+'), (0, '0'), (-1, '−')):
                body.append(text(x0 - 10, ymap(v) + 5, s_, 13, MUTED, 'end'))
                body.append(f'<line x1="{x0}" y1="{ymap(v)}" x2="{x0 + n * w}" y2="{ymap(v)}" stroke="#eef1f4"/>')
        else:
            ymap = lambda v, yt=yt: yt + 64 - 60 * v
            for v, s_ in ((1, 'H'), (0, 'L')):
                body.append(text(x0 - 10, ymap(v) + 5, s_, 13, MUTED, 'end'))
                body.append(f'<line x1="{x0}" y1="{ymap(v)}" x2="{x0 + n * w}" y2="{ymap(v)}" stroke="#eef1f4"/>')
        if code:
            body.append(polyline(step_wave(code_levels(bits, code), x0, w, ymap), BLUE, 3))
    if note:
        body.append(text(20, h - 12, note, 13, MUTED, 'start'))
    save(name, x0 + n * w + 30, h, '\n'.join(body))


ROW = {
    'nrzl': ('NRZ-L', '1 = H, 0 = L'),
    'nrzm': ('NRZ-M (NRZI)', '1 = přechod'),
    'nrzs': ('NRZ-S', '0 = přechod'),
    'rz': ('RZ', '1 = +, 0 = −, pak 0'),
    'man': ('Manchester', '802.3: 1 = L→H'),
    'dman': ('Dif. Manchester', '0 = změna na hraně'),
    'mlt3': ('MLT-3', '1 = další úroveň'),
}


def lc(code, bits, name, note=None, **kw):
    linefig(name, bits, [(*ROW[code], code)], note=note, **kw)


# ---------- modulation ----------

def modfig(name, symbols, rows, title=None, labels=True, w=150, note=None):
    """rows: list of (label, fn) with fn(symbol) -> (A, f, phi) or None = prazdna mrizka."""
    x0, rh, top, ku = 150, 170, 68 if title else 34, 12
    n = len(symbols)
    h = top + rh * len(rows) + (34 if note else 10)
    body = []
    if title:
        body.append(text(20, 26, title, 16, INK, 'start', 'font-weight="bold"'))
    for i in range(n + 1):
        x = x0 + i * w
        body.append(f'<line x1="{x}" y1="{top - 6}" x2="{x}" y2="{top + rh * len(rows) - 10}" stroke="{GRID}" stroke-dasharray="4 3"/>')
        if i < n:
            body.append(text(x + w / 2, top - 12, symbols[i] if labels else '?', 16, INK if labels else MUTED, extra='font-family="monospace"'))
    for r, (lab, fn) in enumerate(rows):
        yc = top + r * rh + 75
        body.append(text(20, yc + 5, lab, 15, INK, 'start', 'font-weight="bold"'))
        for v in (5, 2, -2, -5):
            body.append(f'<line x1="{x0}" y1="{yc - v * ku}" x2="{x0 + n * w}" y2="{yc - v * ku}" stroke="#eef1f4" stroke-dasharray="3 3"/>')
            body.append(text(x0 - 8, yc - v * ku + 4, str(v).replace('-', '−'), 12, MUTED, 'end'))
        body.append(f'<line x1="{x0}" y1="{yc}" x2="{x0 + n * w + 8}" y2="{yc}" stroke="{MUTED}"/>')
        body.append(text(x0 + n * w + 14, yc + 4, 't', 13, MUTED, 'start', 'font-style="italic"'))
        if fn is None:
            continue
        pts = []
        for i, s_ in enumerate(symbols):
            a, f, ph = fn(s_)
            for j in range(121):
                t = j / 120
                pts.append((x0 + (i + t) * w, yc - ku * a * math.sin(2 * math.pi * f * t + ph)))
        body.append(polyline(pts, BLUE, 2.5))
    if note:
        body.append(text(20, h - 12, note, 13, MUTED, 'start'))
    save(name, x0 + n * w + 30, h, '\n'.join(body))


ook = lambda s: (5 if s == '1' else 0, 1, 0)
ask = lambda s: (5 if s == '1' else 2, 1, 0)
fsk = lambda s: (5, 2 if s == '1' else 1, 0)
psk = lambda s: (5, 1, math.pi if s == '1' else 0)
af4 = lambda s: (5 if s[0] == '1' else 2, 2 if s[1] == '1' else 1, 0)            # 1. bit A, 2. bit f
ap4 = lambda s: (5 if s[0] == '1' else 2, 1, math.pi if s[1] == '1' else 0)      # 1. bit A, 2. bit phi
afp8 = lambda s: (5 if s[0] == '1' else 2, 2 if s[1] == '1' else 1, math.pi if s[2] == '1' else 0)


# ---------- constellations ----------

def qpsk():
    cx, cy, u = 200, 200, 90
    body = [f'<line x1="{cx - 160}" y1="{cy}" x2="{cx + 160}" y2="{cy}" stroke="{MUTED}"/>',
            f'<line x1="{cx}" y1="{cy + 160}" x2="{cx}" y2="{cy - 160}" stroke="{MUTED}"/>',
            f'<circle cx="{cx}" cy="{cy}" r="{u * math.sqrt(2):.1f}" fill="none" stroke="{GRID}" stroke-dasharray="4 3"/>',
            text(cx + 165, cy + 5, 'I', 15, MUTED, 'start', 'font-style="italic"'),
            text(cx + 10, cy - 145, 'Q', 15, MUTED, 'start', 'font-style="italic"')]
    for (i, q), lab in (((1, 1), '00'), ((-1, 1), '01'), ((-1, -1), '11'), ((1, -1), '10')):
        x, y = cx + i * u, cy - q * u
        body.append(f'<circle cx="{x}" cy="{y}" r="8" fill="{BLUE}"/>')
        body.append(text(x, y + 28, lab, 15, INK, extra='font-family="monospace" font-weight="bold"'))
        ph = math.degrees(math.atan2(q, i)) % 360
        body.append(text(x, y - 16, f'φ = {ph:.0f}°', 12, MUTED))
    body.append(text(20, 25, 'QPSK (4-PSK): 4 fáze, stejná amplituda, 2 bity / symbol', 16, INK, 'start', 'font-weight="bold"'))
    notes = ['vzdálenost od středu = amplituda A', 'úhel = fáze φ', '',
             'Grayův kód: sousedé se liší', 'v 1 bitu (00–01–11–10)', '',
             'šum posune bod k sousedovi', '→ chybný jen 1 bit ze 2']
    for k, s_ in enumerate(notes):
        body.append(text(390, 90 + 22 * k, s_, 14, INK, 'start'))
    save('qpsk.svg', 640, 400, '\n'.join(body))


# ---------- multiplex ----------

def fdm():
    x0, y0, kpx = 60, 190, 10  # 10 px na kHz, osa 56-112 kHz
    fx = lambda f: x0 + (f - 56) * kpx
    body = [f'<line x1="{fx(56)}" y1="{y0}" x2="{fx(112) + 10}" y2="{y0}" stroke="{INK}" stroke-width="1.5"/>',
            text(fx(112) + 16, y0 + 5, 'f [kHz]', 13, MUTED, 'start')]
    cols = ['#ddf4ff', '#dafbe1', '#fff8c5']
    for k in range(12):
        lo = 60 + 4 * k
        body.append(f'<path d="M{fx(lo + 0.3):.1f},{y0} L{fx(lo + 0.6):.1f},{y0 - 90} L{fx(lo + 3.4):.1f},{y0 - 90} L{fx(lo + 3.7):.1f},{y0} Z" '
                    f'fill="{cols[k % 3]}" stroke="{BLUE}"/>')
        body.append(text(fx(lo + 2), y0 - 100, str(k + 1), 13, INK))
    for f in (60, 72, 84, 96, 108):
        body.append(f'<line x1="{fx(f)}" y1="{y0}" x2="{fx(f)}" y2="{y0 + 6}" stroke="{INK}"/>')
        body.append(text(fx(f), y0 + 22, str(f), 12, MUTED))
    body.append(f'<path d="M{fx(60)},{y0 + 34} v6 H{fx(64)} v-6" fill="none" stroke="{RED}"/>')
    body.append(text(fx(62), y0 + 58, '4 kHz = hlas 0,3–3,4 kHz + ochranné pásmo', 13, RED, 'start'))
    body.append(text(20, 26, 'FDM: 12 hovorů, každý na vlastní nosné (skupina 60–108 kHz)', 16, INK, 'start', 'font-weight="bold"'))
    save('fdm.svg', fx(112) + 80, 270, '\n'.join(body))


def tdm_stdm():
    # 4 zdroje, 3 cykly; aktivita (None = nema co poslat)
    act = [['A1', None, 'C1', None], ['A2', None, None, 'D1'], [None, 'B1', 'C2', None]]
    x0, sw, y1, y2 = 140, 40, 70, 170
    body = [text(20, 26, 'Časový (TDM) vs. statistický (STDM) multiplex', 16, INK, 'start', 'font-weight="bold"'),
            text(20, y1 + 25, 'TDM', 15, INK, 'start', 'font-weight="bold"'),
            text(20, y1 + 43, 'pevné sloty', 12, MUTED, 'start'),
            text(20, y2 + 25, 'STDM', 15, INK, 'start', 'font-weight="bold"'),
            text(20, y2 + 43, 'jen data + adresa', 12, MUTED, 'start')]
    x = x0
    for c, cyc in enumerate(act):
        for s_, who in zip(cyc, 'ABCD'):
            fill = '#ddf4ff' if s_ else '#f6f8fa'
            body.append(f'<rect x="{x}" y="{y1}" width="{sw}" height="40" fill="{fill}" stroke="{GRID}"/>')
            body.append(text(x + sw / 2, y1 + 25, s_ or '–', 14, INK if s_ else MUTED, extra='font-family="monospace"'))
            body.append(text(x + sw / 2, y1 + 56, who, 11, MUTED))
            x += sw
        body.append(f'<line x1="{x}" y1="{y1 - 8}" x2="{x}" y2="{y1 + 48}" stroke="{INK}" stroke-width="2"/>')
    body.append(text(x + 10, y1 + 25, '12 slotů, 5 obsazených', 13, RED, 'start'))
    x = x0
    for cyc in act:
        for s_ in cyc:
            if s_:
                body.append(f'<rect x="{x}" y="{y2}" width="{sw}" height="40" fill="#ddf4ff" stroke="{GRID}"/>')
                body.append(f'<rect x="{x}" y="{y2}" width="12" height="40" fill="#fff8c5" stroke="{GRID}"/>')
                body.append(text(x + 6, y2 + 25, s_[0], 10, INK))
                body.append(text(x + 26, y2 + 25, s_[1], 14, INK, extra='font-family="monospace"'))
                x += sw
    body.append(text(x + 10, y2 + 25, '5 slotů (+ adresa v každém)', 13, GREEN, 'start'))
    body.append(text(20, 250, 'TDM: slot patří zdroji, i když mlčí. STDM: linka se dimenzuje na průměr, při špičce se čeká ve frontě.', 13, MUTED, 'start'))
    save('tdm-stdm.svg', 840, 265, '\n'.join(body))


def e1_frame():
    x0, sw, y = 20, 22, 60
    body = [text(20, 26, 'Rámec E1: 32 slotů × 8 bitů, 8000 rámců/s (1 rámec = 125 µs)', 16, INK, 'start', 'font-weight="bold"')]
    for k in range(32):
        fill = '#ffebe9' if k == 0 else '#fff8c5' if k == 16 else '#ddf4ff'
        body.append(f'<rect x="{x0 + k * sw}" y="{y}" width="{sw}" height="40" fill="{fill}" stroke="{GRID}"/>')
        body.append(text(x0 + k * sw + sw / 2, y + 25, str(k), 11, INK))
    body.append(text(x0, y + 62, 'slot 0 = synchronizace rámce', 13, RED, 'start'))
    body.append(text(x0 + 16 * sw, y + 62, 'slot 16 = signalizace', 13, '#9a6700', 'start'))
    body.append(text(x0, y + 84, 'sloty 1–15 a 17–31 = 30 hovorů po 64 kb/s (8 bitů × 8000 vzorků/s)', 13, BLUE, 'start'))
    save('e1.svg', x0 + 32 * sw + 20, 160, '\n'.join(body))


# ---------- 4B/5B + MLT-3 solution ----------

def b4b5_solution():
    code = '010011111011100'
    linefig('ex4-solution.svg', code, [(*ROW['nrzm'], 'nrzm'), (*ROW['mlt3'], 'mlt3')], w=44,
            title='Řešení 4: 0001 0000 1110 → 01001 11110 11100',
            note='Výchozí stav: NRZI L, MLT-3 na 0 (cyklus 0 → + → 0 → −). Nejdelší řada nul v kódu: 2 (v datech: 4).')


if __name__ == '__main__':
    g.constellation()
    g.qam_carrier()
    g.mlt3()
    qpsk()
    fdm()
    tdm_stdm()
    e1_frame()

    demo = '10110010'
    for c in ('nrzl', 'nrzm', 'rz', 'man', 'dman'):
        lc(c, demo, f'lc-{c}.svg', note='Výchozí úroveň před prvním bitem: L.' if c in ('nrzm', 'dman') else None)
    linefig('lc-nrzs.svg', demo, [(*ROW['nrzs'], 'nrzs')], note='Výchozí úroveň před prvním bitem: L.')
    linefig('lc-compare.svg', '00000000', [(*ROW['nrzl'], 'nrzl'), (*ROW['man'], 'man')], w=50,
            title='Samé nuly: NRZ-L nemá žádnou hranu, Manchester má hranu v každém bitu')

    ex1 = '01001110'
    rows = [ROW[c] for c in ('nrzl', 'nrzm', 'rz', 'man', 'dman')]
    linefig('ex1-grid.svg', ex1, [(*r, None) for r in rows], title='Příklad 1: nakreslete 0100 1110',
            note='NRZ-M a dif. Manchester: výchozí úroveň před prvním bitem je L.')
    linefig('ex1-solution.svg', ex1, [(*ROW[c], c) for c in ('nrzl', 'nrzm', 'rz', 'man', 'dman')],
            title='Řešení 1: 0100 1110')

    linefig('ex2-man.svg', '11010001', [(*ROW['man'], 'man')], labels=False, title='a) Manchester (IEEE 802.3)')
    linefig('ex2-nrzm.svg', '01101100', [(*ROW['nrzm'], 'nrzm')], labels=False, title='b) NRZ-M, výchozí úroveň L')
    linefig('ex2-solution.svg', '11010001', [(*ROW['man'], 'man')], title='Řešení 2a: 1101 0001 = 0xD1')
    linefig('ex2b-solution.svg', '01101100', [(*ROW['nrzm'], 'nrzm')], title='Řešení 2b: 0110 1100 = 0x6C')
    b4b5_solution()

    modfig('mod-ook.svg', '1001', [('OOK', ook)], title='OOK (On-Off Keying): 0 → A = 0, 1 → A = 5; f = 1 Hz, φ = 0')
    modfig('mod-ask.svg', '1001', [('2-ASK', ask)], title='2-ASK: 0 → A = 2, 1 → A = 5; f = 1 Hz, φ = 0')
    modfig('mod-fsk.svg', '1010', [('2-FSK', fsk)], title='2-FSK: 0 → f = 1 Hz, 1 → f = 2 Hz; A = 5, φ = 0')
    modfig('mod-psk.svg', '1001', [('2-PSK', psk)], title='2-PSK: 0 → φ = 0, 1 → φ = π; A = 5, f = 1 Hz')
    modfig('mod-af4.svg', ['11', '01', '10', '00'], [('A + f', af4)], title='4 stavy: 1. bit → A (2 / 5), 2. bit → f (1 / 2 Hz); φ = 0')
    modfig('mod-afp8.svg', ['000', '011', '101', '110'], [('A + f + φ', afp8)],
           title='8 stavů: 1. bit → A (2 / 5), 2. bit → f (1 / 2 Hz), 3. bit → φ (0 / π)')

    modfig('ex5-grid.svg', '1011', [('2-ASK', None), ('2-FSK', None), ('2-PSK', None)], w=120,
           title='Příklad 5: nakreslete 1011')
    modfig('ex5-solution.svg', '1011', [('2-ASK', ask), ('2-FSK', fsk), ('2-PSK', psk)], w=120,
           title='Řešení 5: 1011')
    modfig('ex6-solution.svg', ['10', '01', '11', '00'], [('A + φ', ap4)],
           title='Řešení 6: 1. bit → A (0: 2, 1: 5), 2. bit → φ (0: 0, 1: π); f = 1 Hz')
    modfig('ex7.svg', ['010', '111', '100', '001'], [('?', afp8)], labels=False,
           title='Příklad 7: dekódujte (tabulka 8 stavů: A 2/5, f 1/2 Hz, φ 0/π)')
    modfig('ex7-solution.svg', ['010', '111', '100', '001'], [('A + f + φ', afp8)],
           title='Řešení 7: 010 111 100 001')
