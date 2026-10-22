# KIV/UPS cvičení 7. - řešení příkladů

## Plán cvičení

| příklad | min | jádro / bonus |
|---------|-----|---------------|
| opakování arytmického přenosu, efektivita | 5 | jádro |
| 1 - efektivita a doba přenosu | 10 | jádro |
| teorie chybovosti + 2 - jak velký rámec | 12 | jádro |
| 3 - Ethernet a BER | 10 | jádro |
| teorie byte stuffingu + 4 - byte stuffing | 10 | jádro |
| 5 - tam a zpět | 10 | jádro |
| teorie bit stuffingu + 6 - bit stuffing | 10 | jádro |
| 7 - HDLC | 13 | jádro |
| shrnutí + rezerva | 10 | jádro |
| 8 - parita v praxi | 10 | bonus |
| 9 - chyby za den | 5 | bonus |
| 10 - optimální délka rámce | 10 | bonus |
| 11 - nejhorší případ | 5 | bonus |
| 12 - proč má HDLC vlajku 01111110 | 10 | bonus |

Vzorce a pravidla:

```
efektivita:   e = datové bity / (start + data + parita + stop)
rámec OK:     P = (1 − p)^n           p = BER, n = počet bitů; n zaokrouhlit DOLŮ
max. rámec:   n < log(P) / log(1 − p)
byte stuffing: STX 0x02 | data, před 02 / 03 / 10 vlož DLE 0x10 | ETX 0x03
bit stuffing:  vlajka 11111, po čtyřech 1 vlož 0   |   HDLC: vlajka 01111110, po pěti 1 vlož 0
```

---

## Příklad 1 - efektivita a doba přenosu

**a)**

```
8N1: 8 / (1 + 8 + 1)     = 8 / 10 = 80 %
7E1: 7 / (1 + 7 + 1 + 1) = 7 / 10 = 70 %
7E2: 7 / (1 + 7 + 1 + 2) = 7 / 11 ≐ 63,6 %
8O2: 8 / (1 + 8 + 1 + 2) = 8 / 12 ≐ 66,7 %
5N1: 5 / (1 + 5 + 1)     = 5 / 7  ≐ 71,4 %
```

**b)** 8N1 = 10 bitových intervalů na znak, 1 Bd = 1 bit:

```
115 200 Bd / 10 = 11 520 znaků/s
1 MiB = 1 048 576 B → 1 048 576 / 11 520 ≐ 91,0 s
```

**c)**

```
9600 / 11 ≐ 872,7 znaků/s
1 048 576 / 872,7 ≐ 1201,5 s ≈ 20 min
```

**d)** Víc datových bitů na jeden start a stop bit. Za to platíme: (1) delší rámec má větší pravděpodobnost chyby, (2) přijímač se synchronizuje jen na začátku rámce, takže se hodiny za delší dobu víc rozejdou (tolerance hodin z cvičení 5).

---

## Příklad 2 - jak velký rámec? (1 % na bit, 95 %)

```
p(bit chybný) = 0,01 → p(bit OK) = 0,99
rámec n bitů OK: 0,99^n > 0,95
log(0,99^n) > log(0,95)
n · log(0,99) > log(0,95)
log(0,99) = −0,00436 < 0 → při dělení se nerovnost otočí:
n < log(0,95) / log(0,99) = (−0,02228) / (−0,00436) = 5,1036…
n = 5
```

Kontrola: `0,99^5 = 0,951 > 0,95` ✓, `0,99^6 = 0,941 < 0,95` ✗. Zaokrouhlit nahoru (6) by porušilo podmínku.

---

## Příklad 3 - Ethernet a BER

**a)**

```
n = 1500 B · 8 = 12 000 bitů
BER 10⁻⁶: (1 − 0,000001)^12000 = 0,98807 → 98,8 %
BER 10⁻⁵: (1 − 0,00001)^12000  = 0,88692 → 88,7 %
```

Na kalkulačce: `0,99999^12000` nebo `e^(12000 · ln(0,99999))`.

**b)**

```
(1 − 10⁻⁵)^n > 0,99
n < log(0,99) / log(0,99999) = 1005,03
n = 1005 bitů = 125,6 B → 125 B (celé bajty, zase dolů)
```

---

## Příklad 4 - byte stuffing

```
data:          15 2A 02 CC 05 03 CD 10 12
                     ^^       ^^    ^^        řídicí znaky v datech
+ STX/ETX:  02 15 2A 02 CC 05 03 CD 10 12 03  → přijímač by skončil u prvního 03
stuffing:   02 15 2A 10 02 CC 05 10 03 CD 10 10 12 03
```

DLE se musí escapovat taky: jinak by `10 12` přijímač vyložil jako "DLE + data 12" a bajt `10` by zmizel.

---

## Příklad 5 - tam a zpět

**a)**

```
data:   10 02 41 03 10
rámec:  02 | 10 10 | 10 02 | 41 | 10 03 | 10 10 | 03
      = 02 10 10 10 02 41 10 03 10 10 03
```

**b)** Čteme zleva; po každém `10` je další bajt data:

```
02         STX - začátek
10 10   →  10
48      →  48
10 03   →  03   (escapovaný, není to konec)
49      →  49
10 02   →  02
03         ETX - konec
data: 10 48 03 49 02
```

**c)** rámec 11 B, data 5 B → `e = 5 / 11 ≐ 45,5 %`.

---

## Příklad 6 - bit stuffing (vlajka 11111)

Hledáme čtyři jedničky za sebou (počítadlo se nuluje každou 0 i po vložení):

```
data:     1101011001011111 1001101100
                      ^^^^ čtyři 1 → vložit 0
stuffing: 11010110010111101 1001101100   (vložená 0 na 16. pozici)
rámec:    11111 110101100101111011001101100 11111
```

Pozor: za čtyřmi jedničkami v datech následuje další 1 - bez vložené nuly by přijímač viděl `11111` = vlajku uprostřed dat.

---

## Příklad 7 - HDLC

**a)** Vkládáme 0 po pěti jedničkách:

```
data:   0 11111 1 0 11111 1 0 0
          ^^^^^       ^^^^^
stuff:  0 11111 0 1 0 11111 0 1 0 0  = 011111010111110100
rámec:  01111110 011111010111110100 01111110
```

**b)** Proud: `0111111010111110011111011001111110`

```
01111110 | 101111100111110110 | 01111110
 vlajka         data            vlajka

101111100111110110:
1 0 1 1 1 1 1 [0] 0 1 1 1 1 1 [0] 1 1 0     [0] = vložená, zahodit
→ 1011111011111110
```

Pravidlo přijímače: po pěti jedničkách přijde 0 → zahodit; přijde 1 → je to vlajka (šestá jednička) nebo chyba.

**c)** 2 vložené nuly; s vlajkami přenos nesl 34 bitů pro 16 bitů dat.

---

## Příklad 8 - parita v praxi (bonus)

7E1 = 10 bitů, p = 10⁻³:

```
a) P(aspoň 1 chyba) = 1 − 0,999^10 = 0,00995 → 0,995 %
b) P(právě 1)  = C(10, 1) · p · (1 − p)^9  = 10 · 0,001 · 0,99104 = 0,00991 → 0,991 %
c) P(právě 2)  = C(10, 2) · p² · (1 − p)^8 = 45 · 10⁻⁶ · 0,99203  = 4,46 · 10⁻⁵ → 0,0045 %
```

Parita odhalí lichý počet chyb (b), sudý ne (c). Většina chybných znaků má jen jednu chybu.

---

## Příklad 9 - chyby za den (bonus)

```
a) rámec 1500 B = 12 000 b → 100 000 000 / 12 000 ≐ 8333 rámců/s
b) P(chybný) = 1 − (1 − 10⁻¹⁰)^12000 ≈ 12 000 · 10⁻¹⁰ = 1,2 · 10⁻⁶
c) za den: 8333 · 86 400 ≐ 7,2 · 10⁸ rámců · 1,2 · 10⁻⁶ ≐ 864 chybných rámců
```

---

## Příklad 10 - optimální délka rámce (bonus)

Užitečná propustnost `U(L) = L / (L + 20) · (1 − 10⁻⁴)^(8 · (L + 20))`:

```
L = 64 B:   64 / 84    · 0,9999^672   = 0,762 · 0,935 = 71,2 %
L = 128 B:  128 / 148  · 0,9999^1184  = 0,865 · 0,888 = 76,8 %
L = 512 B:  512 / 532  · 0,9999^4256  = 0,962 · 0,653 = 62,9 %
L = 1500 B: 1500 / 1520 · 0,9999^12160 = 0,987 · 0,296 = 29,2 %
```

Optimum je kolem 148 B (graf ve slidech). Při lepší lince (menší BER) se optimum posouvá k delším rámcům.

---

## Příklad 11 - nejhorší případ (bonus)

```
a) 100 B samých 02 / 03 / 10 → každý bajt + DLE = 200 B, + STX + ETX = 202 B
   e = 100 / 202 ≐ 49,5 %
b) samé 1: 1111 0 1111 0 … → na každé 4 bity 1 navíc → +25 %
c) HDLC: 11111 0 11111 0 … → na každých 5 bitů 1 navíc → +20 %
```

---

## Příklad 12 - proč má HDLC vlajku 01111110 (bonus)

**a)** Vysílač pošle `…0111` + `11111`, data obsahují jen 3 jedničky, nic se nevkládá. Přijímač:

```
…0  1  1  1  1  1  1  1  1
    d  d  d  v  v  v  v  v      d = data, v = vlajka
počítadlo:  1  2  3  4  → další bit 1 = "vlajka"
```

Přijímač ukončí rámec už po 5 jedničkách (3 datových + 2 z vlajky): data přijdou o `111` a zbylé tři jedničky vlajky začnou "další rámec".

**b)** `01111110` začíná a končí nulou, takže jedničky z dat se s jedničkami vlajky nikdy nespojí (před vlajkou je vždy její vlastní 0). V datech je po stuffingu nejvýš 5 jedniček za sebou, vlajka jich má 6 - nedá se splést.
