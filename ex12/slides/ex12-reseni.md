# KIV/UPS cvičení 12. - řešení příkladů

## Plán cvičení

| příklad | min | jádro / bonus |
|---------|-----|---------------|
| teorie (switch, VLAN) | 10 | jádro |
| 1 - MAC tabulka (jeden switch) | 10 | jádro |
| 2 - kolizní a broadcastové domény | 5 | jádro |
| 3 - návrh VLAN | 10 | jádro |
| 4 - router-on-a-stick | 10 | jádro |
| úloha v emulátoru (VLAN, trunk, router-on-a-stick) | 40 | jádro |
| rezerva | 5 | jádro |
| 5 - MAC tabulka (dva switche) | 10 | bonus |
| 6 - 802.1Q | 5 | bonus |
| 7 - smyčka bez STP | 5 | bonus |
| 8 - STP | 15 | bonus |
| úloha v emulátoru (STP) | 15 | bonus |

Pravidla switche:

```
přijde rámec (src, dst) na port p:
  tabulka[src] = p                          učení
  dst = broadcast nebo dst neznámý  → flood (všechny porty kromě p)
  tabulka[dst] == p                 → filter (zahodit)
  jinak                             → forward na tabulka[dst]
```

---

## Příklad 1 - MAC tabulka (jeden switch)

Port 1 = hub s A a E, port 2 = B, port 3 = C, port 4 = D.

| rámec | vstup | učení | akce | tabulka |
|-------|-------|-------|------|---------|
| A → B | 1 | A:1 | B neznámý → flood 2, 3, 4 | A:1 |
| B → A | 2 | B:2 | A na portu 1 → forward 1 | A:1, B:2 |
| E → A | 1 | E:1 | A na portu 1 = vstupní port → filter | A:1, B:2, E:1 |
| C → FF:FF:… | 3 | C:3 | broadcast → flood 1, 2, 4 | A:1, B:2, C:3, E:1 |
| D → C | 4 | D:4 | C na portu 3 → forward 3 | + D:4 |
| B → E | 2 | - | E na portu 1 → forward 1 | A:1, B:2, C:3, D:4, E:1 |

---

## Příklad 2 - domény

**a)** Kolizní doména = každý port switche (a routeru) zvlášť, hub tvoří s připojenými počítači jednu doménu.

```
SW1: R, PC1, PC2, PC3, HUB (PC4–PC6)  = 5
SW2: R, PC7, PC8                       = 3
celkem                                 = 8 kolizních domén
broadcastové: router odděluje SW1 a SW2 = 2
```

**b)** SW2 → hub: R, PC7, PC8 sdílí jedno médium → 5 + 1 = 6 kolizních, broadcastové 2.

**c)** Broadcast od PC4: hub ho pošle PC5, PC6 a SW1; SW1 zaplaví PC1, PC2, PC3 a rozhraní R do SW1. Router broadcast dál nepošle → PC7, PC8 ho nedostanou.

---

## Příklad 3 - návrh VLAN

| switch | port | zařízení | režim | VLAN |
|--------|------|----------|-------|------|
| SW1 | Fa0/1 | PC1 (vývoj) | access | 10 |
| SW1 | Fa0/2 | PC2 (vývoj) | access | 10 |
| SW1 | Fa0/3 | PC3 (ekonomika) | access | 20 |
| SW1 | G0/1 | SW2 | trunk | 10, 20 |
| SW2 | Fa0/1 | PC4 (vývoj) | access | 10 |
| SW2 | Fa0/2 | PC5 (vedení) | access | 30 |
| SW2 | Fa0/3 | PC6 (ekonomika) | access | 20 |
| SW2 | G0/1 | SW1 | trunk | 10, 20 |
| SW2 | G0/2 | R | trunk | 10, 20, 30 |

Adresy: PC1 `192.168.10.11`, PC2 `.10.12`, PC3 `192.168.20.13`, PC4 `192.168.10.14`, PC5 `192.168.30.15`, PC6 `192.168.20.16`, vše `/24`.

**b)** Bez routeru komunikují jen počítače ve stejné VLAN: PC1, PC2, PC4 (VLAN 10, PC4 přes trunk), PC3 a PC6 (VLAN 20). PC5 je ve VLAN 30 sám.

**c)** G0/1 na SW1 zůstane access (VLAN 1): SW2 posílá rámce VLAN 10 a 20 s tagem, SW1 je na access portu zahodí. Funguje jen komunikace uvnitř jednoho switche (PC1 ↔ PC2).

---

## Příklad 4 - router-on-a-stick

**a)**

| podrozhraní | VLAN | adresa | brána pro |
|-------------|------|--------|-----------|
| G0/0.10 | 10 | 192.168.10.1/24 | PC1, PC2, PC4 |
| G0/0.20 | 20 | 192.168.20.1/24 | PC3, PC6 |
| G0/0.30 | 30 | 192.168.30.1/24 | PC5 |

**b)** Cisco IOS:

```
interface g0/0
 no shutdown
interface g0/0.10
 encapsulation dot1Q 10
 ip address 192.168.10.1 255.255.255.0
interface g0/0.20
 encapsulation dot1Q 20
 ip address 192.168.20.1 255.255.255.0
interface g0/0.30
 encapsulation dot1Q 30
 ip address 192.168.30.1 255.255.255.0
```

Linux:

```
ip link add link eth0 name eth0.10 type vlan id 10
ip addr add 192.168.10.1/24 dev eth0.10
ip link set eth0.10 up          # totéž pro 20 a 30
sysctl -w net.ipv4.ip_forward=1
```

**c)** PC5 není v síti PC1 → PC1 pošle rámec bráně `192.168.10.1` (MAC zjistí ARPem, broadcast zůstane ve VLAN 10).

```
PC1 → SW1 Fa0/1        bez tagu
SW1 G0/1 → SW2 G0/1    tag 10
SW2 G0/2 → R G0/0.10   tag 10      ← 1. průchod linkou SW2–R
R: směrování 192.168.10.0/24 → 192.168.30.0/24
R G0/0.30 → SW2 G0/2   tag 30      ← 2. průchod
SW2 Fa0/2 → PC5        bez tagu
```

Odpověď jde stejnou cestou zpět (opět 2 průchody).

**d)** Veškerý provoz mezi VLAN jde po jedné lince dvakrát (k routeru a zpět) → její kapacita se dělí mezi všechny VLAN.

---

## Příklad 5 - dva switche (bonus)

SW1: A = 1, B = 2, SW2 = 3. SW2: C = 1, D = 2, SW1 = 3.

| rámec | SW1 | SW2 | SW1 tabulka | SW2 tabulka |
|-------|-----|-----|-------------|-------------|
| A → D | učí A:1, D neznámý → flood 2, 3 | učí A:3, flood 1, 2 | A:1 | A:3 |
| D → A | učí D:3, forward 1 | učí D:2, forward 3 | A:1, D:3 | A:3, D:2 |
| B → A | učí B:2, forward 1 | rámec nevidí | A:1, B:2, D:3 | A:3, D:2 |
| C → B | učí C:3, forward 2 | učí C:1, B neznámý → flood 2, 3 | A:1, B:2, C:3, D:3 | A:3, C:1, D:2 |
| A → B | forward 2 | rámec nevidí | beze změny | beze změny |

---

## Příklad 6 - 802.1Q (bonus)

```
a) VID 12 bitů: 2^12 = 4096 hodnot, 0 a 4095 rezervované → 4094 VLAN
b) 1518 B + 4 B tag = 1522 B
c) PCP 3 bity → 2^3 = 8 tříd priority
d) 4094 · 4094 = 16 760 836 ≈ 16,8 milionu kombinací
```

---

## Příklad 7 - smyčka bez STP (bonus)

**a)** SW1 dostane broadcast od A → zaplaví SW2 i SW3. SW2 ho pošle SW3 (jiný port než vstupní), SW3 ho pošle SW2. Obě kopie dorazí zpět do SW1, ten je pošle A a znovu dál.

**b)** Ethernetový rámec nemá TTL → obíhá, dokud se smyčka nerozpojí. V trojúhelníku obíhají dvě kopie (každá jedním směrem), v hustší topologii se kopie násobí.

**c)** SW1 vidí zdrojovou MAC A střídavě na portu k A, k SW2 a k SW3 → záznam pro A pořád přeskakuje (MAC flapping), rámce pro A se posílají do smyčky místo k A.

---

## Příklad 8 - STP (bonus)

Bridge ID = priorita / MAC: SW1 `32768 / …:0a`, SW2 `32768 / …:05`, SW3 `4096 / …:ff`. Cena linky 1 Gb/s = 4, 100 Mb/s = 19.

**a)**

```
root bridge: nejnižší priorita → SW3 (4096)
SW1: k SW3 přímo 4, přes SW2 8 → root port k SW3
SW2: k SW3 přímo 4             → root port k SW3
linky k SW3: designated porty na SW3 (root má všechny porty designated)
linka SW1–SW2: oba nabízejí cenu 4 → nižší bridge ID: SW2 (…:05 < …:0a)
  → SW2 designated, SW1 blokuje
```

**b)** Všechny priority 32768 → rozhoduje MAC → root SW2 (`…:05`). SW1 a SW3 mají root port k SW2. Linka SW1–SW3: oba nabízejí 4 → nižší bridge ID SW1 (`…:0a < …:ff`) → designated SW1, **SW3 blokuje**.

**c)** Root SW3. SW1: přímo 19, přes SW2 4 + 4 = 8 → **root port k SW2**. SW2: root port k SW3 (4). Linka SW1–SW3: SW3 je root (cena 0) → designated na SW3, **SW1 blokuje port k SW3**. Provoz SW1 → SW3 jde přes SW2 po rychlých linkách.
