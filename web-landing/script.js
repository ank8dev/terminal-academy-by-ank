// Intersection Observer for Scroll Reveals
document.addEventListener("DOMContentLoaded", () => {
    // Infinite Scrolling Terminal Logic
    const terminalLines = [
        { type: 'input', text: 'sudo rm -rf /var/www/html' },
        { type: 'ank', text: '[ank]: Hold on right there. Are you trying to nuke the server?' },
        { type: 'ank', text: '[ank]: In a graphical OS, files go to a Recycle Bin. What happens here?' },
        { type: 'input', text: 'it deletes the files' },
        { type: 'ank', text: '[ank]: "It deletes the files" is what my grandma would say.' },
        { type: 'ank', text: '[ank]: Try explaining reference counts and inodes.' },
        { type: 'input', text: 'it unlinks the inode reference' },
        { type: 'ank', text: '[ank]: Better. The reference count drops to 0, data blocks are marked free.' },
        { type: 'input', text: 'iptables -A INPUT -p tcp --dport 22 -j DROP' },
        { type: 'ank', text: '[ank]: ...Did you just drop all SSH traffic?' },
        { type: 'ank', text: '[ank]: Congratulations, you just locked yourself out of the server.' },
        { type: 'ank', text: '[ank]: Hope you have physical access to the datacenter.' },
        { type: 'input', text: 'docker rm $(docker ps -aq)' },
        { type: 'ank', text: '[ank]: Ah, the classic "delete everything and hope it works" strategy.' },
        { type: 'ank', text: '[ank]: Let\'s see what production thinks about that.' }
    ];

    const container = document.getElementById('typewriter-container');
    let lineIndex = 0;
    let charIndex = 0;
    let isEasterEggActive = false;

    function typeLine() {
        if (!container) return;
        
        // Pause infinite loop if easter egg is running
        if (isEasterEggActive) {
            setTimeout(typeLine, 1000);
            return;
        }
        
        const lineData = terminalLines[lineIndex % terminalLines.length];
        
        // Remove previous cursor
        const oldCursor = document.querySelector('.term-cursor');
        if (oldCursor) oldCursor.remove();

        const lineDiv = document.createElement('div');
        lineDiv.className = 'line';
        container.appendChild(lineDiv);

        // Prevent DOM bloat by removing old lines
        if (container.children.length > 50) {
            container.removeChild(container.firstChild);
        }

        if (lineData.type === 'input') {
            lineDiv.innerHTML = '<span class="term-prompt">user@local ~$</span> <span class="term-cmd"></span><span class="term-cursor"></span>';
            const cmdSpan = lineDiv.querySelector('.term-cmd');
            
            function typeChar() {
                if (charIndex < lineData.text.length) {
                    cmdSpan.innerHTML += lineData.text.charAt(charIndex);
                    charIndex++;
                    container.scrollTop = container.scrollHeight;
                    setTimeout(typeChar, Math.random() * 40 + 20);
                } else {
                    charIndex = 0;
                    lineIndex++;
                    setTimeout(typeLine, 600);
                }
            }
            setTimeout(typeChar, 800);
        } else {
            const spanClass = lineData.type === 'ank' ? 'term-ank' : 'term-out';
            lineDiv.innerHTML = `<span class="${spanClass}">${lineData.text}</span><span class="term-cursor"></span>`;
            container.scrollTop = container.scrollHeight;
            lineIndex++;
            setTimeout(typeLine, lineData.type === 'ank' ? 1500 : 300);
        }
    }

    setTimeout(typeLine, 1000);

    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries, obs) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                // Unobserve if you only want it to animate once
                obs.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.reveal-up').forEach(el => {
        observer.observe(el);
    });

    // Count-up Animation
    const statsObserver = new IntersectionObserver((entries, obs) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const countEls = entry.target.querySelectorAll('.count-up');
                countEls.forEach(el => {
                    const target = parseInt(el.getAttribute('data-val'), 10);
                    animateValue(el, 0, target, 1500);
                });
                obs.unobserve(entry.target);
            }
        });
    });

    const statsRow = document.querySelector('.stats-row');
    if (statsRow) statsObserver.observe(statsRow);

    function animateValue(obj, start, end, duration) {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            // Ease out cubic
            const easeProgress = 1 - Math.pow(1 - progress, 3);
            obj.innerHTML = Math.floor(easeProgress * (end - start) + start);
            if (progress < 1) {
                window.requestAnimationFrame(step);
            } else {
                obj.innerHTML = end;
            }
        };
        window.requestAnimationFrame(step);
    }

    // Interactive 3D Terminal Tilt Effect
    const terminalMockup = document.querySelector('.terminal-mockup');
    if (terminalMockup) {
        terminalMockup.addEventListener('mousemove', (e) => {
            if (window.innerWidth < 1024) return; // Disable on touch/mobile
            const rect = terminalMockup.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            // Max rotation of 15 degrees
            const rotateX = ((y - centerY) / centerY) * -15;
            const rotateY = ((x - centerX) / centerX) * 15;
            
            terminalMockup.style.transform = `perspective(1000px) scale(1.02) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
            terminalMockup.style.transition = 'transform 0.1s ease-out';
        });

        terminalMockup.addEventListener('mouseleave', () => {
            terminalMockup.style.transform = 'perspective(1000px) scale(1) rotateX(0deg) rotateY(0deg)';
            terminalMockup.style.transition = 'transform 0.6s cubic-bezier(0.16, 1, 0.3, 1)';
        });
    }

    // ==========================================
    // Reactive Lenis-inspired Scroll Velocity Canvas
    // ==========================================
    const canvas = document.getElementById('network-canvas');
    if (canvas) {
        const ctx = canvas.getContext('2d');
        let width, height;
        let particles = [];
        
        let lastScrollTop = window.scrollY;
        let lastScrollTime = Date.now();
        let scrollVelocity = 0;
        let targetVelocity = 0;

        window.addEventListener('scroll', () => {
            const now = Date.now();
            const scrollTop = window.scrollY;
            const dt = now - lastScrollTime;
            if (dt > 0) {
                // Calculate speed of scrolling
                const rawSpeed = Math.abs(scrollTop - lastScrollTop) / dt;
                targetVelocity = Math.min(rawSpeed * 5, 25); // cap velocity at 25
            }
            lastScrollTop = scrollTop;
            lastScrollTime = now;
        });

        function resize() {
            width = canvas.width = window.innerWidth;
            height = canvas.height = window.innerHeight;
        }
        window.addEventListener('resize', resize);
        resize();

        class Particle {
            constructor() {
                this.x = Math.random() * width;
                this.y = Math.random() * height;
                this.vx = (Math.random() - 0.5) * 0.5;
                this.vy = (Math.random() - 0.5) * 0.5;
                this.radius = Math.random() * 2 + 1;
            }
            update(vel) {
                // Accelerate particles based on scroll velocity
                const multiplier = 1 + vel * 0.8;
                this.x += this.vx * multiplier;
                this.y += this.vy * multiplier;
                
                if (this.x < 0 || this.x > width) this.vx *= -1;
                if (this.y < 0 || this.y > height) this.vy *= -1;
            }
            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(255, 85, 0, ${0.4 + scrollVelocity * 0.02})`;
                ctx.fill();
            }
        }

        // Initialize particles
        const particleCount = Math.min(Math.floor(width / 15), 100);
        for (let i = 0; i < particleCount; i++) {
            particles.push(new Particle());
        }

        function animateCanvas() {
            // Smoothly decay scroll velocity
            scrollVelocity += (targetVelocity - scrollVelocity) * 0.08;
            targetVelocity *= 0.95; // decay target speed

            ctx.clearRect(0, 0, width, height);
            
            for (let i = 0; i < particles.length; i++) {
                particles[i].update(scrollVelocity);
                particles[i].draw();
                
                for (let j = i + 1; j < particles.length; j++) {
                    const dx = particles[i].x - particles[j].x;
                    const dy = particles[i].y - particles[j].y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    
                    if (dist < 160) {
                        ctx.beginPath();
                        
                        // Shift colors from burnt amber to bright orange when velocity increases
                        const ratio = Math.min(scrollVelocity / 15, 1);
                        const r = Math.floor(180 + (255 - 180) * ratio); // 180 (burnt) -> 255 (vivid)
                        const g = Math.floor(83 + (85 - 83) * ratio);    // 83 (burnt) -> 85 (vivid)
                        const b = 0;
                        const alpha = (0.2 + ratio * 0.45) - (dist / 160) * (0.2 + ratio * 0.45);

                        ctx.strokeStyle = `rgba(${r}, ${g}, ${b}, ${alpha})`;
                        ctx.lineWidth = 1 + ratio * 2; // thicken connection lines
                        ctx.moveTo(particles[i].x, particles[i].y);
                        ctx.lineTo(particles[j].x, particles[j].y);
                        ctx.stroke();
                    }
                }
            }
            requestAnimationFrame(animateCanvas);
        }
        animateCanvas();
    }



    // ==========================================
    // Easter Egg: "ank/goof" Konami Code
    // ==========================================
    let secretCode = "ank/goof";
    let inputSequence = "";

    document.addEventListener('keydown', (e) => {
        // Only track single characters (letters and slash)
        if (e.key.length === 1 && e.key.match(/[a-z\/]/i)) {
            inputSequence += e.key.toLowerCase();
            if (inputSequence.length > secretCode.length) {
                inputSequence = inputSequence.slice(1);
            }
            if (inputSequence === secretCode) {
                triggerEasterEgg();
                inputSequence = "";
            }
        } else if (e.key === 'Backspace') {
            inputSequence = inputSequence.slice(0, -1);
        }
    });

    function triggerEasterEgg() {
        if (isEasterEggActive) return; // Prevent triggering multiple times
        isEasterEggActive = true;
        
        const mainTerminal = document.getElementById('typewriter-container');
        const mockup = document.querySelector('.terminal-mockup:not(.terminal-lesson)');
        if (!mainTerminal || !mockup) return;

        // Glitch flash effect
        mockup.style.boxShadow = "0 0 100px rgba(255, 85, 0, 1)";
        mockup.style.transform = "perspective(1000px) scale(1.05) rotateX(5deg) rotateY(-5deg)";
        setTimeout(() => {
            mockup.style.boxShadow = "";
            mockup.style.transform = "";
        }, 500);

        // Clear terminal
        mainTerminal.innerHTML = '';
        
        const eggLines = [
            { type: 'input', text: 'ank/goof' },
            { type: 'ank', text: '[ank]: ...' },
            { type: 'ank', text: '[ank]: You think typing undocumented commands makes you a hacker?' },
            { type: 'ank', text: '[ank]: My internal logs show you haven\'t even configured your SSH keys yet.' },
            { type: 'ank', text: '[ank]: Stop looking for easter eggs. The real reward is system uptime.' },
            { type: 'ank', text: '[ank]: Now go clone the repo before I drop your connection.' }
        ];

        let eggLineIdx = 0;
        let eggCharIdx = 0;

        function typeEggLine() {
            if (eggLineIdx >= eggLines.length) {
                // Resume normal operations after a delay
                setTimeout(() => {
                    isEasterEggActive = false;
                    mainTerminal.innerHTML = '';
                }, 8000);
                return;
            }

            const lineData = eggLines[eggLineIdx];
            const oldCursor = mainTerminal.querySelector('.term-cursor');
            if (oldCursor) oldCursor.remove();

            const lineDiv = document.createElement('div');
            lineDiv.className = 'line';
            mainTerminal.appendChild(lineDiv);

            if (lineData.type === 'input') {
                lineDiv.innerHTML = '<span class="term-prompt">user@local ~$</span> <span class="term-cmd"></span><span class="term-cursor"></span>';
                const cmdSpan = lineDiv.querySelector('.term-cmd');
                
                function typeChar() {
                    if (eggCharIdx < lineData.text.length) {
                        cmdSpan.innerHTML += lineData.text.charAt(eggCharIdx);
                        eggCharIdx++;
                        mainTerminal.scrollTop = mainTerminal.scrollHeight;
                        setTimeout(typeChar, 40);
                    } else {
                        eggCharIdx = 0;
                        eggLineIdx++;
                        setTimeout(typeEggLine, 800);
                    }
                }
                setTimeout(typeChar, 400);
            } else {
                lineDiv.innerHTML = `<span class="term-ank">${lineData.text}</span><span class="term-cursor"></span>`;
                mainTerminal.scrollTop = mainTerminal.scrollHeight;
                eggLineIdx++;
                setTimeout(typeEggLine, 1800);
            }
        }
        
        // Start typing easter egg
        setTimeout(typeEggLine, 800);
    }

    // Interactive 3D Tilt for Lesson Terminal (Max 10 deg)
    const lessonTerminalMockup = document.querySelector('.terminal-lesson');
    if (lessonTerminalMockup) {
        lessonTerminalMockup.addEventListener('mousemove', (e) => {
            if (window.innerWidth < 1024) return; // Disable on touch/mobile
            const rect = lessonTerminalMockup.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const rotateX = ((y - centerY) / centerY) * -10;
            const rotateY = ((x - centerX) / centerX) * 10;
            lessonTerminalMockup.style.transform = `perspective(1000px) scale(1.02) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
            lessonTerminalMockup.style.transition = 'transform 0.1s ease-out';
        });

        lessonTerminalMockup.addEventListener('mouseleave', () => {
            lessonTerminalMockup.style.transform = 'perspective(1000px) scale(1) rotateX(0deg) rotateY(0deg)';
            lessonTerminalMockup.style.transition = 'transform 0.6s cubic-bezier(0.16, 1, 0.3, 1)';
        });
    }

    // Interactive 3D Tilt for Feature Cards (Max 5 deg)
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            if (window.innerWidth < 1024) return;
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const rotateX = ((y - centerY) / centerY) * -5;
            const rotateY = ((x - centerX) / centerX) * 5;
            card.style.transform = `perspective(1000px) scale(1.02) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
            card.style.transition = 'transform 0.1s ease-out';
        });
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) scale(1) rotateX(0deg) rotateY(0deg)';
            card.style.transition = 'transform 0.6s cubic-bezier(0.16, 1, 0.3, 1)';
        });
    });

    // ==========================================
    // Theme Toggle Logic
    // ==========================================
    const themeToggleBtn = document.getElementById('theme-toggle');
    const sunIcon = document.getElementById('theme-icon-sun');
    const moonIcon = document.getElementById('theme-icon-moon');
    
    // Check saved theme
    const savedTheme = localStorage.getItem('academy_theme') || 'dark';
    if (savedTheme === 'light') {
        document.body.classList.add('theme-light');
        if (sunIcon && moonIcon) {
            sunIcon.style.display = 'none';
            moonIcon.style.display = 'block';
        }
    }
    
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', (e) => {
            
            const toggleLogic = () => {
                document.body.classList.toggle('theme-light');
                const isLight = document.body.classList.contains('theme-light');
                localStorage.setItem('academy_theme', isLight ? 'light' : 'dark');
                
                if (sunIcon && moonIcon) {
                    if (isLight) {
                        sunIcon.style.display = 'none';
                        moonIcon.style.display = 'block';
                    } else {
                        sunIcon.style.display = 'block';
                        moonIcon.style.display = 'none';
                    }
                }
            };

            // Wave Transition API
            if (!document.startViewTransition) {
                toggleLogic();
                return;
            }

            const x = e.clientX;
            const y = e.clientY;
            
            const transition = document.startViewTransition(() => {
                toggleLogic();
            });

            transition.ready.then(() => {
                document.documentElement.animate(
                    {
                        clipPath: [
                            'polygon(0 0, 100% 0, 100% 0, 0 0)',
                            'polygon(0 0, 100% 0, 100% 100%, 0 100%)'
                        ]
                    },
                    {
                        duration: 800,
                        easing: 'ease-in-out',
                        pseudoElement: '::view-transition-new(root)'
                    }
                );
            });
        });
    }

    // ==========================================
    // Variant Switcher Controller
    // ==========================================
    const switcherBtns = document.querySelectorAll('.switcher-btn');
    switcherBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetVariant = btn.getAttribute('data-target');
            document.body.setAttribute('data-active-variant', targetVariant);
            
            // Update active state in switcher UI
            switcherBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Trigger count up statistics on switching back to V1
            if (targetVariant === "1") {
                const countEls = document.querySelectorAll('.count-up');
                countEls.forEach(el => {
                    const target = parseInt(el.getAttribute('data-val'), 10);
                    animateValue(el, 0, target, 1500);
                });
            }
        });
    });

    // ==========================================
    // Variant 2: Dashboard Workspace Simulator
    // ==========================================
    const syllabusItems = document.querySelectorAll('.syllabus-item');
    const simLessonTitle = document.getElementById('sim-lesson-title');
    const simLessonDesc = document.getElementById('sim-lesson-desc');
    const simAnkAdvice = document.getElementById('sim-ank-advice');
    const v2ShellInput = document.getElementById('v2-shell-input');
    const v2ShellHistory = document.getElementById('v2-shell-history');
    const simTaskBar = document.getElementById('sim-task-bar');
    const simTaskPercent = document.getElementById('sim-task-percent');
    const simCpu = document.getElementById('sim-cpu');

    // Simulate CPU variations periodically
    setInterval(() => {
        if (simCpu) {
            const val = (Math.random() * 4 + 0.5).toFixed(1);
            simCpu.textContent = `${val}%`;
        }
    }, 2000);

    const lessonDataMap = {
        linux: {
            title: "Linux Files & Inodes",
            desc: "Master filesystem link structures. Locate the file 'app.py' and check its inode reference number using visual shell descriptors.",
            advice: 'Ank: "Try running \'ls -li\' to reveal the inode pointers mapping the index list."',
            progress: "25%",
            width: "25%"
        },
        network: {
            title: "SSH & Port Tunneling",
            desc: "Configure remote access channels. Create an encrypted tunnel mapping local port 8080 to the sandbox environment port 80.",
            advice: 'Ank: "Try running \'ssh -L 8080:localhost:80 guest@sandbox\' to establish connection."',
            progress: "50%",
            width: "50%"
        },
        security: {
            title: "fail2ban IP Defense",
            desc: "Analyze telemetry streams for intrusion vectors. Ban malicious IP hosts sending high-rate connection requests.",
            advice: 'Ank: "Check the ban status by running \'fail2ban-client status sshd\'."',
            progress: "75%",
            width: "75%"
        },
        services: {
            title: "systemd Daemons",
            desc: "Manage persistent background service lifecycles. Boot and verify the target Nginx service daemon is active.",
            advice: 'Ank: "Execute \'systemctl status nginx\' to check state telemetry."',
            progress: "100%",
            width: "100%"
        }
    };

    let activeLessonKey = "linux";

    syllabusItems.forEach(item => {
        item.addEventListener('click', () => {
            syllabusItems.forEach(i => {
                i.classList.remove('active');
                const badge = i.querySelector('.status-badge');
                if (badge && badge.textContent === 'Current') {
                    badge.textContent = 'Completed';
                    badge.className = 'status-badge completed';
                }
            });
            item.classList.add('active');
            const currentBadge = item.querySelector('.status-badge');
            if (currentBadge) {
                currentBadge.textContent = 'Current';
                currentBadge.className = 'status-badge active';
            }

            const lessonKey = item.getAttribute('data-lesson');
            activeLessonKey = lessonKey;
            const data = lessonDataMap[lessonKey];
            if (data) {
                simLessonTitle.textContent = data.title;
                simLessonDesc.textContent = data.desc;
                simAnkAdvice.textContent = data.advice;
                simTaskBar.style.width = data.width;
                simTaskPercent.textContent = data.progress;
            }
        });
    });

    if (v2ShellInput) {
        v2ShellInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                const cmd = v2ShellInput.value.trim();
                if (!cmd) return;
                v2ShellInput.value = '';

                // Log command to history
                const userLine = document.createElement('div');
                userLine.className = 'history-line input';
                userLine.innerHTML = `<span style="color: var(--accent-primary); font-weight: bold;">guest@sandbox:~$</span> ${cmd}`;
                v2ShellHistory.appendChild(userLine);

                // Simulate command response
                setTimeout(() => {
                    const responseLine = document.createElement('div');
                    responseLine.className = 'history-line output';
                    const cmdLower = cmd.toLowerCase();

                    if (cmdLower === 'clear') {
                        v2ShellHistory.innerHTML = '';
                        return;
                    } else if (cmdLower === 'ls' || cmdLower === 'ls -la' || cmdLower === 'ls -l' || cmdLower === 'ls -li') {
                        if (activeLessonKey === 'linux') {
                            responseLine.innerHTML = `total 16<br>
1048577 -rw-r--r--   1 guest  guest   240 Jul 12 14:36 app.py<br>
1048578 -rw-r--r--   1 guest  guest   105 Jul 12 14:36 config.txt<br>
1048579 drwxr-xr-x   2 guest  guest   4096 Jul 12 14:36 src`;
                        } else {
                            responseLine.innerHTML = `total 8<br>
1048578 -rw-r--r--   1 guest  guest   105 Jul 12 14:36 config.txt`;
                        }
                    } else if (cmdLower.includes('ssh') && activeLessonKey === 'network') {
                        responseLine.innerHTML = `ssh: Connecting to sandbox [localhost:80]...<br>
guest@sandbox password: **********<br>
✓ SSH tunnel established successfully: local port 8080 forwarded.`;
                    } else if (cmdLower.includes('fail2ban') && activeLessonKey === 'security') {
                        responseLine.innerHTML = `Status for the jail: sshd<br>
|- Filter<br>
|  |- Currently failed: 1<br>
|  |- Total failed: 14<br>
|  \`- File list: /var/log/auth.log<br>
\`- Actions<br>
   |- Currently banned: 3<br>
   |- Total banned: 3<br>
   \`- Banned IP list: 198.51.100.42, 203.0.113.19, 192.0.2.115`;
                    } else if (cmdLower.includes('systemctl') && activeLessonKey === 'services') {
                        responseLine.innerHTML = `● nginx.service - High-performance HTTP server<br>
     Loaded: loaded (/lib/systemd/system/nginx.service; enabled)<br>
     Active: active (running) since Sun 2026-07-12 14:30:15 UTC<br>
   Main PID: 824 (nginx)`;
                    } else if (cmdLower === 'docker ps') {
                        responseLine.innerHTML = `CONTAINER ID   IMAGE          COMMAND                  CREATED         STATUS         PORTS<br>
9e8d7c6b5a4f   alpine:latest  "/bin/sh"                10 min ago      Up 10 min      80/tcp -> 8080/tcp`;
                    } else {
                        responseLine.className = 'history-line ank';
                        responseLine.textContent = `Ank: "Hmm, '${cmd}' is not the focus here. Look at your objectives and the advice bubble."`;
                    }

                    v2ShellHistory.appendChild(responseLine);
                    v2ShellHistory.parentElement.scrollTop = v2ShellHistory.parentElement.scrollHeight;
                }, 400);
            }
        });
    }

    // ==========================================
    // Variant 3: Documentation Playground Sandbox
    // ==========================================
    const v3ShellInput = document.getElementById('v3-shell-input');
    const v3ShellHistory = document.getElementById('v3-shell-history');
    const playgroundStatus = document.getElementById('playground-status');

    if (v3ShellInput) {
        v3ShellInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                const cmd = v3ShellInput.value.trim();
                if (!cmd) return;
                v3ShellInput.value = '';

                // Log command to history
                const userLine = document.createElement('div');
                userLine.className = 'history-line input';
                userLine.innerHTML = `<span style="color: var(--accent-primary); font-weight: bold;">sandbox@playground:~$</span> ${cmd}`;
                v3ShellHistory.appendChild(userLine);

                setTimeout(() => {
                    const responseLine = document.createElement('div');
                    responseLine.className = 'history-line output';
                    const cleanCmd = cmd.replace(/\s+/g, ' ');

                    if (cleanCmd === 'chmod 644 config.txt' || cleanCmd === 'chmod u=rw,g=r,o=r config.txt') {
                        playgroundStatus.textContent = '✓ TASK COMPLETED';
                        playgroundStatus.style.color = '#22c55e';
                        responseLine.innerHTML = `<span style="color: #22c55e; font-weight: bold;">✓ Verification Success!</span><br>
- Owner: Read & Write (rw-)<br>
- Group: Read (r--) <br>
- Others: Read (r--)<br>
Ank: "Excellent permissions mapping. You've completed the documentation playground task!"`;
                    } else if (cleanCmd === 'ls -l' || cleanCmd === 'ls -la') {
                        const perm = (playgroundStatus.textContent === '✓ TASK COMPLETED') ? '-rw-r--r--' : '-rwxrwxrwx';
                        responseLine.innerHTML = `${perm} 1 sandbox sandbox 105 Jul 12 14:36 config.txt`;
                    } else {
                        responseLine.innerHTML = `bash: operation not permitted or invalid command syntax.<br>
Ank: "Try specifying 'chmod 644 config.txt' to grant read-write to owner and read-only to others."`;
                    }

                    v3ShellHistory.appendChild(responseLine);
                    v3ShellHistory.parentElement.scrollTop = v3ShellHistory.parentElement.scrollHeight;
                }, 400);
            }
        });
    }

    // ==========================================
    // Variant 4: Motion Topology Connections
    // ==========================================
    const floatingNodes = document.querySelectorAll('.floating-node[data-target-glow]');
    floatingNodes.forEach(node => {
        const pathId = node.getAttribute('data-target-glow');
        const pathEl = document.getElementById(pathId);
        
        node.addEventListener('mouseenter', () => {
            if (pathEl) {
                pathEl.style.opacity = "1";
                pathEl.style.strokeWidth = "4";
                pathEl.style.filter = "drop-shadow(0 0 8px #ff5500)";
            }
        });
        node.addEventListener('mouseleave', () => {
            if (pathEl) {
                pathEl.style.opacity = "0";
                pathEl.style.strokeWidth = "3";
                pathEl.style.filter = "none";
            }
        });
    });

    // Lenis scroll background morphing animation
    window.addEventListener('scroll', () => {
        const scrollPercent = window.scrollY / (document.documentElement.scrollHeight - window.innerHeight);
        
        // Morph the SVG paths in Variant 4 dynamically based on scroll position & velocity!
        const pathDocker = document.getElementById('path-docker');
        const glowDocker = document.getElementById('glow-docker');
        const pathAlpine = document.getElementById('path-alpine');
        const glowAlpine = document.getElementById('glow-alpine');
        const pathNginx = document.getElementById('path-nginx');
        const glowNginx = document.getElementById('glow-nginx');
        const pathPostgres = document.getElementById('path-postgres');
        const glowPostgres = document.getElementById('glow-postgres');

        // Dynamically shift the control point Q based on scroll progress
        const shiftX = scrollPercent * 160; 
        
        if (pathDocker && glowDocker) {
            const d = `M 120 150 Q ${280 + shiftX} ${180 - shiftX * 0.5} 400 250`;
            pathDocker.setAttribute('d', d);
            glowDocker.setAttribute('d', d);
        }
        if (pathAlpine && glowAlpine) {
            const d = `M 120 350 Q ${280 + shiftX} ${320 + shiftX * 0.5} 400 250`;
            pathAlpine.setAttribute('d', d);
            glowAlpine.setAttribute('d', d);
        }
        if (pathNginx && glowNginx) {
            const d = `M 880 150 Q ${720 - shiftX} ${180 - shiftX * 0.5} 600 250`;
            pathNginx.setAttribute('d', d);
            glowNginx.setAttribute('d', d);
        }
        if (pathPostgres && glowPostgres) {
            const d = `M 880 350 Q ${720 - shiftX} ${320 + shiftX * 0.5} 600 250`;
            pathPostgres.setAttribute('d', d);
            glowPostgres.setAttribute('d', d);
        }
    });

    // ==========================================
    // Variant 5: Bento Box Matrix logs generator
    // ==========================================
    const bentoLogs = document.getElementById('bento-live-logs');
    if (bentoLogs) {
        const logLines = [
            "[INFO] Alpine container booted successfully.",
            "[INFO] namespace-01 virtual subnet created.",
            "[WARN] CPU utilization spike: container processing logs.",
            "[INFO] Port 80 successfully forwarded to 8080.",
            "[SUCCESS] fail2ban SSH policy applied.",
            "[INFO] Telemetry tracking active.",
            "[INFO] Heartbeat verification token checked."
        ];
        
        setInterval(() => {
            const randomLine = logLines[Math.floor(Math.random() * logLines.length)];
            const time = new Date().toLocaleTimeString();
            const logColor = randomLine.includes('WARN') ? '#f59e0b' : (randomLine.includes('SUCCESS') ? '#22c55e' : '#a1a1aa');
            
            bentoLogs.innerHTML += `<br><span style="color: ${logColor};">[${time}] ${randomLine}</span>`;
            if (bentoLogs.innerHTML.split('<br>').length > 5) {
                const parts = bentoLogs.innerHTML.split('<br>');
                bentoLogs.innerHTML = parts.slice(parts.length - 4).join('<br>');
            }
        }, 3000);
    }

    // ==========================================
    // Variant 2: Telemetry Logs Generator
    // ==========================================
    const telemetryLogs = document.getElementById('sim-telemetry-logs');
    if (telemetryLogs) {
        const logLines = [
            "[INFO] Alpine container connection ping active.",
            "[INFO] namespace-01 virtual routing validated.",
            "[WARN] CPU status check: normal.",
            "[INFO] port 8080 mapped to local guest interface.",
            "[SUCCESS] fail2ban SSH policy applied.",
            "[INFO] Telemetry logging stream running."
        ];
        
        setInterval(() => {
            const randomLine = logLines[Math.floor(Math.random() * logLines.length)];
            const time = new Date().toLocaleTimeString();
            const logColor = randomLine.includes('WARN') ? '#f59e0b' : (randomLine.includes('SUCCESS') ? '#22c55e' : '#a1a1aa');
            
            telemetryLogs.innerHTML += `<br><span style="color: ${logColor};">[${time}] ${randomLine}</span>`;
            if (telemetryLogs.innerHTML.split('<br>').length > 4) {
                const parts = telemetryLogs.innerHTML.split('<br>');
                telemetryLogs.innerHTML = parts.slice(parts.length - 3).join('<br>');
            }
        }, 4000);
    }

});
