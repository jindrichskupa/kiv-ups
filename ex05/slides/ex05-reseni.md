# KIV/UPS cvičení 5. - řešení příkladů

Vzorce:

```
v_p:       v_p = v_m · log2(N)            bitová rychlost [b/s] = modulační rychlost [Bd] × bitů na symbol (N = počet stavů)
Nyquist:   C = 2 · B · log2(N)
Shannon:   C = B · log2(1 + S/N)          S/N jako poměr, ne dB! (SNR = Signal-to-Noise Ratio, odstup signál/šum)
dB:        X = 10 · log10(P1 / P2)        S/N = 10^(SNR_dB / 10)
log2(x) = ln(x) / ln(2) = log10(x) / 0,301
```

---

## Příklad 1 - Nyquist

Kanál bez šumu, `B = 4 kHz`.

**a) 2 úrovně**

```
C = 2 · 4000 · log2(2) = 2 · 4000 · 1 = 8000 b/s = 8 kb/s
```

**b) 8 úrovní**

```
log2(8) = 3
C = 2 · 4000 · 3 = 24 000 b/s = 24 kb/s
```

**c) kolik úrovní pro 64 kb/s**

```
64 000 = 2 · 4000 · log2(N)
log2(N) = 64 000 / 8000 = 8
N = 2^8 = 256
```

Nyquist počítá s kanálem **bez šumu**, takže 256 úrovní mu nevadí. Jak by to vypadalo prakticky: při rozkmitu signálu 1 V je mezi sousedními úrovněmi `1 V / 255 ≈ 4 mV`. Kdyby na lince byl šum (rušení) jen ±2 mV, přijímač by sousední úrovně začal plést. Počet úrovní tedy reálně omezuje **poměr velikosti signálu a šumu** - kolik přesně, řekne Shannon o pár slidů dál.

---

## Příklad 2 - decibely

Pravidla: **+10 dB = ×10**, **+3 dB = ×2** (přesně 1,995), záporné dB = dělení.

**dB → poměr**

| dB | rozklad | poměr | přesně |
|----|---------|-------|--------|
| 6 | 3 + 3 | 2 · 2 = 4 | 3,98 |
| 9 | 3 + 3 + 3 | 2 · 2 · 2 = 8 | 7,94 |
| 13 | 10 + 3 | 10 · 2 = 20 | 19,95 |
| 23 | 10 + 10 + 3 | 100 · 2 = 200 | 199,5 |
| 37 | 40 − 3 | 10 000 / 2 = 5000 | 5012 |
| −10 | −10 | 1 / 10 = 0,1 | 0,1 |

**poměr → dB**

| poměr | rozklad | dB |
|-------|---------|----|
| 1000 | 10^3 | 3 · 10 = 30 dB |
| 316 | ≈ 100 · √10 = 10^2,5 | 25 dB |
| 2 | | 3 dB (3,01) |
| 50 000 | 100 000 / 2 | 50 − 3 = 47 dB |

---

## Příklad 3 - Shannon

**a) telefonní linka, `B = 3100 Hz`, `SNR = 30 dB`**

```
1) převod dB → poměr:   S/N = 10^(30/10) = 10^3 = 1000
2) log2(1 + 1000) = log2(1001) = ln(1001) / ln(2) = 6,909 / 0,693 ≈ 9,967
3) C = 3100 · 9,967 ≈ 30 898 b/s ≈ 30,9 kb/s
```

**b) odhad `B · SNR_dB / 3`**

```
C ≈ 3100 · 30 / 3 = 31 000 b/s
```

Rozdíl cca 0,3 %. Proč to funguje: pro `S/N ≫ 1` je `log2(1 + S/N) ≈ log2(S/N) = SNR_dB / (10 · log10(2)) = SNR_dB / 3,01`.

**c) `B = 1 MHz`, `S/N = 255`**

```
SNR_dB = 10 · log10(255) ≈ 24,07 dB
C = 10^6 · log2(1 + 255) = 10^6 · log2(256) = 10^6 · 8 = 8 Mb/s
```

**d) kolik úrovní má smysl (Nyquist)**

Hledáme `N`, při kterém Nyquist dosáhne Shannonovy meze:

```
2 · B · log2(N) = B · log2(1 + S/N)
log2(N) = log2(256) / 2 = 4
N = 2^4 = 16          (obecně N = √(1 + S/N))

kontrola: 2 · 10^6 · log2(16) = 2 · 10^6 · 4 = 8 Mb/s
```

* `N = 8` → `2 · 10^6 · 3 = 6 Mb/s` - kanál nevyužijeme
* `N = 32` → Nyquist 10 Mb/s, ale Shannon nepustí víc než 8 Mb/s - úrovně se v šumu nerozliší

---

## Příklad 4 - kapacita z pásma a SNR

**a) SNR 10 dB, pásmo 1 - 3 MHz**

```
1) šířka pásma:          B = f_max − f_min = 3 MHz − 1 MHz = 2 MHz
2) převod dB → poměr:    S/N = 10^(SNR_dB / 10) = 10^(10/10) = 10
3) Shannon:              C = B · log2(1 + S/N) = 2 · 10^6 · log2(11)
                         log2(11) = ln(11) / ln(2) = 2,398 / 0,693 ≈ 3,459
                         C ≈ 2 · 10^6 · 3,459 ≈ 6,92 Mb/s
```

Časté chyby: dosadit `B = 3 MHz` (horní mez místo šířky pásma) nebo `S/N = 10` přímo jako dB (`log2(1 + 10)` sedí jen náhodou, protože 10 dB = 10×; pro 20 dB už `S/N = 100`, ne 20).

**b) kolik úrovní**

```
N = √(1 + S/N) = √11 ≈ 3,3
```

Počet úrovní volíme jako mocninu 2 (každý symbol pak nese celý počet bitů), zaokrouhlujeme **dolů**:

* `N = 2` → Nyquist `2 · 2 · 10^6 · log2(2) = 4 Mb/s` (pod Shannonovou mezí, OK)
* `N = 4` → Nyquist `2 · 2 · 10^6 · log2(4) = 8 Mb/s` > 6,92 Mb/s → nad Shannonovou mezí, úrovně by se v šumu nerozlišily

Shannonova mez (6,92 Mb/s) vyjde necelá - nevadí, je to strop, ne rychlost konkrétního kódování.

---

## Příklad 5 - potřebné SNR

Chceme `C = 100 Mb/s`, `B = 20 MHz`. Vyjádříme S/N ze Shannona:

```
C = B · log2(1 + S/N)
C / B = log2(1 + S/N)
S/N = 2^(C/B) − 1
```

**20 MHz**

```
C / B = 100 / 20 = 5
S/N = 2^5 − 1 = 31
SNR_dB = 10 · log10(31) ≈ 14,9 dB
```

**40 MHz**

```
C / B = 100 / 40 = 2,5
S/N = 2^2,5 − 1 = 5,657 − 1 = 4,657
SNR_dB = 10 · log10(4,657) ≈ 6,7 dB
```

Dvojnásobné pásmo sníží potřebné SNR o ~8 dB. Pozor: šum roste s pásmem (výkon šumu `P_sum = N0 · B`), takže při stejném vysílacím výkonu klesne reálné SNR o 3 dB. I tak se to vyplatí (8 dB > 3 dB).

---

## Příklad 6 - útlum a kapacita

**a) útlum trasy**

Každý článek násobí výkon svým poměrem, v dB se proto útlumy sčítají:

```
útlum = útlum_kabelu + útlum_konektorů
      = (10 km · 3 dB/km) + (2 · 1,5 dB)
      = 30 + 3
      = 33 dB

poměr: 30 dB = ×1000, 3 dB = ×2 → 1000 · 2 = 2000× slabší
(přesně 10^3,3 ≈ 1995)
```

**b) SNR**

Signál byl na začátku o 63 dB nad šumem, cestou ztratil 33 dB:

```
SNR = 63 dB − 33 dB = 30 dB
S/N = 10^3 = 1000
```

**c) kapacita**

```
C = 10^6 · log2(1 + 1000) ≈ 10^6 · 9,967 ≈ 9,97 Mb/s
```

---

## Příklad 7 - modem V.32 (motivační)

Linka 300 - 3400 Hz, SNR ≈ 30 dB. Modem V.32: nosná 1800 Hz, 2400 Bd, QAM-16.

**a) šířka pásma**

```
B = f_max − f_min = 3400 − 300 = 3100 Hz
```

**b) bitová rychlost modemu**

QAM-16 má 16 stavů (bodů konstelace), každý symbol tedy nese `log2(16) = 4` bity:

```
v_p = v_m · log2(N) = 2400 · 4 = 9600 b/s
```

**c) Shannonova mez a využití**

```
S/N = 10^(30/10) = 1000
C = 3100 · log2(1001) ≈ 3100 · 9,967 ≈ 30 900 b/s
využití = 9600 / 30 900 ≈ 31 %
```

Rezerva je velká - proto mohly přijít V.32bis (14,4k) a V.34 (33,6k) na stejné lince.

**d) V.32bis - 14 400 b/s při 2400 Bd**

```
bitů na symbol = 14 400 / 2400 = 6
počet stavů    = 2^6 = 64
```

Reálně má V.32bis konstelaci se **128 body**: 6 datových bitů + 1 bit trellis kódu = 7 bitů. Redundantní bit dovolí opravit chyby, takže body mohou být blíže u sebe (stejný princip jako PAM-5 u 1000BASE-T).

**e) proč ne 4800 Bd**

QAM signál s modulační rychlostí `R` zabere v pásmu přibližně `R` Hz kolem nosné:

```
2400 Bd → 1800 ± 1200 Hz = 600 - 3000 Hz     vejde se do 300 - 3400 Hz ✓
4800 Bd → šířka ≈ 4800 Hz > 3100 Hz          nevejde se ✗
```

Symboly by se slévaly (ISI). Rychlost jde zvýšit jen víc bity na symbol, a ty omezuje SNR (Shannon).

**f) proč "modem"**

* telefonní linka nepřenese stejnosměrnou složku (oddělovací transformátory, 48 V napájení telefonu) ani nízké frekvence
* nad 3,4 kHz ji ořízne filtr před PCM vzorkováním v ústředně
* obdélníkový signál (UART, NRZ) má hodně energie u 0 Hz a vysoké harmonické → neprošel by
* data se proto **namodulují** na sinusovou nosnou uprostřed pásma: **MO**dulator-**DEM**odulator

**Proč zrovna tahle čísla**

| parametr | proč |
|----------|------|
| 300 - 3400 Hz | stačí pro srozumitelnost řeči; dole pryč brum 50 Hz, nahoře rezerva pod 4 kHz (Nyquist pro PCM 8 kHz) |
| nosná 1800 Hz | střed pásma, okraje nejvíc zkreslují |
| 2400 Bd | nejvíc, co se s rezervou vejde; násobek 600 Bd starších modemů |
| 16 stavů | víc SNR bez kódování spolehlivě neunese |
| 33,6 kb/s (V.34) | prakticky Shannonova mez analogové linky |
| 56 kb/s (V.90) | ústředna je digitální: `8000 vzorků/s × 7 bitů = 56 000 b/s`, jen směr k uživateli |

---

## Příklad 8 - Ethernet 100 → 1000 Mb/s (motivační)

**a) 100BASE-TX, jeden směr**

```
125 MBd × 1 bit/symbol = 125 Mb/s na lince
z každých 5 bitů jsou 4 data → 125 · 4/5 = 100 Mb/s
```

**b) jak 10×, na stejném Cat5**

Modulační rychlost zůstává **125 MBd** (stejné spektrum → ověřeno, že Cat5 to unese). Zbylé dva nástroje:

```
                    100BASE-TX                1000BASE-T          zisk
páry na směr        1                         4 (oba směry)       ×4
užit. bitů/symbol   1 · 4/5 = 0,8             2 (PAM-5)           ×2,5
modulační rychlost  125 MBd                   125 MBd             ×1
----------------------------------------------------------------------
celkem              125 · 1 · 0,8 = 100       125 · 4 · 2 = 1000   ×10
```

**c) proč ne 1250 MBd**

Podle Nyquista `v_m ≤ 2B` → pro 1250 MBd je potřeba pásmo aspoň `1250 / 2 = 625 MHz`. Cat5 je specifikován do 100 MHz a útlum i přeslechy s frekvencí rychle rostou.

Závěr: **Cat5 na to nestačí**. Jenže zadání bylo „stejný kabel“ - v budovách ho byly nataženy miliony metrů a nikdo nechtěl kvůli gigabitu sekat do zdí. Modulační rychlost proto zůstala 125 MBd a zrychlení se našlo jinde (4 páry, 2 bity/symbol).

Kde se kabel vyměnit dal, to šlo i „hrubou silou“: optický gigabit (1000BASE-SX/LX) jede právě **1250 MBd**, 1 bit/symbol, 8 z 10 bitů jsou data → 1000 Mb/s. Optické vlákno má pásmo o řády větší než kroucená dvojlinka.

**d) proč PAM-5 a ne PAM-4**

```
PAM-4: 4^4 = 256 = 2^8      → přesně 8 datových bitů, žádná rezerva
PAM-5: 5^4 = 625 ≥ 512 = 2^9 → 8 datových + 1 trellis bit, zbylé 113 = řídicí symboly
```

Trellis kód (dekódovaný Viterbiho algoritmem) přidá cca 6 dB SNR - víc, než se ztratí tím, že 5 úrovní je blíže u sebe než 4.

**e) oba směry na jednom páru**

Vysílač i přijímač jsou na obou koncích páru zároveň. Přijímač zná svůj vlastní vysílaný signál a jeho odraz (echo) od signálu na páru **odečte** (echo cancellation, princip hybridu z telefonu).

**Proč zrovna tahle čísla**

| parametr | proč |
|----------|------|
| 125 MBd | převzato ze starší sítě FDDI, ověřeno na Cat5 |
| 4 z 5 bitů | pátý bit zajistí hrany pro obnovu hodin; cena 20 % |
| 4 páry | Cat5 je má všechny, 10/100 využíval jen 2 |
| PAM-5 | 2 bity/symbol + rezerva pro trellis kód a řídicí symboly |
| Cat5e | doplněná specifikace kabelu (přeslechy, odrazy) pro jistotu |

---

## Příklad 9 - nakreslete 'K' a 'k'

`'K'` = ASCII 75 = `0x4B` = `0100 1011b`

**a) 8N1**

Datové bity se posílají od **LSB** (D0) po MSB (D7):

| bit | D7 | D6 | D5 | D4 | D3 | D2 | D1 | D0 |
|-----|----|----|----|----|----|----|----|----|
| hodnota | 0 | 1 | 0 | 0 | 1 | 0 | 1 | 1 |

Pořadí na lince: `START | D0 D1 D2 D3 D4 D5 D6 D7 | STOP`

```
klid  START  D0 D1 D2 D3 D4 D5 D6 D7  STOP  klid
 1      0     1  1  0  1  0  0  1  0    1     1
```

![K 8N1](images/uart-K-8n1.svg)

**b) 7E1**

* 7 datových bitů: `100 1011b` (D6..D0)
* od LSB: `1 1 0 1 0 0 1`
* počet jedniček v datech = 4 → sudá parita: `P = 0` (celkový počet jedniček včetně P musí být sudý)

```
klid  START  D0 D1 D2 D3 D4 D5 D6  P  STOP  klid
 1      0     1  1  0  1  0  0  1  0    1     1
```

![K 7E1](images/uart-K-7e1.svg)

Oba rámce mají 10 bitových intervalů.

**c) 'k' v 8E2**

`'k'` = ASCII 107 = `0x6B` = `0110 1011b` - proti `'K'` (`0100 1011b`) se liší jen bit D5 (malé a velké písmeno se v ASCII liší o 32 = `2^5`).

* od LSB: `1 1 0 1 0 1 1 0`
* počet jedniček v datech = 5 (lichý) → sudá parita: `P = 1`, aby celkový počet jedniček byl sudý (6)
* 2 stop bity = linka zůstane v klidu (log. 1) 2 bitové intervaly

```
klid  START  D0 D1 D2 D3 D4 D5 D6 D7  P  STOP STOP  klid
 1      0     1  1  0  1  0  1  1  0  1    1    1     1
```

![k 8E2](images/uart-k-8e2.svg)

Rámec má `1 + 8 + 1 + 2 = 12` bitových intervalů → užitečných je jen `8 / 12 ≈ 67 %` (u 8N1 80 %).

---

## Příklad 10 - dekódujte

![UART decode](images/uart-decode-solution.svg)

Postup:

1. najít sestupnou hranu z klidu (1 → 0) = začátek START bitu
2. rozdělit čas na bitové intervaly (9600 Bd → 104 µs)
3. číst hodnotu **uprostřed** každého intervalu
4. ověřit START = 0 a STOP = 1
5. datové bity otočit (přišly od LSB)

```
na lince:   START  D0 D1 D2 D3 D4 D5 D6 D7  STOP
             0     0  0  0  1  0  1  1  0    1   ✓ start = 0, stop = 1

D7..D0 = 0 1 1 0 1 0 0 0 = 0110 1000b = 0x68 = 104 = 'h'
```

**Parita při 8E1:** jedniček v datech = 3 (lichý počet) → `P = 1`, aby jich celkem byl sudý počet.

---

## Příklad 11 - doba přenosu a tolerance

Při 2 úrovních (`N = 2`) platí `1 Bd = 1 b/s`, tj. 9600 Bd = 9600 bitových intervalů za sekundu (včetně start/stop bitů).

**a) 1 KiB = 1024 B**

| režim | bitů na znak | celkem bitů | čas |
|-------|--------------|-------------|-----|
| 9600 8N1 | 1 + 8 + 0 + 1 = 10 | 10 240 | 10 240 / 9600 ≈ **1,07 s** |
| 9600 8E2 | 1 + 8 + 1 + 2 = 12 | 12 288 | 12 288 / 9600 = **1,28 s** |
| 115200 8N1 | 10 | 10 240 | 10 240 / 115 200 ≈ **88,9 ms** |

**b) užitečná rychlost 115200 8N1**

```
115 200 / 10 bitů na znak = 11 520 B/s     (užitečných 92 160 b/s = 80 %)
```

Častá chyba: `115 200 / 8 = 14 400 B/s` - zapomíná na start a stop bit.

**c) vysílač 9800 Bd, přijímač 9600 Bd**

```
relativní odchylka = |9800 − 9600| / 9600 ≈ 2,08 %
```

Rozdíl `200 Bd` je tedy prostě rozdíl rychlostí vysílače a přijímače; v poměru k nominální rychlosti je to odchylka hodin.

Přijímač se synchronizuje na sestupné hraně START bitu a dál už jen odpočítává bitové intervaly `T`. Poslední vzorek je uprostřed STOP bitu: START (1) + 8 datových bitů (8) + polovina STOP bitu (0,5) = `9,5 T` od hrany. Každý bit chyba přibude, takže u posledního vzorku je největší:

```
posun = 9,5 · 2,08 % ≈ 0,198 bitu
```

Vzorek musí zůstat v rámci bitu, tj. posun < 0,5 bitu → `0,198 < 0,5` → **znak se přijme správně**.

Přesněji: `9,5 T_rx` odpovídá `9,5 · 9800 / 9600 ≈ 9,70 T_tx` → pořád v intervalu STOP bitu `⟨9, 10)`.

Mezní odchylka pro 8N1: `0,5 / 9,5 ≈ 5,3 %` (součet chyb obou stran; v praxi se doporučuje < 2 - 3 %).
