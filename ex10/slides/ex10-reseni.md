# KIV/UPS cvičení 10. - řešení příkladů

## Plán cvičení

| příklad | min | |
|---------|-----|-|
| zadání, topologie | 5 | jádro |
| 1 - co se děje (kroky u tabule) | 15 | jádro |
| 2 - hlavičky cestou tam | 15 | jádro |
| 3 - cesta zpět a NAT tabulka | 10 | jádro |
| 4 - ARP | 8 | jádro |
| 5 - DNS dotaz | 8 | jádro |
| 6 - TTL | 5 | jádro |
| 7 - dva počítače za NATem | 8 | jádro |
| rezerva | 16 | |
| 8 - cíl ve stejné síti | 5 | bonus |
| 9 - port forwarding | 10 | bonus |
| 10 - co je rozbité | 8 | bonus |
| 11 - IPv6 | 5 | bonus |

Síť:

```
PC      192.168.0.10/24   MAC 02:00:00:00:00:0a   brána a DNS 192.168.0.1
R1 LAN  192.168.0.1/24    MAC 02:00:00:00:00:01
R1 WAN  84.14.25.201/16   MAC 02:00:00:00:00:02   výchozí brána 84.14.0.1 (ISP)
internet: 5 routerů
R2      47.85.0.1/16      MAC 02:00:00:00:00:21
server  47.85.1.25/16     MAC 02:00:00:00:00:25   HTTP :80, www.stranka.cz
PC i server posílají s TTL 64, NAT na R1 přidělí vnější port 40001
```

Pravidla: MAC = další skok (mění se na každém routeru), IP = koncové body (mění jen NAT), port mění jen NAT, TTL − 1 na každém routeru.

---

## Příklad 1 - kroky

1. DNS: PC zjistí `www.stranka.cz → 47.85.1.25` (dotaz UDP 53 na R1, viz příklad 5).
2. TCP: PC otevře spojení `192.168.0.10:51000 → 47.85.1.25:80` (port 51000 z efemérního rozsahu, Linux 32768–60999), 3-way handshake SYN, SYN-ACK, ACK.
3. HTTP: `GET / HTTP/1.1`, `Host: www.stranka.cz` → serializace do bajtů → TCP segment → IP paket.
4. Směrování na PC: `47.85.1.25` není v `192.168.0.0/24` → vyhovuje jen `default via 192.168.0.1`.
5. ARP na `192.168.0.1` (pokud není v cache) → Ethernet rámec: src MAC PC, dst MAC R1 LAN → odeslání (fyzická vrstva: kódování, signál).
6. R1 přijme rámec (dst MAC = moje) → rozbalí paket (dst IP ≠ moje) → směruje (výchozí cesta do internetu) → NAT: src `192.168.0.10:51000` → `84.14.25.201:40001`, záznam do NAT tabulky → TTL − 1 → ARP na `84.14.0.1` → nový rámec.
7. Internet: každý router stejně - přijme rámec, sníží TTL, vybere cestu, zabalí do nového rámce.
8. R2: `47.85.1.25` je v přímo připojené síti `47.85.0.0/16` → ARP na server → rámec s dst MAC serveru.
9. Server: rámec pro mě, paket pro mě, TCP port 80 → předá HTTP démonovi → odpověď.
10. Odpověď: `47.85.1.25:80 → 84.14.25.201:40001` stejnou logikou zpět, R1 podle NAT tabulky přepíše cíl na `192.168.0.10:51000` a doručí do LAN.

---

## Příklad 2 - hlavičky cestou tam

```
úsek ①  PC → R1
  MAC  02:..:0a → 02:..:01
  IP   192.168.0.10 → 47.85.1.25
  port 51000 → 80
  TTL  64

úsek ②  R1 → internet (po NAT)
  MAC  02:..:02 → MAC routeru 84.14.0.1
  IP   84.14.25.201 → 47.85.1.25          src IP přepsaná NATem
  port 40001 → 80                         src port přepsaný NATem
  TTL  63                                 R1 snížil o 1

úsek ③  R2 → server
  MAC  02:..:21 → 02:..:25
  IP   84.14.25.201 → 47.85.1.25
  port 40001 → 80
  TTL  64 − 1 (R1) − 5 (internet) − 1 (R2) = 57
```

---

## Příklad 3 - cesta zpět a NAT tabulka

```
úsek ③  server → R2
  MAC  02:..:25 → 02:..:21
  IP   47.85.1.25 → 84.14.25.201
  port 80 → 40001
  TTL  64

úsek ②  internet → R1
  MAC  poslední router ISP → 02:..:02
  IP   47.85.1.25 → 84.14.25.201
  port 80 → 40001
  TTL  64 − 1 (R2) − 5 = 58

úsek ①  R1 → PC (po zpětném NAT)
  MAC  02:..:01 → 02:..:0a
  IP   47.85.1.25 → 192.168.0.10         dst IP přepsaná zpět
  port 80 → 51000                         dst port přepsaný zpět
  TTL  57
```

**b)** NAT tabulka R1:

```
TCP  vnitřní 192.168.0.10:51000   vnější 84.14.25.201:40001   vzdálený 47.85.1.25:80
```

**c)** Paket na `84.14.25.201:40001` bez záznamu: R1 neví, komu patří → zahodí (nebo odpoví RST). Spojení se z pohledu klienta zasekne a skončí timeoutem.

---

## Příklad 4 - ARP

| kdo | ptá se na | proč |
|-----|-----------|------|
| PC | `192.168.0.1` | brána pro cíl mimo LAN |
| R1 | `84.14.0.1` | svoje výchozí brána |
| routery v internetu | svůj další skok | každý segment zvlášť |
| R2 | `47.85.1.25` | server je v přímo připojené síti |
| server | `47.85.0.1` | brána pro odpověď (často už v cache z příchozího paketu) |

PC se na MAC serveru nikdy nezeptá - ARP je broadcast v rámci jedné L2 sítě a server v ní není. ARP cache PC: `192.168.0.1 → 02:00:00:00:00:01`.

---

## Příklad 5 - DNS dotaz

```
PC → R1:   UDP 192.168.0.10:53000 → 192.168.0.1:53    "A www.stranka.cz?"
R1 (rekurzivní resolver) se ptá ze své adresy 84.14.25.201:
   kořenový server → "zeptej se .cz"
   server .cz      → "zeptej se ns.stranka.cz"
   ns.stranka.cz   → "www.stranka.cz A 47.85.1.25, TTL 3600"
R1 → PC:   UDP 192.168.0.1:53 → 192.168.0.10:53000    "47.85.1.25"
```

- Dotaz PC → R1 zůstává v LAN, NAT ho nepřekládá.
- Dotazy R1 do internetu jsou provoz samotného routeru (zdroj je jeho WAN adresa), NAT nepotřebují.
- S DNS `8.8.8.8` jde dotaz z PC přes bránu jako každý jiný paket: ARP na bránu, NAT vytvoří UDP záznam `192.168.0.10:53000 ↔ 84.14.25.201:40002 ↔ 8.8.8.8:53`.

---

## Příklad 6 - TTL

```
a) 64 − 7 = 57      (R1 + 5 routerů + R2)
b) odpověď: 64 − 7 = 57 → "ttl=57"
c) traceroute: 1 R1, 2–6 internet, 7 R2, 8 server → 8 řádků
```

---

## Příklad 7 - dva počítače za NATem

```
TCP  192.168.0.10:51000  ↔  84.14.25.201:40001  ↔  47.85.1.25:80
TCP  192.168.0.11:51000  ↔  84.14.25.201:40002  ↔  47.85.1.25:80
```

Odpověď na `:40001` patří PC1, na `:40002` PC2. Server vidí dvě spojení ze stejné IP `84.14.25.201`, lišící se jen portem.

---

## Příklad 8 (bonus) - cíl ve stejné síti

`192.168.0.20` je v `192.168.0.0/24` → směrovací tabulka PC vybere `192.168.0.0/24 dev eth0` (přímo). ARP na `192.168.0.20`, rámec s MAC tiskárny přes switch. Router nic nedělá, TTL dorazí 64, NAT neproběhne.

---

## Příklad 9 (bonus) - port forwarding

```
pravidlo R1 (DNAT):  TCP 84.14.25.201:4242 → 192.168.0.50:4242

tam:   203.0.113.7:55555 → 84.14.25.201:4242      (internet → R1)
       203.0.113.7:55555 → 192.168.0.50:4242      (R1 → server, přepsaný cíl)
zpět:  192.168.0.50:4242 → 203.0.113.7:55555      (server → R1)
       84.14.25.201:4242 → 203.0.113.7:55555      (R1 → internet, přepsaný zdroj)
```

Privátní adresy `192.168.0.0/16` se v internetu nesměrují (stejnou mají miliony domácností), kamarád proto musí cílit na veřejnou adresu R1.

---

## Příklad 10 (bonus) - co je rozbité?

```
a) LAN a brána OK, chyba za R1          → traceroute 47.85.1.25, ip route na R1
b) IP konektivita OK, chyba v DNS       → dig www.stranka.cz; dig @8.8.8.8 www.stranka.cz
c) IP OK, TCP 80 bez odpovědi = filtr   → nc -zv 47.85.1.25 80, firewall na serveru / R2
d) RST = paket došel, nikdo neposlouchá → na serveru ss -tlnp | grep :80
```

---

## Příklad 11 (bonus) - IPv6

- Zdroj `2001:db8:1::10` je stejný na všech úsecích, NAT se nepoužívá.
- ARP → NDP (Neighbor Solicitation na solicited-node multicast, Neighbor Advertisement). TTL → Hop Limit, snižuje se stejně.
- NAT tabulka není. Ochranu před příchozími spojeními dává stavový firewall na R1: pouští jen pakety patřící spojení navázaným zevnitř.
