"""Generate SVG figures for KIV/UPS ex08 (parity grid, ARQ timelines). Usage: python3 gen_svg08.py <out_dir>"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_svg as g  # noqa: E402
from gen_svg import text, INK, MUTED, BLUE, RED, GREEN  # noqa: E402

g.OUT = sys.argv[1]
save = g.save
GRID = '#d0d7de'
ORANGE = '#9a6700'


# ---------- 2D parity ----------

DATA = ['1011', '0110', '1100', '0011']


def parity2d(name, data, title, flips=(), solve=False):
    """flips: (row, col) bits flipped in transit; solve: highlight mismatching parities."""
    rows = [list(r) for r in data]
    rp = [str(r.count('1') % 2) for r in data]
    cp = [str(sum(r[c] == '1' for r in data) % 2) for c in range(4)]
    for r, c in flips:
        rows[r][c] = '0' if rows[r][c] == '1' else '1'
    bad_r = {r for r in range(4) if str(rows[r].count('1') % 2) != rp[r]}
    bad_c = {c for c in range(4) if str(sum(rows[r][c] == '1' for r in range(4)) % 2) != cp[c]}
    x0, y0, s = 80, 60, 46
    body = [text(20, 28, title, 16, INK, 'start', 'font-weight="bold"')]
    for r in range(5):
        for c in range(5):
            if r == 4 and c == 4:
                v, fill = str(rp.count('1') % 2), '#fff8c5'
            elif r == 4:
                v, fill = cp[c], '#fff8c5'
            elif c == 4:
                v, fill = rp[r], '#fff8c5'
            else:
                v, fill = rows[r][c], '#ffffff'
            if solve and ((r == 4 and c in bad_c) or (c == 4 and r in bad_r)):
                fill = '#ffebe9'
            if solve and (r, c) in flips:
                fill = '#ffebe9'
            body.append(f'<rect x="{x0 + c * s}" y="{y0 + r * s}" width="{s}" height="{s}" fill="{fill}" stroke="{GRID}"/>')
            col = RED if solve and (r, c) in flips else INK
            body.append(text(x0 + c * s + s / 2, y0 + r * s + s / 2 + 7, v, 20, col, extra='font-family="monospace"'))
    body.append(f'<line x1="{x0 + 4 * s}" y1="{y0 - 6}" x2="{x0 + 4 * s}" y2="{y0 + 5 * s + 6}" stroke="{INK}" stroke-width="2"/>')
    body.append(f'<line x1="{x0 - 6}" y1="{y0 + 4 * s}" x2="{x0 + 5 * s + 6}" y2="{y0 + 4 * s}" stroke="{INK}" stroke-width="2"/>')
    body.append(text(x0 + 4.5 * s, y0 - 10, 'P řádku', 12, MUTED))
    body.append(text(x0 - 10, y0 + 4.5 * s + 5, 'P sloupce', 12, MUTED, 'end'))
    save(name, x0 + 5 * s + 30, y0 + 5 * s + 20, '\n'.join(body))


# ---------- ARQ timelines ----------

UX, X0, YS, YR, D = 56, 120, 100, 260, 1.5  # px per time unit, sender/receiver line y, propagation delay


def timeline(name, title, frames=(), acks=(), notes=(), units=12, grid_only=False):
    """frames: (t_send, label, state) state in ok/lost/discard/buffer; acks: (t_send_at_receiver, label, lost)."""
    sx = lambda t: X0 + t * UX
    body = [text(20, 28, title, 16, INK, 'start', 'font-weight="bold"'),
            text(20, YS + 5, 'Odesílatel', 14, INK, 'start', 'font-weight="bold"'),
            text(20, YR + 5, 'Příjemce', 14, INK, 'start', 'font-weight="bold"')]
    for t in range(units + 1):
        body.append(f'<line x1="{sx(t)}" y1="{YS}" x2="{sx(t)}" y2="{YR}" stroke="#eef1f4"/>')
        body.append(text(sx(t), YR + 40, str(t), 11, MUTED))
    for y in (YS, YR):
        body.append(f'<line x1="{sx(0)}" y1="{y}" x2="{sx(units) + 10}" y2="{y}" stroke="{INK}" stroke-width="1.5"/>')
    body.append(text(sx(units) + 16, YR + 40, 't', 12, MUTED, 'start', 'font-style="italic"'))
    if grid_only:
        save(name, sx(units) + 40, YR + 60, '\n'.join(body))
        return
    colors = {'ok': BLUE, 'lost': RED, 'discard': MUTED, 'buffer': ORANGE}
    for t, lab, st in frames:
        col = colors[st]
        x1, x2 = sx(t), sx(t + D)
        if st == 'lost':
            xm, ym = sx(t + D * 0.55), YS + (YR - YS) * 0.55
            body.append(f'<line x1="{x1}" y1="{YS}" x2="{xm}" y2="{ym}" stroke="{col}" stroke-width="2"/>')
            body.append(text(xm + 2, ym + 8, '✗', 22, RED))
        else:
            body.append(f'<line x1="{x1}" y1="{YS}" x2="{x2}" y2="{YR}" stroke="{col}" stroke-width="2" marker-end="url(#a{st})"/>')
            tag = {'ok': '', 'discard': 'zahodí', 'buffer': 'uloží'}[st]
            if tag:
                body.append(text(x2, YR + 22, tag, 11, col))
        body.append(f'<rect x="{x1 - 16}" y="{YS - 30}" width="32" height="22" fill="#ddf4ff" stroke="{col}"/>')
        body.append(text(x1, YS - 14, lab, 13, INK, extra='font-family="monospace"'))
    for t, lab, lost in acks:
        x1, x2 = sx(t), sx(t + D)
        body.append(f'<line x1="{x1}" y1="{YR}" x2="{x2}" y2="{YS}" stroke="{GREEN}" stroke-width="1.5" stroke-dasharray="5 3" marker-end="url(#aack)"/>')
        body.append(text(x1 + 4, YR - 6, lab, 11, GREEN, 'start'))
    for t, s_ in notes:
        body.append(text(sx(t), YS - 40, s_, 12, RED))
    defs = '<defs>' + ''.join(
        f'<marker id="a{k}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
        f'<path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>'
        for k, c in (('ok', BLUE), ('discard', MUTED), ('buffer', ORANGE), ('ack', GREEN))) + '</defs>'
    save(name, sx(units) + 40, YR + 60, defs + '\n'.join(body))


def snw():
    title = 'Stop-and-Wait: rámec → čekání na ACK → další rámec'
    sx = lambda t: X0 + t * UX
    tdata, tack = 2, 0.6
    body = [text(20, 28, title, 16, INK, 'start', 'font-weight="bold"'),
            text(20, YS + 5, 'Odesílatel', 14, INK, 'start', 'font-weight="bold"'),
            text(20, YR + 5, 'Příjemce', 14, INK, 'start', 'font-weight="bold"')]
    for y in (YS, YR):
        body.append(f'<line x1="{sx(0)}" y1="{y}" x2="{sx(11)}" y2="{y}" stroke="{INK}" stroke-width="1.5"/>')
    # DATA: rovnobeznik (vysila se t_data, leti t_d)
    p = [(sx(0), YS), (sx(tdata), YS), (sx(tdata + D * 2), YR), (sx(D * 2), YR)]
    body.append('<polygon points="' + ' '.join(f'{x},{y}' for x, y in p) + f'" fill="#ddf4ff" stroke="{BLUE}"/>')
    body.append(text(sx(tdata / 2 + D), (YS + YR) / 2 + 5, 'DATA', 14, BLUE, extra='font-weight="bold"'))
    ta0 = tdata + D * 2
    p = [(sx(ta0), YR), (sx(ta0 + tack), YR), (sx(ta0 + tack + D * 2), YS), (sx(ta0 + D * 2), YS)]
    body.append('<polygon points="' + ' '.join(f'{x},{y}' for x, y in p) + f'" fill="#dafbe1" stroke="{GREEN}"/>')
    body.append(text(sx(ta0 + tack / 2 + D) + 8, (YS + YR) / 2 + 5, 'ACK', 14, GREEN, extra='font-weight="bold"'))
    end = ta0 + tack + D * 2

    def dim(t1, t2, y, lab, col):
        body.append(f'<path d="M{sx(t1)},{y - 5} v10 M{sx(t1)},{y} H{sx(t2)} M{sx(t2)},{y - 5} v10" fill="none" stroke="{col}"/>')
        body.append(text((sx(t1) + sx(t2)) / 2, y - 8, lab, 13, col))
    dim(0, tdata, YS - 20, 't_data', BLUE)
    dim(0, D * 2, YR + 30, 't_d', MUTED)
    dim(ta0, ta0 + tack, YR + 30, 't_ack', GREEN)
    dim(ta0 + tack, end, YS - 20, 't_d', MUTED)
    dim(0, end, YS - 50, 'cyklus = t_data + t_ack + 2 · t_d', RED)
    body.append(f'<rect x="{sx(end)}" y="{YS - 22}" width="{tdata * UX}" height="22" fill="#ddf4ff" stroke="{BLUE}"/>')
    body.append(text(sx(end + tdata / 2), YS - 6, 'další', 12, BLUE))
    body.append(text(20, YR + 75, 'Efektivita e = t_data / (t_data + t_ack + 2 · t_d) - po celý zbytek cyklu linka mlčí.', 13, MUTED, 'start'))
    save('snw.svg', sx(11) + 30, YR + 90, '\n'.join(body))


def arq():
    common = [(0, 'F0', 'ok'), (1, 'F1', 'ok'), (2, 'F2', 'lost'), (3, 'F3', None), (4, 'F4', None), (5, 'F5', None)]
    first_acks = [(1.5, 'ACK0', False), (2.5, 'ACK1', False)]
    gbn = [(t, l, s or 'discard') for t, l, s in common] + [(7, 'F2', 'ok'), (8, 'F3', 'ok'), (9, 'F4', 'ok'), (10, 'F5', 'ok')]
    gbn_acks = first_acks + [(4.5, 'ACK1', False), (5.5, 'ACK1', False), (6.5, 'ACK1', False),
                             (8.5, 'ACK2', False), (9.5, 'ACK3', False), (10.5, 'ACK4', False), (11.5, 'ACK5', False)]
    timeline('gbn-solution.svg', 'Řešení: Go-Back-N, Ws = 4, ztracený F2, timeout 5', gbn, gbn_acks,
             [(7, 'timeout F2 → znovu F2–F5')], units=14)
    sr = [(t, l, s or 'buffer') for t, l, s in common] + [(7, 'F2', 'ok'), (10, 'F6', 'ok'), (11, 'F7', 'ok'), (12, 'F8', 'ok')]
    sr_acks = first_acks + [(4.5, 'ACK3', False), (5.5, 'ACK4', False), (6.5, 'ACK5', False), (8.5, 'ACK2', False), (11.5, 'ACK6', False)]
    timeline('sr-solution.svg', 'Řešení: Selective Repeat, Ws = Wr = 4, ztracený F2, timeout 5', sr, sr_acks,
             [(7, 'timeout F2 → jen F2')], units=14)
    timeline('arq-grid.svg', 'Příklad: Ws = 4, F2 se ztratí, timeout 5 jednotek, cesta 1,5 jednotky', units=14, grid_only=True)


if __name__ == '__main__':
    parity2d('parity-send.svg', DATA, 'Odeslaný blok (sudá parita)')
    parity2d('parity-1err.svg', DATA, 'Přijato - najděte chybu', flips=[(1, 2)])
    parity2d('parity-1err-solution.svg', DATA, 'Řešení: řádek 2 × sloupec 3', flips=[(1, 2)], solve=True)
    parity2d('parity-2err.svg', DATA, 'Přijato - 2 chyby v řádku 2', flips=[(1, 1), (1, 2)], solve=True)
    snw()
    arq()
