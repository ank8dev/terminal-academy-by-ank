# Level 1 — Hidden in Plain Sight

## The concept

On Unix-like systems (Linux, macOS), a file or folder whose name starts with a
dot (`.`) is **hidden** from a normal `ls`. Examples you already have on your
own machine: `.bashrc`, `.ssh/`, `.config/`.

This is **not a security feature**. The file is completely readable; it is just
not shown by default, to keep listings tidy. Attackers love this, because people
hide secrets (passwords, API keys, tokens) in dotfiles and then forget they are
there. Finding them is often step one of a real attack.

## The commands

| Command | What it does |
|---|---|
| `ls -a` | List **all** entries, including hidden ones (`-a` = all). |
| `ls -la` | The same, in long format (owner, size, permissions). |
| `find . -name '.*'` | Walk every folder and list hidden entries. |
| `grep -r FLAG .` | Search the text of every file under here for `FLAG`. |
| `cat <file>` | Print a file's contents. |

## How to solve it

1. `ls -a` — notice the dot-folders like `.config`.
2. Walk into them: `cd .config && ls -a`, and keep going.
3. Or skip the walking: `grep -r FLAG . 2>/dev/null` finds the flag text directly.
4. `cat` the file that holds it, copy the `FLAG{...}` value, and submit it:
   `academy hack submit 1 FLAG{...}`.

## How defenders prevent this

- **Never store secrets in files on disk in clear text**, hidden or not. Use a
  secrets manager (Vault, your cloud's secret store) or encrypted files.
- **Scan for secrets.** Tools like `git-secrets`, `trufflehog` and `gitleaks`
  look for tokens that were committed or left on disk by mistake.
- **Least privilege.** If an attacker lands on the box as a low-privilege user,
  make sure there is nothing valuable they can simply read.
- **Remember:** "hidden" only hides from a quick glance. Treat every readable
  file as readable by anyone who reaches that account.
