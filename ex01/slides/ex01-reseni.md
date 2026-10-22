# KIV/UPS cvičení 1. - řešení příkladů

Postup diagnostiky (zdola nahoru):

```
1. link       ip link / ipconfig          je kabel / Wi-Fi připojené? (UP, LOWER_UP vs. NO-CARRIER)
2. adresa     ip a / ipconfig /all        mám adresu? 169.254.x.x = DHCP selhal, jen fe80:: = nepřišlo RA
3. brána      ip r, ip -6 r, ping <brána> mám default route? vidím na bránu?
4. internet   ping 8.8.8.8, traceroute    funguje směrování ven?
5. DNS        dig, Resolve-DnsName        funguje překlad jmen?
6. aplikace   ss -tlnp, nc, tcpdump       poslouchá server? co teče po drátě?
```

Adresy v příkladech: `192.168.1.0/24` je lokální síť, `192.0.2.0/24`, `198.51.100.0/24` a `203.0.113.0/24` jsou dokumentační adresy (RFC 5737), pro IPv6 `2001:db8::/32` (RFC 3849); lokální IPv6 síť je `2001:db8:1::/64` a zastupují "internet".

Plán cvičení (90 min, z toho ~10 min zápočet a semestrálka):

| příklad | min | |
|---|---|---|
| 1 | 5 | jádro |
| 2 | 8 | jádro |
| 3 | 5 | jádro |
| 4 | 5 | jádro |
| 5 | 5 | jádro |
| 6 | 5 | jádro |
| 7 | 5 | jádro |
| 8 | 5 | jádro |
| 9 | 8 | jádro |
| 10 | 10 | jádro |
| 11 | 8 | jádro |
| 12 | 6 | jádro |
| 13 | - | bonus |
| 14 | - | bonus |
| 15 | - | bonus |
| 16 | - | bonus |
| 17 | - | bonus |
| 18 | - | bonus |

---

## Příklad 1 - moje síť

**Linux**

```
ip a                     inet 192.168.1.42/24 ... dynamic enp0s3   → adresa, maska /24, "dynamic" = z DHCP
                         link/ether 08:00:27:3a:5c:11               → MAC
ip r                     default via 192.168.1.1 dev enp0s3         → výchozí brána
resolvectl status        DNS Servers: 192.168.1.1                   → DNS (nebo cat /etc/resolv.conf)
ip -6 a                  inet6 2001:db8:1:0:a00:27ff:fe3a:5c11/64 scope global dynamic   → globální IPv6, prefix /64
                         inet6 fe80::a00:27ff:fe3a:5c11/64 scope link                    → link-local
ip -6 r                  default via fe80::3e84:6aff:fe12:3456 dev enp0s3 proto ra        → IPv6 brána (z RA)
```

V `/etc/resolv.conf` je u systemd často jen `nameserver 127.0.0.53` - to je lokální resolver, skutečný DNS server ukáže až `resolvectl status`.

**Windows**

```
ipconfig /all            IPv4 Address, Subnet Mask, Default Gateway, DNS Servers,
                         Physical Address (MAC), DHCP Enabled: Yes
```

**Schéma**

```
   [můj PC]                 [soused]
 192.168.1.42            192.168.1.20
 08:00:27:3a:5c:11       08:00:27:aa:bb:cc
        \                    /
         +------ switch -----+
                   |
              [brána / router]  192.168.1.1, 3c:84:6a:12:34:56
                   |
              ( internet ) --- DNS server (může být i brána sama)
```

- PC, soused i brána mají stejný prefix `192.168.1.` → jsou ve stejné síti a komunikují **přímo** (přes switch)
- MAC adresy znáte jen ve své lokální síti (ARP cache, viz příklad 17)

---

## Příklad 2 - výpis `ip a` a `ip r`

**a) rozhraní**

```
1: lo      loopback 127.0.0.1/8                 - vždy přítomné, nikam nevede
2: enp0s3  UP, LOWER_UP, 192.168.1.42/24        - připojený Ethernet, MAC 08:00:27:3a:5c:11
3: wlp2s0  NO-CARRIER, state DOWN, bez adresy   - Wi-Fi zapnutá, ale nepřipojená
```

Celkem 3 rozhraní, připojené je jen `enp0s3`.

**b) kam půjde paket** - jádro hledá **nejdelší shodný prefix** (longest prefix match):

```
cíl            192.168.1.0/24   10.20.0.0/16   default (/0)   výsledek
8.8.8.8        ne               ne             ano            brána 192.168.1.1
192.168.1.20   ano (/24)        ne             ano            přímo na enp0s3 (ARP na .20)
10.20.5.5      ne               ano (/16)      ano            router 192.168.1.254
127.0.0.1      -                -              -              lo (lokální tabulka, má přednost)
```

- `default` (`0.0.0.0/0`) sedí na **všechno**, ale má nejkratší prefix → použije se, jen když nic jiného nesedí
- loopback řeší samostatná tabulka `local` (`ip route show table local`), paket počítač neopustí

**c)**

```
sudo ip route add 10.20.0.0/16 via 192.168.1.254
```

`192.168.1.254` musí být ve stejné síti jako `enp0s3`, jinak jádro hlásí `Nexthop has invalid gateway`.

---

## Příklad 3 - zápis IPv4 adres a masek

**a)** Maska = prefix jedniček zleva:

```
/20 = 11111111.11111111.11110000.00000000 = 255.255.240.0
/27 = 11111111.11111111.11111111.11100000 = 255.255.255.224
255.255.252.0   → 252 = 11111100 → 8 + 8 + 6 = /22
255.255.255.248 → 248 = 11111000 → 8 + 8 + 8 + 5 = /29
```

Rychle z hlavy: poslední nenulový oktet masky je `256 − velikost bloku` (240 → bloky po 16, 224 → po 32, 252 → po 4, 248 → po 8).

**b)**

```
192.168.1.42 = 11000000.10101000.00000001.00101010     (42 = 32 + 8 + 2)
10.0.0.255   = 00001010.00000000.00000000.11111111
```

**c)**

- `192.168.1.256` - oktet má 8 bitů, max. 255
- `255.255.253.0` - jako maska neplatná: `253 = 11111101`, jedničky masky musí být souvislé zleva
- `10.1.2` - formálně neúplná; `inet_aton()` ji přečte jako `10.1.0.2` (poslední číslo vyplní zbylých 16 bitů)
- `010.0.0.1` - `inet_aton()` bere úvodní 0 jako osmičkovou soustavu → `8.0.0.1`

**d)**

```
/24: 2^8 = 256 adres, 256 − 2 = 254 počítačů
/26: 2^6 = 64 adres,  62 počítačů
/30: 2^2 = 4 adresy,  2 počítače (spoj dvou routerů)
```

---

## Příklad 4 - zápis IPv6 adres

Pravidla zkracování (RFC 5952):

```
1. v každé 16bitové skupině vynechat úvodní nuly        0db8 → db8, 0000 → 0
2. nejdelší souvislou řadu nulových skupin nahradit ::   (jen jednou!)
3. při dvou stejně dlouhých řadách zkrátit tu první
4. jediná nulová skupina se na :: nezkracuje             (zůstane :0:)
5. malá písmena
```

**a)**

```
2001:0db8:0000:0000:0000:ff00:0042:8329
2001: db8:   0:   0:   0:ff00:  42:8329     (pravidlo 1)
2001:db8::ff00:42:8329                       (pravidlo 2 - tři nulové skupiny)

fe80:0000:0000:0000:0a00:27ff:fe3a:5c11
fe80::a00:27ff:fe3a:5c11

2001:0db8:0000:0001:0000:0000:0000:0001
2001:db8:0:1:0:0:0:1                         řady nul: 1 skupina (3.) a 3 skupiny (5.-7.)
2001:db8:0:1::1                              zkrátí se delší řada

2001:0db8:0000:0000:0001:0000:0000:0001
2001:db8:0:0:1:0:0:1                         dvě řady po 2 skupinách
2001:db8::1:0:0:1                            zkrátí se první
```

**b)** Při rozvinutí se `::` nahradí tolika nulovými skupinami, aby jich bylo celkem 8:

```
2001:db8::1   → 2 + 1 skupin známých, chybí 5   → 2001:0db8:0000:0000:0000:0000:0000:0001
::1           → 1 známá, chybí 7                → 0000:0000:0000:0000:0000:0000:0000:0001
fe80::a:b     → 3 známé, chybí 5                → fe80:0000:0000:0000:0000:0000:000a:000b
```

**c)** Všechny tři jsou neplatné:

- `2001:db8::1::2` - dvě `::`; nedá se určit, kolik nul patří ke které (`2001:db8:0:1:0:0:0:2`? `2001:db8:0:0:0:1:0:2`?)
- `2001:db8:0:0:0:0:0:1:5` - 9 skupin = 144 bitů
- `2001:db8::g1` - `g` není hexadecimální číslice

---

## Příklad 5 - jaký typ IPv4 adresy?

```
adresa            rozsah             typ                               dosah                       IPv6
127.0.0.1         127.0.0.0/8        loopback                          tento počítač               ::1
169.254.13.7      169.254.0.0/16     link-local (nouzová bez DHCP)     lokální linka               fe80::/10
10.0.0.5          10.0.0.0/8         privátní                          vnitřní síť, ven přes NAT   fd00::/8
172.20.1.1        172.16.0.0/12      privátní (172.16.0.0–172.31.255.255)
172.32.1.1        -                  VEŘEJNÁ (mimo 172.16/12)          internet
192.168.1.10      192.168.0.0/16     privátní
192.168.1.255     192.168.1.0/24     broadcast této sítě               lokální síť                 (ff02::1)
255.255.255.255   -                  omezený broadcast                 lokální linka               (ff02::1)
224.0.0.1         224.0.0.0/4        multicast (všechny uzly)          lokální linka               ff02::1
0.0.0.0           0.0.0.0/8          nespecifikovaná                   "žádná" / "všechny" (bind)  ::
100.64.12.3       100.64.0.0/10      sdílený prostor operátora (CGNAT) síť operátora               -
192.0.2.10        192.0.2.0/24       dokumentační (RFC 5737)           nesměruje se                2001:db8::/32
```

- `172.16.0.0/12` končí na `172.31.255.255` (12 bitů: 172 = 8 bitů, z druhého oktetu jen horní 4 → 16–31)
- broadcast sítě = všechny hostitelské bity 1; pro `/24` je to `.255`
- IPv6 broadcast nemá - "všem na lince" je multicast `ff02::1`

---

## Příklad 6 - jaký typ IPv6 adresy?

```
adresa                       rozsah            typ                            dosah
::1                          ::1/128           loopback                       tento počítač
fe80::3e84:6aff:fe12:3456    fe80::/10         link-local unicast             jen lokální linka
2001:db8:1::42               2000::/3          globální unicast (dokumentační) internet
fd12:3456:789a::1            fc00::/7 (fd..)   ULA - unique local             organizace, ne internet
ff02::1                      ff00::/8          multicast (všechny uzly)       lokální linka (ff02 = link scope)
::                           ::/128            nespecifikovaná                "žádná" (zdroj při startu) / "všechny" (bind)
```

- `2001:db8::/32` je vyhrazený pro dokumentaci - v internetu se nesměruje, ale jinak se chová jako globální adresa
- IPv6 nemá broadcast; "všem na lince" = multicast `ff02::1`
- link-local adresu má v IPv6 **každé** rozhraní vždy, IPv4 `169.254.x.x` jen jako nouzové řešení

---

## Příklad 7 - ping a TTL

**a)** Každý router sníží TTL o 1. Odpověď přišla s `ttl=57`.

```
výchozí TTL operačních systémů:  Linux, macOS = 64,  Windows = 128,  síťové prvky často 255
nejbližší vyšší hodnota k 57 je 64  →  64 − 57 = 7 routerů na cestě zpět
```

Kdyby přišlo `ttl=121`, šlo by nejspíš o Windows: `128 − 121 = 7`. Je to jen odhad - cesta tam a zpět se může lišit a výchozí TTL lze změnit.

**b)** `time` = RTT (Round-Trip Time), doba od odeslání Echo Request do příchodu Echo Reply, tedy **tam i zpět**. Cesta jedním směrem je zhruba polovina, ale přesně to z pingu zjistit nejde.

**c)** Ping používá ICMP, web TCP na portu 80/443. Firewall (na serveru nebo cestou) může ICMP zahazovat a TCP pouštět. Ověření portu: `nc -zv 192.0.2.80 443`, `curl -I https://...`, ve Windows `Test-NetConnection 192.0.2.80 -Port 443`.

**d)** `ping fe80::3e84:6aff:fe12:3456` → `connect: Invalid argument`

Link-local prefix `fe80::/64` existuje na **každém** rozhraní (`enp0s3`, `wlp2s0`, ...). Z adresy nejde poznat, na kterou linku paket poslat, proto je potřeba uvést zónu (rozhraní):

```
ping fe80::3e84:6aff:fe12:3456%enp0s3
ping -6 -I enp0s3 fe80::3e84:6aff:fe12:3456
```

Ve Windows je zóna číslo rozhraní: `ping fe80::3e84:6aff:fe12:3456%12` (číslo ukáže `ipconfig` nebo `Get-NetIPInterface`).

V IPv6 se pole TTL jmenuje **Hop Limit** a funguje stejně (každý router ho sníží o 1). `ping -6` ho vypisuje jako `ttl=`.

---

## Příklad 8 - traceroute

**a)** Cíl `198.51.100.10` není v síti `192.168.1.0/24` → podle `default` jde paket na bránu `192.168.1.1`. Brána je první router, a tedy první, kdo TTL sníží na 0.

**b)** `* * *` = na všechny 3 sondy s TTL = 3 nepřišla odpověď do timeoutu. Router paket nejspíš normálně přeposílá, jen:

- neposílá ICMP Time Exceeded (filtr), nebo
- má jejich odesílání omezené (rate limit).

Cesta **není** přerušená - hop 4 i cíl odpověděly, takže pakety přes hop 3 prošly. Přerušení by vypadalo tak, že od nějakého řádku dál jsou už jen hvězdičky.

**c)** Na každou hodnotu TTL se posílají 3 sondy (výchozí `-q 3`), časy ukazují kolísání RTT.

**d)**

```
TTL = 1  → router 1 sníží na 0, paket zahodí, pošle ICMP Time Exceeded  → známe hop 1
TTL = 2  → router 1 sníží na 1, router 2 na 0 → Time Exceeded od hop 2  → známe hop 2
...
TTL = 5  → paket dojde až k cíli → cíl odpoví (ICMP Port Unreachable / Echo Reply) → konec
```

Linuxový `traceroute` posílá standardně UDP na vysoké porty, Windows `tracert` ICMP Echo. Proto mohou dát různý výsledek.

**e)** `traceroute -6 2001:4860:4860::8888` (IPv6 DNS server Google) - první hop je link-local adresa brány nebo její globální adresa, dál bývá cesta **jiná** než pro `8.8.8.8`: IPv6 provoz může jít jinými routery, tunelem nebo jiným poskytovatelem. Pokud počítač nemá globální IPv6 adresu, skončí příkaz hned chybou `connect: Network is unreachable`.

---

## Příklad 9 - kdo poslouchá (`ss -tlnp`)

**a)**

```
Local Address        znamená                         dostupné zvenku?
0.0.0.0:22           všechna IPv4 rozhraní           ano (SSH)
[::]:22              všechna IPv6 rozhraní           ano (SSH přes IPv6)
*:8080               všechna rozhraní, IPv4 i IPv6   ano (Java aplikace)
127.0.0.53%lo:53     jen loopback                    ne (lokální DNS resolver systemd)
127.0.0.1:4242       jen loopback                    ne (upsserver!)
[::1]:5000           jen IPv6 loopback               ne (python3)
```

`*` u Javy = socket na `[::]` bez `IPV6_V6ONLY` - přijímá IPv6 i IPv4 spojení. IPv4 klient se pak v aplikaci jeví jako IPv4-mapped adresa `::ffff:192.168.1.20`.

**b)** Server zavolal `bind` s adresou `127.0.0.1`. Na adrese `192.168.1.42`, port 4242, tedy nikdo neposlouchá. Na příchozí SYN jádro odpoví RST a klient hlásí `Connection refused`. Lokálně (`nc 127.0.0.1 4242`) přitom vše funguje - proto "na mém PC to jde".

Oprava v C:

```c
struct sockaddr_in addr;
memset(&addr, 0, sizeof(addr));
addr.sin_family = AF_INET;
addr.sin_port = htons(4242);
addr.sin_addr.s_addr = htonl(INADDR_ANY);   /* 0.0.0.0 - všechna rozhraní */
bind(fd, (struct sockaddr *)&addr, sizeof(addr));
```

Po opravě by `ss` ukázal `0.0.0.0:4242`. Pro IPv6 i IPv4 najednou: socket `AF_INET6`, adresa `in6addr_any` (`::`) a `IPV6_V6ONLY` = 0 → `ss` ukáže `*:4242`.

**c)** `-t` TCP, `-l` jen naslouchající (LISTEN), `-n` čísla portů a adres místo jmen (`22` místo `ssh`), `-p` proces a PID. Sloupec procesu u cizích procesů vidí jen `root` → `sudo ss -tlnp`.

---

## Příklad 10 - chat přes `nc` a `tcpdump`

```
#  směr                        příznaky  seq/ack                 význam
1  .20:51544 → .42:4242        [S]       seq 2840213357          SYN - klient chce spojení
2  .42:4242  → .20:51544       [S.]      seq 1094410563, ack …58 SYN-ACK - server souhlasí
3  .20 → .42                   [.]       ack 1                   ACK - spojení navázáno
4  .20 → .42                   [P.]      seq 1:7, length 6       data "Ahoj!\n" (6 bajtů)
5  .42 → .20                   [.]       ack 7                   server potvrzuje bajty 1-6
6  .20 → .42                   [F.]      seq 7                   klient končí (Ctrl+D / Ctrl+C)
7  .42 → .20                   [F.]      ack 8                   server také končí
8  .20 → .42                   [.]       ack 2                   poslední ACK
```

- **klient** je ten, kdo posílá první SYN: `192.168.1.20`, port `51544` - náhodný (efemérní) port přidělený jádrem při `connect`
- **server** `192.168.1.42:4242` - port zvolený v `nc -l 4242`
- `ack 2840213358` = ISN klienta + 1 (SYN "spotřebuje" jedno pořadové číslo, stejně jako FIN)
- od řádku 3 tcpdump píše **relativní** čísla (od ISN); absolutní ukáže přepínač `-S`
- `seq 1:7` = bajty 1 až 6; `ack 7` = "další čekám bajt 7"
- `ack 8` na FIN klienta (FIN zabral pořadové číslo 7), `ack 2` na FIN serveru

Data přímo ve výpisu: `sudo tcpdump -i enp0s3 -nn -A port 4242` (`-A` = ASCII obsah) nebo `-X` (hex + ASCII).

**IPv6** (`nc -6 -l 4242` na A, `nc 2001:db8:1::42 4242` na B, `sudo tcpdump -i enp0s3 -nn ip6 and port 4242`):

```
IP6 2001:db8:1::20.51544 > 2001:db8:1::42.4242: Flags [S], seq ..., length 0
IP6 2001:db8:1::42.4242 > 2001:db8:1::20.51544: Flags [S.], ...
...
```

Mění se jen síťová vrstva (`IP6`, adresy); TCP část - příznaky, `seq`, `ack`, `length` - je stejná. Port se od IPv6 adresy odděluje tečkou (tcpdump) nebo zápisem `[2001:db8:1::42]:4242` (URL, `ss`).

---

## Příklad 11 - co je rozbité?

**a) brána ano, 8.8.8.8 ne**

```
ip r                       je tam "default via 192.168.1.1"?  ping brány funguje i bez default route!
                           chybí → sudo ip route add default via 192.168.1.1
traceroute -n 8.8.8.8      kde se cesta zastaví?
  - za hop 1 už jen * * *  → problém na bráně / u poskytovatele (router nemá cestu ven, NAT, firewall)
ping 1.1.1.1               jen zablokovaný 8.8.8.8, nebo nic?
```

**b) 8.8.8.8 ano, seznam.cz ne**

IP konektivita funguje, chyba je v překladu jmen (DNS).

```
resolvectl status          / cat /etc/resolv.conf     jaký DNS server je nastavený?
dig seznam.cz              timeout / SERVFAIL?
dig @8.8.8.8 seznam.cz     funguje → vadný nebo nedostupný nastavený DNS server
                           nefunguje → někdo blokuje DNS (UDP/TCP 53)
```

**c) adresa 169.254.13.7/16**

`169.254.0.0/16` je link-local autokonfigurace - počítač si ji přidělil sám, protože **nedostal odpověď od DHCP**. Bez brány a DNS nejde nic mimo lokální segment.

```
ip link                    je link UP? (pokud ne → bod d)
sudo dhclient -v enp0s3    / nmcli con up ...   chodí DHCPOFFER?
sudo tcpdump -nn port 67 or port 68              odchází DHCPDISCOVER, vrací se něco?
```

Příčiny: nefunkční DHCP server, port switche ve špatné VLAN, vyčerpaný rozsah adres.

**d) NO-CARRIER, state DOWN**

Na fyzické vrstvě není signál: odpojený nebo vadný kabel, vypnutý port switche, ve VM odpojená virtuální karta. Diagnostika: kontrolky na kartě/switchi, `ethtool enp0s3` (`Link detected: no`), jiný kabel/port.

**e) IPv4 jde, IPv6 má jen `fe80::`**

Link-local adresu si rozhraní vytvoří vždy samo. Globální adresa ani výchozí cesta nevznikly, protože **nepřišlo Router Advertisement**.

```
ip -6 r                         chybí "default via fe80::..."
sudo tcpdump -nn -i enp0s3 icmp6    chodí RA (router advertisement)?
                                - nechodí → v síti není IPv6 router / switch RA filtruje (RA guard)
                                - chodí, ale adresa nevzniká → příznak M (adresa jen z DHCPv6), nebo
                                  net.ipv6.conf.enp0s3.accept_ra = 0
```

Mnoho sítí IPv6 vůbec nemá - pak je to normální stav a aplikace musí použít IPv4.

---

## Příklad 12 - semestrálka se nepřipojí

**a) `Connection refused` (okamžitě)**

Paket k A **došel** a jádro A odpovědělo RST = na tomto `IP:port` nic neposlouchá.

```
na A:  ss -tlnp | grep 4242       běží server? na jakém portu? 127.0.0.1 nebo 0.0.0.0?
```

Typicky: server spadl, jiný port v konfiguraci, `bind` na `127.0.0.1` (příklad 9).

**b) `Connection timed out`**

Na SYN nepřišla **žádná** odpověď - klient několikrát opakoval a vzdal to.

```
na B:  ping <A>                   je A vůbec vidět?
na B:  nc -zv <A> 4242            test portu bez vlastního klienta
na A:  sudo tcpdump -nn port 4242 přichází SYN?
         - nepřichází → špatná IP, směrování, firewall cestou
         - přichází, ale bez SYN-ACK → firewall na A (iptables/nftables, Windows Defender Firewall)
```

**c) `No route to host`**

Klient dostal ICMP Host Unreachable nebo nezná cestu: chybí route, ARP na cíl neodpovídá (stroj je vypnutý, jiná síť), firewall odmítá s `icmp-host-prohibited`. Ověření: `ip r get <A>`, `ip neigh` (stav `FAILED` = ARP bez odpovědi).

**d) spojení je, ale server "nic nedostane"**

Síť je v pořádku (handshake proběhl), problém je v aplikaci nebo protokolu:

```
sudo tcpdump -nn -A port 4242     odchází vůbec něco? jaké bajty?
```

Časté příčiny: klient nevolá `flush()` (Java `BufferedWriter`/`PrintWriter`), chybí oddělovač `\n` a server čeká na konec řádku, špatný formát zprávy (magic, délka, padding), server čte víc bajtů, než přišlo, a blokuje v `recv`.

**e) `localhost` jde, IPv4 adresa ne, `::1` taky ne**

```
nc localhost 4242      → funguje
nc 192.168.1.42 4242   → refused
nc ::1 4242            → refused
```

Server poslouchá jen na `127.0.0.1`: `localhost` se přeložil na `127.0.0.1` (v `/etc/hosts`), adresa karty ani IPv6 loopback nemají naslouchající socket. Oprava jako v příkladu 9 - `bind` na `0.0.0.0` (jen IPv4) nebo `::` bez `IPV6_V6ONLY` (obojí). Pozor i na opačný případ: server jen na `::1` a klient, kterému se `localhost` přeložil na `127.0.0.1`.

---

## Příklad 13 - konfigurace ručně (ve dvojici) (bonus)

PC X a soused Y (X, Y = čísla počítačů), oba na `enp0s3`.

```
# a) IPv4 adresa ze sítě 10.99.0.0/24
sudo ip addr add 10.99.0.X/24 dev enp0s3
ip a show enp0s3                         → přibyl řádek inet 10.99.0.X/24
ip r                                     → přibyla cesta 10.99.0.0/24 dev enp0s3 proto kernel
ping 10.99.0.Y

# b) IPv6
sudo ip -6 addr add 2001:db8:99::X/64 dev enp0s3
ping -6 2001:db8:99::Y

# c) cesta přes souseda
sudo ip route add 10.50.0.0/16 via 10.99.0.Y
ip route get 10.50.1.1                   → 10.50.1.1 via 10.99.0.Y dev enp0s3 src 10.99.0.X

# d) úklid
sudo ip route del 10.50.0.0/16
sudo ip addr del 10.99.0.X/24 dev enp0s3
sudo ip -6 addr del 2001:db8:99::X/64 dev enp0s3
```

- Obě adresy (`192.168.1.X` z DHCP i `10.99.0.X`) jsou na jedné kartě současně - rozhraní může mít adres libovolně mnoho.
- Paket na `10.50.1.1` teď odejde sousedovi. Ten ho bez zapnutého přeposílání (`sysctl net.ipv4.ip_forward=1`) a vlastní cesty dál nepošle - ping tedy neprojde, ale `tcpdump` na sousedovi ho ukáže.
- Ruční změny přes `ip` po restartu (nebo po obnovení DHCP) zmizí. Trvale: `nmcli`, netplan, `/etc/network/interfaces` podle distribuce.

Windows (PowerShell jako správce):

```
New-NetIPAddress -IPAddress 10.99.0.X -PrefixLength 24 -InterfaceAlias Ethernet
New-NetIPAddress -IPAddress 2001:db8:99::X -PrefixLength 64 -InterfaceAlias Ethernet
route ADD 10.50.0.0 MASK 255.255.0.0 10.99.0.Y
Remove-NetIPAddress -IPAddress 10.99.0.X
```

---

## Příklad 14 - DHCP: výpis `ip -4 a` a zachycení (bonus)

**a)**

- `dynamic` u adresy a `proto dhcp` u výchozí cesty = obojí přišlo z DHCP (ručně přidaná adresa by měla `valid_lft forever`)
- `valid_lft 85980sec` = zápůjčka (lease) platí ještě 85 980 s; typická zápůjčka 1 den = 86 400 s, uplynulo tedy 420 s

**b)** DORA:

```
1 Discover  klient → broadcast   "je tu DHCP server?"          klient nemá adresu → zdroj 0.0.0.0
2 Offer     server → klient      "nabízím 192.168.1.42/24"
3 Request   klient → broadcast   "beru 192.168.1.42 od 192.168.1.1"  (ostatní servery vědí, že prohrály)
4 ACK       server → klient      "potvrzuji, lease 86400 s"
```

Klient ještě nemá adresu (zdroj `0.0.0.0`) ani nezná server (cíl `255.255.255.255`). Server odpovídá broadcastem nebo přímo na MAC klienta - podle příznaku v Discover. Porty: server 67, klient 68 (UDP).

**c)** Kromě adresy: maska (option 1), brána (option 3), DNS servery (option 6), doména (option 15), doba zápůjčky (option 51), případně NTP apod.

IPv6 (příklad 15): bránu a prefix ohlásí router v RA, adresu si počítač složí sám (SLAAC) nebo ji dostane z DHCPv6; DNS přijde v RA (RDNSS) nebo z DHCPv6. Výchozí bránu DHCPv6 nepředává.

Obnova: v T1 = 50 % zápůjčky klient pošle Request přímo serveru (unicast); když neodpoví, v T2 = 87,5 % broadcastem; po vypršení adresu zahodí a začne znovu od Discover.

---

## Příklad 15 - výpis `ip -6 a` a `ip -6 r` (bonus)

**a)** `enp0s3` má 3 IPv6 adresy:

```
2001:db8:1:0:5d2e:91c4:7b1a:3f02/64  global temporary  - dočasná (privacy), náhodná, pro odchozí spojení
2001:db8:1:0:a00:27ff:fe3a:5c11/64   global            - stabilní, odvozená z MAC (EUI-64)
fe80::a00:27ff:fe3a:5c11/64          link              - link-local, jen lokální linka
```

Navíc `lo` má `::1`. Prefix sítě je ve všech globálních adresách `2001:db8:1:0::/64` = `2001:db8:1::/64`.

**b)** EUI-64 - z 48bitové MAC se udělá 64bitový identifikátor rozhraní:

```
MAC                          08:00:27:3a:5c:11
rozdělit napůl               08:00:27  |  3a:5c:11
vložit ff:fe doprostřed      08:00:27:ff:fe:3a:5c:11
první bajt 08 = 0000 1000
překlopit 7. bit (U/L)       0000 1010 = 0a
výsledek                     0a:00:27:ff:fe:3a:5c:11  →  0a00:27ff:fe3a:5c11  →  a00:27ff:fe3a:5c11
```

Bit U/L (universal/local) říká, zda je identifikátor globálně jedinečný; v IPv6 má obrácený význam, proto se překlápí.

**c)** `temporary` - dočasná adresa podle RFC 8981 (dříve RFC 4941). Stabilní adresa obsahuje MAC → web by mohl poznat stejné zařízení v jakékoli síti. Proto systém pro odchozí spojení používá náhodnou adresu, kterou po čase (typicky den) vymění. `mngtmpaddr` = z této adresy se dočasné odvozují.

**d)**

```
2001:db8:1::/64 dev enp0s3 proto ra       síť na lince, prefix ohlásil router v RA
fe80::/64 dev enp0s3 proto kernel         link-local síť, vytvoří jádro vždy
default via fe80::3e84:6aff:fe12:3456     brána = link-local adresa routeru
```

- router posílá **Router Advertisement** (ICMPv6, na `ff02::1`): "jsem router, prefix sítě je `2001:db8:1::/64`"
- počítač si z prefixu a vlastního identifikátoru složí adresu (**SLAAC**) a odesílatele RA si dá jako výchozí bránu
- RA chodí ze zdrojové link-local adresy routeru, proto je i brána link-local - na sousedy na lince globální adresu nepotřebujeme
- výhoda: když se změní globální prefix (jiný poskytovatel), brána zůstane stejná

**DHCPv6** je alternativa: příznaky v RA (`M` = managed, `O` = other) řeknou, zda si adresu vyžádat od DHCPv6 serveru, nebo jen další údaje (DNS). Výchozí bránu ale DHCPv6 nepředává - ta vždy přichází z RA.

---

## Příklad 16 - DNS (`dig`) (bonus)

Výsledky se v čase mění, výpis níže je ilustrativní (adresy RFC 5737):

```
$ dig zcu.cz A +noall +answer
zcu.cz.        300   IN   A      192.0.2.10

$ dig seznam.cz MX +short
10 mx1.seznam.cz.
20 mx2.seznam.cz.
```

**a)** `dig zcu.cz A`, `dig zcu.cz AAAA` (IPv6; když doména IPv6 nemá, sekce ANSWER je prázdná)

**b)** `dig seznam.cz MX` - číslo před jménem je **priorita**: nižší číslo = zkusí se dřív. Při stejné prioritě se zátěž rozkládá.

**c)** `dig zcu.cz NS` - autoritativní jmenné servery domény (obvykle aspoň 2, kvůli dostupnosti)

**d)** `dig zcu.cz TXT` - typicky:

```
"v=spf1 ... -all"                   SPF - které servery smí posílat poštu za doménu
"google-site-verification=..."      ověření vlastnictví domény pro službu
"MS=..."                            totéž pro Microsoft 365
```

**e)** `dig zcu.cz SOA` - primární jmenný server, e-mail správce (první tečka = `@`), sériové číslo zóny a časovače (refresh, retry, expire, minimum).

**f)** `dig www.<doména> CNAME` nebo jen `dig www.<doména>` - v sekci ANSWER je nejdřív `CNAME` (alias), pak `A` cílového jména. Resolver řetěz projde sám.

```
www.example.org.   3600  IN  CNAME  web.hosting.example.net.
web.hosting.example.net.  300  IN  A  198.51.100.80
```

**ping: IPv4, nebo IPv6?** `ping zcu.cz` přeloží jméno přes `getaddrinfo()`; ten vrátí `AAAA` i `A` a seřadí je podle pravidel RFC 6724. Má-li počítač globální IPv6 a doména `AAAA`, obvykle vyhraje IPv6. Bez globální IPv6 se použije IPv4. `ping -4` / `ping -6` volbu vynutí. Stejně se chová klient semestrálky, který se připojuje na jméno - proto je dobré, aby server poslouchal na obou protokolech.

**TTL (2. sloupec)**

```
zcu.cz.   300   IN   A   ...      →  resolver smí odpověď držet 300 s v cache
o 40 s později:
zcu.cz.   260   IN   A   ...      →  odpovídá cache, TTL se odpočítává
```

Až TTL doběhne na 0, resolver se zeptá autoritativního serveru znovu. Proto se změna DNS záznamu neprojeví hned všude - staré odpovědi dožívají v cache až po dobu TTL.

---

## Příklad 17 - ARP a NDP (bonus)

**a)** `ip neigh` (Windows `arp -a`). Typicky je tam aspoň brána - s ní počítač mluví pořád.

**b)** Po `ping 192.168.1.20`:

```
1. cíl je v mé síti (/24) → potřebuji MAC souseda
2. ARP Request  (broadcast ff:ff:ff:ff:ff:ff): "Who has 192.168.1.20? Tell 192.168.1.42"
3. ARP Reply    (unicast):                     "192.168.1.20 is at 08:00:27:aa:bb:cc"
4. teprve teď odejde ICMP Echo Request v rámci s cílovou MAC 08:00:27:aa:bb:cc
```

V cache přibyl řádek `192.168.1.20 ... lladdr 08:00:27:aa:bb:cc REACHABLE`. ARP lze vidět i v `tcpdump -nn arp`.

Po `ping -6 2001:db8:1::20` (NDP):

```
1. Neighbor Solicitation (ICMPv6) na solicited-node multicast ff02::1:ff00:20
   (ff02::1:ff + posledních 24 bitů cílové adresy) - neruší všechny, jen kandidáty
2. Neighbor Advertisement (unicast): "2001:db8:1::20 je na 08:00:27:aa:bb:cc"
```

V `ip -6 neigh` přibyl `2001:db8:1::20 ... lladdr 08:00:27:aa:bb:cc REACHABLE`. Je to tatáž MAC jako u `192.168.1.20` - stejný počítač, dvě adresy. Záznam brány má příznak `router` (posílá RA). Zachycení: `sudo tcpdump -nn icmp6`.

**c)** Pro `8.8.8.8` záznam **nepřibyl**. `8.8.8.8` není v síti `192.168.1.0/24`, paket jde bráně. ARP se ptá jen v rámci jedné lokální (L2) sítě - broadcast přes router neprojde.

**d)**

```
Ethernet:  src 08:00:27:3a:5c:11 (já)       dst 3c:84:6a:12:34:56 (brána)
IP:        src 192.168.1.42                 dst 8.8.8.8
```

IP adresa = konečný cíl, MAC = nejbližší skok. Každý router rámec rozbalí a pošle dál v novém rámci s novými MAC. IP adresy se cestou nemění (výjimka: NAT na domácím routeru přepíše zdrojovou IP).

---

## Příklad 18 - totéž ve Windows (bonus)

**a)**

```
C:\> ipconfig /all
Ethernet adapter Ethernet:
   Physical Address. . . . . . . . . : 08-00-27-3A-5C-11
   DHCP Enabled. . . . . . . . . . . : Yes
   IPv4 Address. . . . . . . . . . . : 192.168.1.42(Preferred)
   Subnet Mask . . . . . . . . . . . : 255.255.255.0
   Default Gateway . . . . . . . . . : 192.168.1.1
   DNS Servers . . . . . . . . . . . : 192.168.1.1
```

Maska `255.255.255.0` = `/24`. Windows píše MAC s pomlčkami.

IPv6 část téhož výpisu:

```
   IPv6 Address. . . . . . . . . . . : 2001:db8:1:0:a00:27ff:fe3a:5c11(Preferred)
   Temporary IPv6 Address. . . . . . : 2001:db8:1:0:5d2e:91c4:7b1a:3f02(Preferred)
   Link-local IPv6 Address . . . . . : fe80::a00:27ff:fe3a:5c11%12(Preferred)
   Default Gateway . . . . . . . . . : fe80::3e84:6aff:fe12:3456%12
                                       192.168.1.1
```

`%12` = číslo rozhraní (zóna). Windows mívá místo EUI-64 náhodný identifikátor i u stabilní adresy.

**b)**

```
PS> Test-NetConnection 192.168.1.42 -Port 4242

WARNING: TCP connect to (192.168.1.42 : 4242) failed
ComputerName           : 192.168.1.42
RemoteAddress          : 192.168.1.42
RemotePort             : 4242
InterfaceAlias         : Ethernet
SourceAddress          : 192.168.1.20
PingSucceeded          : True
TcpTestSucceeded       : False
```

`PingSucceeded: True` + `TcpTestSucceeded: False` = stroj je vidět, ale na portu nikdo neposlouchá nebo ho blokuje firewall (stejná úvaha jako příklad 12). Když soused poslouchá, je `TcpTestSucceeded: True`.

IPv6: `Test-NetConnection 2001:db8:1::42 -Port 4242` - výstup stejný, `RemoteAddress` a `SourceAddress` jsou IPv6. Při zadání jména `Test-NetConnection` (stejně jako klient) zvolí IPv6, má-li jméno `AAAA` a počítač globální IPv6.

**c)**

```
PS> Get-NetTCPConnection -State Listen -LocalPort 445
LocalAddress  LocalPort  RemoteAddress  RemotePort  State   OwningProcess
0.0.0.0       445        0.0.0.0        0           Listen  4
PS> Get-Process -Id 4
... System
```

```
C:\> netstat -ano | findstr :445
  TCP    0.0.0.0:445    0.0.0.0:0    LISTENING    4
C:\> tasklist /FI "PID eq 4"
System                           4 Services ...
```

Port 445 je SMB (sdílení souborů), obsluhuje ho jádro Windows (proces `System`, PID 4).

**d)**

```
PS> Resolve-DnsName -Name www.google.com -Type AAAA
PS> Resolve-DnsName -Name seznam.cz -Type MX       # NameExchange + Preference (= priorita)
PS> Clear-DnsClientCache                           # totéž co ipconfig /flushdns
```
