"""Generate SVG figures for KIV/UPS ex02 (socket call sequence diagrams). Usage: python3 gen_svg02.py <out_dir>"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_svg as g  # noqa: E402
from gen_svg import text, INK, MUTED, BLUE, RED  # noqa: E402

g.OUT = sys.argv[1]
XS, XC, TOP, RH = 230, 590, 70, 38


def seq(name, title, rows, blocks, note=None):
    """rows: list of (server_label, client_label, arrow) with arrow None or (dir 'c2s'/'s2c', label)."""
    y = lambda r: TOP + 20 + r * RH
    h = y(len(rows)) + (40 if note else 10)
    body = [text(20, 28, title, 16, INK, 'start', 'font-weight="bold"'),
            text(XS, TOP - 8, 'Server', 15, INK, extra='font-weight="bold"'),
            text(XC, TOP - 8, 'Klient', 15, INK, extra='font-weight="bold"'),
            '<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{BLUE}"/></marker></defs>']
    for x in (XS, XC):
        body.append(f'<line x1="{x}" y1="{TOP}" x2="{x}" y2="{y(len(rows)) - 10}" stroke="{MUTED}" stroke-dasharray="5 4"/>')
    for side, r0, r1 in blocks:
        x = XS if side == 's' else XC
        body.append(f'<rect x="{x - 5}" y="{y(r0)}" width="10" height="{y(r1) - y(r0)}" fill="{RED}" opacity="0.75"/>')
    for r, (sl, cl, arrow) in enumerate(rows):
        if sl:
            body.append(text(XS - 14, y(r) + 5, sl, 14, INK, 'end', 'font-family="monospace"'))
        if cl:
            body.append(text(XC + 14, y(r) + 5, cl, 14, INK, 'start', 'font-family="monospace"'))
        if arrow:
            d, lab = arrow
            x1, x2 = (XC - 6, XS + 6) if d == 'c2s' else (XS + 6, XC - 6)
            body.append(f'<line x1="{x1}" y1="{y(r)}" x2="{x2}" y2="{y(r) + RH * 0.8}" stroke="{BLUE}" stroke-width="2" marker-end="url(#ar)"/>')
            body.append(text((XS + XC) / 2, y(r) + RH * 0.4 - 6, lab, 13, BLUE))
    body.append(f'<rect x="20" y="{h - 30 if note else h - 4}" width="10" height="14" fill="{RED}" opacity="0.75"/>' if note else '')
    if note:
        body.append(text(38, h - 18, note, 13, MUTED, 'start'))
    save_w = XC + 230
    g.save(name, save_w, h, '\n'.join(body))


seq('seq-tcp.svg', 'TCP: pořadí volání a kde se blokuje', [
    ('socket()', None, None),
    ('bind(4242)', None, None),
    ('listen()', 'socket()', None),
    ('accept()', 'connect()', ('c2s', 'SYN')),
    (None, None, ('s2c', 'SYN + ACK')),
    (None, None, ('c2s', 'ACK')),
    ('← nový socket', '← 0', None),
    ('recv()', 'send("Ahoj")', ('c2s', 'Ahoj')),
    ('← 4', 'recv()', None),
    ('send("OK")', None, ('s2c', 'OK')),
    (None, '← 2', None),
    ('recv()', 'close()', ('c2s', 'FIN')),
    ('← 0 → close()', None, None),
], [('s', 3, 6), ('c', 3, 6), ('s', 7, 8), ('c', 8, 10), ('s', 11, 12)],
    note='červeně = volání blokuje (vlákno čeká); accept() vrací NOVÝ socket pro klienta, poslouchající zůstává')

seq('seq-udp.svg', 'UDP: bez spojení, adresa v každém volání', [
    ('socket()', 'socket()', None),
    ('bind(4242)', None, None),
    ('recvfrom()', 'sendto("Ahoj", srv)', ('c2s', 'Ahoj')),
    ('← 4 + adresa klienta', 'recvfrom()', None),
    ('sendto("OK", klient)', None, ('s2c', 'OK')),
    (None, '← 2 + adresa serveru', None),
    ('close()', 'close()', None),
], [('s', 2, 3), ('c', 3, 5)],
    note='červeně = blokuje; žádný handshake ani FIN; klient bind() nevolá - port přidělí systém při prvním sendto()')
