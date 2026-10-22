# KIV/UPS cvičení 6. - řešení příkladů

Vzorce a pravidla:

```
v_p = v_m · log2(N)          bitová rychlost [b/s] = modulační rychlost [Bd] × bitů na symbol
NRZ-L:     1 = H, 0 = L
NRZ-M:     1 = přechod na začátku bitu, 0 = beze změny        (NRZ-S naopak)
RZ:        1 = +, 0 = −, v polovině bitu návrat na 0
Manchester (IEEE 802.3): 1 = L→H uprostřed, 0 = H→L uprostřed
Dif. Manchester: uprostřed vždy přechod; 0 = změna na začátku, 1 = bez změny
MLT-3:     1 = posun na další úroveň v cyklu 0 → + → 0 → −, 0 = beze změny
y(t) = A · sin(2π · f · t + φ)
```

Obrázky řešení jsou ve slidech (`images/ex*-solution.svg`).

Plán cvičení (90 min):

| příklad | min | |
|---|---|---|
| 1 | 10 | jádro |
| 2 | 6 | jádro |
| 3 | 6 | jádro |
| 4 | 8 | jádro |
| 5 | 10 | jádro |
| 6 | 8 | jádro |
| 7 | 6 | jádro |
| 8 | 5 | jádro |
| 9 | 5 | jádro |
| 10 | 6 | jádro |
| 11 | - | bonus |
| 12 | - | bonus |
| 13 | - | bonus |

---

## Příklad 1 - nakreslete 0100 1110

Postup po bitech (výchozí úroveň L):

| bit | 0 | 1 | 0 | 0 | 1 | 1 | 1 | 0 |
|-----|---|---|---|---|---|---|---|---|
| NRZ-L | L | H | L | L | H | H | H | L |
| NRZ-M | L | **H** | H | H | **L** | **H** | **L** | L |
| RZ | −,0 | +,0 | −,0 | −,0 | +,0 | +,0 | +,0 | −,0 |
| Manchester | H→L | L→H | H→L | H→L | L→H | L→H | L→H | H→L |
| Dif. M. | H→L | L→H | L→H | L→H | H→L | L→H | H→L | H→L |

Dif. Manchester krok po kroku: před prvním bitem je L. Bit 0 → změna na začátku (L→H), první polovina H, uprostřed přechod → L. Bit 1 → beze změny, první polovina L, uprostřed → H. Bit 0 → změna (H→L), L, uprostřed → H. A tak dál.

---

## Příklad 2 - dekódujte

**a) Manchester (802.3):** čteme jen přechody uprostřed bitů: L→H = 1, H→L = 0.

```
L→H L→H H→L L→H H→L H→L H→L L→H
 1   1   0   1   0   0   0   1    = 1101 0001b = 0xD1
```

**b) NRZ-M, výchozí L:** přechod na začátku bitu = 1, beze změny = 0.

```
úroveň: L   H   L   L   H   L   L   L
změna:  ne  ano ano ne  ano ano ne  ne
bit:    0   1   1   0   1   1   0   0    = 0110 1100b = 0x6C
```

---

## Příklad 3 - frekvence a pásmo (10 Mb/s)

**a)** NRZ-L: 1 bit = 1 symbol → 10 MBd. Manchester: každý bit má 2 půlbity → 20 MBd.

**b)** Nejvyšší frekvence vznikne při nejčastějších změnách:

```
NRZ-L,      1010…: H, L, H, L      perioda = 2 bity = 2 · 100 ns = 200 ns → f = 5 MHz
Manchester, 1111…: L H | L H | …   perioda = 1 bit = 100 ns          → f = 10 MHz
```

**c)** bitů na Bd: NRZ-L 10/10 = 1, Manchester 10/20 = 0,5, 4B/5B 4/5 = 0,8.

**d)** Manchester a dif. Manchester: každý bit je polovinu času H a polovinu L, takže průměr je 0 pro libovolná data. NRZ-L ani RZ ne (samé jedničky → průměr kladný).

---

## Příklad 4 - 4B/5B a MLT-3

**a)** podle tabulky:

```
0001 → 01001
0000 → 11110
1110 → 11100
kód: 01001 11110 11100
```

**b)** NRZI (1 = přechod, start L) a MLT-3 (1 = další úroveň, start 0):

```
bit:    0 1 0 0 1 1 1 1 1 0 1 1 1 0 0
NRZI:   L H H H L H L H L L H L H H H
MLT-3:  0 + + + 0 − 0 + 0 0 − 0 + + +
```

**c)** data `0001 0000 1110`: nejdelší řada nul = 4 (`0000`). Kód: nejvýš 2 nuly za sebou (`…11100` na konci, `0100…` uvnitř).

**d)** 100 Mb/s · 5/4 = 125 Mb/s na lince = 125 MBd (NRZI i MLT-3 nesou 1 bit na symbol).

---

## Příklad 5 - ASK, FSK, PSK pro 1011

| bit | 1 | 0 | 1 | 1 |
|-----|---|---|---|---|
| 2-ASK | A = 5 | A = 2 | A = 5 | A = 5 |
| 2-FSK | 2 periody | 1 perioda | 2 periody | 2 periody |
| 2-PSK | start dolů (π) | start nahoru (0) | dolů | dolů |

f = 1 Hz → v každém intervalu (1 s) přesně jedna perioda; f = 2 Hz → dvě.

---

## Příklad 6 - návrh 4stavové modulace

**a)** 4 stavy = 2 bity, každá veličina nese 1 bit:

| | 0 | 1 |
|-|---|---|
| A (1. bit) | 2 V | 5 V |
| φ (2. bit) | 0 | π |

**b)**

```
10 → A = 5, φ = 0      01 → A = 2, φ = π
11 → A = 5, φ = π      00 → A = 2, φ = 0
```

**c)**

```
4 stavy: log2(4) = 2 b → 1200 · 2 = 2400 b/s
8 stavů: log2(8) = 3 b → 1200 · 3 = 3600 b/s
```

Tabulku lze navrhnout i jinak (např. 1. bit = φ) - důležité je, aby ji znaly obě strany.

---

## Příklad 7 - dekódujte (8 stavů)

| interval | vrchol | period | start | A | f | φ | bity |
|----------|--------|--------|-------|---|---|---|------|
| 1 | 2 | 2 | nahoru | 0 | 1 | 0 | `010` |
| 2 | 5 | 2 | dolů | 1 | 1 | 1 | `111` |
| 3 | 5 | 1 | nahoru | 1 | 0 | 0 | `100` |
| 4 | 2 | 1 | dolů | 0 | 0 | 1 | `001` |

Výsledek: `010 111 100 001`.

---

## Příklad 8 - kolik stavů?

```
a) 9600 / 2400 = 4 b/symbol → N = 2^4 = 16
b) 2400 / 600  = 4 b/symbol → N = 16
c) 14400 / 2400 = 6 b/symbol → N = 2^6 = 64
d) QAM-256: log2(256) = 8 b, QAM-1024: log2(1024) = 10 b → 10 / 8 = 1,25 → +25 %
```

**e)** 8-PSK: 8 bodů na kružnici po 360° / 8 = 45°. Grayův kód dokola: `000, 001, 011, 010, 110, 111, 101, 100` (sousedé, včetně posledního a prvního, se liší v 1 bitu).

---

## Příklad 9 - FDM

```
a) (108 − 60) kHz / 4 kHz = 12 hovorů
b) 2483,5 − 2400 = 83,5 MHz; 83,5 / 20 = 4,17 → max. 4 kanály
c) kanál n má střed 2407 + 5 · n MHz; nepřekrývají se, když se středy liší o ≥ 20 MHz = 4 kanály
   → 1, 5, 9, 13 (2412, 2432, 2452, 2472 MHz)
```

V USA jsou povolené jen kanály 1–11, proto se všude uvádí 1, 6, 11 (historicky 22 MHz kanály 802.11b → rozestup 5 kanálů).

---

## Příklad 10 - TDM

```
a) E1: 32 slotů · 8 b · 8000 rámců/s = 2 048 000 b/s = 2,048 Mb/s
b) užitečné: 30 hovorů · 8 b · 8000 = 30 · 64 kb/s = 1,92 Mb/s
   efektivita 30 / 32 = 93,75 %
c) T1: (24 · 8 + 1) · 8000 = 193 · 8000 = 1 544 000 b/s = 1,544 Mb/s
   užitečné 24 · 64 kb/s = 1,536 Mb/s → 192 / 193 = 99,5 %
d) rámec: 1 / 8000 = 125 µs
   slot:  125 µs / 32 = 3,906 µs
   bit:   1 / 2 048 000 = 488 ns   (= 3,906 µs / 8)
```

---

## Příklad 11 - 16-PSK vs. QAM-16 (bonus)

**a)** 16-PSK, body na kružnici o poloměru 1, sousední body svírají úhel 22,5°. Tětiva:

```
d = 2 · r · sin(úhel / 2) = 2 · sin(11,25°) = 2 · 0,195 ≈ 0,39
```

**b)** QAM-16 na mřížce `I, Q ∈ {−3, −1, 1, 3}`. Roh (3, 3) má amplitudu `√18 ≈ 4,24`. Normujeme na max. amplitudu 1:

```
krok mřížky 2 → d = 2 / 4,24 ≈ 0,47
```

**c)** 0,47 / 0,39 ≈ 1,2 → u QAM-16 jsou body o ~20 % dál, je odolnější vůči šumu.

---

## Příklad 12 - statistický multiplex (bonus)

```
a) TDM: 4 · 9600 = 38 400 b/s
b) průměrná data: 4 · 9600 · 0,25 = 9600 b/s
   blok = 15 B dat + 1 B adresy → přenese se 16/15 dat
   9600 · 16 / 15 = 10 240 b/s
```

**c)** Linka (dimenzovaná na ~10 kb/s) při špičce 38,4 kb/s nestíhá: bloky čekají ve frontě → roste zpoždění; když je fronta plná, data se zahazují. Statistický multiplex šetří kapacitu za cenu proměnlivého zpoždění.

---

## Příklad 13 - WDM (bonus)

```
a) 80 · 100 Gb/s = 8000 Gb/s = 8 Tb/s
b) 8 Tb/s / 100 Gb/s = 80 vláken
```
