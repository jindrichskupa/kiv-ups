# KIV/UPS cvičení 8. - řešení příkladů

## Plán cvičení

| příklad | min | jádro / bonus |
|---------|-----|---------------|
| úvod a teorie (přehled, CRC postup, schémata) | 6 | jádro |
| 1 - parita znaků | 4 | jádro |
| 2 - dvourozměrná parita | 10 | jádro |
| 3 - kontrolní součet | 6 | jádro |
| 4 - CRC, G = 1011 | 10 | jádro |
| 5 - CRC, G = 10011, ověření, chyba | 14 | jádro |
| 6 - efektivita Stop-and-Wait | 8 | jádro |
| 7 - okno Go-Back-N | 8 | jádro |
| 8 - nakreslete GBN a SR | 12 | jádro |
| rezerva | 12 | |
| 9 - Hammingův kód (7,4) | 10 | bonus |
| 10 - rychlejší linka | 5 | bonus |
| 11 - číslování rámců | 8 | bonus |
| 12 - satelit | 6 | bonus |

Vzorce:

```
t_data = L_data · 8 / v_p        t_ack = L_ack · 8 / v_p        t_d = doba šíření
Stop-and-Wait: e = t_data / (t_data + t_ack + 2 · t_d)
okno Ws:       e = min(1, Ws · t_data / (t_data + t_ack + 2 · t_d))
okno pro 100 %: Ws = ⌈(t_data + t_ack + 2 · t_d) / t_data⌉
číslování k bitů: GBN Ws ≤ 2^k − 1, SR Ws ≤ 2^(k−1)
CRC: M · x^st(G) dělit G (XOR), zbytek připojit; příjemce: zbytek 0 = OK
```

---

## Příklad 1 - parita znaků

```
K = 0x4B = 100 1011  → 4 jedničky → sudá P = 0, lichá P = 1
I = 0x49 = 100 1001  → 3 jedničky → sudá P = 1, lichá P = 0
V = 0x56 = 101 0110  → 4 jedničky → sudá P = 0, lichá P = 1
```

**b)** Dvě chyby změní počet jedniček o 0 nebo ±2 → sudost zůstane, parita sedí, chyba **nezjištěna**.

---

## Příklad 2 - dvourozměrná parita

Odeslaný blok (sudá parita, P = poslední sloupec / řádek):

```
1 0 1 1 | 1
0 1 1 0 | 0
1 1 0 0 | 0
0 0 1 1 | 0
--------+--
0 0 1 0 | 1
```

**a)** Přijatý řádek 2 je `0 1 0 0`: má 1 jedničku, ale P = 0 → nesedí řádek 2. Sloupec 3 má `1 0 0 1` = 2 jedničky, ale P = 1 → nesedí sloupec 3. Chyba je na průsečíku (řádek 2, sloupec 3) → překlopit zpět na 1.

**b)** Řádek 2 přijat jako `0 0 0 0`: parita řádku 0 = P → sedí. Nesedí sloupce 2 a 3. Víme, že chyba je ve sloupcích 2 a 3, ale ne ve kterém řádku (mohly by to být i řádky 1 a 4…) → zjištěno, neopravitelné.

---

## Příklad 3 - kontrolní součet

```
a) 05 + 1A + 20 + 44 = 5 + 26 + 32 + 68 = 131 = 0x83
b) 48 + 65 + 6C + 6C + 6F = 72 + 101 + 108 + 108 + 111 = 500 = 0x1F4 → mod 256 = 0xF4
c) 04 + 1B + 20 + 44 = 4 + 27 + 32 + 68 = 131 = 0x83   (−1 a +1 se vyruší)
   1A + 05 + 20 + 44 = 0x83                            (sčítání je komutativní)
```

Příjemce **chybu nepozná** ani v jednom případě.

---

## Příklad 4 - CRC, G = 1011, M = 110101

Stupeň G = 3 → připíšeme 3 nuly: `110101 000`.

```
110101000
1011
01100
 1011
 01111
  1011
  01000
   1011
   00110
    0000
    01100
     1011
     0111
```

Zbytek `R = 111` → rámec `110101 111`.

**b)** Ověření `110101111`:

```
110101111
1011
01100
 1011
 01111
  1011
  01001
   1011
   00101
    0000
    01011
     1011
     0000
```

Zbytek `000` → bez chyby.

---

## Příklad 5 - CRC, G = 10011, M = 1101011011

Stupeň 4 → připíšeme 4 nuly: `1101011011 0000`.

```
11010110110000
10011
010011
 10011
 000001
  00000
  000010
   00000
   000101
    00000
    001011
     00000
     010110
      10011
      001010
       00000
       010100
        10011
        001110
         00000
         01110
```

Zbytek `1110` → rámec `1101011011 1110`.

**b)** Ověření `11010110111110`:

```
11010110111110
10011
010011
 10011
 000001
  00000
  000010
   00000
   000101
    00000
    001011
     00000
     010111
      10011
      001001
       00000
       010011
        10011
        000000
         00000
         00000
```

Zbytek `0000` → OK.

**c)** Přijato `11010100111110` (7. bit zleva 1 → 0):

```
11010100111110
10011
010011
 10011
 000000
  00000
  000000
   00000
   000001
    00000
    000011
     00000
     000111
      00000
      001111
       00000
       011111
        10011
        011000
         10011
         01011
```

Zbytek `1011 ≠ 0` → chyba zjištěna, rámec se zahodí (a vyžádá se znovu).

---

## Příklad 6 - efektivita Stop-and-Wait

```
t_data = 80 · 8 / 14400  = 640 / 14400 s = 44,4 ms
t_ack  =  1 · 8 / 14400  =   8 / 14400 s = 0,55 ms
a) t_d = 1 ms:   e = 44,4 / (44,4 + 0,55 + 2)   = 44,4 / 46,95  ≐ 0,9456 = 94,56 %
b) t_d = 270 ms: e = 44,4 / (44,4 + 0,55 + 540) = 44,4 / 584,95 ≐ 0,0759 = 7,59 %
```

---

## Příklad 7 - okno Go-Back-N

```
cyklus = 44,4 + 0,55 + 2 · 150 = 344,95 ms
a) e = 44,4 / 344,95 ≐ 12,9 %
b) Ws = 344,95 / 44,4 ≐ 7,77
   Ws = 7: e = 7 · 44,4 / 344,95 = 310,8 / 344,95 ≐ 90,1 %
   Ws = 8: e = 8 · 44,4 / 344,95 = 355,2 / 344,95 > 1 → e = 100 %
```

Proč zdroje (a PDF) zaokrouhlují dolů: ⌊7,77⌋ = 7 je největší okno, pro které vzorec vyjde ≤ 1. Okno 8 už linku zcela vyplní: než odesílatel odvysílá 8 rámců (355,2 ms), vrátí se ACK prvního (344,95 ms) a může pokračovat bez pauzy. Výsledek nad 1 nemá smysl → efektivita je 100 %. Nejmenší okno pro 100 % je tedy ⌈7,77⌉ = 8.

---

## Příklad 8 - GBN a SR

Časování (jednotky): Fi se odešle v čase i, dojde v i + 1,5; ACK se vrací 1,5 jednotky.

**Go-Back-N:**

```
t = 0..3   F0, F1, F2 (ztracen), F3 - okno 0–3 plné
t = 3      ACK0 dojde → okno 1–4 → t = 4: F4
t = 4      ACK1 dojde → okno 2–5 → t = 5: F5
           příjemce F3, F4, F5 zahodí (čeká F2), pokaždé zopakuje ACK1
t = 7      timeout F2 (2 + 5) → znovu F2, F3, F4, F5 (t = 7, 8, 9, 10)
celkem: F0 F1 F2 F3 F4 F5 + F2 F3 F4 F5 = 10 vysílání
```

**Selective Repeat:**

```
t = 0..5   stejně jako GBN, ale příjemce F3, F4, F5 uloží a potvrdí ACK3, ACK4, ACK5
t = 7      timeout F2 → znovu jen F2
t = 8,5    F2 dojde → příjemce předá F2–F5 aplikaci, pošle ACK2
t = 10     ACK2 dojde → okno se posune na 6–9 → F6, F7, …
celkem do doručení F0–F5: 6 + 1 = 7 vysílání
```

---

## Příklad 9 - Hammingův kód (7,4) (bonus)

Pozice: `1 2 3 4 5 6 7` = `p1 p2 d1 p4 d2 d3 d4`.

```
1011: d1 = 1, d2 = 0, d3 = 1, d4 = 1
p1 = d1 ⊕ d2 ⊕ d4 = 1 ⊕ 0 ⊕ 1 = 0
p2 = d1 ⊕ d3 ⊕ d4 = 1 ⊕ 1 ⊕ 1 = 1
p4 = d2 ⊕ d3 ⊕ d4 = 0 ⊕ 1 ⊕ 1 = 0
→ 0 1 1 0 0 1 1 = 0110011

0110: d1 = 0, d2 = 1, d3 = 1, d4 = 0
p1 = 0 ⊕ 1 ⊕ 0 = 1, p2 = 0 ⊕ 1 ⊕ 0 = 1, p4 = 1 ⊕ 1 ⊕ 0 = 0
→ 1 1 0 0 1 1 0 = 1100110
```

**b)** Přijato `0110111` (b1 … b7):

```
s1 = b1 ⊕ b3 ⊕ b5 ⊕ b7 = 0 ⊕ 1 ⊕ 1 ⊕ 1 = 1
s2 = b2 ⊕ b3 ⊕ b6 ⊕ b7 = 1 ⊕ 1 ⊕ 1 ⊕ 1 = 0
s4 = b4 ⊕ b5 ⊕ b6 ⊕ b7 = 0 ⊕ 1 ⊕ 1 ⊕ 1 = 1
s4 s2 s1 = 101 = 5 → chyba na pozici 5 (d2)
oprava: 0110011 → data d1 d2 d3 d4 = 1011
```

---

## Příklad 10 - rychlejší linka (bonus)

```
t_data = 1000 · 8 / 1 000 000 = 8 ms
t_ack  =   64 · 8 / 1 000 000 = 0,512 ms
cyklus = 8 + 0,512 + 20 = 28,512 ms
a) e = 8 / 28,512 ≐ 28,1 %
b) Ws = ⌈28,512 / 8⌉ = ⌈3,56⌉ = 4
```

---

## Příklad 11 - číslování rámců (bonus)

**a)** k = 3 → čísla 0–7. GBN: Ws ≤ 2³ − 1 = 7. SR: Ws ≤ 2² = 4.

**b)** GBN, Ws = 8: odesílatel pošle F0 … F7, příjemce všechny přijme a čeká další F0 (nový cyklus). Všechny ACK se ztratí → odesílateli vyprší timeout → pošle znovu staré F0. Příjemce čeká "F0" → přijme duplicitu jako nová data. S Ws = 7 by čekal F7 a staré F0 by poznal.

Pro SR (Ws = Wr = 5 při k = 3): příjemce po přijetí F0–F4 čeká okno 5, 6, 7, 0, 1. Opakované staré F0 padne do okna → přijato jako nové. Při Ws = Wr ≤ 4 se staré a nové okno nepřekrývají.

---

## Příklad 12 - satelit (bonus)

```
cyklus = 8 + 0,512 + 2 · 270 = 548,512 ms
a) e = 8 / 548,512 ≐ 1,46 %
b) Ws = ⌈548,512 / 8⌉ = ⌈68,56⌉ = 69 rámců
c) GBN: 2^k − 1 ≥ 69 → 2^7 − 1 = 127 ≥ 69 → k = 7
   SR:  2^(k−1) ≥ 69 → 2^7 = 128 ≥ 69     → k = 8
```
