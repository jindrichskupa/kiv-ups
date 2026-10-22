"""Generate SVG figures for KIV/UPS ex07 (efficiency, frame errors, byte/bit stuffing). Usage: python3 gen_svg07.py <out_dir>"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_svg as g  # noqa: E402
from gen_svg import text, polyline, INK, MUTED, BLUE, RED, GREEN  # noqa: E402

g.OUT = sys.argv[1]
save = g.save
GRID = '#d0d7de'
STX, ETX, DLE = 0x02, 0x03, 0x10


# ---------- stuffing logic (also used for the self-check) ----------

def byte_stuff(data):
    """-> list of (byte, kind): flag / data / hit (data byte = ridici znak) / stuff (vlozeny DLE)."""
    out = [(STX, 'flag')]
    for b in data:
        if b in (STX, ETX, DLE):
            out += [(DLE, 'stuff'), (b, 'hit')]
        else:
            out.append((b, 'data'))
    return out + [(ETX, 'flag')]


def byte_unstuff(frame):
    assert frame[0] == STX and frame[-1] == ETX
    out, esc = [], False
    for b in frame[1:-1]:
        if esc or b != DLE:
            out.append(b)
            esc = False
        else:
            esc = True
    return out


def bit_stuff(bits, k):
    """vlozi 0 po k jednickach -> list of (bit, kind)"""
    out, c = [], 0
    for b in bits:
        out.append((b, 'data'))
        c = c + 1 if b == '1' else 0
        if c == k:
            out.append(('0', 'stuff'))
            c = 0
    return out


def bit_unstuff(bits, k):
    out, c = '', 0
    for b in bits:
        if c == k:
            assert b == '0', 'po k jednickach musi byt vlozena 0'
            c = 0
            continue
        out += b
        c = c + 1 if b == '1' else 0
    return out


# ---------- figures ----------

FILL = {'flag': ('#dafbe1', GREEN), 'data': ('#ffffff', INK), 'hit': ('#ffebe9', RED),
        'stuff': ('#ddf4ff', BLUE), 'plain': ('#ffffff', INK)}


def cells(name, rows, title=None, cw=40, legend=True):
    """rows: list of (label, [(text, kind), ...])"""
    x0, rh, top = 190, 58, 52 if title else 20
    n = max(len(r[1]) for r in rows)
    h = top + rh * len(rows) + (40 if legend else 10)
    body = []
    if title:
        body.append(text(20, 28, title, 16, INK, 'start', 'font-weight="bold"'))
    for r, (lab, cs) in enumerate(rows):
        y = top + r * rh
        body.append(text(20, y + 26, lab, 14, INK, 'start', 'font-weight="bold"'))
        for i, (t, kind) in enumerate(cs):
            fill, col = FILL[kind]
            body.append(f'<rect x="{x0 + i * cw}" y="{y}" width="{cw}" height="38" fill="{fill}" stroke="{GRID}"/>')
            body.append(text(x0 + i * cw + cw / 2, y + 25, t, 15 if cw >= 30 else 14, col,
                             extra='font-family="monospace"' + (' font-weight="bold"' if kind != 'data' else '')))
    if legend:
        y, x = h - 18, 20
        for kind, lab in (('flag', 'řídicí znak / vlajka'), ('hit', 'data = řídicí kombinace'), ('stuff', 'vložené')):
            fill, col = FILL[kind]
            body.append(f'<rect x="{x}" y="{y - 12}" width="14" height="14" fill="{fill}" stroke="{col}"/>')
            body.append(text(x + 20, y, lab, 13, MUTED, 'start'))
            x += 220
    save(name, x0 + n * cw + 20, h, '\n'.join(body))


def hexrow(seq):
    return [(f'{b:02X}', k) for b, k in seq]


def bitrow(seq):
    return [(b, k) for b, k in seq]


def mark_runs(bits, k):
    """data radek: obarvi bity, ktere tvori k jednicek za sebou (tam se bude vkladat)"""
    kinds, c = ['data'] * len(bits), 0
    for i, b in enumerate(bits):
        c = c + 1 if b == '1' else 0
        if c == k:
            for j in range(i - k + 1, i + 1):
                kinds[j] = 'hit'
            c = 0
    return list(zip(bits, kinds))


def plot(name, title, curves, xmax, xlabel, ylabel, xticks, mark=None, w=640, h=330):
    x0, y0, pw, ph = 70, 280, w - 110, 220
    sx = lambda x: x0 + x / xmax * pw
    sy = lambda y: y0 - y * ph
    body = [text(20, 26, title, 16, INK, 'start', 'font-weight="bold"'),
            f'<line x1="{x0}" y1="{y0}" x2="{x0 + pw}" y2="{y0}" stroke="{INK}"/>',
            f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0 - ph}" stroke="{INK}"/>',
            text(x0 + pw, y0 + 38, xlabel, 13, MUTED, 'end'),
            text(x0 - 10, y0 - ph - 12, ylabel, 13, MUTED, 'start')]
    for v in (0, .25, .5, .75, 1):
        body.append(f'<line x1="{x0}" y1="{sy(v)}" x2="{x0 + pw}" y2="{sy(v)}" stroke="#eef1f4"/>')
        body.append(text(x0 - 8, sy(v) + 4, f'{round(v * 100)} %', 12, MUTED, 'end'))
    for xt in xticks:
        body.append(f'<line x1="{sx(xt)}" y1="{y0}" x2="{sx(xt)}" y2="{y0 + 5}" stroke="{INK}"/>')
        body.append(text(sx(xt), y0 + 20, str(xt), 12, MUTED))
    for k, (lab, col, fn) in enumerate(curves):
        pts = [(sx(x), sy(fn(x))) for x in [xmax * i / 300 for i in range(1, 301)]]
        body.append(polyline(pts, col, 2.5))
        body.append(text(x0 + 20, sy(.3) + 20 * k, lab, 13, col, 'start'))
    if mark:
        mx, my, ml = mark
        body.append(f'<circle cx="{sx(mx)}" cy="{sy(my)}" r="5" fill="{RED}"/>')
        right = mx > .7 * xmax
        body.append(text(sx(mx) + (-10 if right else 10), sy(my) + (22 if right else -8), ml, 13, RED, 'end' if right else 'start'))
    save(name, w, h, '\n'.join(body))


def goodput(L, hdr=20, ber=1e-4):
    return L / (L + hdr) * (1 - ber) ** (8 * (L + hdr))


if __name__ == '__main__':
    # --- self-check: priklady z PDF i nove ---
    pdf_bytes = [0x15, 0x2A, 0x02, 0xCC, 0x05, 0x03, 0xCD, 0x10, 0x12]
    st = byte_stuff(pdf_bytes)
    assert ' '.join(f'{b:02X}' for b, _ in st) == '02 15 2A 10 02 CC 05 10 03 CD 10 10 12 03'
    ex = [0x10, 0x02, 0x41, 0x03, 0x10]
    st2 = byte_stuff(ex)
    assert ' '.join(f'{b:02X}' for b, _ in st2) == '02 10 10 10 02 41 10 03 10 10 03'
    assert byte_unstuff([0x02, 0x10, 0x10, 0x48, 0x10, 0x03, 0x49, 0x10, 0x02, 0x03]) == [0x10, 0x48, 0x03, 0x49, 0x02]
    pdf_bits = '11010110010111111001101100'
    sb = bit_stuff(pdf_bits, 4)
    assert ''.join(b for b, _ in sb) == '110101100101111011001101100'
    hd = '0111111011111100'
    sh = bit_stuff(hd, 5)
    assert ''.join(b for b, _ in sh) == '011111010111110100'
    assert bit_unstuff('011111010111110100', 5) == hd
    p15 = '0111111010111110011111011001111110'
    assert p15[:8] == p15[-8:] == '01111110' and bit_unstuff(p15[8:-8], 5) == '1011111011111110'
    assert round(math.log(.95) / math.log(.99), 4) == 5.1036

    g.uart_static('uart-k-7e2.svg', 0x4B, "'K' v 7E2: 1 start + 7 dat + parita + 2 stop = 11 bitů, z toho 7 užitečných", data_bits=7, parity='E', stop=2)

    cells('bytes-pdf.svg', [('data', hexrow([(b, 'hit' if b in (2, 3, 0x10) else 'data') for b in pdf_bytes])),
                            ('+ STX / ETX', hexrow([(STX, 'flag')] + [(b, 'hit' if b in (2, 3, 0x10) else 'data') for b in pdf_bytes] + [(ETX, 'flag')])),
                            ('byte stuffing', hexrow(st))],
          title='Byte stuffing: před každý řídicí znak v datech vlož DLE (0x10)')
    cells('bytes-ex-solution.svg', [('data', hexrow([(b, 'hit') if b in (2, 3, 0x10) else (b, 'data') for b in ex])),
                                    ('rámec', hexrow(st2))], title='Řešení: 10 02 41 03 10')
    cells('bits-pdf.svg', [('data', bitrow(mark_runs(pdf_bits, 4))),
                           ('+ vlajky', bitrow([('1', 'flag')] * 5 + mark_runs(pdf_bits, 4) + [('1', 'flag')] * 5)),
                           ('bit stuffing', bitrow([('1', 'flag')] * 5 + sb + [('1', 'flag')] * 5))],
          title='Bit stuffing (vlajka 11111): po každých čtyřech 1 v datech vlož 0', cw=20)
    flag = [(b, 'flag') for b in '01111110']
    cells('bits-hdlc-solution.svg', [('data', bitrow(mark_runs(hd, 5))), ('rámec', bitrow(flag + sh + flag))],
          title='Řešení: HDLC, vlajka 01111110, 0 po pěti 1', cw=22)

    plot('frame-ok.svg', 'Pravděpodobnost bezchybného rámce podle délky', [
        ('BER 10⁻⁴', RED, lambda n: (1 - 1e-4) ** n),
        ('BER 10⁻⁵', '#9a6700', lambda n: (1 - 1e-5) ** n),
        ('BER 10⁻⁶', BLUE, lambda n: (1 - 1e-6) ** n)],
        12000, 'délka rámce [bit]', 'P(rámec OK)', [0, 2000, 4000, 6000, 8000, 10000, 12000],
        mark=(12000, (1 - 1e-5) ** 12000, '1500 B: 88,7 %'))
    best = max(range(1, 4001), key=goodput)
    plot('goodput.svg', 'Užitečná propustnost: hlavička 20 B, BER 10⁻⁴', [
        ('podíl užitečných dat v bezchybných rámcích', GREEN, goodput)],
        1500, 'data v rámci [B]', 'užitečná propustnost', [0, 250, 500, 750, 1000, 1250, 1500],
        mark=(best, goodput(best), f'optimum ≈ {best} B'))
    print('optimum', best, goodput(best))
