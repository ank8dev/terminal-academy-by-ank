# Level 2 — Permission Denied

## The concept

Every Unix file carries **permission bits**: three groups of three.

```
-rw-r--r--
 │ │  │  └── others:  what everyone else may do
 │ │  └───── group:   what members of the file's group may do
 │ └──────── owner:   what the file's owner may do
 └────────── type:    - file, d directory, l link
```

Each group is **r** (read), **w** (write), **x** (execute). A dash means "not
allowed". The same bits as a number: r=4, w=2, x=1, added per group. So
`rw-r--r--` is `644`, and `rw-------` is `600` (owner only).

The vault file is `600` and owned by `root`, so you — a normal user — get
**Permission denied**. That lock is correct. The mistake is elsewhere: a
**backup copy** was left `644` (world-readable). One careless copy undoes the
whole lock.

## The commands

| Command | What it does |
|---|---|
| `ls -l` | Show permission bits, owner and group. |
| `stat <file>` | Show the same, plus the octal mode. |
| `cat <file>` | Read a file (fails without read permission). |
| `find / -name 'flag*' -perm -o=r 2>/dev/null` | Find files named `flag*` that **others can read**. |

`-perm -o=r` means "the 'others' group has at least read". That is exactly the
mistake we are hunting.

## How to solve it

1. `cat /home/player/vault/flag.txt` → `Permission denied`. See the lock with
   `ls -l /home/player/vault`.
2. Hunt for a readable copy (skip the noisy system folders):
   `find /home /var /tmp /opt /etc -name 'flag*' -perm -o=r 2>/dev/null`.
3. `cat` the backup it finds (under `/var/tmp/backups/`) and submit the flag:
   `academy hack submit 2 FLAG{...}`.

## How defenders prevent this

- **Make backups as careful as the original.** A copy should inherit the
  original's strict permissions, not fall back to a default `644`.
- **Audit for world-readable secrets:**
  `find / -perm -o=r -name '*secret*'` style scans, run regularly.
- **Separate duties with groups**, not "readable by everyone". Give a specific
  group access instead of `others`.
- **Encrypt backups.** Even a readable backup file is useless if its contents
  are encrypted.
