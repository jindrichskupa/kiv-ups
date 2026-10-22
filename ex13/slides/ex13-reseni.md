# KIV/UPS cvičení 13. - řešení příkladů

## Plán cvičení

| příklad | min | jádro / bonus |
|---------|-----|---------------|
| teorie (statické/dynamické, DV, LS, výběr cesty) | 10 | jádro |
| 1 - statické cesty | 10 | jádro |
| 2 - iterace distance vector | 10 | jádro |
| 3 - Dijkstra | 10 | jádro |
| 4 - kterou cestu? (prefix, AD) | 5 | jádro |
| úloha v emulátoru (OSPF, výpadek linky) | 40 | jádro |
| rezerva | 5 | jádro |
| 5 - count to infinity, split horizon | 10 | bonus |
| 6 - referenční šířka pásma | 5 | bonus |
| 7 - oblasti OSPF | 5 | bonus |
| úloha v emulátoru (cena, RIP vs. OSPF) | 15 | bonus |

Vzorce a pravidla:

```
distance vector:  d(X) = min přes sousedy S ( cena(S) + d_S(X) ),   RIP: cena = 1 skok, 16 = ∞
Dijkstra:         vyber nehotový uzel s nejmenší d, označ hotový, sousedům d = min(d, d_uzel + cena)
OSPF cena:        max(1, reference / šířka pásma),   výchozí reference 100 Mb/s
výběr cesty:      nejdelší prefix → AD (připojená 0, statická 1, OSPF 110, RIP 120) → metrika
```

---

## Příklad 1 - statické cesty

Každý router potřebuje cestu do všech sítí, které nejsou připojené přímo.

| router | přímo připojené | potřebuje cestu do |
|--------|-----------------|--------------------|
| R1 | LAN1, 10.0.12.0/30 | LAN2, LAN3, 10.0.23.0/30 → 3 cesty |
| R2 | LAN2, 10.0.12.0/30, 10.0.23.0/30 | LAN1, LAN3 → 2 cesty |
| R3 | LAN3, 10.0.23.0/30 | LAN1, LAN2, 10.0.12.0/30 → 3 cesty |

**a)**

```
R1: ip route 10.2.0.0  255.255.255.0   10.0.12.2
    ip route 10.3.0.0  255.255.255.0   10.0.12.2
    ip route 10.0.23.0 255.255.255.252 10.0.12.2
R2: ip route 10.1.0.0  255.255.255.0   10.0.12.1
    ip route 10.3.0.0  255.255.255.0   10.0.23.2
R3: ip route 10.1.0.0  255.255.255.0   10.0.23.1
    ip route 10.2.0.0  255.255.255.0   10.0.23.1
    ip route 10.0.12.0 255.255.255.252 10.0.23.1
celkem 8 cest
```

**b)** R1 a R3 mají jen jednoho souseda → všechny jejich cesty vedou stejně → výchozí cesta:

```
R1: ip route 0.0.0.0 0.0.0.0 10.0.12.2
R3: ip route 0.0.0.0 0.0.0.0 10.0.23.1
R2: beze změny (2 cesty, má dva směry)       celkem 4 cesty
```

**c)** LAN4 za R3: R3 ji má připojenou, R1 ji pokryje výchozí cestou → jen R2: `ip route 10.4.0.0 255.255.255.0 10.0.23.2`.

**d)** Linka R1–R2 je jediná cesta z LAN1 → LAN1 je odříznutá. Statické cesty se nepřepočítají ani tam, kde by náhradní cesta existovala.

---

## Příklad 2 - iterace distance vector

Linky: A–B, A–C, B–C, C–D, D–E. Vektor = vzdálenosti k (A, B, C, D, E), ∞ = zatím neznámá.

Postup: nový vektor routeru = minimum přes sousedy z (1 + sousedův vektor z minulé výměny).

```
start:    každý zná jen sebe: A = 0 ∞ ∞ ∞ ∞, …

1. výměna (dozví se sousedy):
  A 0 1 1 ∞ ∞   B 1 0 1 ∞ ∞   C 1 1 0 1 ∞   D ∞ ∞ 1 0 1   E ∞ ∞ ∞ 1 0
2. výměna (sousedé sousedů):
  A 0 1 1 2 ∞   B 1 0 1 2 ∞   C 1 1 0 1 2   D 2 2 1 0 1   E ∞ ∞ 2 1 0
3. výměna:
  A 0 1 1 2 3   B 1 0 1 2 3   C 1 1 0 1 2   D 2 2 1 0 1   E 3 3 2 1 0
4. výměna: beze změny → ustáleno
```

Příklad výpočtu: A po 2. výměně do D = min(1 + B_D, 1 + C_D) = min(1 + ∞, 1 + 1) = 2.

**b)** Každá výměna posune informaci o 1 skok. Nejvzdálenější dvojice (A–E, B–E) jsou 3 skoky od sebe → 3 výměny.

---

## Příklad 3 - Dijkstra z A

Linky: A–B 2, A–C 5, B–C 2, B–D 4, C–D 1, C–E 6, D–E 2, D–F 7, E–F 1.

```
krok 1: hotový A (0)    B = 0+2 = 2 (A), C = 0+5 = 5 (A)
krok 2: hotový B (2)    C = min(5, 2+2) = 4 (B), D = 2+4 = 6 (B)
krok 3: hotový C (4)    D = min(6, 4+1) = 5 (C), E = 4+6 = 10 (C)
krok 4: hotový D (5)    E = min(10, 5+2) = 7 (D), F = 5+7 = 12 (D)
krok 5: hotový E (7)    F = min(12, 7+1) = 8 (E)
krok 6: hotový F (8)
```

**b)** Cesty: B = A–B, C = A–B–C, D = A–B–C–D, E = A–B–C–D–E, F = A–B–C–D–E–F.

| cíl | cena | next hop |
|-----|------|----------|
| B | 2 | B |
| C | 4 | B |
| D | 5 | B |
| E | 7 | B |
| F | 8 | B |

**c)** Bez C–D:

```
krok 1: A (0)   B 2 (A), C 5 (A)
krok 2: B (2)   C 4 (B), D 6 (B)
krok 3: C (4)   E 10 (C)
krok 4: D (6)   E = min(10, 6+2) = 8 (D), F = 6+7 = 13 (D)
krok 5: E (8)   F = min(13, 8+1) = 9 (E)
→ B 2, C 4, D 6, E 8, F 9, next hop pořád B
```

---

## Příklad 4 - kterou cestu?

**a)** Stejný prefix `/16` ze tří zdrojů → rozhoduje AD: statická 1 < OSPF 110 < RIP 120 → statická přes `10.0.3.2`.

**b)** Bez statické: OSPF 110 < RIP 120 → přes `10.0.2.2`. Metriky (2 skoky vs. cena 30) se neporovnávají.

**c)** Nejdřív nejdelší shodný prefix:

```
10.5.1.7: sedí na 10.5.1.0/24 (OSPF) i 10.5.0.0/16 (statická) → /24 → přes 10.0.2.2
10.5.2.7: sedí jen na 10.5.0.0/16                              → statická → přes 10.0.3.2
```

**d)** `ip route 10.5.0.0 255.255.0.0 10.0.3.2 200` - AD 200 > 120 → v tabulce je jen tehdy, když OSPF i RIP cestu ztratí.

---

## Úloha v emulátoru - očekávané výsledky

- `show ip ospf neighbor`: každý router má 2 sousedy ve stavu `FULL`.
- `show ip route` na R1: `O 10.2.0.0/24 [110/x] via 10.0.12.2`, `O 10.3.0.0/24 [110/x] via 10.0.13.2` (x = součet cen linek, závisí na typu rozhraní v emulátoru).
- `traceroute` LAN1 → LAN2: R1, R2, cíl.
- Po `shutdown` linky R1–R2: router výpadek rozhraní zjistí hned, pošle nové LSA, ztratí se typicky jen jednotky pingů; traceroute pak jde R1, R3, R2.
- Kdyby linka "umřela" bez výpadku rozhraní (např. přes switch mezi routery), čeká se na dead interval (40 s).

---

## Příklad 5 - count to infinity (bonus)

Před výpadkem: A = 3 (přes B), B = 2 (přes C), C = 1. C ztratí N → C = 16.

**a)** Bez split horizonu (všichni posílají vše všem, výpočet z hodnot minulé výměny):

```
1.: A = 1 + B(2) = 3, B = min(1 + A(3), 1 + C(16)) = 4, C = 1 + B(2) = 3   ← C věří B
2.: A = 1 + 4 = 5,    B = min(1 + 3, 1 + 3) = 4,          C = 1 + 4 = 5
3.: A = 5,            B = 6,                              C = 5
4.: A = 7,            B = 6,                              C = 7
…
15.: A = B = C = 16 → nedosažitelná
```

**b)** 15 výměn · 30 s = 450 s = 7,5 min, po celou dobu se pakety do N točí ve smyčce mezi routery.

**c)** Se split horizonem B neposílá C cestu do N (naučil se ji od C), A neposílá cestu B:

```
1.: C = 16 (od B nic neslyší), B = 1 + C(16) = 16, A = 1 + B(2) = 3
2.: A = 1 + B(16) = 16
→ 2 výměny
```

**d)** Hodnota 16 znamená nekonečno → počítání se zastaví nejvýš po 15 krocích. Daň: síť s cestou delší než 15 skoků RIP neumí.

---

## Příklad 6 - referenční šířka pásma (bonus)

```
cena = max(1, reference / šířka pásma)

a) reference 100 Mb/s:
   1 Gb/s:   100 / 1000 = 0,1 → 1
   100 Mb/s: 100 / 100  = 1
   R1–R2–R4 = 1 + 1 = 2,  R1–R4 = 1   → přímo, po 100 Mb/s
b) reference 100 Gb/s = 100 000 Mb/s:
   1 Gb/s:   100 000 / 1000 = 100
   100 Mb/s: 100 000 / 100  = 1000
   R1–R2–R4 = 200, R1–R4 = 1000        → přes R2, po 1 Gb/s
c) 10 Gb/s:  ref 100 Mb/s → 1;  ref 100 Gb/s → 100 000 / 10 000 = 10
   25 Gb/s:  ref 100 Mb/s → 1;  ref 100 Gb/s → 100 000 / 25 000 = 4
```

---

## Příklad 7 - oblasti OSPF (bonus)

**a)** Jedna oblast: změna linky se zaplaví do všech 200 routerů a všichni přepočítají Dijkstru. Po rozdělení: LSA o lince zůstane v area 1, Dijkstru počítá jen jejích 50 routerů; ABR do páteře pošle jen souhrn "které sítě jsou za mnou a za kolik" - ostatní oblasti si jen upraví ceny, mapu nepřepočítávají.

**b)** ABR (Area Border Router) má rozhraní v area 0 i v další oblasti, drží LSDB obou a předává mezi nimi souhrnné LSA.

**c)** Mezi oblastmi OSPF předává jen souhrny (jako distance vector). Hvězdicová topologie s páteří uprostřed zaručí, že tyto souhrny nevytvoří smyčku.
