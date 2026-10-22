# KIV/UPS cvičení 9. - řešení příkladů

## Plán cvičení

| příklad | min | |
|---------|-----|-|
| úvod, tahák, postup | 5 | jádro |
| 1 - třída a typ adresy | 5 | jádro |
| 2 - síť, broadcast, hosté (`145.12.28.140/21`) | 10 | jádro |
| 3 - tabulka čtyř adres | 12 | jádro |
| 4 - stejná síť? | 5 | jádro |
| 5 - maska z počtu hostů | 5 | jádro |
| 6 - longest prefix match | 8 | jádro |
| 7 - VLSM a směrovací tabulky | 25 | jádro |
| rezerva | 15 | |
| 8 - dělení sítě | 5 | bonus |
| 9 - agregace | 5 | bonus |
| 10 - najděte chybu | 8 | bonus |
| 11 - VLSM ze zadání přednášky | 15 | bonus |
| 12 - IPv6 prefixy | 5 | bonus |

Postup:

```
síť        = adresa AND maska
broadcast  = síť OR (NOT maska)          hostitelské bity na 1
hostů      = 2^(32 − prefix) − 2
krok       = 256 − maska v oktetu, do kterého prefix zasahuje
maska z počtu hostů: n + 2 → zaokrouhlit nahoru na 2^k → prefix 32 − k
```

---

## Příklad 1 - třída a typ adresy

Třída podle úvodních bitů 1. oktetu: `0` A, `10` B, `110` C, `1110` D, `1111` E.

```
145 = 1001 0001 → 10… → B, veřejná
 10 = 0000 1010 → 0…  → A, privátní 10.0.0.0/8
172 = 1010 1100 → 10… → B
      172.16.0.0/12 = 172.16.0.0 – 172.31.255.255
      172.31.255.254 → privátní, 172.32.0.1 → veřejná
192 = 1100 0000 → 110… → C, 192.168.0.0/16 privátní; .255 je při /24 broadcast
224 = 1110 0000 → D, multicast (224.0.0.5 = všechny OSPF routery)
169 = 1010 1001 → B, 169.254.0.0/16 link-local (selhalo DHCP)
127 = 0111 1111 → A, loopback
240 = 1111 0000 → E, rezerva
```

---

## Příklad 2 - `145.12.28.140/21`

Maska /21 = 8 + 8 + 5 jedniček → `255.255.248.0`. Zasahuje do 3. oktetu.

```
28  = 0001 1100
248 = 1111 1000
AND = 0001 1000 = 24     → síť      145.12.24.0
OR ~ = 0001 1111 = 31    → broadcast 145.12.31.255
```

Hostů: 32 − 21 = 11 bitů → 2¹¹ − 2 = 2048 − 2 = **2046**. První `145.12.24.1`, poslední `145.12.31.254`. Třída B (`145` = `10010001`).

Kontrola krokem: 256 − 248 = 8, násobky 8: 0, 8, 16, **24**, 32 → 28 leží v 24–31.

---

## Příklad 3 - tabulka

**`10.37.200.77/19`**: /19 → 3. oktet maska `224` (`1110 0000`), krok 32.

```
200 = 1100 1000
224 = 1110 0000
AND = 1100 0000 = 192 → síť 10.37.192.0, broadcast 10.37.223.255
hostů 2^13 − 2 = 8190, první 10.37.192.1, poslední 10.37.223.254
```

**`172.20.5.130/26`**: 4. oktet maska `192`, krok 64 → bloky 0, 64, **128**, 192.

```
síť 172.20.5.128, broadcast 172.20.5.191, hostů 2^6 − 2 = 62, .129 – .190
```

**`200.100.50.25/28`**: maska `240`, krok 16 → bloky 0, **16**, 32.

```
síť 200.100.50.16, broadcast 200.100.50.31, hostů 2^4 − 2 = 14, .17 – .30
```

**`85.160.3.77/12`**: /12 → 2. oktet maska `240`, krok 16 → bloky …, 144, **160**, 176.

```
síť 85.160.0.0, broadcast 85.175.255.255, hostů 2^20 − 2 = 1 048 574
```

---

## Příklad 4 - stejná síť?

```
a) /27, krok 32:  200 → blok 192–223,  190 → blok 160–191  → různé sítě
b) /25, krok 128: 200 → blok 128–255,  190 → blok 128–255  → stejná síť 192.168.10.128/25
```

**c)** A (`10.0.0.5/8`): je `10.1.0.5` v `10.0.0.0/8`? Ano → posílá přímo, ARP na `10.1.0.5`. B (`10.1.0.5/16`): je `10.0.0.5` v `10.1.0.0/16`? Ne → posílá přes svou bránu. Cesta tam a zpět je jiná.

---

## Příklad 5 - maska z počtu hostů

```
 5 + 2 =    7 →    8 = 2^3  → /29  255.255.255.248
30 + 2 =   32 →   32 = 2^5  → /27  255.255.255.224
60 + 2 =   62 →   64 = 2^6  → /26  255.255.255.192
62 + 2 =   64 →   64 = 2^6  → /26
63 + 2 =   65 →  128 = 2^7  → /25  255.255.255.128
500 + 2 = 502 →  512 = 2^9  → /23  255.255.254.0
1000 + 2 = 1002 → 1024 = 2^10 → /22  255.255.252.0
```

---

## Příklad 6 - longest prefix match

Pro každý cíl vypíšeme záznamy, které vyhovují (cíl AND maska = síť záznamu), a vybereme nejdelší prefix:

```
10.1.2.5    → /0 ✓  10/8 ✓  10.1/16 ✓  10.1.2/24 ✓   → R4
10.1.3.5    → /0 ✓  10/8 ✓  10.1/16 ✓  10.1.2/24 ✗   → R3
10.2.0.1    → /0 ✓  10/8 ✓  10.1/16 ✗               → R2
8.8.8.8     → /0 ✓  10/8 ✗                          → R1
10.1.2.255  → jako 10.1.2.5                         → R4
```

---

## Příklad 7 - VLSM `192.168.100.0/24`

1. Seřadit od největší: A 100, B 50, C 20, D 10, L1 2, L2 2.
2. Velikost bloku (+ 2, mocnina dvou): 128, 64, 32, 16, 4, 4.
3. Přidělovat postupně od začátku:

```
A  128 → /25  192.168.100.0   – .127   brána .1
B   64 → /26  192.168.100.128 – .191   brána .129
C   32 → /27  192.168.100.192 – .223   brána .193
D   16 → /28  192.168.100.224 – .239   brána .225
L1   4 → /30  192.168.100.240 – .243   R1 .241, R2 .242
L2   4 → /30  192.168.100.244 – .247   R1 .245, ISP .246
volné       192.168.100.248/29 (.248 – .255)
```

**b)** 128 + 64 + 32 + 16 + 4 + 4 = 248 → volných 8 adres.

**c)** Směrovací tabulky:

```
R1:
192.168.100.0/25     přímo (A)
192.168.100.128/26   přímo (B)
192.168.100.240/30   přímo (L1)
192.168.100.244/30   přímo (L2)
192.168.100.192/27   via 192.168.100.242
192.168.100.224/28   via 192.168.100.242      (obě lze sloučit: 192.168.100.192/26 via .242)
0.0.0.0/0            via 192.168.100.246

R2:
192.168.100.192/27   přímo (C)
192.168.100.224/28   přímo (D)
192.168.100.240/30   přímo (L1)
0.0.0.0/0            via 192.168.100.241
```

ISP potřebuje zpětnou cestu `192.168.100.0/24 via 192.168.100.245`.

---

## Příklad 8 (bonus) - dělení sítě

```
8 podsítí = 2^3 → +3 bity → /19, krok ve 3. oktetu 256 − 224 = 32
172.16.0.0/19, 172.16.32.0/19, 172.16.64.0/19, …, 172.16.224.0/19
/24 → /26: 2^(26−24) = 4         /24 → /30: 2^(30−24) = 64
hostů v /19: 2^13 − 2 = 8190
```

---

## Příklad 9 (bonus) - agregace

```
4 = 0000 0100
5 = 0000 0101
6 = 0000 0110
7 = 0000 0111
    ^^^^ ^^ společných 6 bitů ve 3. oktetu → 16 + 6 = /22 → 192.168.4.0/22
```

`10.1.0.0`, `10.1.1.0`, `10.1.2.0`: 0 a 1 se liší jen v posledním bitu → `10.1.0.0/23`. Přidat 2 vyžaduje /22, která zahrne i 3 → přesně to nejde, minimum jsou 2 záznamy.

---

## Příklad 10 (bonus) - najděte chybu

```
a) brána 192.168.2.1 není v 192.168.1.0/24
b) 192.168.1.255/24 = broadcast
c) 192.168.1.0/24   = adresa sítě
d) 192.168.1.64/26: blok 64–127 → .64 je adresa sítě; brána .1 je v bloku 0–63
e) PC je nastavené správně; chyba je na bráně (chybí cesta do 172.17.0.0/16) nebo na serveru (chybí cesta zpět)
```

---

## Příklad 11 (bonus) - VLSM ze zadání přednášky

```
A 134 + 65 = 199 → 199 + 2 = 201 → 256 → /24   147.92.0.0/24
B  40 + 10 =  50 →  52 →  64 → /26   147.92.1.0/26     (.0 – .63)
C  15 +  5 =  20 →  22 →  32 → /27   147.92.1.64/27    (.64 – .95)
D   5 +  2 =   7 →   9 →  16 → /28   147.92.1.96/28    (.96 – .111)
E          =   2 →   4 →   4 → /30   147.92.1.112/30   (.112 – .115)
```

---

## Příklad 12 (bonus) - IPv6

```
/48 → /64: 64 − 48 = 16 bitů → 2^16 = 65 536 sítí
LAN 9 (desátá od nuly): 2001:db8:abcd:0009::/64 = 2001:db8:abcd:9::/64
v /64: 2^64 = 18 446 744 073 709 551 616 adres
```
