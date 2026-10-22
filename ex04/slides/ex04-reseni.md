# KIV/UPS cvičení 4. - řešení příkladů

## Plán cvičení

| příklad | min | jádro / bonus |
|---------|-----|---------------|
| úvod a teorie (hlavička, TLV vs. oddělovače, UER, stavový diagram) | 10 | jádro |
| 1 - serializace ChatMessage | 8 | jádro |
| 2 - deserializace | 5 | jádro |
| 3 - TCP fragmentace | 8 | jádro |
| 4 - escapování | 7 | jádro |
| 5 - co se smí kdy (stavový diagram) | 7 | jádro |
| úkol - chat klient | 30 | jádro |
| rezerva, diskuse | 15 | jádro |
| 6 - volitelné pole | 5 | bonus |
| 7 - TLV | 5 | bonus |
| 8 - text vs. binár | 5 | bonus |
| 9 - ASN.1 MoveMessage | 5 | bonus |
| 10 - stavový diagram hry | 10 | bonus (domácí úkol) |
| 11 - tabulka stav × zpráva | 8 | bonus |
| 12 - validace | 8 | bonus |
| 13 - keepalive | 5 | bonus |

Pravidla UER:

```
pevný řetězec / výčet stejně dlouhých řetězců  → zapsat tak, jak je
INTEGER(p..q)                                  → číslo doplněné nulami na šířku podle q
IA5String (SIZE(p..q))                         → délka (šířka podle q) + řetězec
SEQUENCE (SIZE(p..q)) OF X                     → počet prvků (šířka podle q) + prvky
šířka: q < 10 → 1, q < 100 → 2, q < 1000 → 3, q < 10 000 → 4
hlavička = magic (6) + command (4) + totalLength (4) = 14 B, totalLength = délka těla bez hlavičky
```

---

## Příklad 1 - serializace ChatMessage

Pole po řadě podle definice:

```
magic        "KIVUPS"                      6 B
command      "chat"                        4 B
totalLength  INTEGER(0..9999) → 4 číslice  4 B  (doplníme na konci)
message      SIZE(1..999) → délka 3 číslice: "014" + "Chatova zprava"   3 + 14 = 17 B
parameters   SIZE(0..10)  → q = 10, počet 2 číslice: "02"                2 B
  key        výčet "color" | "tsize" (oba 5 znaků) → pevně: "color"      5 B
  value      SIZE(1..99) → "04" + "blue"                                 6 B
  key        "tsize"                                                     5 B
  value      "05" + "large"                                              7 B
```

Tělo: 17 + 2 + 5 + 6 + 5 + 7 = **42 B** → `totalLength = 0042`, celá zpráva 14 + 42 = **56 B**.

```
KIVUPSchat0042014Chatova zprava02color04bluetsize05large
```

V podkladech je `KIVUPSchat00410014Chatova zprava2color04bluesize05large` - délka zprávy má 4 číslice místo 3, počet parametrů 1 číslici místo 2 (q = 10 už nesplňuje q < 10) a klíč `size` místo `tsize`. Tělo pak má 41 B, což odpovídá uvedenému `totalLength = 41`.

---

## Příklad 2 - deserializace

**a)** `KIVUPSexit001311Jdu na obed`

```
KIVUPS | exit | 0013 → tělo 13 B
ExitMessage: reason SIZE(1..99) → 2 číslice: "11" → 11 znaků "Jdu na obed"
kontrola: 2 + 11 = 13 ✓
```

**b)** `KIVUPSchat0020005Ahoj!01color03red`

```
KIVUPS | chat | 0020 → tělo 20 B
message: "005" → "Ahoj!"           3 + 5 = 8
parameters: "01" → 1 parametr      2
  key "color"                      5
  value "03" → "red"               2 + 3 = 5
kontrola: 8 + 2 + 5 + 5 = 20 ✓
```

**c)** `KIVUPSconn000604Pepa` → `conn`, tělo 6 B, nick `04` → `Pepa` (NickType SIZE(4..32) → 2 číslice).

---

## Příklad 3 - TCP fragmentace

Parser drží buffer a opakuje: mám ≥ 14 B? → přečti `totalLength` → mám ≥ 14 + totalLength B? → vyjmi zprávu, zbytek nech v bufferu.

```
po recv 1: "KIVUPSco"                                  8 B  < 14 → čekej
po recv 2: "KIVUPSconn000604PepaKIVUPSchat00"         32 B
           hlavička conn, totalLength 6 → potřebuji 20 B, mám 32 → zpráva conn ven
           zbytek "KIVUPSchat00"                       12 B < 14 → čekej
po recv 3: "KIVUPSchat0020005Ahoj!01color03red"       34 B
           hlavička chat, totalLength 20 → potřebuji 34 B, mám 34 → zpráva chat ven
           buffer prázdný
```

**c)** Server, který bere `recv()` = zpráva, by recv 1 odmítl jako krátký a recv 2 jako nevalidní (za koncem `conn` jsou další bajty) - odpojil by správně fungujícího klienta.

---

## Příklad 4 - escapování

Kódování: každý `\` → `\\`, každý `|` → `\|`, každý konec řádku v textu → `\n` (dva znaky), na konec zprávy skutečný konec řádku `⏎`.

```
a) a|b        → CHAT|a\|b⏎
b) C:\temp    → CHAT|C:\\temp⏎
c) ahoj⏎cau   → CHAT|ahoj\ncau⏎
```

**d)** Dekódování znak po znaku `CHAT|a\\|b⏎`:

```
C H A T        → pole 1 "CHAT"
|              → oddělovač
a              → pole 2 "a"
\\             → escapovaný znak "\" → pole 2 "a\"
|              → oddělovač (není před ním neescapovaný "\")
b              → pole 3 "b"
⏎              → konec zprávy
```

Výsledek: 3 pole `CHAT`, `a\`, `b`.

---

## Příklad 5 - co se smí kdy

- a) CONNECTED → jediný přechod je `NickMessage`.
- b) `ChatMessage` v CONNECTED je chyba stavu: syntaxe je v pořádku, ale klient ještě nemá jméno. Server odpoví chybou nebo klienta odpojí (podle protokolu).
- c) `ExitMessage` → DISCONNECTED: rozeslat ostatním `disc` s jeho jménem, uvolnit jméno, smazat buffer klienta, `close()`.
- d) Sémantická chyba - zpráva je syntakticky i stavově v pořádku, ale obsah nesedí (`oldNick` není jeho jméno). Server musí pamatovat, kdo je kdo, a nevěřit klientovi.

---

## Úkol - chat klient

Kostra klienta (pseudokód):

```
sock = connect(server, 4242)
send(sock, "KIVUPS" + "nick" + len4(body) + body)       # body = len2(nick) + nick
loop:
    buf += recv(sock)
    while len(buf) >= 14 and len(buf) >= 14 + int(buf[10:14]):
        msg = buf[:14 + int(buf[10:14])]; buf = buf[len(msg):]
        zpracuj(msg)
```

Kontrola ručně: `printf 'KIVUPSnick000604PepaKIVUPSchat0010005Ahoj!00' | nc <server> 4242` - chat má tělo `005Ahoj!` (8) + `00` (žádné parametry, 2) = 10 B.

---

## Příklad 6 - volitelné pole (bonus)

```
a) newNick "Pepa123": SIZE(4..32) → "07Pepa123" (9 B)
   KIVUPSnick0009 07Pepa123            → KIVUPSnick000907Pepa123
b) + oldNick "Franta": "06Franta" (8 B) → tělo 17 B
   KIVUPSnick001707Pepa12306Franta
```

**c)** Po přečtení `newNick` porovnat přečtené bajty s `totalLength`: zbývá 0 → `oldNick` chybí, zbývá víc → čteme `oldNick`.

---

## Příklad 7 - TLV (bonus)

```
a) "03" → 3 znaky "Eva"; "08" → 8 znaků "12345678"
b) "03" + "Jan" + "08" + "heslo123" = 03Jan08heslo123
c) 2 číslice → max. 99 znaků → heslo 120 znaků odmítnout (nebo délka na 3 číslice)
d) typ 0x01, délka 3 = 0x0003 (big-endian: 00 03), "Eva" = 45 76 61
   → 01 00 03 45 76 61
```

---

## Příklad 8 - text vs. binár (bonus)

```
a) "MOVE" 4 + "|" 1 + "7" 1 + "|" 1 + "12" 2 + "|" 1 + "1" 1 + "⏎" 1 = 12 B
b) opkód 1 + x 1 + y 1 + hráč 1 = 4 B
c) 15 hodnot ≤ 16 = 2^4 → 4 bity; 2 hráči → 1 bit; 4 + 4 + 1 = 9 bitů → 2 B
```

**d)** Textový: ladí se `nc` a `tcpdump -A`, nehrozí endianita ani zarovnání struktur. Úspora 8 B na tahu je při několika tazích za minutu zanedbatelná.

---

## Příklad 9 - ASN.1 MoveMessage (bonus)

```
MessageType ::= IA5String("nick" | "chat" | "conn" | "disc" | "exit" | "move")

MoveMessage ::= SEQUENCE {
  header  MessageHeader{{"move"}},
  x       INTEGER(0..14),
  y       INTEGER(0..14)
}
```

Serializace `x = 7, y = 12`: `INTEGER(0..14)` → q = 14 < 100 → 2 číslice → tělo `0712` (4 B):

```
KIVUPSmove00040712
```

---

## Příklad 10 - stavový diagram hry (bonus)

Obrázek `images/game-states.svg`. Stavy: CONNECTED → (LOGIN ok) LOBBY → (CREATE/JOIN) WAITING → (soupeř přišel) IN_GAME {MY_TURN ⇄ OPPONENT_TURN} → (výhra/prohra/remíza) GAME_OVER → (REMATCH/LEAVE) LOBBY. Chybný LOGIN a chybný MOVE vrací chybu a stav se nemění. PING timeout → DISCONNECTED; LOGIN stejným jménem do 60 s → zpět do rozehrané hry.

Řešení není jediné - důležité je, aby každý stav měl jasný výčet povolených zpráv a aby byl vyřešený výpadek.

---

## Příklad 11 - tabulka stav × zpráva (bonus)

Viz slide Řešení 11. Každá buňka "chyba" = ERR + počítadlo chyb; LEAVE ve hře = vzdání (soupeř vyhrává); PING je povolený vždy.

---

## Příklad 12 - validace (bonus)

```
a) magic "KIVUPX" ≠ "KIVUPS"           → odpojit hned
b) "foo!" není v MessageType           → ERR, chyby + 1 (délka 0000 je čitelná, zprávu lze přeskočit)
c) totalLength "-005" není číslo       → konec zprávy nelze určit → odpojit
d) max. tělo ChatMessage:
   message 3 + 999, parameters 2 + 10 · (key 5 + délka 2 + value 99)
   = 1002 + 2 + 1060 = 2064 B < 9999   → odpojit hned (nečekat, nealokovat 9999 B)
e) "02Jo": NickType SIZE(4..32)         → ERR
f) totalLength 6, ale "07Pepa123" = 9 B → po 6 B by parser četl "a123" jako začátek další zprávy → odpojit
```

---

## Příklad 13 - keepalive (bonus)

```
a) klient: PING každých 5 s; server: PONG; server odpojí po 15 s bez jakékoli zprávy
b) poslední zpráva v čase t → odpojení v t + 15 s (výpadek těsně po PINGu: až ~15 s, nejhůř ~20 s od posledního PINGu)
c) TCP_KEEPALIVE (Linux výchozí): 7200 s + 9 · 75 s = 7875 s ≈ 2 h 11 min
```

**d)** Pozastavit hru, oznámit soupeři, držet stav (např. 60 s). Přihlášení stejným jménem → RECONNECT do rozehrané hry, po vypršení hra končí (kontumace).
