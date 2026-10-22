"""Generate SVG figures for KIV/UPS ex09 + ex10 (topologies). Usage: python3 gen_svg09.py <ex09_images> <ex10_images>"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_svg as g  # noqa: E402
from gen_svg import text, INK, MUTED, BLUE, RED, GREEN  # noqa: E402

OUT09, OUT10 = sys.argv[1], sys.argv[2]
LINE = '#57606a'


def save(out, name, w, h, body):
    g.OUT = out
    g.save(name, w, h, '\n'.join(body))


def line(x1, y1, x2, y2, color=LINE, width=2, dash=''):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"{d}/>'


def cloud(cx, cy, label, sub='', w=120, h=70, fill='#f6f8fa'):
    rx, ry = w / 2, h / 2
    bumps = [(-0.55, 0.1, 0.42), (-0.2, -0.35, 0.45), (0.25, -0.3, 0.42), (0.55, 0.08, 0.4), (0.15, 0.3, 0.45), (-0.25, 0.3, 0.42)]
    out = [f'<g fill="{fill}" stroke="{LINE}" stroke-width="1.5">']
    for dx, dy, r in bumps:
        out.append(f'<ellipse cx="{cx + dx * rx:.1f}" cy="{cy + dy * ry:.1f}" rx="{r * rx:.1f}" ry="{r * ry * 1.2:.1f}"/>')
    out.append('</g>')
    out.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx * 0.75:.1f}" ry="{ry * 0.6:.1f}" fill="{fill}"/>')
    out.append(text(cx, cy - 2 if sub else cy + 5, label, 15, INK, extra='font-weight="bold"'))
    if sub:
        out.append(text(cx, cy + 16, sub, 13, MUTED))
    return out


def router(cx, cy, label):
    r = 24
    out = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#ddf4ff" stroke="{BLUE}" stroke-width="2"/>']
    for dx, dy in ((1, 1), (-1, -1), (1, -1), (-1, 1)):
        x1, y1 = cx + dx * 5, cy + dy * 5
        x2, y2 = cx + dx * 15, cy + dy * 15
        if dx == dy:  # sipky ven
            out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{BLUE}" stroke-width="2.5"/>')
        else:  # sipky dovnitr
            out.append(f'<line x1="{x2}" y1="{y2}" x2="{x1}" y2="{y1}" stroke="{BLUE}" stroke-width="2.5"/>')
    out.append(text(cx, cy + r + 18, label, 14, INK, extra='font-weight="bold"'))
    return out


def pc(cx, cy, label):
    return [f'<rect x="{cx - 22}" y="{cy - 18}" width="44" height="30" rx="3" fill="#ddf4ff" stroke="{BLUE}" stroke-width="2"/>',
            f'<rect x="{cx - 8}" y="{cy + 12}" width="16" height="6" fill="{BLUE}"/>',
            f'<rect x="{cx - 16}" y="{cy + 18}" width="32" height="3" fill="{BLUE}"/>',
            text(cx, cy + 40, label, 14, INK, extra='font-weight="bold"')]


def server(cx, cy, label):
    out = [f'<rect x="{cx - 18}" y="{cy - 30}" width="36" height="60" rx="3" fill="#ddf4ff" stroke="{BLUE}" stroke-width="2"/>']
    for k in range(4):
        out.append(f'<line x1="{cx - 10}" y1="{cy - 20 + k * 9}" x2="{cx + 10}" y2="{cy - 20 + k * 9}" stroke="{BLUE}" stroke-width="2"/>')
    out.append(text(cx, cy + 50, label, 14, INK, extra='font-weight="bold"'))
    return out


def lab(x, y, s, anchor='middle', color=MUTED, size=13):
    return text(x, y, s, size, color, anchor, 'font-family="monospace"')


# ---------- ex09 ----------

def vlsm_pdf():
    b = [text(20, 26, 'Firma 147.92.0.0/16: 2 budovy, 2 routery, připojení do internetu z R2', 16, INK, 'start', 'font-weight="bold"')]
    r1, r2 = (260, 200), (500, 200)
    b += [line(*r1, *r2), line(*r2, 680, 200), line(*r1, 170, 105), line(*r1, 170, 295), line(*r2, 590, 105), line(*r2, 590, 295)]
    b += cloud(150, 90, 'A', '134 + 65 PC') + cloud(150, 310, 'B', '40 + 10 PC') + cloud(610, 90, 'C', '15 + 5 PC') + cloud(610, 310, 'D', '5 + 2 PC')
    b += cloud(740, 200, 'Internet', w=110, h=60)
    b += router(*r1, 'R1') + router(*r2, 'R2')
    b.append(text(380, 188, 'E (2 adresy)', 13, RED, extra='font-weight="bold"'))
    save(OUT09, 'vlsm-pdf.svg', 820, 370, b)


def vlsm_new(solution=False):
    t = 'Řešení 7: rozvržení 192.168.100.0/24' if solution else 'Příklad 7: síť 192.168.100.0/24'
    b = [text(20, 26, t, 16, INK, 'start', 'font-weight="bold"')]
    r1, r2, isp = (300, 210), (560, 210), (300, 60)
    b += [line(*r1, *r2), line(*r1, *isp), line(*r1, 200, 120), line(*r1, 200, 300), line(*r2, 650, 120), line(*r2, 650, 300)]
    b += cloud(180, 110, 'A', '100 PC') + cloud(180, 315, 'B', '50 PC') + cloud(680, 110, 'C', '20 PC') + cloud(680, 315, 'D', '10 PC')
    b += cloud(300, 60, 'ISP', w=100, h=50)
    b += router(*r1, 'R1') + router(*r2, 'R2')
    b.append(text(430, 198, 'L1 (P2P)', 13, RED, extra='font-weight="bold"'))
    b.append(text(312, 125, 'L2 (P2P)', 13, RED, 'start', 'font-weight="bold"'))
    if solution:
        b += [lab(200, 160, '.0/25  gw .1', 'start', BLUE), lab(205, 268, '.128/26  gw .129', 'start', BLUE),
              lab(530, 160, '.192/27  gw .193', 'start', BLUE), lab(540, 268, '.224/28  gw .225', 'start', BLUE),
              lab(330, 232, '.241', 'start', GREEN), lab(530, 232, '.242', 'end', GREEN),
              lab(312, 145, '.245 (R1) ↔ .246 (ISP)', 'start', GREEN), lab(430, 248, '.240/30', 'middle', GREEN),
              lab(312, 165, '.244/30', 'start', GREEN)]
    save(OUT09, 'vlsm-new-solution.svg' if solution else 'vlsm-new.svg', 780, 380, b)


# ---------- ex10 ----------

def path10():
    b = [text(20, 26, 'Otevřu v prohlížeči http://www.stranka.cz (PC připojené kabelem)', 16, INK, 'start', 'font-weight="bold"')]
    p, r1, cl, r2, s = (90, 190), (250, 190), (470, 190), (690, 190), (840, 190)
    b += [line(*p, *r1), line(*r1, cl[0] - 60, 190), line(cl[0] + 60, 190, *r2), line(*r2, *s)]
    b += pc(*p, 'PC') + router(*r1, 'R1 (NAT)') + cloud(*cl, 'Internet', '5 routerů', w=130, h=80) + router(*r2, 'R2') + server(*s, 'server')
    b += [lab(90, 120, '192.168.0.10/24'), lab(90, 138, 'MAC 02:..:0A'),
          lab(170, 175, '.0.1/24'), lab(170, 245, 'MAC 02:..:01'),
          lab(282, 175, '84.14.25.201/16', 'start'), lab(282, 245, 'MAC 02:..:02', 'start'),
          lab(660, 175, '47.85.0.1/16', 'end'), lab(660, 245, 'MAC 02:..:21', 'end'),
          lab(840, 120, '47.85.1.25/16'), lab(840, 138, 'MAC 02:..:25'),
          text(840, 100, 'HTTP :80, www.stranka.cz', 13, INK)]
    b += [text(170, 300, 'úsek ①', 14, RED, extra='font-weight="bold"'), text(470, 300, 'úsek ② (internet)', 14, RED, extra='font-weight="bold"'),
          text(765, 300, 'úsek ③', 14, RED, extra='font-weight="bold"')]
    b.append(text(20, 335, 'DNS resolver: 192.168.0.1 (R1). MAC adresy zkrácené: 02:00:00:00:00:XX.', 13, MUTED, 'start'))
    save(OUT10, 'path.svg', 930, 350, b)


def nat_two():
    b = [text(20, 26, 'Dva počítače za jedním NATem, oba na stejný server', 16, INK, 'start', 'font-weight="bold"')]
    b += [line(90, 90, 260, 160), line(90, 230, 260, 160), line(260, 160, 470, 160), line(560, 160, 700, 160)]
    b += pc(90, 90, 'PC1 192.168.0.10') + pc(90, 230, 'PC2 192.168.0.11') + router(260, 160, 'R1 84.14.25.201')
    b += cloud(515, 160, 'Internet', w=110, h=60) + server(720, 160, 'server 47.85.1.25:80')
    b += [lab(160, 105, ':51000', 'start', BLUE), lab(160, 222, ':51000', 'start', BLUE),
          text(370, 125, '?', 22, RED, extra='font-weight="bold"')]
    save(OUT10, 'nat-two.svg', 820, 290, b)


def port_fwd():
    b = [text(20, 26, 'Herní server doma: jak se na něj dostane kamarád z internetu?', 16, INK, 'start', 'font-weight="bold"')]
    b += [line(110, 150, 300, 150), line(300, 150, 470, 150), line(570, 150, 690, 150)]
    b += server(110, 150, 'server 192.168.0.50') + router(300, 150, 'R1 84.14.25.201') + cloud(520, 150, 'Internet', w=110, h=60) + pc(710, 150, 'kamarád')
    b += [lab(110, 85, 'poslouchá :4242'), lab(710, 95, '203.0.113.7')]
    save(OUT10, 'port-forward.svg', 800, 250, b)


if __name__ == '__main__':
    vlsm_pdf()
    vlsm_new()
    vlsm_new(True)
    path10()
    nat_two()
    port_fwd()
