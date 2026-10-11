// Mock Tauri API for Browser Environment
// Intercepts invoke and listen calls to run the unmodified React desktop widgets in a browser.

let cmdBuffer = '';
const listeners: Record<string, Function[]> = {};

// Helper to broadcast PTY output to all registered listeners
export const triggerPtyData = (payload: string) => {
  const handlers = listeners['pty-data'] || [];
  handlers.forEach(handler => handler({ payload }));
};

// Simulated State for the Terminal
let configPermissions = '-rwxrwxrwx';
let isSshConnected = false;

// Command Processor
const executeCommand = (command: string) => {
  const cleanCmd = command.trim().replace(/\s+/g, ' ');
  const cmdLower = cleanCmd.toLowerCase();

  if (cmdLower === '') {
    triggerPtyData('\r\nstudent@sandbox:~$ ');
    return;
  }

  if (cmdLower === 'clear') {
    triggerPtyData('\x1b[2J\x1b[Hstudent@sandbox:~$ ');
    return;
  }

  if (cmdLower === 'ls' || cmdLower === 'ls -la' || cmdLower === 'ls -l' || cmdLower === 'ls -li') {
    const showInodes = cmdLower.includes('-li') || cmdLower.includes('i');
    const showDetails = cmdLower.includes('-l') || cmdLower.includes('i');

    let output = '';
    if (showDetails) {
      output = `total 16\r\n`;
      output += `${showInodes ? '1048577 ' : ''}-rw-r--r--   1 student  student   240 Jul 12 14:36 app.py\r\n`;
      output += `${showInodes ? '1048578 ' : ''}${configPermissions}   1 student  student   105 Jul 12 14:36 config.txt\r\n`;
      output += `${showInodes ? '1048579 ' : ''}drwxr-xr-x   2 student  student   4096 Jul 12 14:36 src`;
    } else {
      output = `app.py    config.txt    src`;
    }

    triggerPtyData(`\r\n${output}\r\nstudent@sandbox:~$ `);
    return;
  }

  if (cleanCmd.startsWith('chmod ')) {
    const parts = cleanCmd.split(' ');
    if (parts.length >= 3) {
      const perms = parts[1];
      const file = parts[2];
      if (file === 'config.txt') {
        if (perms === '644' || perms === 'u=rw,g=r,o=r') {
          configPermissions = '-rw-r--r--';
          triggerPtyData(`\r\n\x1b[32m✓ Verification Success!\x1b[0m\r\n- Owner: Read & Write (rw-)\r\n- Group: Read (r--)\r\n- Others: Read (r--)\r\nAnk: "Excellent permissions mapping. You've completed the documentation playground task!"\r\nstudent@sandbox:~$ `);
          return;
        }
      }
    }
    triggerPtyData(`\r\nbash: operation not permitted or invalid command syntax.\r\nAnk: "Try specifying 'chmod 644 config.txt' to grant read-write to owner and read-only to others."\r\nstudent@sandbox:~$ `);
    return;
  }

  if (cleanCmd.startsWith('ssh ')) {
    if (cleanCmd.includes('-L') && cleanCmd.includes('8080') && cleanCmd.includes('80')) {
      isSshConnected = true;
      triggerPtyData(`\r\nssh: Connecting to sandbox [localhost:80]...\r\nstudent@sandbox password: **********\r\n\x1b[32m✓ SSH tunnel established successfully: local port 8080 forwarded.\x1b[0m\r\nstudent@sandbox:~$ `);
      return;
    }
    triggerPtyData(`\r\nssh: connection failed. Make sure to specify local port mappings correctly.\r\nstudent@sandbox:~$ `);
    return;
  }

  if (cmdLower.includes('fail2ban-client status sshd')) {
    triggerPtyData(`\r\nStatus for the jail: sshd\r\n|- Filter\r\n|  |- Currently failed: 1\r\n|  |- Total failed: 14\r\n|  \`- File list: /var/log/auth.log\r\n\`- Actions\r\n   |- Currently banned: 3\r\n   |- Total banned: 3\r\n   \`- Banned IP list: 198.51.100.42, 203.0.113.19, 192.0.2.115\r\nstudent@sandbox:~$ `);
    return;
  }

  if (cmdLower.includes('systemctl status nginx') || cmdLower.includes('service nginx status')) {
    triggerPtyData(`\r\n● nginx.service - High-performance HTTP server\r\n     Loaded: loaded (/lib/systemd/system/nginx.service; enabled)\r\n     Active: active (running) since Sun 2026-07-12 14:30:15 UTC\r\n   Main PID: 824 (nginx)\r\nstudent@sandbox:~$ `);
    return;
  }

  if (cmdLower === 'docker ps' || cmdLower === 'docker ps -a') {
    triggerPtyData(`\r\nCONTAINER ID   IMAGE          COMMAND                  CREATED         STATUS         PORTS\r\n9e8d7c6b5a4f   alpine:latest  "/bin/sh"                10 min ago      Up 10 min      80/tcp -> 8080/tcp\r\nstudent@sandbox:~$ `);
    return;
  }

  if (cmdLower === 'reset-sandbox' || cmdLower === 'reset') {
    triggerPtyData(`\r\n\x1b[33m[SYSTEM] Recycling container sandbox instance...\x1b[0m\r\n\x1b[32m[SYSTEM] Sandbox successfully recycled! Press Enter to start shell.\x1b[0m\r\nstudent@sandbox:~$ `);
    return;
  }

  // Fallback warning from AI Mentor Ank
  triggerPtyData(`\r\nAnk: "Hmm, '${cleanCmd}' is not the focus here. Look at your objectives and the advice bubble."\r\nstudent@sandbox:~$ `);
};

export const invoke = async (cmd: string, args?: any): Promise<any> => {
  console.log(`[Tauri Mock] invoke: ${cmd}`, args);

  if (cmd === 'spawn_pty') {
    setTimeout(() => {
      triggerPtyData('\r\n\x1b[36mWelcome to Terminal Academy local Alpine sandbox PTY!\x1b[0m\r\nstudent@sandbox:~$ ');
    }, 100);
    return Promise.resolve();
  }

  if (cmd === 'write_pty') {
    const data: string = args.data;

    // Handle Enter key
    if (data === '\r' || data === '\n' || data === '\r\n') {
      const commandToRun = cmdBuffer;
      cmdBuffer = '';
      executeCommand(commandToRun);
      return Promise.resolve();
    }

    // Handle Backspace (ASCII 127 or 8)
    if (data === '\x7f' || data === '\x08') {
      if (cmdBuffer.length > 0) {
        cmdBuffer = cmdBuffer.slice(0, -1);
        triggerPtyData('\b \b'); // backspace, space, backspace to delete visually
      }
      return Promise.resolve();
    }

    // Handle Ctrl+C
    if (data === '\x03') {
      cmdBuffer = '';
      triggerPtyData('^C\r\nstudent@sandbox:~$ ');
      return Promise.resolve();
    }

    // Append standard character keys and echo back to XTerm
    cmdBuffer += data;
    triggerPtyData(data);
    return Promise.resolve();
  }

  if (cmd === 'resize_pty') {
    return Promise.resolve();
  }

  if (cmd === 'reset_sandbox') {
    configPermissions = '-rwxrwxrwx';
    isSshConnected = false;
    setTimeout(() => {
      triggerPtyData('\r\n\x1b[33m[SYSTEM] Recycling container sandbox...\x1b[0m\r\n\x1b[32m[SYSTEM] Sandbox successfully recycled!\x1b[0m\r\nstudent@sandbox:~$ ');
    }, 200);
    return Promise.resolve();
  }

  return Promise.reject(new Error(`Unknown mock tauri backend command: ${cmd}`));
};

export const listen = async (event: string, handler: Function): Promise<any> => {
  console.log(`[Tauri Mock] listen: ${event}`);

  if (!listeners[event]) {
    listeners[event] = [];
  }
  listeners[event].push(handler);

  // Return unsubscribe handler
  return Promise.resolve(() => {
    listeners[event] = listeners[event].filter(h => h !== handler);
  });
};
