"""Generate SVG figures for KIV/UPS ex04 (application protocol). Usage: python3 gen_svg04.py <out_dir>"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_svg as g  # noqa: E402
from gen_svg import text, INK, MUTED, BLUE, RED, GREEN  # noqa: E402

g.OUT = sys.argv[1]
save = g.save
GRID = '#d0d7de'
FILL = {'hdr': '#ffebe9', 'len': '#fff8c5', 'val': '#ddf4ff', 'key': '#dafbe1', 'rest': '#f6f8fa'}
DEFS = (f'<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">'
        f'<path d="M0,0 L10,5 L0,10 z" fill="{INK}"/></marker>'
        f'<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">'
        f'<path d="M0,0 L10,5 L0,10 z" fill="{RED}"/></marker></defs>')
MONO = 'font-family="Menlo, Consolas, monospace"'


def state(x, y, label, w=170, h=46, fill='#ddf4ff', bold=True):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{BLUE}" stroke-width="2"/>'
            + text(x + w / 2, y + h / 2 + 5, label, 14, INK, extra='font-weight="bold"' if bold else ''))


def arrow(pts, label=None, lx=None, ly=None, color=INK, dashed=False, anchor='middle', size=12):
    d = 'M' + ' L'.join(f'{x},{y}' for x, y in pts)
    m = 'arr' if color == RED else 'ar'
    out = f'<path d="{d}" fill="none" stroke="{color}" stroke-width="1.6" marker-end="url(#{m})"{" stroke-dasharray=\"6 4\"" if dashed else ""}/>'
    if label:
        out += text(lx, ly, label, size, color, anchor)
    return out


def curve(d, label=None, lx=None, ly=None, color=INK, dashed=False, anchor='middle', size=12):
    m = 'arr' if color == RED else 'ar'
    out = f'<path d="{d}" fill="none" stroke="{color}" stroke-width="1.6" marker-end="url(#{m})"{" stroke-dasharray=\"6 4\"" if dashed else ""}/>'
    if label:
        out += text(lx, ly, label, size, color, anchor)
    return out


def chat_states():
    b = [DEFS]
    b.append(text(60, 108, 'TCP spojení', 12, MUTED) + text(60, 124, 'navázáno', 12, MUTED))
    b.append(arrow([(30, 140), (118, 140)]))
    b.append(state(120, 117, 'CONNECTED'))
    b.append(arrow([(290, 140), (398, 140)], 'NickMessage', 344, 130))
    b.append(state(400, 117, 'CHATTING'))
    b.append(curve('M455,117 C440,50 530,50 515,117', 'ChatMessage', 485, 58))
    b.append(curve('M455,163 C440,230 530,230 515,163', 'NickMessage', 485, 232))
    b.append(arrow([(570, 140), (678, 140)], 'ExitMessage', 624, 130))
    b.append(state(680, 117, 'DISCONNECTED'))
    b.append(arrow([(850, 140), (900, 140)]))
    b.append(text(900, 108, 'TCP spojení', 12, MUTED, 'end') + text(900, 124, 'ukončeno', 12, MUTED, 'end'))
    b.append(curve('M205,163 C205,290 765,290 765,165', 'TCP spojení spadlo (recv vrátí 0 / −1) – z libovolného stavu', 485, 282,
                   color=RED, dashed=True, size=12))
    save('chat-states.svg', 920, 300, '\n'.join(b))


def game_states():
    b = [DEFS, text(20, 26, 'Řešení 10: stavový diagram piškvorek (jedna z možných variant)', 16, INK, 'start', 'font-weight="bold"'),
         '<g transform="translate(0,40)">']
    b.append(state(40, 70, 'CONNECTED'))
    b.append(state(330, 70, 'LOBBY'))
    b.append(state(620, 70, 'WAITING'))
    # IN_GAME group
    b.append(f'<rect x="300" y="190" width="520" height="130" rx="14" fill="#f6f8fa" stroke="{MUTED}" stroke-dasharray="6 4"/>')
    b.append(text(808, 212, 'IN_GAME', 13, MUTED, 'end', 'font-weight="bold"'))
    b.append(state(330, 240, 'MY_TURN', fill='#dafbe1'))
    b.append(state(620, 240, 'OPPONENT_TURN', fill='#fff8c5'))
    b.append(state(330, 400, 'GAME_OVER'))
    b.append(state(40, 400, 'DISCONNECTED', fill='#ffebe9'))
    # transitions
    b.append(curve('M90,70 C70,20 160,20 140,70', 'LOGIN chybný → LOGIN_ERR', 115, 30, size=11))
    b.append(arrow([(210, 93), (328, 93)], 'LOGIN ok', 269, 84))
    b.append(arrow([(500, 85), (618, 85)], 'CREATE / JOIN', 559, 76))
    b.append(arrow([(618, 103), (500, 103)], 'LEAVE', 559, 121))
    b.append(arrow([(705, 116), (705, 238)], 'soupeř přišel', 712, 175, anchor='start'))
    b.append(arrow([(500, 255), (618, 255)], 'MOVE ok', 559, 247))
    b.append(arrow([(618, 275), (500, 275)], 'soupeř: MOVE', 559, 295))
    b.append(curve('M360,240 C340,190 420,190 400,240', 'MOVE špatný → MOVE_ERR', 380, 186, size=11))
    b.append(arrow([(415, 320), (415, 398)], 'výhra / prohra / remíza', 424, 362, anchor='start'))
    b.append(curve('M330,410 C250,380 300,170 395,118', 'REMATCH / LEAVE', 250, 300, anchor='end'))
    b.append(curve('M300,300 C200,330 160,360 125,398', 'PING timeout (15 s)', 190, 345, color=RED, dashed=True, anchor='end'))
    b.append(curve('M210,435 C270,470 520,470 700,322', 'LOGIN stejné jméno do 60 s → obnovit hru (RECONNECT)', 470, 480,
                   color=GREEN, size=12))
    b.append(text(20, 520, 'Z libovolného stavu: PING ← → PONG; neznámá / nevalidní zpráva → ERR, po 3 chybách odpojit.', 13, MUTED, 'start'))
    b.append('</g>')
    save('game-states.svg', 840, 580, '\n'.join(b))


def segs_row(y, segs, x0=150, cw=12.5, labels=True):
    out, x = [], x0
    for s_, kind, lab in segs:
        w = len(s_) * cw
        out.append(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="30" fill="{FILL[kind]}" stroke="{GRID}"/>')
        out.append(text(x + w / 2, y + 20, s_.replace(' ', '␣'), 15, INK, extra=MONO))
        if labels and lab:
            out.append(text(x + w / 2, y + 48, lab, 10, MUTED))
        x += w
    return out, x


def uer_layout():
    segs = [('KIVUPS', 'hdr', 'magic'), ('chat', 'hdr', 'command'), ('0042', 'len', 'totalLength'),
            ('014', 'len', 'délka'), ('Chatova zprava', 'val', 'message'), ('02', 'len', 'počet'),
            ('color', 'key', 'key'), ('04', 'len', 'dél.'), ('blue', 'val', 'value'),
            ('tsize', 'key', 'key'), ('05', 'len', 'dél.'), ('large', 'val', 'value')]
    b = [text(20, 26, 'Řešení 1: ChatMessage podle UER (14 B hlavička + 42 B tělo = 56 B)', 16, INK, 'start', 'font-weight="bold"')]
    cw = 14
    row, xe = segs_row(50, segs, x0=20, cw=cw)
    b += row
    xh = 20 + 14 * cw
    b.append(f'<path d="M20,112 v6 H{xh} v-6" fill="none" stroke="{RED}"/>' + text((20 + xh) / 2, 134, 'hlavička 14 B', 12, RED))
    b.append(f'<path d="M{xh},112 v6 H{xe:.0f} v-6" fill="none" stroke="{BLUE}"/>' + text((xh + xe) / 2, 134, 'tělo 42 B = totalLength', 12, BLUE))
    save('uer-layout.svg', int(xe) + 20, 150, '\n'.join(b))


def buffer():
    conn, chat = 'KIVUPSconn000604Pepa', 'KIVUPSchat0020005Ahoj!01color03red'
    b = [text(20, 26, 'Řešení 3: stav bufferu parseru po každém recv()', 16, INK, 'start', 'font-weight="bold"')]
    rows = [
        ('po recv 1', [('KIVUPSco', 'rest', None)], '8 B &lt; 14 B hlavičky → čekej', MUTED),
        ('po recv 2', [(conn, 'val', 'conn: 14 + 6 = 20 B → hotová zpráva'), ('KIVUPSchat00', 'rest', 'zbytek 12 B → čekej')],
         '1 zpráva ven, 12 B zůstává', GREEN),
        ('po recv 3', [(chat, 'val', 'chat: 14 + 20 = 34 B → hotová zpráva')], '1 zpráva ven, buffer prázdný', GREEN),
    ]
    y = 50
    for lab, segs, note, col in rows:
        b.append(text(20, y + 20, lab, 13, INK, 'start', 'font-weight="bold"'))
        row, xe = segs_row(y, segs, x0=110, cw=11)
        b += row
        b.append(text(110, y + 66, note, 13, col, 'start'))
        y += 92
    b.append(text(20, y + 6, 'recv 1 = "KIVUPSco", recv 2 = "nn000604PepaKIVUPSchat00", recv 3 = "20005Ahoj!01color03red"', 12, MUTED, 'start', MONO))
    save('buffer.svg', 110 + 34 * 11 + 260, y + 20, '\n'.join(b))


if __name__ == '__main__':
    chat_states()
    game_states()
    uer_layout()
    buffer()
