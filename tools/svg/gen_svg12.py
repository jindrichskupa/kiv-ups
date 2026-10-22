"""Generate SVG figures for KIV/UPS ex12 (switching, VLAN, STP) and ex13 (routing).
Usage: python3 gen_svg12.py <ex12_images_dir> <ex13_images_dir>"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_svg as g  # noqa: E402
from gen_svg import text, INK, MUTED, BLUE, RED, GREEN  # noqa: E402

GRID = '#d0d7de'
ORANGE = '#bc4c00'
VCOL = {10: BLUE, 20: GREEN, 30: ORANGE}
VFILL = {10: '#ddf4ff', 20: '#dafbe1', 30: '#fff1e5'}


def node_svg(x, y, kind, label, sub=None, fill=None, stroke=None):
    out = []
    if kind == 'router':
        out.append(f'<circle cx="{x}" cy="{y}" r="24" fill="{fill or "#ddf4ff"}" stroke="{stroke or BLUE}" stroke-width="2"/>')
        out.append(text(x, y + 5, label, 14, INK, extra='font-weight="bold"'))
        sy = y + 42
    elif kind == 'switch':
        out.append(f'<rect x="{x - 38}" y="{y - 17}" width="76" height="34" rx="6" fill="{fill or "#dafbe1"}" stroke="{stroke or GREEN}" stroke-width="2"/>')
        out.append(text(x, y + 5, label, 14, INK, extra='font-weight="bold"'))
        sy = y + 34
    elif kind == 'hub':
        out.append(f'<rect x="{x - 32}" y="{y - 15}" width="64" height="30" rx="4" fill="#f6f8fa" stroke="{MUTED}" stroke-width="2" stroke-dasharray="5 3"/>')
        out.append(text(x, y + 5, label, 13, INK, extra='font-weight="bold"'))
        sy = y + 32
    elif kind == 'pc':
        out.append(f'<rect x="{x - 24}" y="{y - 15}" width="48" height="30" rx="3" fill="{fill or "#fff"}" stroke="{stroke or INK}" stroke-width="1.5"/>')
        out.append(text(x, y + 5, label, 13, INK, extra='font-weight="bold"'))
        sy = y + 32
    elif kind == 'lan':
        out.append(f'<ellipse cx="{x}" cy="{y}" rx="54" ry="22" fill="{fill or "#fff8c5"}" stroke="#9a6700" stroke-width="1.5"/>')
        out.append(text(x, y + 5, label, 13, INK, extra='font-weight="bold"'))
        sy = y + 40
    if sub and sub.startswith('^'):
        lines = sub[1:].split('\n')
        top = {'router': 30, 'switch': 23}.get(kind, 22)
        for k, s_ in enumerate(lines):
            out.append(text(x, y - top - 16 * (len(lines) - 1 - k), s_, 12, MUTED))
    elif sub:
        for k, s_ in enumerate(sub.split('\n')):
            out.append(text(x, sy + 16 * k, s_, 12, MUTED))
    return out


def topo(name, w, h, nodes, links, title=None, notes=()):
    body = []
    if title:
        body.append(text(20, 26, title, 16, INK, 'start', 'font-weight="bold"'))
    for ln in links:
        (x1, y1), (x2, y2) = nodes[ln['a']][:2], nodes[ln['b']][:2]
        col, wd = ln.get('color', MUTED), ln.get('width', 2)
        dash = f' stroke-dasharray="{ln["dash"]}"' if ln.get('dash') else ''
        body.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="{wd}"{dash}/>')
        if ln.get('label'):
            mx, my = (x1 + x2) / 2 + ln.get('dx', 0), (y1 + y2) / 2 + ln.get('dy', -8)
            body.append(f'<rect x="{mx - 4 - 3.6 * len(ln["label"])}" y="{my - 14}" width="{8 + 7.2 * len(ln["label"])}" height="19" rx="3" fill="#fff" opacity="0.9"/>')
            body.append(text(mx, my, ln['label'], 13, ln.get('lcolor', INK), extra='font-weight="bold"'))
        for key, t in (('pa', 0.24), ('pb', 0.76)):
            if ln.get(key):
                px, py = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
                off = ln.get(key + 'o', (10, -6))
                lab = ln[key]
                lcol = RED if lab.endswith('B') and ln.get('roles') else ln.get(key + 'c', MUTED)
                body.append(text(px + off[0], py + off[1], lab, 12, lcol, 'start', 'font-family="monospace"'))
        if ln.get('cross'):
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            body.append(f'<path d="M{mx - 10},{my - 10} L{mx + 10},{my + 10} M{mx + 10},{my - 10} L{mx - 10},{my + 10}" stroke="{RED}" stroke-width="4"/>')
    for nid, (x, y, kind, label, *rest) in nodes.items():
        sub = rest[0] if rest else None
        fill = rest[1] if len(rest) > 1 else None
        stroke = rest[2] if len(rest) > 2 else None
        body += node_svg(x, y, kind, label, sub, fill, stroke)
    for k, n in enumerate(notes):
        body.append(text(20, h - 14 - 20 * (len(notes) - 1 - k), n, 13, MUTED, 'start'))
    g.save(name, w, h, '\n'.join(body))


# ================= ex12 =================

def mac1():
    nodes = {'SW': (380, 90, 'switch', 'SW'), 'H': (130, 200, 'hub', 'HUB'),
             'A': (60, 300, 'pc', 'A', 'MAC A'), 'E': (200, 300, 'pc', 'E', 'MAC E'),
             'B': (320, 260, 'pc', 'B', 'MAC B'), 'C': (460, 260, 'pc', 'C', 'MAC C'), 'D': (620, 200, 'pc', 'D', 'MAC D')}
    links = [dict(a='SW', b='H', pa='1', pao=(-18, -2)), dict(a='H', b='A'), dict(a='H', b='E'),
             dict(a='SW', b='B', pa='2', pao=(-16, 4)), dict(a='SW', b='C', pa='3', pao=(8, 4)), dict(a='SW', b='D', pa='4', pao=(4, -8))]
    topo('mac1.svg', 700, 360, nodes, links, 'Příklad 1: jeden switch, na portu 1 je rozbočovač (hub)')


def mac2():
    nodes = {'S1': (220, 90, 'switch', 'SW1'), 'S2': (500, 90, 'switch', 'SW2'),
             'A': (130, 220, 'pc', 'A'), 'B': (300, 220, 'pc', 'B'), 'C': (420, 220, 'pc', 'C'), 'D': (590, 220, 'pc', 'D')}
    links = [dict(a='S1', b='S2', pa='3', pb='3', pao=(4, -8), pbo=(-14, -8)),
             dict(a='S1', b='A', pa='1', pao=(-18, 0)), dict(a='S1', b='B', pa='2', pao=(8, 0)),
             dict(a='S2', b='C', pa='1', pao=(-18, 0)), dict(a='S2', b='D', pa='2', pao=(8, 0))]
    topo('mac2.svg', 720, 270, nodes, links, 'Příklad 5: dva switche propojené porty 3')


def domains():
    nodes = {'R': (380, 70, 'router', 'R'), 'S1': (200, 160, 'switch', 'SW1'), 'S2': (580, 160, 'switch', 'SW2'),
             'P1': (60, 270, 'pc', 'PC1'), 'P2': (140, 270, 'pc', 'PC2'), 'P3': (220, 270, 'pc', 'PC3'),
             'H': (330, 260, 'hub', 'HUB'), 'P4': (260, 360, 'pc', 'PC4'), 'P5': (330, 360, 'pc', 'PC5'), 'P6': (400, 360, 'pc', 'PC6'),
             'P7': (530, 270, 'pc', 'PC7'), 'P8': (640, 270, 'pc', 'PC8')}
    links = [dict(a='R', b='S1'), dict(a='R', b='S2'), dict(a='S1', b='P1'), dict(a='S1', b='P2'), dict(a='S1', b='P3'),
             dict(a='S1', b='H'), dict(a='H', b='P4'), dict(a='H', b='P5'), dict(a='H', b='P6'), dict(a='S2', b='P7'), dict(a='S2', b='P8')]
    topo('domains.svg', 720, 410, nodes, links, 'Příklad 2: kolik je kolizních a kolik broadcastových domén?')


def dot1q():
    fields = [('cílová MAC', 5, '#f6f8fa'), ('zdrojová MAC', 5, '#f6f8fa'), ('TPID\n0x8100', 3.4, '#ffebe9'), ('TCI', 3.4, '#ffebe9'),
              ('EtherType', 3.6, '#f6f8fa'), ('data 46–1500 B', 8, '#ddf4ff'), ('FCS', 2.6, '#f6f8fa')]
    sizes = ['6 B', '6 B', '2 B', '2 B', '2 B', '', '4 B']
    x, u, y = 20, 25, 60
    body = [text(20, 28, 'Ethernetový rámec s tagem 802.1Q (vložené 4 B červeně)', 16, INK, 'start', 'font-weight="bold"')]
    tci_x = None
    for (lab, wu, fill), sz in zip(fields, sizes):
        wpx = wu * u
        body.append(f'<rect x="{x}" y="{y}" width="{wpx}" height="50" fill="{fill}" stroke="{GRID}"/>')
        for k, line in enumerate(lab.split('\n')):
            body.append(text(x + wpx / 2, y + 22 + 16 * k - (8 if '\n' in lab else 0) + 4, line, 13, INK))
        if sz:
            body.append(text(x + wpx / 2, y + 68, sz, 12, MUTED))
        if lab == 'TCI':
            tci_x = (x, x + wpx)
        x += wpx
    # rozpad TCI
    bx, by, bu = 190, 170, 32
    parts = [('PCP', 3, 'priorita 0–7', 130), ('DEI', 1, 'drop', 70), ('VID', 12, 'číslo VLAN', 320)]
    body.append(f'<path d="M{tci_x[0]},{y + 50} L{bx},{by} M{tci_x[1]},{y + 50} L{bx + 520},{by}" stroke="{MUTED}" fill="none" stroke-dasharray="3 3"/>')
    for lab, bits, note, wpx in parts:
        body.append(f'<rect x="{bx}" y="{by}" width="{wpx}" height="40" fill="#ffebe9" stroke="{GRID}"/>')
        body.append(text(bx + wpx / 2, by + 25, f'{lab} ({bits} b)', 13, INK, extra='font-weight="bold"'))
        if note:
            body.append(text(bx + wpx / 2, by + 58, note, 12, MUTED))
        bx += wpx
    g.save('dot1q.svg', max(x, bx) + 20, 250, '\n'.join(body))


VLAN_NODES = {
    'R': (560, 60, 'router', 'R'),
    'S1': (220, 160, 'switch', 'SW1'), 'S2': (560, 160, 'switch', 'SW2'),
    'P1': (70, 290, 'pc', 'PC1', 'vývoj'), 'P2': (180, 290, 'pc', 'PC2', 'vývoj'), 'P3': (290, 290, 'pc', 'PC3', 'ekonomika'),
    'P4': (440, 290, 'pc', 'PC4', 'vývoj'), 'P5': (560, 290, 'pc', 'PC5', 'vedení'), 'P6': (680, 290, 'pc', 'PC6', 'ekonomika'),
}
VLAN_OF = {'P1': 10, 'P2': 10, 'P3': 20, 'P4': 10, 'P5': 30, 'P6': 20}
IP_OF = {'P1': '192.168.10.11', 'P2': '192.168.10.12', 'P3': '192.168.20.13', 'P4': '192.168.10.14', 'P5': '192.168.30.15', 'P6': '192.168.20.16'}


def vlan(solution):
    nodes = dict(VLAN_NODES)
    links = [dict(a='S1', b='S2', pa='G0/1', pb='G0/1', pao=(0, -8), pbo=(-40, -8)),
             dict(a='S2', b='R', pa='G0/2', pb='G0/0', pao=(8, 0), pbo=(8, 10))]
    ports = {'P1': ('S1', 'Fa0/1'), 'P2': ('S1', 'Fa0/2'), 'P3': ('S1', 'Fa0/3'), 'P4': ('S2', 'Fa0/1'), 'P5': ('S2', 'Fa0/2'), 'P6': ('S2', 'Fa0/3')}
    for p, (sw, port) in ports.items():
        x, y, kind, label, sub = nodes[p]
        if solution:
            v = VLAN_OF[p]
            nodes[p] = (x, y, kind, label, f'VLAN {v}\n{IP_OF[p]}', VFILL[v], VCOL[v])
            links.append(dict(a=sw, b=p, pb=port, pbo=(-44 if x < nodes[sw][0] else 6, -4), color=VCOL[v], width=3))
        else:
            links.append(dict(a=sw, b=p, pb=port, pbo=(-44 if x < nodes[sw][0] else 6, -4)))
    if solution:
        links[0].update(label='trunk 10, 20', color=INK, width=4, dy=-10)
        links[1].update(label='trunk 10, 20, 30', color=INK, width=4, dx=70, dy=4)
        title = 'Řešení 3: access porty podle oddělení, mezi switchi a k routeru trunk'
    else:
        title = 'Příklad 3: firma se dvěma switchi a třemi odděleními'
    topo('vlan-solution.svg' if solution else 'vlan.svg', 760, 370, nodes, links, title)


def loop():
    nodes = {'S1': (120, 90, 'switch', 'SW1'), 'S2': (420, 90, 'switch', 'SW2'), 'S3': (270, 220, 'switch', 'SW3'),
             'A': (60, 220, 'pc', 'A'), }
    links = [dict(a='S1', b='S2'), dict(a='S2', b='S3'), dict(a='S3', b='S1'), dict(a='S1', b='A')]
    topo('loop.svg', 520, 290, nodes, links, 'Příklad 7: tři switche do trojúhelníku, STP vypnuté')


STP_IDS = {'a': {'S1': '32768 / …:0a', 'S2': '32768 / …:05', 'S3': '4096 / …:ff'},
           'b': {'S1': '32768 / …:0a', 'S2': '32768 / …:05', 'S3': '32768 / …:ff'}}


def stp(name, ids, costs, roles=None, title=''):
    nodes = {'S1': (140, 100, 'switch', 'SW1', '^' + ids['S1']), 'S2': (560, 100, 'switch', 'SW2', '^' + ids['S2']),
             'S3': (350, 290, 'switch', 'SW3', ids['S3'])}
    links = [dict(a='S1', b='S2', label=costs[0], dx=60, dy=-10), dict(a='S2', b='S3', label=costs[1], dx=40, dy=0),
             dict(a='S3', b='S1', label=costs[2], dx=-40, dy=30)]
    if roles:
        for ln, (ra, rb, blocked) in zip(links, roles):
            ln.update(pa=ra, pb=rb, roles=True, pac=GREEN, pbc=GREEN)
            if blocked:
                ln.update(color=RED, dash='6 4', cross=True)
    topo(name, 700, 380, nodes, links, title,
         notes=['bridge ID = priorita / MAC; cena: 1 Gb/s = 4, 100 Mb/s = 19'] + (['R = root port, D = designated, B = blokovaný'] if roles else []))


# ================= ex13 =================

def chain13():
    nodes = {'L1': (80, 200, 'lan', 'LAN1', '10.1.0.0/24'), 'R1': (230, 110, 'router', 'R1'),
             'R2': (430, 110, 'router', 'R2'), 'L2': (430, 240, 'lan', 'LAN2', '10.2.0.0/24'),
             'R3': (630, 110, 'router', 'R3'), 'L3': (780, 200, 'lan', 'LAN3', '10.3.0.0/24')}
    links = [dict(a='L1', b='R1', pb='.1', pbo=(-26, 22)), dict(a='R1', b='R2', label='10.0.12.0/30', pa='.1', pb='.2', pao=(-6, 20), pbo=(-12, 20)),
             dict(a='R2', b='L2', pa='.1', pao=(6, 4)),
             dict(a='R2', b='R3', label='10.0.23.0/30', pa='.1', pb='.2', pao=(-6, 20), pbo=(-12, 20)), dict(a='R3', b='L3', pa='.1', pao=(6, 20))]
    topo('chain.svg', 860, 300, nodes, links, 'Příklad 1: tři routery v řadě, každý má svou LAN')


DV_POS = {'A': (100, 90), 'B': (100, 250), 'C': (280, 170), 'D': (460, 170), 'E': (640, 170)}


def dv5():
    nodes = {k: (x, y, 'router', k) for k, (x, y) in DV_POS.items()}
    links = [dict(a=a, b=b) for a, b in (('A', 'B'), ('A', 'C'), ('B', 'C'), ('C', 'D'), ('D', 'E'))]
    topo('dv5.svg', 720, 300, nodes, links, 'Příklad 2: RIP, metrika = počet skoků (hop count)')


def cti(split=False):
    nodes = {'A': (90, 100, 'router', 'A'), 'B': (270, 100, 'router', 'B'), 'C': (450, 100, 'router', 'C'),
             'N': (640, 100, 'lan', 'síť N')}
    links = [dict(a='A', b='B'), dict(a='B', b='C'), dict(a='C', b='N', cross=True, color=RED, dash='6 4')]
    topo('cti.svg', 720, 190, nodes, links, 'Příklad 5: linka C – N vypadne',
         notes=['před výpadkem: A → N = 3, B → N = 2, C → N = 1 (skoky)'])


OSPF_POS = {'A': (90, 200), 'B': (260, 90), 'C': (260, 310), 'D': (450, 200), 'E': (640, 310), 'F': (640, 90)}
OSPF_E = {('A', 'B'): 2, ('A', 'C'): 5, ('B', 'C'): 2, ('B', 'D'): 4, ('C', 'D'): 1, ('C', 'E'): 6, ('D', 'E'): 2, ('D', 'F'): 7, ('E', 'F'): 1}
OSPF_TREE = {('A', 'B'), ('B', 'C'), ('C', 'D'), ('D', 'E'), ('E', 'F')}
OSPF_DIST = {'A': 0, 'B': 2, 'C': 4, 'D': 5, 'E': 7, 'F': 8}


def ospf(solution):
    nodes = {}
    for k, (x, y) in OSPF_POS.items():
        if solution:
            nodes[k] = (x, y, 'router', k, ('^' if y < 150 else '') + f'vzdálenost {OSPF_DIST[k]}', '#ffebe9' if k == 'A' else None, RED if k == 'A' else None)
        else:
            nodes[k] = (x, y, 'router', k)
    links = []
    for (a, b), c in OSPF_E.items():
        ln = dict(a=a, b=b, label=str(c), dy=4)
        if solution:
            ln.update(color=RED if (a, b) in OSPF_TREE else GRID, width=4 if (a, b) in OSPF_TREE else 2)
        links.append(ln)
    if solution:
        topo('ospf-solution.svg', 740, 390, nodes, links, 'Řešení 3: strom nejkratších cest z A (červeně)')
    else:
        topo('ospf.svg', 740, 370, nodes, links, 'Příklad 3: OSPF, čísla = ceny linek, počítá router A')


def refbw():
    nodes = {'R1': (90, 190, 'router', 'R1'), 'R2': (330, 70, 'router', 'R2'), 'R4': (570, 190, 'router', 'R4'),
             'N': (720, 190, 'lan', 'síť X')}
    links = [dict(a='R1', b='R2', label='1 Gb/s', dx=-30), dict(a='R2', b='R4', label='1 Gb/s', dx=30),
             dict(a='R1', b='R4', label='100 Mb/s', dy=-6), dict(a='R4', b='N')]
    topo('refbw.svg', 800, 250, nodes, links, 'Příklad 6: kudy půjde provoz z R1 do sítě X?')


def lab13():
    nodes = {'R1': (180, 100, 'router', 'R1', None), 'R2': (520, 100, 'router', 'R2', None), 'R3': (350, 260, 'router', 'R3', None),
             'L1': (60, 200, 'lan', 'LAN1', '10.1.0.0/24'), 'L2': (650, 200, 'lan', 'LAN2', '10.2.0.0/24'),
             'L3': (350, 380, 'lan', 'LAN3', '10.3.0.0/24')}
    links = [dict(a='R1', b='R2', label='10.0.12.0/30'), dict(a='R2', b='R3', label='10.0.23.0/30', dx=50, dy=0),
             dict(a='R1', b='R3', label='10.0.13.0/30', dx=-50, dy=0), dict(a='R1', b='L1'), dict(a='R2', b='L2'), dict(a='R3', b='L3')]
    topo('lab13.svg', 720, 450, nodes, links, 'Úloha do emulátoru: OSPF area 0 na třech routerech',
         notes=['na každé /30 lince má router s nižším číslem .1, druhý .2; brána v LAN = .1'])


if __name__ == '__main__':
    g.OUT = sys.argv[1]
    mac1()
    mac2()
    domains()
    dot1q()
    vlan(False)
    vlan(True)
    loop()
    stp('stp.svg', STP_IDS['a'], ['4', '4', '4'], title='Příklad 8: zvolte root bridge a zablokovaný port')
    stp('stp-a.svg', STP_IDS['a'], ['4', '4', '4'], roles=[('B', 'D', True), ('R', 'D', False), ('D', 'R', False)],
        title='Řešení 8a: root = SW3 (nejnižší priorita 4096)')
    stp('stp-b.svg', STP_IDS['b'], ['4', '4', '4'], roles=[('R', 'D', False), ('D', 'R', False), ('B', 'D', True)],
        title='Řešení 8b: stejné priority → root = SW2 (nejnižší MAC)')
    stp('stp-c.svg', STP_IDS['a'], ['4', '4', '19'], roles=[('R', 'D', False), ('R', 'D', False), ('D', 'B', True)],
        title='Řešení 8c: SW1–SW3 jen 100 Mb/s → přes SW2 je to levnější')
    g.OUT = sys.argv[2]
    chain13()
    dv5()
    cti()
    ospf(False)
    ospf(True)
    refbw()
    lab13()
