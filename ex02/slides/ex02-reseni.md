# KIV/UPS cvičení 2. - řešení příkladů

## Plán cvičení

| příklad | min | |
|---------|-----|-|
| úvod, tahák volání | 5 | |
| 1 - nakreslete TCP | 10 | jádro |
| 2 - endianita | 8 | jádro |
| 3 - najděte chyby | 12 | jádro |
| 4 - TCP je proud bajtů | 8 | jádro |
| 5 - chybové stavy | 10 | jádro |
| 6 - doplňte `select()` | 15 | jádro |
| 7 - zvolte architekturu | 10 | jádro |
| shrnutí | 5 | |
| 8 - nakreslete UDP | 5 | bonus |
| 9 - vyplňte adresu | 7 | bonus |
| 10 - kolik bajtů odejde | 5 | bonus |
| 11 - co vrátil `recv` | 7 | bonus |
| 12 - UDP a buffer | 5 | bonus |
| 13 - neblokující socket + `sleep` | 7 | bonus |
| 14 - kolik stojí vlákna | 7 | bonus |
| 15 - totéž ve Windows | 5 | bonus |

Tahák:

```
TCP server:  socket → bind → listen → accept → recv/send → close
TCP klient:  socket → connect → send/recv → close
UDP server:  socket → bind → recvfrom/sendto → close
UDP klient:  socket → sendto/recvfrom → close
síťové pořadí bajtů = big-endian; htons/htonl tam, ntohs/ntohl zpět
recv: > 0 počet bajtů, 0 = protějšek zavřel, -1 = chyba (errno)
```

---

## Příklad 1 - nakreslete TCP

Obrázek `images/seq-tcp.svg`. Postup:

1. Server: `socket()`, `bind(4242)`, `listen()`, pak `accept()` - **blokuje**, dokud se někdo nepřipojí.
2. Klient: `socket()`, `connect()` - **blokuje** po dobu handshake `SYN → SYN+ACK → ACK`.
3. Po ACK se oba odblokují: `connect()` vrátí 0, `accept()` vrátí **nový** socket (poslouchající socket zůstává pro další klienty).
4. Server `recv()` blokuje, dokud nepřijdou data; klient `send("Ahoj")` neblokuje (data jen zkopíruje do bufferu jádra).
5. Server `send("OK")`, klient `recv()` blokuje do příchodu odpovědi.
6. Klient `close()` → FIN; serverový `recv()` vrátí 0 → server zavře socket klienta.

---

## Příklad 2 - endianita

**a)** `8080 / 16 = 505 zb. 0`, `505 / 16 = 31 zb. 9`, `31 = 0x1F` → `8080 = 0x1F90`.

```
po síti (big-endian):     1F 90
v paměti x86 (little):    90 1F
```

**b)** Bez `htons` uloží x86 do struktury bajty `90 1F`, jádro je čte jako síťové pořadí:

```
0x901F = 9 · 4096 + 0 · 256 + 1 · 16 + 15 = 36864 + 31 = 36895
```

**c)** `0x0A000001` → bajty `0A 00 00 01` → **10.0.0.1**. `htonl` na x86 bajty prohodí: `0x0100000A`.

**d)** Port, jehož oba bajty jsou stejné: `0x0000`, `0x0101` = 257, `0x0202` = 514, …, `0x1F1F` = 7967.

---

## Příklad 3 - najděte chyby

```c
int s = socket(AF_INET, SOCK_STREAM, 0);          /* nekontroluje -1 */
struct sockaddr_in a;                             /* chybí memset(&a, 0, sizeof(a)) */
a.sin_family = AF_INET;
a.sin_port = 4242;                                /* htons(4242); takto port 37392 */
a.sin_addr.s_addr = inet_addr("127.0.0.1");       /* jen lokálně → htonl(INADDR_ANY) */
bind(s, (struct sockaddr *)&a, sizeof(a));        /* nekontroluje (Address already in use) */
listen(s, 5);                                     /* nekontroluje */
int c = accept(s, NULL, NULL);                    /* nekontroluje -1 */
char *buf = malloc(256);                          /* nekontroluje NULL */
int n = recv(c, buf, sizeof(buf), 0);             /* sizeof(ukazatele) = 8 → 255 */
buf[n] = '\0';                                    /* n == -1 → buf[-1]; n == 0 → odpojení */
if (strcmp(buf, "LOGIN pepa\n") == 0)             /* zpráva nemusí přijít celá najednou */
    send(c, "OK\n", 4, 0);                        /* 4 → 3, jinak se pošle i \0 */
                                                  /* chybí close(c), close(s), free(buf) */
```

`4242 = 0x1092`, na x86 v paměti `92 10` → síť přečte `0x9210 = 37392`.

---

## Příklad 4 - TCP je proud bajtů

**a)** TCP přenáší proud bajtů, hranice jednotlivých `send` neuchovává. Server dostane celkem 6 B v 1 až 6 voláních, např.:

```
recv → 6 "ABABAB"          (vše najednou, typické na loopbacku)
recv → 2 "AB", recv → 4 "ABAB"
recv → 1 "A", recv → 3 "BAB", recv → 2 "AB"
```

**b)** UDP zachovává hranice zpráv: 3 volání po 2 B (pokud se nic neztratí; pořadí není zaručeno).

**c)** `100 000 / 4096 = 24,4` → nejméně 25 volání; `recv` může vrátit i méně než 4096, takže typicky víc.

---

## Příklad 5 - chybové stavy

| situace | co vidí server | proč |
|---------|----------------|------|
| a) `kill -9` klienta | `recv` vrátí 0 | jádro klienta při ukončení procesu zavře sockety a pošle FIN |
| b) vytažený kabel | nic, `recv` čeká | nic nepřijde, ani FIN; zjistí se až při `send` (po vyčerpání retransmisí, minuty) |
| c) `send` do zavřeného spojení | 1. `send` OK, další SIGPIPE | protějšek odpoví RST, další zápis → signál, proces skončí |
| d) restart serveru | `bind`: Address already in use | port je v TIME_WAIT (řádově desítky sekund) |

Opravy: c) `send(c, buf, len, MSG_NOSIGNAL)` nebo `signal(SIGPIPE, SIG_IGN)`; d) `int on = 1; setsockopt(s, SOL_SOCKET, SO_REUSEADDR, &on, sizeof(on));` před `bind`; b) v protokolu ping/pong a timeout.

---

## Příklad 6 - doplňte `select()`

```c
for (int i = 0; i < n; i++) {
    FD_SET(cl[i], &rd);                       /* (1) */
    if (cl[i] > maxfd) maxfd = cl[i];
}
select(maxfd + 1, &rd, NULL, NULL, NULL);     /* (2) */
if (FD_ISSET(srv, &rd)) {
    int c = accept(srv, NULL, NULL);
    if (c >= 0 && n < 64) cl[n++] = c; else if (c >= 0) close(c);
}
for (int i = 0; i < n; i++)
    if (FD_ISSET(cl[i], &rd)) {               /* (3) */
        int r = recv(cl[i], buf, sizeof(buf), 0);
        if (r <= 0) { close(cl[i]); cl[i] = cl[--n]; i--; }   /* odpojen: přesunout poslední na jeho místo */
        else handle(i, buf, r);
    }
```

- `select` v `rd` nechá jen sockety, na kterých jsou data → před každým voláním se množina musí naplnit znovu.
- 1. parametr = nejvyšší deskriptor + 1 (velikost bitové mapy), ne počet socketů.
- `i--` po odebrání: na pozici `i` je teď jiný klient, kterého je potřeba také zkontrolovat.

---

## Příklad 7 - zvolte architekturu

| scénář | doporučení | proč |
|--------|-----------|------|
| a) piškvorky, 20 hráčů | A (nebo C) | malá zátěž, nejjednodušší kód; vlákno čeká na `recv` svého klienta |
| b) chat, 500 klientů | C | zpráva = krátká práce; 500 vláken by jen spalo a zabíralo paměť |
| c) lobby + 100 místností | D | místnosti jsou nezávislé, vlákno místnosti obsluhuje jen svoje 4 sockety |
| d) AI počítá sekundy | B | výpočet v jiném vlákně, síťové vlákno dál obsluhuje ostatní klienty |

Jiné odpovědi jsou přípustné, pokud je student zdůvodní. Ve variantách A, B, D vlákna sdílí stav (seznam hráčů, místnosti) → mutex.

---

## Příklad 8 - nakreslete UDP (bonus)

Obrázek `images/seq-udp.svg`.

- **a)** odpadá `listen`, `accept`, `connect` (není spojení) a s nimi handshake a FIN.
- **b)** `recvfrom(s, buf, len, 0, (struct sockaddr *)&from, &fromlen)` vyplní adresu a port odesílatele; server pošle odpověď `sendto(…, &from, fromlen)`.
- **c)** Datagram dojde na počítač serveru, na portu nikdo neposlouchá → ICMP port unreachable, datagram zahozen. Klient blokuje na `recvfrom` navždy → nastavit timeout:

```c
struct timeval tv = { .tv_sec = 2 };
setsockopt(s, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));   /* recvfrom pak vrátí -1, errno EAGAIN */
```

---

## Příklad 9 - vyplňte adresu (bonus)

```c
struct sockaddr_in a;
memset(&a, 0, sizeof(a));
a.sin_family      = AF_INET;
a.sin_port        = htons(4242);
a.sin_addr.s_addr = htonl(INADDR_ANY);                 /* server */
inet_pton(AF_INET, "192.168.1.42", &a.sin_addr);       /* klient, vrací 1 = OK */
bind(s, (struct sockaddr *)&a, sizeof(a));
```

IPv6:

```c
struct sockaddr_in6 a6;
memset(&a6, 0, sizeof(a6));
a6.sin6_family = AF_INET6;
a6.sin6_port   = htons(4242);
a6.sin6_addr   = in6addr_any;                          /* nebo inet_pton(AF_INET6, "2001:db8:1::42", …) */
```

`struct sockaddr` je "obecná" hlavička, podle `sa_family` jádro pozná skutečný typ; délka zajistí, že nečte mimo strukturu.

---

## Příklad 10 - kolik bajtů odejde (bonus)

```
strlen("KIVUPS")   = 6        K I V U P S
sizeof("KIVUPS")   = 7        K I V U P S \0
sizeof(char *)     = 8        ukazatel na 64bit systému → KIVUPS\0 + 1 bajt za řetězcem
sizeof(char a[])   = 7        pole o 7 prvcích
```

---

## Příklad 11 - co vrátil `recv` (bonus)

- `n == 100` - buffer se zaplnil, další data mohou čekat v jádře.
- `n == 37` - normální; zpráva může být rozdělena, dočíst.
- `n == 0` - protějšek poslal FIN; další `recv` bude vracet 0 → `close()`.
- `n == -1, ECONNRESET` - přišel RST (protějšek spadl, zavřel s neprečtenými daty) → `close()`.
- `n == -1, EINTR` - přerušeno signálem, nic se nestalo → zopakovat.

---

## Příklad 12 - UDP a buffer (bonus)

- **a)** vrátí 512, zbylých 488 B je zahozeno (Linux: příznak `MSG_TRUNC` v `msg_flags`, s `recv(…, MSG_TRUNC)` vrátí skutečnou délku 1000).
- **b)** 100 - jedno volání vrátí vždy právě jeden datagram.
- **c)** IPv4 garantuje doručení paketu 576 B bez fragmentace → po odečtení hlaviček IP (20) a UDP (8) ~ 548 B, proto "do 500 B". Na Ethernetu bez fragmentace: `1500 − 20 − 8 = 1472 B`.

---

## Příklad 13 - neblokující socket + `sleep` (bonus)

- **a)** zpráva čeká v jádře, než se smyčka probudí → zpoždění 0–1 s (průměr 0,5 s). Bez `sleep` smyčka točí `recv` → `EAGAIN` pořád dokola = 100 % jednoho jádra.
- **b)** `recv` vrací 0 pořád dokola, smyčka nikdy neskončí.
- **c)**

```c
for (;;) {
    int r = recv(c, buf, sizeof(buf), 0);    /* blokující: vlákno spí, dokud nepřijdou data */
    if (r <= 0) break;                       /* odpojení nebo chyba */
    handle(buf, r);
}
close(c);
```

---

## Příklad 14 - kolik stojí vlákna (bonus)

```
a) 1 000 · 8 MB  =  8 000 MB ≈ 7,8 GiB virtuální paměti
   10 000 · 8 MB = 80 000 MB ≈ 78 GiB
c) 3 GB = 3072 MB; 3072 / 8 = 384 vláken (minus místo pro kód a haldu)
```

- **b)** `mmap` zásobníku jen rezervuje adresy; fyzická stránka (4 kB) se přidělí až při prvním zápisu. Vlákno, které jen čeká v `recv`, použije pár stránek. Proto `top` ukazuje velké VIRT, ale malé RES.
- **d)** `fork()` zkopíruje proces (copy-on-write) → změna stavu hry v jednom procesu není vidět v ostatních; sdílení přes pipe, sdílenou paměť, soubory. Vlákna sdílí paměť přímo, ale přístup musí hlídat mutex.

---

## Příklad 15 - totéž ve Windows (bonus)

```c
#include <winsock2.h>
#include <ws2tcpip.h>            /* inet_pton, getaddrinfo */
#pragma comment(lib, "ws2_32.lib")

WSADATA w;
if (WSAStartup(MAKEWORD(2, 2), &w) != 0) return 1;
SOCKET s = socket(AF_INET, SOCK_STREAM, 0);
if (s == INVALID_SOCKET) printf("chyba %d\n", WSAGetLastError());
/* … bind, listen, accept, recv, send stejně … */
closesocket(s);
WSACleanup();
```

`select()` ve Windows přijme jen sockety - nelze v něm čekat současně na stdin nebo soubor.
