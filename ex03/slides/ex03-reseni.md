# KIV/UPS cvičení 3. - řešení příkladů

## Plán cvičení

| příklad | min | |
|---------|-----|-|
| úvod, tahák jazyků | 5 | |
| 1 - bajty z `DataOutputStream` | 10 | jádro |
| 2 - C server čte Javu | 8 | jádro |
| 3 - text a konce řádků | 10 | jádro |
| 4 - Python `struct` | 10 | jádro |
| 5 - C# `BinaryWriter` | 8 | jádro |
| 6 - jedna zpráva, tři jazyky | 15 | jádro |
| 7 - co se skrývá pod obalem | 10 | jádro |
| shrnutí | 5 | |
| 8 - UTF-8 | 5 | bonus |
| 9 - `ObjectOutputStream` | 5 | bonus |
| 10 - konec spojení | 7 | bonus |
| 11 - vlákna a virtuální vlákna | 7 | bonus |
| 12 - řetězení proudů | 5 | bonus |
| 13 - UDP v Javě | 7 | bonus |

Tahák:

```
síťové pořadí = big-endian (nejvyšší bajt první)
Java DataOutputStream:  big-endian; writeUTF = 2 B délka (v bajtech) + modified UTF-8
C# BinaryWriter:        little-endian; Write(string) = 7bitová délka + UTF-8
Python struct:          '!' = síť, '<' = little, bez prefixu = nativní pořadí + zarovnání
konec spojení:  C recv 0 | Java read -1, readLine null, readInt EOFException | Python b'' | C# Read 0
```

---

## Příklad 1 - bajty z `DataOutputStream`

**a)**

```
writeInt(258)       258 = 1 · 256 + 2 = 0x00000102      → 00 00 01 02
writeShort(-2)      -2 v 16 b dvojkovém doplňku = 0xFFFE  → FF FE
writeBoolean(true)                                     → 01
writeUTF("Ahoj")    délka 4 B = 0x0004, A h o j         → 00 04 41 68 6F 6A
writeBytes("OK\n")  O K \n                              → 4F 4B 0A
                                              celkem 4 + 2 + 1 + 6 + 3 = 16 B
```

**b)** `"KIVU"` = `4B 49 56 55` → `0x4B495655` = `75 · 2^24 + 73 · 2^16 + 86 · 2^8 + 85` = **1 263 097 429**.

---

## Příklad 2 - C server čte Javu

**a)** x86 je little-endian, bajty v paměti čte od nejnižšího:

```
00 00 01 02 → 0x02010000 = 2 · 2^24 + 1 · 2^16 = 33 554 432 + 65 536 = 33 619 968
FF FE       → 0xFEFF = 65 279 → jako short: 65 279 − 65 536 = −257
```

**b)**

```c
static int recv_all(int c, void *p, size_t n) {
    size_t got = 0;
    while (got < n) {
        ssize_t r = recv(c, (char *)p + got, n - got, 0);
        if (r <= 0) return r;          /* 0 = odpojení, -1 = chyba */
        got += r;
    }
    return (int)got;
}

uint32_t nx; uint16_t ny;
if (recv_all(c, &nx, 4) != 4 || recv_all(c, &ny, 2) != 2) { close(c); return; }
int32_t x = (int32_t)ntohl(nx);        /* 258 */
int16_t y = (int16_t)ntohs(ny);        /* -2 */
```

Dále hrozí: `recv` vrátí méně bajtů (řeší `recv_all`), `int`/`short` nemusí mít 4/2 B (řeší `int32_t`, `int16_t`).

---

## Příklad 3 - text a konce řádků

- **a)** `PrintWriter(OutputStream)` nemá autoflush, `println` zapíše jen do bufferu. Server čeká na `\n`, klient v `readLine()` na odpověď → oba čekají navždy. Oprava: `w.flush()` po zprávě nebo `new PrintWriter(out, true)` (autoflush při `println`).
- **b)** `println` používá `System.lineSeparator()`: Linux `\n`, Windows `\r\n`. C server dostane `"LOGIN pepa\r"` a `strcmp` selže.
- **c)** `readLine` vrací řádek až po `\n`, `\r` nebo `\r\n` (bez nich); bez konce řádku blokuje, dokud se spojení nezavře (pak vrátí zbytek, příště `null`).

Robustní verze:

```java
var w = new PrintWriter(new OutputStreamWriter(sock.getOutputStream(), StandardCharsets.UTF_8));
var r = new BufferedReader(new InputStreamReader(sock.getInputStream(), StandardCharsets.UTF_8));
w.print("LOGIN pepa\n");
w.flush();
String odp = r.readLine();
```

---

## Příklad 4 - Python `struct`

```
4242 = 0x1092, 1 = 0x00000001

'!HI'  10 92 | 00 00 00 01              6 B
'<HI'  92 10 | 01 00 00 00              6 B
'HI'   92 10 | 00 00 | 01 00 00 00      8 B   (I zarovnáno na násobek 4 → 2 B výplň; na x86/ARM little-endian)
x = 0x00000102 = 258
```

**b)**

```python
s.sendall(a)                     # send() vrátí počet odeslaných bajtů, může být < len(a)

def recv_all(s, n):
    buf = b''
    while len(buf) < n:
        part = s.recv(n - len(buf))
        if not part:             # b'' = protějšek zavřel spojení
            raise ConnectionError('spojení ukončeno')
        buf += part
    return buf
```

---

## Příklad 5 - C# `BinaryWriter`

**a)**

```
Write(258)          02 01 00 00          int32 little-endian
Write((short)-2)    FE FF                int16 little-endian
Write("Ahoj")       04 41 68 6F 6A       délka jako 7bitové číslo (4 < 128 → 1 B) + UTF-8
```

**b)** Java čte big-endian:

```
readInt   02 01 00 00 → 0x02010000 = 33 619 968
readShort FE FF       → 0xFEFF     = −257
readUTF   04 41       → délka 0x0441 = 1089 B → čeká na dalších 1089 bajtů (máme jen 4: 68 6F 6A + nic)
```

**c)**

```csharp
w.Write(IPAddress.HostToNetworkOrder(258));            // System.Net, int/short/long
// nebo
Span<byte> b = stackalloc byte[4];
BinaryPrimitives.WriteInt32BigEndian(b, 258);          // System.Buffers.Binary
stream.Write(b);
```

---

## Příklad 6 - jedna zpráva, tři jazyky

**a)**

```
'U' 'P'   = 55 50
login     = 01
délka 4   = 00 04     (big-endian)
"pepa"    = 70 65 70 61
→ 55 50 01 00 04 70 65 70 61   (9 B)
```

**b)**

```java
DataOutputStream out = new DataOutputStream(sock.getOutputStream());
byte[] jm = "pepa".getBytes(StandardCharsets.US_ASCII);
out.writeBytes("UP");
out.writeByte(1);
out.writeShort(jm.length);
out.write(jm);
out.flush();
```

```python
import struct
jm = 'pepa'.encode('ascii')
s.sendall(struct.pack('!2sBH', b'UP', 1, len(jm)) + jm)
```

```csharp
var w = new BinaryWriter(client.GetStream());
byte[] jm = Encoding.ASCII.GetBytes("pepa");
w.Write(Encoding.ASCII.GetBytes("UP"));                     // Write(byte[]) = surové bajty bez délky
w.Write((byte)1);
w.Write(IPAddress.HostToNetworkOrder((short)jm.Length));
w.Write(jm);
w.Flush();
```

Ověření bez serveru: `nc -l 4242 | xxd` a spustit klienta.

---

## Příklad 7 - co se skrývá pod obalem

| obal | BSD volání |
|------|------------|
| `new ServerSocket(4242)` / `socket()+bind()+listen()` / `TcpListener.Start()` | `socket`, `bind`, `listen` (Java v Linuxu nastaví i `SO_REUSEADDR`) |
| `accept()` / `AcceptTcpClient()` | `accept` → nový socket pro klienta |
| `new Socket("zcu.cz", 4242)` / `connect(('zcu.cz', 4242))` / `new TcpClient(…)` | `getaddrinfo` (překlad jména) + `socket` + `connect` |
| `in.read(buf)` / `recv(1024)` / `stream.Read(…)` | `recv` (vrací 1 až n bajtů) |
| `close()` / `Close()` | `close` (Windows `closesocket`) |

---

## Příklad 8 - UTF-8 (bonus)

```
Ž  l  u  ť     o  u  č     k  ý
C5 BD 6C 75 C5 A5 6F 75 C4 8D 6B C3 BD   → 9 znaků, 13 B
writeUTF: 00 0D + 13 B = 15 B
strlen = 13, len(str) = 9, len(str.encode()) = 13
```

---

## Příklad 9 - `ObjectOutputStream` (bonus)

- **a)** `AC ED` (STREAM_MAGIC) `00 05` (STREAM_VERSION).
- **b)** Následuje `TC_OBJECT`, popis třídy (`TC_CLASSDESC`, plné jméno třídy, `serialVersionUID`, příznaky, počet a typy položek) a až pak hodnoty `3` a `4`. Implementovat to v C je zbytečně složité a křehké. Mezi dvěma Java programy musí být třída `Tah` stejná (jinak `InvalidClassException`) a deserializace z nedůvěryhodného zdroje umožňuje útoky.

---

## Příklad 10 - konec spojení (bonus)

| jazyk | volání | při zavření spojení |
|-------|--------|---------------------|
| Java | `InputStream.read(buf)` | `-1` |
| Java | `DataInputStream.readInt()` | `EOFException` |
| Java | `BufferedReader.readLine()` | `null` |
| Python | `socket.recv(n)` | `b''` |
| C# | `NetworkStream.Read(…)`, `Socket.Receive(…)` | `0` |

**d)** `recv` po zavření vrací okamžitě `b''` pořád dokola → smyčka tiskne `b''` a spotřebuje 100 % CPU. Oprava:

```python
while True:
    data = conn.recv(1024)
    if not data:
        break
    print(data)
conn.close()
```

---

## Příklad 11 - vlákna a virtuální vlákna (bonus)

```
a) 10 000 · 1 MB = 10 000 MB ≈ 9,8 GiB rezervované virtuální paměti
```

- **b)** Virtuální vlákno je objekt v JVM; jeho zásobník je na haldě a roste podle potřeby (u čekajícího vlákna řádově jednotky kB). Blokující `read` virtuální vlákno "zaparkuje" a nosné vlákno OS obslouží jiné → 10 000 klientů řádově desítky MB.
- **c)** Ne: CPython při blokujícím I/O (`recv`, `accept`) GIL uvolní, ostatní vlákna běží. Problém by byl výpočet v Pythonu (např. AI soupeř) - pak `multiprocessing`.

---

## Příklad 12 - řetězení proudů (bonus)

- **a)** `BufferedOutputStream` drží data (výchozí 8 KiB buffer), dokud se nezaplní nebo nezavolá `flush()`/`close()`. Server nic nedostal, klient blokuje v `readInt()`.
- **b)** Méně systémových volání a malých TCP segmentů. Zprávu sestavit celou, pak `out.flush()`.

```java
out.writeInt(42);
out.flush();
int odp = in.readInt();
```

---

## Příklad 13 - UDP v Javě (bonus)

1. `receive` nastaví `p.getLength()` na délku přijatého datagramu a **další** `receive` přijme nejvýš tolik bajtů → před každým `receive` `p.setLength(buf.length)` (nebo nový `DatagramPacket`).
2. `new String(buf)` převede všech 512 B → `new String(buf, 0, p.getLength(), UTF_8)`.

Odpověď: adresa a port odesílatele jsou v `p.getAddress()`, `p.getPort()` (nebo `p.getSocketAddress()`).
