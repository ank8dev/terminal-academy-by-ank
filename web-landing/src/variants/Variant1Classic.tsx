import React, { useState, useEffect, useRef } from 'react';
import { motion, useScroll, useTransform, useInView } from 'framer-motion';
import { Download, Github, Zap, CheckCircle2 } from 'lucide-react';
import { useScheduledOnScroll } from '../hooks/useScheduledOnScroll';

/* ── Fade-in section wrapper ── */
function FadeSection({ children, className = '', id = '' }: { children: React.ReactNode; className?: string; id?: string }) {
  return (
    <motion.section
      id={id}
      className={className}
      initial={{ opacity: 0, y: 45 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-60px' }}
      transition={{ duration: 0.65 }}
    >
      {children}
    </motion.section>
  );
}

/* ── Animated counter ── */
function AnimatedCounter({ end, suffix = '', label }: { end: number; suffix?: string; label: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, margin: '-100px' });
  const [count, setCount] = useState(0);

  useEffect(() => {
    if (!isInView) return;
    let frame: number;
    const start = performance.now();
    const tick = (now: number) => {
      const p = Math.min((now - start) / 1200, 1);
      setCount(Math.round((1 - Math.pow(1 - p, 3)) * end));
      if (p < 1) frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [isInView, end]);

  return (
    <div ref={ref} className="v1-stat-card">
      <span className="v1-stat-number">{count}{suffix}</span>
      <span className="v1-stat-label">{label}</span>
    </div>
  );
}

/* ── GLASSMORPHIC CAPABILITY CARD PREVIEWS ── */
function AnimatedChatCard({ play }: { play: boolean }) {
  const [step, setStep] = useState(0);
  useEffect(() => {
    if (!play) { setStep(0); return; }
    const t1 = setTimeout(() => setStep(1), 800);
    const t2 = setTimeout(() => setStep(2), 1800);
    return () => { clearTimeout(t1); clearTimeout(t2); };
  }, [play]);

  return (
    <div className="cap-glass-card">
      <div className="window-bar"><span /><span /><span /></div>
      <div className="chat-scene">
        <div className="chat-bubble student"><span>How do I modify this user?</span></div>
        {step >= 1 && (
          <div className="chat-bubble mentor">
            <span>What SQL query processes privilege links?</span>
          </div>
        )}
        {step >= 2 && (
          <div className="chat-bubble suggestion">
            <span>💡 Review GRANT models.</span>
          </div>
        )}
      </div>
    </div>
  );
}

function AnimatedCliCard({ play }: { play: boolean }) {
  const [step, setStep] = useState(0);
  useEffect(() => {
    if (!play) { setStep(0); return; }
    const t1 = setTimeout(() => setStep(1), 800);
    const t2 = setTimeout(() => setStep(2), 1600);
    return () => { clearTimeout(t1); clearTimeout(t2); };
  }, [play]);

  return (
    <div className="cap-glass-card">
      <div className="window-bar"><span /><span /><span /></div>
      <div className="cli-scene">
        <pre className="cli-line">student@terminal:~$ cat /etc/shadow</pre>
        {step >= 1 && <pre className="cli-output error">Permission denied (error 13)</pre>}
        {step >= 2 && <pre className="cli-line">student@terminal:~$ sudo !!</pre>}
      </div>
    </div>
  );
}

function AnimatedChecklistCard({ play }: { play: boolean }) {
  const [percent, setPercent] = useState(0);
  useEffect(() => {
    if (!play) { setPercent(0); return; }
    const t1 = setTimeout(() => setPercent(50), 800);
    const t2 = setTimeout(() => setPercent(100), 1600);
    return () => { clearTimeout(t1); clearTimeout(t2); };
  }, [play]);

  return (
    <div className="cap-glass-card">
      <div className="window-bar"><span /><span /><span /></div>
      <div className="checklist-scene">
        <div className="progress-row">
          <span>Incident Checklist</span>
          <span>{percent}%</span>
        </div>
        <div className="checklist-item done"><CheckCircle2 size={12} /><span>Docker overlay network</span></div>
        <div className={`checklist-item ${percent >= 100 ? 'done' : ''}`}><CheckCircle2 size={12} /><span>Nginx cert credentials</span></div>
      </div>
    </div>
  );
}

/* ══════════════════════════════════════════════════════════════════
   PREMIUM YELLOW SHOWCASE CARDS — Chapter 1: Incident Lifecycle
   Abstract CSS-animated product showcases. No dashboard widgets.
   ══════════════════════════════════════════════════════════════════ */

function Showcase1Detection() {
  const cells = Array.from({ length: 28 });
  return (
    <div className="sc-panel sc-yellow">
      <div className="sc-grid-7x4">
        {cells.map((_, i) => {
          const col = i % 7;
          const row = Math.floor(i / 7);
          const delay = (col * 0.09 + row * 0.13).toFixed(2);
          return <div key={i} className="sc-cell" style={{ animationDelay: `${delay}s` }} />;
        })}
      </div>
    </div>
  );
}

function Showcase2Investigation() {
  const bars = [
    { h: 0.55, d: 0 }, { h: 0.82, d: 0.15 }, { h: 0.38, d: 0.30 },
    { h: 0.95, d: 0.45 }, { h: 0.62, d: 0.60 }, { h: 0.48, d: 0.75 },
  ];
  return (
    <div className="sc-panel sc-yellow">
      <div className="sc-bars-v">
        {bars.map((b, i) => (
          <div
            key={i}
            className="sc-bar-v"
            style={{ '--bh': b.h, animationDelay: `${b.d}s` } as React.CSSProperties}
          />
        ))}
      </div>
    </div>
  );
}

function Showcase3Containment() {
  return (
    <div className="sc-panel sc-yellow">
      <div className="sc-rings-center">
        <div className="sc-ring sc-ring-outer" />
        <div className="sc-ring sc-ring-mid" />
        <div className="sc-ring sc-ring-inner" />
        <div className="sc-center-dot" />
      </div>
    </div>
  );
}

function Showcase4Recovery() {
  return (
    <div className="sc-panel sc-yellow">
      <div className="sc-nodes-row">
        <div className="sc-node-line" />
        {[0, 1, 2, 3].map(i => (
          <div key={i} className="sc-node-item" style={{ animationDelay: `${i * 0.48}s` }}>
            <div className="sc-node-circle" />
            <div className="sc-node-pulse" />
          </div>
        ))}
      </div>
    </div>
  );
}

/* ══════════════════════════════════════════════════════════════════
   YELLOW MINI SHOWCASES — Chapter 2: System Architecture
   Same visual language, square format on yellow card against dark bg.
   ══════════════════════════════════════════════════════════════════ */

function ArchShowcase1() {
  const cells = Array.from({ length: 16 });
  return (
    <div className="arch-sc-content">
      <div className="arch-sc-grid">
        {cells.map((_, i) => {
          const col = i % 4;
          const row = Math.floor(i / 4);
          return <div key={i} className="arch-sc-cell" style={{ animationDelay: `${(col * 0.10 + row * 0.16).toFixed(2)}s` }} />;
        })}
      </div>
    </div>
  );
}

function ArchShowcase2() {
  const bars = [{ h: 0.5, d: 0 }, { h: 0.82, d: 0.18 }, { h: 0.35, d: 0.36 }, { h: 0.72, d: 0.54 }];
  return (
    <div className="arch-sc-content">
      <div className="arch-sc-bars">
        {bars.map((b, i) => (
          <div key={i} className="arch-sc-bar" style={{ '--bh': b.h, animationDelay: `${b.d}s` } as React.CSSProperties} />
        ))}
      </div>
    </div>
  );
}

function ArchShowcase3() {
  return (
    <div className="arch-sc-content">
      <div className="arch-sc-rings">
        <div className="arch-ring arch-ring-outer" />
        <div className="arch-ring arch-ring-inner" />
        <div className="arch-ring-dot" />
      </div>
    </div>
  );
}

function ArchShowcase4() {
  return (
    <div className="arch-sc-content">
      <div className="arch-sc-nodes">
        <div className="arch-node-line" />
        {[0, 1, 2].map(i => (
          <div key={i} className="arch-node-item" style={{ animationDelay: `${i * 0.52}s` }}>
            <div className="arch-node-dot" />
            <div className="arch-node-pulse" />
          </div>
        ))}
      </div>
    </div>
  );
}

/* ══════════════════════════════════════════════════════════════════
   MAIN VARIANT COMPONENT
   ══════════════════════════════════════════════════════════════════ */

export default function Variant1Classic() {
  const stickyScrollRef = useRef<HTMLDivElement>(null);
  const stickyInnerRef = useRef<HTMLDivElement>(null);
  const cardRefs = useRef<(HTMLDivElement | null)[]>([]);

  const archScrollRef = useRef<HTMLDivElement>(null);
  const archInnerRef = useRef<HTMLDivElement>(null);
  const archPanelRefs = useRef<(HTMLDivElement | null)[]>([]);

  const { scrollYProgress } = useScroll();

  const bgTransition = useTransform(
    scrollYProgress,
    [0, 0.25, 0.5, 0.75, 1],
    ['#050506', '#140c0a', '#241209', '#100806', '#050506']
  );

  /* ── CHAPTER 1: Extended pre-approach transition engine ── */
  const applyLifecycleSceneLayout = () => {
    const section = stickyScrollRef.current;
    const inner = stickyInnerRef.current;
    if (!section || !inner) return;

    const sectionRect = section.getBoundingClientRect();
    const viewportHeight = window.innerHeight;
    const innerWidth = inner.clientWidth;
    const innerHeight = inner.clientHeight;
    const scrollRange = Math.max(1, sectionRect.height - viewportHeight);
    const progressScale = 1.45;

    const progress = Math.min(Math.max(0, -sectionRect.top / scrollRange), 1) * progressScale;
    const rawProgress = -sectionRect.top / scrollRange;

    // Extended transition: begins 1.5 viewports before the section pins
    let transitionT = 0;
    if (sectionRect.top > 0 && sectionRect.top < viewportHeight * 1.5) {
      transitionT = (1 - sectionRect.top / (viewportHeight * 1.5)) * 0.85;
    } else if (rawProgress >= 0 && rawProgress <= 1) {
      if (rawProgress < 0.1) {
        transitionT = 0.85 + (rawProgress / 0.1) * 0.15;
      } else if (rawProgress > 0.85) {
        transitionT = (1 - rawProgress) / 0.15;
      } else {
        transitionT = 1.0;
      }
    }

    // Smoothstep for more organic feel
    const eased = transitionT * transitionT * (3 - 2 * transitionT);

    // Warm-white overlay (transparent approaching → opaque white when pinned)
    inner.style.backgroundColor = `rgba(255, 253, 247, ${eased})`;

    // Text morphs to near-black in the white scene
    const tR = Math.round(243 - 228 * transitionT);
    const tG = Math.round(244 - 221 * transitionT);
    const tB = Math.round(246 - 204 * transitionT);
    inner.style.color = `rgb(${tR}, ${tG}, ${tB})`;

    // Background typography: cross-fade layers, warm amber color
    const headings = inner.querySelectorAll('.v1-sticky-bg-text-layer');
    headings.forEach((heading, idx) => {
      if (!(heading instanceof HTMLElement)) return;
      let opacity = 0;
      if (idx === 0) {
        opacity = Math.max(0, 1 - progress / 0.35);
      } else if (idx === 1) {
        opacity = progress < 0.35 ? progress / 0.35 : Math.max(0, 1 - (progress - 0.35) / 0.35);
      } else if (idx === 2) {
        opacity = progress < 0.70 ? 0 : progress < 1.05 ? (progress - 0.70) / 0.35 : Math.max(0, 1 - (progress - 1.05) / 0.35);
      } else if (idx === 3) {
        opacity = progress < 1.05 ? 0 : Math.min(1, (progress - 1.05) / 0.35);
      }
      const hR = Math.round((1 - transitionT) * 255 + transitionT * 200);
      const hG = Math.round((1 - transitionT) * 85 + transitionT * 120);
      heading.style.color = `rgb(${hR}, ${hG}, 0)`;
      heading.style.opacity = String(opacity * (transitionT < 0.5 ? 0.055 : 0.10));
    });

    // Card choreography
    const CARD_TRAVEL_START = 0.05;
    const CARD_TRAVEL_STEP = 0.30;
    const cardCount = 4;
    const isDesktop = innerWidth >= 768;
    const cardWidth = Math.max(0, Math.min(isDesktop ? 450 : 360, innerWidth - 48));

    const getCardLeft = (idx: number, cardW: number) => {
      if (!isDesktop) return (innerWidth - cardW) / 2;
      if (idx === 0) return innerWidth - cardW - innerWidth * 0.06;
      if (idx === 1) return innerWidth * 0.06;
      if (idx === 2) return innerWidth - cardW - innerWidth * 0.14;
      return innerWidth * 0.14;
    };

    const getCardSettledY = (idx: number) => {
      if (!isDesktop) return innerHeight * 0.2 + idx * 40;
      if (idx === 0) return innerHeight * 0.15;
      if (idx === 1) return innerHeight * 0.38;
      if (idx === 2) return innerHeight * 0.52;
      return innerHeight * 0.22;
    };

    const exitProgress = Math.min(Math.max(0, (progress - 1.25) / 0.2), 1);

    for (let index = 0; index < cardCount; index++) {
      const node = cardRefs.current[index];
      if (!node) continue;
      const cardStart = CARD_TRAVEL_START + index * CARD_TRAVEL_STEP;
      const entryTravel = Math.min(Math.max(0, (progress - cardStart) / 0.26), 1);
      const x = getCardLeft(index, cardWidth);
      const ySettled = getCardSettledY(index);
      const yCurrent = innerHeight * 1.15 - entryTravel * (1.15 * innerHeight - ySettled);
      const yFinal = yCurrent - exitProgress * (ySettled + 400);
      node.style.width = `${cardWidth}px`;
      node.style.zIndex = String(10 + index);
      node.style.opacity = String(entryTravel);
      node.style.transform = `translate3d(${x}px, ${yFinal}px, 0)`;
    }
  };

  /* ── CHAPTER 2: System architectures — stays dark, yellow cards ── */
  const applyArchitectureSceneLayout = () => {
    const section = archScrollRef.current;
    const inner = archInnerRef.current;
    if (!section || !inner) return;

    const sectionRect = section.getBoundingClientRect();
    const viewportHeight = window.innerHeight;
    const scrollRange = Math.max(1, sectionRect.height - viewportHeight);

    const rawProgress = Math.min(Math.max(0, -sectionRect.top / scrollRange), 1);
    const stepCount = 4;
    const progress = rawProgress * stepCount;

    const steps = inner.querySelectorAll('.arch-editorial-step');
    steps.forEach((step, idx) => {
      if (!(step instanceof HTMLElement)) return;
      const isActive = progress >= idx && progress < idx + 1;
      step.style.color = isActive ? '#ff5500' : 'var(--text-muted)';
      step.style.opacity = isActive ? '1.0' : '0.4';
    });

    for (let index = 0; index < stepCount; index++) {
      const panel = archPanelRefs.current[index];
      if (!panel) continue;
      let opacity = 0;
      let scale = 0.88;
      if (progress >= index && progress < index + 1) {
        const fraction = progress - index;
        opacity = fraction < 0.2 ? fraction / 0.2 : fraction > 0.8 ? (1 - fraction) / 0.2 : 1.0;
        scale = 0.88 + opacity * 0.12;
      }
      panel.style.opacity = String(opacity);
      panel.style.transform = `scale(${scale})`;
    }
  };

  useScheduledOnScroll(() => {
    applyLifecycleSceneLayout();
    applyArchitectureSceneLayout();
  });

  return (
    <div className="v1-root">
      <motion.div className="v1-dynamic-backsheet" style={{ backgroundColor: bgTransition }} />
      <div className="v1-glow-bottom-right" />

      {/* HEADER */}
      <header className="v1-header">
        <div className="v1-header-inner">
          <div className="v1-logo"><span>t//a</span></div>
          <nav className="v1-nav">
            <a href="#capabilities" className="v1-nav-link">Capabilities</a>
            <a href="#lifecycle" className="v1-nav-link">Incident Lifecycle</a>
            <a href="#architecture" className="v1-nav-link">Architecture</a>
            <a href="#download" className="v1-nav-link">Download</a>
            <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="v1-nav-link">
              <Github size={18} />
            </a>
          </nav>
        </div>
      </header>

      {/* HERO */}
      <section className="v1-hero">
        <div className="v1-hero-bg-word">TERMINAL</div>
        <div className="v1-hero-content">
          <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }} className="v1-hero-badge">
            <Zap size={14} />
            <span className="badge-display-text">Open Source</span>
            <span className="badge-dot-separator">·</span>
            <span className="badge-display-text">Cross-Platform</span>
            <span className="badge-dot-separator">·</span>
            <span className="badge-display-text">Offline-First</span>
          </motion.div>
          <motion.h1 initial={{ opacity: 0, y: 35, filter: 'blur(8px)' }} animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }} transition={{ duration: 1.1, ease: [0.16, 1, 0.3, 1] }} className="v1-hero-title" style={{ fontFamily: 'var(--font-display)' }}>
            <span>Terminal Academy</span>
          </motion.h1>
          <p className="v1-hero-subtitle" style={{ fontFamily: 'var(--font-display)', color: 'var(--text-muted)' }}>
            The systems-first education platform
          </p>
          <p className="v1-hero-desc">
            Master Linux administration, networking, DevOps, and application hosting through realistic,
            isolated terminal exercises. No cloud. No subscriptions. Just you and the command line.
          </p>
          <div className="v1-hero-ctas">
            <motion.button className="v1-btn-primary" whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.97 }}>
              <Download size={18} /> Download Client
            </motion.button>
            <motion.a href="https://github.com" target="_blank" rel="noopener noreferrer" className="v1-btn-ghost" whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.97 }}>
              <Github size={18} /> View on GitHub
            </motion.a>
          </div>
        </div>
      </section>

      {/* STATS */}
      <FadeSection className="v1-section">
        <h2 className="v1-section-title">Built Different</h2>
        <p className="v1-section-subtitle">A ~6MB desktop app that runs real containers. No Electron. No cloud. No bloat.</p>
        <div className="v1-stats-row">
          <AnimatedCounter end={6} suffix="MB" label="Installer Size" />
          <AnimatedCounter end={100} suffix="%" label="Terminal Native" />
          <AnimatedCounter end={0} suffix="" label="Cloud Dependencies" />
        </div>
      </FadeSection>

      {/* CHAPTER 1: INCIDENT LIFECYCLE */}
      <div ref={stickyScrollRef} className="v1-sticky-scroll-container" id="lifecycle">
        <div ref={stickyInnerRef} className="v1-sticky-viewport">
          <div className="v1-sticky-bg-text-wrapper">
            <div className="v1-sticky-bg-text-layer font-display">The Incident Lifecycle</div>
            <div className="v1-sticky-bg-text-layer font-display">01 // Detection</div>
            <div className="v1-sticky-bg-text-layer font-display">02 // Investigation</div>
            <div className="v1-sticky-bg-text-layer font-display">03 // Containment</div>
            <div className="v1-sticky-bg-text-layer font-display">04 // Recovery</div>
          </div>
          <div className="v1-sticky-narrative-box">
            <div className="v1-sticky-card-layer" ref={(el) => { cardRefs.current[0] = el; }} style={{ opacity: 0, transform: 'translate3d(0, 115%, 0)' }}>
              <Showcase1Detection />
            </div>
            <div className="v1-sticky-card-layer" ref={(el) => { cardRefs.current[1] = el; }} style={{ opacity: 0, transform: 'translate3d(0, 115%, 0)' }}>
              <Showcase2Investigation />
            </div>
            <div className="v1-sticky-card-layer" ref={(el) => { cardRefs.current[2] = el; }} style={{ opacity: 0, transform: 'translate3d(0, 115%, 0)' }}>
              <Showcase3Containment />
            </div>
            <div className="v1-sticky-card-layer" ref={(el) => { cardRefs.current[3] = el; }} style={{ opacity: 0, transform: 'translate3d(0, 115%, 0)' }}>
              <Showcase4Recovery />
            </div>
          </div>
        </div>
      </div>

      {/* INTERACTIVE CAPABILITIES */}
      <section className="v1-section" id="capabilities">
        <h2 className="v1-section-title">Interactive Capabilities</h2>
        <p className="v1-section-subtitle">A masterclass in terminal interactions, real-time Socratic feedback, and progress verification loops.</p>
        <div className="editorial-capabilities-list">
          <div className="editorial-row">
            <div className="editorial-text-col">
              <span className="row-number">01</span>
              <h3>Socratic AI Mentor</h3>
              <p>Ank queries diagnostic reasoning in real-time, helping you debug config issues without simply providing copy-paste commands.</p>
            </div>
            <div className="editorial-visual-col"><AnimatedChatCard play={true} /></div>
          </div>
          <div className="editorial-row">
            <div className="editorial-text-col">
              <span className="row-number">02</span>
              <h3>Disposable Linux Shell</h3>
              <p>Spin up sandboxed Alpine containers in milliseconds. Test Nginx configuration, write complex shell operations, and inspect port links.</p>
            </div>
            <div className="editorial-visual-col"><AnimatedCliCard play={true} /></div>
          </div>
          <div className="editorial-row">
            <div className="editorial-text-col">
              <span className="row-number">03</span>
              <h3>Incident Checklists</h3>
              <p>Automated verification engines audit network files, certificate configurations, and system metrics to mark tasks complete.</p>
            </div>
            <div className="editorial-visual-col"><AnimatedChecklistCard play={true} /></div>
          </div>
        </div>
      </section>

      {/* CHAPTER 2: SYSTEM ARCHITECTURES */}
      <div ref={archScrollRef} className="v2-sticky-scroll-container" id="architecture">
        <div ref={archInnerRef} className="v2-sticky-viewport">
          <div className="v2-sticky-bg-text font-display">SYSTEM ARCHITECTURES</div>
          <div className="arch-split-container">
            <div className="arch-editorial-col">
              <div className="arch-editorial-step">
                <span className="step-num">01 /</span>
                <h3>Kernel Scheduling</h3>
                <p>Manage background user scopes, cpu resource limits, and isolate virtual process threads.</p>
              </div>
              <div className="arch-editorial-step">
                <span className="step-num">02 /</span>
                <h3>Network Channels</h3>
                <p>Deploy overlay networks, isolate Docker bridges, and proxy TCP traffic ports.</p>
              </div>
              <div className="arch-editorial-step">
                <span className="step-num">03 /</span>
                <h3>System Daemons</h3>
                <p>Manage systemd scripts, log output pipelines, and check process health diagnostics.</p>
              </div>
              <div className="arch-editorial-step">
                <span className="step-num">04 /</span>
                <h3>Disk Volumes</h3>
                <p>Mount storage drives, configuration directories, and secure filesystems offline.</p>
              </div>
            </div>
            <div className="arch-visual-col">
              <div className="arch-visual-wrapper">
                <div className="arch-visual-panel" ref={(el) => { archPanelRefs.current[0] = el; }} style={{ opacity: 0 }}>
                  <ArchShowcase1 />
                </div>
                <div className="arch-visual-panel" ref={(el) => { archPanelRefs.current[1] = el; }} style={{ opacity: 0 }}>
                  <ArchShowcase2 />
                </div>
                <div className="arch-visual-panel" ref={(el) => { archPanelRefs.current[2] = el; }} style={{ opacity: 0 }}>
                  <ArchShowcase3 />
                </div>
                <div className="arch-visual-panel" ref={(el) => { archPanelRefs.current[3] = el; }} style={{ opacity: 0 }}>
                  <ArchShowcase4 />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* CURRICULUM */}
      <section className="v1-section">
        <h2 className="v1-section-title">The Curriculum</h2>
        <p className="v1-section-subtitle">50+ realistic incidents fanned across 4 comprehensive educational branches.</p>
        <div className="editorial-curriculum-list">
          {[
            { num: '01', name: 'Linux Core & SysAdmin', modules: '12 incidents', desc: 'File systems, user permission groups, package logs, mount points, systemd configuration, and process management.' },
            { num: '02', name: 'Networking & Security', modules: '10 incidents', desc: 'Ingress paths, port tunnels, DNS lookups, iptables firewall tables, SSH routing, and packet diagnostics.' },
            { num: '03', name: 'DevOps & Containers', modules: '14 incidents', desc: 'Docker networks, container storage directories, Docker Compose trees, registry builds, and Alpine optimization.' },
            { num: '04', name: 'DevOps Ingress & SSL', modules: '8 incidents', desc: 'Nginx config layouts, reverse proxies, SSL certificate updates, proxy balance pools, and volume sync paths.' }
          ].map((c, i) => (
            <div key={i} className="editorial-curr-row">
              <div className="curr-meta">
                <span className="curr-num">{c.num}</span>
                <div>
                  <h3 className="font-display">{c.name}</h3>
                  <span className="curr-badge">{c.modules}</span>
                </div>
              </div>
              <p className="curr-desc">{c.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* PLATFORMS */}
      <FadeSection className="v1-section">
        <h2 className="v1-section-title">Available Everywhere</h2>
        <p className="v1-section-subtitle">Lightweight desktop application packages built for your operating system.</p>
        <div className="editorial-platform-list">
          {[
            { os: 'macOS', size: '~6MB DMG', note: 'Universal build targeting Intel & Apple Silicon architectures' },
            { os: 'Windows', size: '~3MB MSI', note: 'Optimized installer compatible with Windows 10 & 11' },
            { os: 'Linux', size: '~8MB AppImage', note: 'Standalone application image targeting major distributions' }
          ].map((p, i) => (
            <div key={i} className="editorial-plat-row">
              <div className="plat-meta">
                <h3>{p.os}</h3>
                <span>{p.size}</span>
              </div>
              <p>{p.note}</p>
              <button className="plat-dl-btn"><Download size={14} /> Download</button>
            </div>
          ))}
        </div>
      </FadeSection>

      {/* PREMIUM CINEMATIC CTA */}
      <FadeSection className="v1-cta-section" id="download">
        <div className="v1-cta-cinematic">
          <div className="v1-cta-rule" />
          <p className="v1-cta-eyebrow">// Get started today</p>
          <h2 className="v1-cta-headline">
            Start<br />
            <span className="v1-cta-accent">Learning</span><br />
            Today.
          </h2>
          <div className="v1-cta-terminal-line">
            <span className="v1-cta-prompt">$</span>
            <code className="v1-cta-code-text">curl -fsSL https://terminal.academy/install.sh | sh</code>
          </div>
          <div className="v1-hero-ctas" style={{ justifyContent: 'flex-start', marginTop: '48px' }}>
            <motion.button className="v1-btn-primary" whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.97 }}>
              <Download size={18} /> Download Client
            </motion.button>
            <motion.a href="https://github.com" target="_blank" rel="noopener noreferrer" className="v1-btn-ghost" whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.97 }}>
              <Github size={18} /> View on GitHub
            </motion.a>
          </div>
          <div className="v1-cta-ambient" />
        </div>
      </FadeSection>

      {/* FOOTER */}
      <footer className="v1-footer">
        <div className="v1-footer-columns">
          <div className="v1-footer-col">
            <div className="v1-logo" style={{ marginBottom: '8px' }}><span>t//a</span></div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>The systems-first education platform for engineers who master the command line.</p>
          </div>
          <div className="v1-footer-col">
            <h4>Product</h4>
            <a href="#capabilities">Capabilities</a>
            <a href="#lifecycle">Incident Lifecycle</a>
            <a href="#download">Download</a>
          </div>
          <div className="v1-footer-col">
            <h4>Resources</h4>
            <a href="https://github.com" target="_blank" rel="noopener noreferrer">GitHub</a>
            <a href="#">Documentation</a>
            <a href="#">License (AGPL-3.0)</a>
          </div>
        </div>
        <div className="v1-footer-bottom">
          © 2025 Terminal Academy · Built with Tauri + React
        </div>
      </footer>

      <style>{`
        .v1-root { background: transparent; color: var(--text-main); font-family: var(--font-sans); position: relative; }
        .font-display { font-family: var(--font-display); }

        .v1-dynamic-backsheet { position: fixed; inset: 0; z-index: -2; pointer-events: none; background: radial-gradient(circle at 50% 50%, rgba(255,85,0,0.08) 0%, #000000 80%); }
        .v1-glow-bottom-right { position: fixed; bottom: -20%; right: -20%; width: 1100px; height: 1100px; background: radial-gradient(circle, rgba(255,85,0,0.28) 0%, rgba(245,158,11,0.14) 45%, rgba(251,191,36,0.04) 75%, transparent 100%); filter: blur(150px); pointer-events: none; z-index: 1; }

        .v1-header { position: sticky; top: 0; z-index: 100; background: var(--nav-bg); backdrop-filter: blur(20px); border-bottom: 1px solid var(--border-color); }
        .v1-header-inner { max-width: 1200px; margin: 0 auto; padding: 16px 24px; display: flex; justify-content: space-between; align-items: center; }
        .v1-logo { font-family: var(--font-display); font-weight: 800; font-size: 1.35rem; color: var(--text-main); letter-spacing: -0.04em; text-transform: lowercase; }
        .v1-nav { display: flex; gap: 20px; align-items: center; }
        .v1-nav-link { display: flex; align-items: center; gap: 6px; color: var(--text-muted); text-decoration: none; font-size: 0.9rem; transition: color 0.2s; }
        .v1-nav-link:hover { color: var(--accent-primary); }

        .v1-hero { position: relative; padding: 180px 24px 140px; text-align: center; overflow: hidden; }
        .v1-hero-bg-word { position: absolute; left: 10%; top: 15%; font-family: var(--font-display); font-size: 10vw; color: rgba(255,85,0,0.02); font-weight: 800; pointer-events: none; user-select: none; }
        .v1-hero-content { position: relative; z-index: 10; max-width: 900px; margin: 0 auto; }
        .v1-hero-badge { display: inline-flex; align-items: center; gap: 12px; padding: 8px 24px; background: rgba(255,85,0,0.08); border: 1px solid rgba(255,85,0,0.18); border-radius: 24px; margin-bottom: 32px; font-family: var(--font-display); font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; font-size: 0.76rem; color: var(--accent-primary); }
        .badge-display-text { background: linear-gradient(135deg, #ff5500, #fbbf24); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
        .badge-dot-separator { color: rgba(255,85,0,0.35); font-weight: 800; }
        .v1-hero-title { font-size: clamp(3.2rem, 8vw, 6.2rem); font-weight: 800; letter-spacing: -0.05em; line-height: 1.02; margin-bottom: 24px; color: var(--text-main); text-transform: uppercase; }
        .v1-hero-title span { background: linear-gradient(135deg, #ff5500, #f59e0b, #fbbf24); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
        .v1-hero-subtitle { font-size: clamp(1.25rem, 2.5vw, 1.8rem); font-weight: 600; margin-bottom: 28px; max-width: 650px; margin-left: auto; margin-right: auto; letter-spacing: -0.02em; }
        .v1-hero-desc { font-size: 1.15rem; color: var(--text-muted); max-width: 620px; margin: 0 auto 40px; line-height: 1.75; }
        .v1-hero-ctas { display: flex; gap: 16px; justify-content: center; flex-wrap: wrap; }

        .v1-btn-primary { display: inline-flex; align-items: center; gap: 8px; padding: 14px 28px; background: linear-gradient(135deg, #ff5500, #f59e0b); color: #fff; border: none; border-radius: 12px; font-size: 1rem; font-weight: 600; cursor: pointer; font-family: var(--font-sans); box-shadow: 0 4px 20px rgba(255,85,0,0.25); transition: transform 0.2s, box-shadow 0.2s; }
        .v1-btn-primary:hover { box-shadow: 0 6px 24px rgba(245,158,11,0.4); }
        .v1-btn-ghost { display: inline-flex; align-items: center; gap: 8px; padding: 14px 28px; background: transparent; color: var(--text-main); border: 1px solid var(--border-color); border-radius: 12px; font-size: 1rem; font-weight: 500; cursor: pointer; text-decoration: none; font-family: var(--font-sans); transition: border-color 0.2s; }
        .v1-btn-ghost:hover { border-color: var(--accent-primary); }

        .v1-section { max-width: 1100px; margin: 0 auto; padding: 120px 24px; position: relative; z-index: 10; }
        .v1-section-title { font-size: 2.6rem; font-weight: 800; text-align: center; margin-bottom: 14px; font-family: var(--font-display); letter-spacing: -0.03em; text-transform: uppercase; }
        .v1-section-subtitle { text-align: center; color: var(--text-muted); margin-bottom: 64px; font-size: 1.15rem; max-width: 650px; margin-left: auto; margin-right: auto; line-height: 1.6; }
        .v1-stats-row { display: flex; justify-content: center; gap: 64px; flex-wrap: wrap; }
        .v1-stat-card { text-align: center; }
        .v1-stat-number { display: block; font-size: 3.8rem; font-weight: 800; font-family: var(--font-mono); color: var(--accent-primary); line-height: 1; }
        .v1-stat-label { display: block; margin-top: 10px; font-size: 0.95rem; color: var(--text-muted); }

        /* STICKY CH1 */
        .v1-sticky-scroll-container { position: relative; height: 280vh; width: 100%; }
        .v1-sticky-viewport { position: sticky; top: 0; height: 100vh; width: 100%; overflow: hidden; display: flex; align-items: center; justify-content: center; background: transparent; color: var(--text-main); z-index: 20; }
        .v1-sticky-bg-text-wrapper { position: absolute; width: 100%; height: 100vh; top: 0; left: 0; display: flex; align-items: center; justify-content: center; pointer-events: none; z-index: 1; }
        .v1-sticky-bg-text-layer { position: absolute; width: 100%; text-align: center; top: 22%; font-size: clamp(3rem, 10vw, 7.5rem); font-weight: 800; font-family: var(--font-display); text-transform: uppercase; letter-spacing: -0.04em; opacity: 0; will-change: opacity; }
        .v1-sticky-narrative-box { position: relative; width: 100%; height: 100vh; z-index: 10; }
        .v1-sticky-card-layer { position: absolute; left: 0; top: 0; display: flex; align-items: center; justify-content: center; will-change: transform, opacity; }

        /* YELLOW CARDS */
        .sc-panel { width: 100%; height: 360px; border-radius: 24px; overflow: hidden; display: flex; align-items: center; justify-content: center; position: relative; }
        .sc-yellow { background: #FFE500; border: 1.5px solid rgba(0,0,0,0.07); box-shadow: 0 40px 80px rgba(0,0,0,0.10), 0 8px 24px rgba(200,140,0,0.20), 0 1px 0 rgba(255,255,255,0.65) inset; }

        /* Grid 7x4 */
        .sc-grid-7x4 { display: grid; grid-template-columns: repeat(7, 1fr); gap: 8px; padding: 44px; width: 100%; height: 100%; box-sizing: border-box; }
        .sc-cell { border-radius: 4px; background: rgba(0,0,0,0.07); animation: scCellPulse 2.8s ease-in-out infinite; }
        @keyframes scCellPulse { 0%, 100% { opacity: 0.45; background: rgba(0,0,0,0.07); } 50% { opacity: 1; background: rgba(0,0,0,0.28); } }

        /* Flow bars */
        .sc-bars-v { display: flex; align-items: flex-end; justify-content: center; gap: 14px; padding: 56px 48px 64px; height: 100%; width: 100%; box-sizing: border-box; }
        .sc-bar-v { flex: 1; max-width: 32px; min-height: 8px; height: calc(var(--bh) * 200px); background: rgba(0,0,0,0.22); border-radius: 4px 4px 0 0; transform-origin: bottom; animation: scBarGrow 2.2s ease-in-out infinite; }
        @keyframes scBarGrow { 0%, 100% { transform: scaleY(0.78); opacity: 0.45; } 50% { transform: scaleY(1.0); opacity: 1; } }

        /* Orbit rings */
        .sc-rings-center { position: relative; width: 200px; height: 200px; display: flex; align-items: center; justify-content: center; }
        .sc-ring { position: absolute; border-radius: 50%; }
        .sc-ring-outer { width: 180px; height: 180px; border: 1.5px dashed rgba(0,0,0,0.14); animation: scRingCW 18s linear infinite; }
        .sc-ring-mid { width: 118px; height: 118px; border: 1.5px solid rgba(0,0,0,0.20); animation: scRingCCW 11s linear infinite; }
        .sc-ring-inner { width: 60px; height: 60px; border: 2px dashed rgba(0,0,0,0.28); animation: scRingCW 6s linear infinite; }
        .sc-center-dot { width: 14px; height: 14px; border-radius: 50%; background: rgba(0,0,0,0.42); position: absolute; animation: scDotPulse 2.2s ease-in-out infinite; }
        @keyframes scRingCW { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        @keyframes scRingCCW { from { transform: rotate(0deg); } to { transform: rotate(-360deg); } }
        @keyframes scDotPulse { 0%, 100% { transform: scale(0.75); opacity: 0.55; } 50% { transform: scale(1.25); opacity: 1; } }

        /* Node chain */
        .sc-nodes-row { display: flex; align-items: center; justify-content: space-between; width: calc(100% - 80px); position: relative; }
        .sc-node-line { position: absolute; height: 1.5px; width: 100%; background: rgba(0,0,0,0.12); top: 50%; transform: translateY(-50%); }
        .sc-node-item { position: relative; z-index: 2; display: flex; align-items: center; justify-content: center; animation: scNodeGlow 1.92s ease-in-out infinite; }
        .sc-node-circle { width: 22px; height: 22px; border-radius: 50%; background: rgba(0,0,0,0.14); border: 2px solid rgba(0,0,0,0.26); }
        .sc-node-pulse { position: absolute; width: 40px; height: 40px; border-radius: 50%; background: radial-gradient(circle, rgba(0,0,0,0.12) 0%, transparent 70%); animation: scNodePulse 1.92s ease-in-out infinite; }
        @keyframes scNodeGlow { 0%, 100% { opacity: 0.28; } 50% { opacity: 1; } }
        @keyframes scNodePulse { 0%, 100% { transform: scale(0.7); opacity: 0; } 50% { transform: scale(1.3); opacity: 1; } }

        /* GLASSMORPHIC CAPABILITY CARDS */
        .editorial-capabilities-list { display: flex; flex-direction: column; gap: 90px; margin-top: 60px; }
        .editorial-row { display: grid; grid-template-columns: 1fr 1.1fr; gap: 64px; align-items: center; padding-bottom: 60px; border-bottom: 1px solid var(--border-color); }
        .editorial-row:last-child { border-bottom: none; }
        .editorial-text-col { display: flex; flex-direction: column; gap: 16px; }
        .row-number { font-family: var(--font-display); font-size: 1.8rem; font-weight: 800; color: var(--accent-primary); }
        .editorial-text-col h3 { font-size: 2.2rem; font-weight: 800; font-family: var(--font-display); text-transform: uppercase; letter-spacing: -0.02em; }
        .editorial-text-col p { font-size: 1.1rem; color: var(--text-muted); line-height: 1.7; }
        .editorial-visual-col { display: flex; justify-content: center; }
        .cap-glass-card { width: 100%; max-width: 440px; height: 250px; background: rgba(12,10,16,0.68); backdrop-filter: blur(28px); -webkit-backdrop-filter: blur(28px); border: 1px solid rgba(255,85,0,0.16); border-radius: 20px; box-shadow: 0 24px 64px rgba(0,0,0,0.42), 0 1px 0 rgba(255,85,0,0.09) inset; display: flex; flex-direction: column; overflow: hidden; padding: 18px; transition: border-color 0.3s ease, box-shadow 0.3s ease; }
        .cap-glass-card:hover { border-color: rgba(255,85,0,0.30); box-shadow: 0 32px 80px rgba(0,0,0,0.52), 0 0 0 1px rgba(255,85,0,0.08), 0 1px 0 rgba(255,85,0,0.14) inset; }
        .window-bar { display: flex; gap: 7px; margin-bottom: 18px; }
        .window-bar span { width: 11px; height: 11px; border-radius: 50%; }
        .window-bar span:nth-child(1) { background: rgba(255,85,0,0.55); }
        .window-bar span:nth-child(2) { background: rgba(251,191,36,0.55); }
        .window-bar span:nth-child(3) { background: rgba(255,85,0,0.20); }
        .chat-scene { display: flex; flex-direction: column; gap: 8px; font-family: var(--font-mono); font-size: 0.76rem; }
        .chat-bubble { padding: 6px 12px; border-radius: 10px; max-width: 80%; }
        .chat-bubble.student { background: rgba(255,255,255,0.03); color: var(--text-muted); align-self: flex-end; }
        .chat-bubble.mentor { background: rgba(255,85,0,0.08); color: var(--text-main); border-left: 2px solid var(--accent-primary); align-self: flex-start; }
        .chat-bubble.suggestion { background: rgba(251,191,36,0.06); color: #fbbf24; align-self: center; font-size: 0.72rem; }
        .cli-scene { font-family: var(--font-mono); font-size: 0.76rem; line-height: 1.6; }
        .cli-line { color: var(--accent-primary); margin: 0; }
        .cli-output.error { margin: 4px 0; color: #ff5500; background: rgba(255,85,0,0.04); padding: 4px 8px; border-radius: 4px; }
        .checklist-scene { font-family: var(--font-mono); font-size: 0.76rem; display: flex; flex-direction: column; gap: 10px; }
        .progress-row { display: flex; justify-content: space-between; color: var(--text-muted); font-size: 0.7rem; }
        .checklist-item { display: flex; align-items: center; gap: 8px; color: var(--text-muted); }
        .checklist-item.done { color: var(--text-main); }
        .checklist-item.done svg { color: #fbbf24; }

        /* STICKY CH2 */
        .v2-sticky-scroll-container { position: relative; height: 280vh; width: 100%; background: #050506; }
        .v2-sticky-viewport { position: sticky; top: 0; height: 100vh; width: 100%; overflow: hidden; display: flex; align-items: center; justify-content: center; background: #050506; color: #ffffff; z-index: 20; }
        .v2-sticky-bg-text { position: absolute; width: 100%; text-align: center; top: 22%; font-size: clamp(3rem,10vw,7.5rem); font-weight: 800; color: rgba(255,85,0,0.04); text-transform: uppercase; letter-spacing: -0.04em; pointer-events: none; z-index: 1; font-family: var(--font-display); }
        .arch-split-container { position: relative; z-index: 10; width: 100%; max-width: 1100px; margin: 0 auto; display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 80px; align-items: center; padding: 0 24px; }
        .arch-editorial-col { display: flex; flex-direction: column; gap: 32px; }
        .arch-editorial-step { display: flex; flex-direction: column; gap: 8px; opacity: 0.4; color: var(--text-muted); transition: all 0.5s ease; }
        .step-num { font-family: var(--font-mono); font-size: 0.8rem; font-weight: 700; letter-spacing: 0.1em; }
        .arch-editorial-step h3 { font-size: 1.8rem; font-weight: 800; font-family: var(--font-display); text-transform: uppercase; letter-spacing: -0.01em; color: inherit; }
        .arch-editorial-step p { font-size: 0.95rem; line-height: 1.6; color: inherit; }
        .arch-visual-col { display: flex; justify-content: center; align-items: center; }
        .arch-visual-wrapper { position: relative; width: 320px; height: 320px; background: #FFE500; border: 1.5px solid rgba(0,0,0,0.07); border-radius: 24px; box-shadow: 0 40px 80px rgba(0,0,0,0.35), 0 4px 16px rgba(255,220,0,0.25); display: flex; align-items: center; justify-content: center; overflow: hidden; }
        .arch-visual-panel { position: absolute; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; will-change: opacity, transform; }

        /* Arch showcase content */
        .arch-sc-content { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; }
        .arch-sc-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; padding: 48px; width: 100%; height: 100%; box-sizing: border-box; }
        .arch-sc-cell { border-radius: 5px; background: rgba(0,0,0,0.08); animation: scCellPulse 2.8s ease-in-out infinite; }
        .arch-sc-bars { display: flex; align-items: flex-end; justify-content: center; gap: 16px; padding: 60px 52px 72px; height: 100%; width: 100%; box-sizing: border-box; }
        .arch-sc-bar { flex: 1; max-width: 36px; min-height: 10px; height: calc(var(--bh) * 160px); background: rgba(0,0,0,0.22); border-radius: 4px 4px 0 0; transform-origin: bottom; animation: scBarGrow 2.2s ease-in-out infinite; }
        .arch-sc-rings { position: relative; width: 160px; height: 160px; display: flex; align-items: center; justify-content: center; }
        .arch-ring { position: absolute; border-radius: 50%; }
        .arch-ring-outer { width: 150px; height: 150px; border: 1.5px dashed rgba(0,0,0,0.16); animation: scRingCW 16s linear infinite; }
        .arch-ring-inner { width: 80px; height: 80px; border: 1.5px solid rgba(0,0,0,0.22); animation: scRingCCW 9s linear infinite; }
        .arch-ring-dot { width: 14px; height: 14px; border-radius: 50%; background: rgba(0,0,0,0.40); position: absolute; animation: scDotPulse 2s ease-in-out infinite; }
        .arch-sc-nodes { display: flex; align-items: center; justify-content: space-between; width: calc(100% - 72px); position: relative; }
        .arch-node-line { position: absolute; height: 1.5px; width: 100%; background: rgba(0,0,0,0.14); top: 50%; transform: translateY(-50%); }
        .arch-node-item { position: relative; z-index: 2; display: flex; align-items: center; justify-content: center; animation: scNodeGlow 1.92s ease-in-out infinite; }
        .arch-node-dot { width: 20px; height: 20px; border-radius: 50%; background: rgba(0,0,0,0.16); border: 2px solid rgba(0,0,0,0.28); }
        .arch-node-pulse { position: absolute; width: 38px; height: 38px; border-radius: 50%; background: radial-gradient(circle, rgba(0,0,0,0.14) 0%, transparent 70%); animation: scNodePulse 1.92s ease-in-out infinite; }

        /* CURRICULUM */
        .editorial-curriculum-list { display: flex; flex-direction: column; gap: 40px; margin-top: 60px; }
        .editorial-curr-row { display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 64px; align-items: center; padding-bottom: 40px; border-bottom: 1.5px solid var(--border-color); }
        .editorial-curr-row:last-child { border-bottom: none; }
        .curr-meta { display: flex; gap: 24px; align-items: center; }
        .curr-num { font-family: var(--font-display); font-size: 2.2rem; font-weight: 800; color: var(--accent-primary); }
        .curr-meta h3 { font-size: 1.8rem; font-weight: 800; text-transform: uppercase; letter-spacing: -0.01em; }
        .curr-badge { display: inline-block; font-family: var(--font-mono); font-size: 0.72rem; font-weight: 700; color: #fbbf24; text-transform: uppercase; margin-top: 4px; }
        .curr-desc { font-size: 1.05rem; color: var(--text-muted); line-height: 1.7; }

        /* PLATFORMS */
        .editorial-platform-list { display: flex; flex-direction: column; gap: 36px; margin-top: 60px; }
        .editorial-plat-row { display: grid; grid-template-columns: 1fr 1fr 0.5fr; gap: 40px; align-items: center; padding-bottom: 36px; border-bottom: 1.5px solid var(--border-color); }
        .editorial-plat-row:last-child { border-bottom: none; }
        .plat-meta { display: flex; flex-direction: column; gap: 4px; }
        .plat-meta h3 { font-size: 1.8rem; font-weight: 800; font-family: var(--font-display); text-transform: uppercase; }
        .plat-meta span { font-family: var(--font-mono); font-size: 0.85rem; color: var(--accent-primary); font-weight: 700; }
        .editorial-plat-row p { color: var(--text-muted); font-size: 0.98rem; line-height: 1.6; }
        .plat-dl-btn { display: inline-flex; align-items: center; gap: 8px; padding: 10px 20px; background: transparent; border: 1.5px solid var(--border-color); border-radius: 10px; color: var(--text-main); font-family: var(--font-sans); font-size: 0.85rem; font-weight: 600; cursor: pointer; justify-content: center; transition: border-color 0.2s; }
        .plat-dl-btn:hover { border-color: var(--accent-primary); }

        /* CINEMATIC CTA */
        .v1-cta-section { padding: 0; }
        .v1-cta-cinematic { max-width: 1100px; margin: 0 auto; padding: 120px 24px 140px; position: relative; z-index: 10; }
        .v1-cta-rule { width: 100%; height: 1px; background: linear-gradient(90deg, var(--accent-primary), transparent); margin-bottom: 72px; opacity: 0.25; }
        .v1-cta-eyebrow { font-family: var(--font-mono); font-size: 0.78rem; letter-spacing: 0.14em; text-transform: uppercase; color: var(--accent-primary); margin-bottom: 36px; opacity: 0.7; }
        .v1-cta-headline { font-size: clamp(3.5rem, 9vw, 7rem); font-weight: 800; font-family: var(--font-display); letter-spacing: -0.05em; line-height: 0.92; margin-bottom: 64px; text-transform: uppercase; }
        .v1-cta-accent { background: linear-gradient(135deg, #ff5500, #fbbf24); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
        .v1-cta-terminal-line { display: flex; align-items: center; gap: 16px; padding: 20px 0; border-top: 1px solid var(--border-color); border-bottom: 1px solid var(--border-color); max-width: 640px; }
        .v1-cta-prompt { font-family: var(--font-mono); font-size: 1.1rem; color: var(--accent-primary); opacity: 0.5; }
        .v1-cta-code-text { font-family: var(--font-mono); font-size: 0.95rem; color: var(--text-muted); }
        .v1-cta-ambient { position: absolute; bottom: -160px; left: -60px; width: 700px; height: 700px; background: radial-gradient(circle, rgba(255,85,0,0.05) 0%, transparent 65%); pointer-events: none; }

        /* FOOTER */
        .v1-footer { border-top: 1px solid var(--border-color); padding: 64px 24px 24px; position: relative; z-index: 10; }
        .v1-footer-columns { max-width: 900px; margin: 0 auto 40px; display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 40px; }
        .v1-footer-col { display: flex; flex-direction: column; gap: 8px; }
        .v1-footer-col h4 { font-size: 0.85rem; font-weight: 600; margin-bottom: 4px; }
        .v1-footer-col a { color: var(--text-muted); font-size: 0.85rem; text-decoration: none; }
        .v1-footer-col a:hover { color: var(--accent-primary); }
        .v1-footer-bottom { text-align: center; font-size: 0.8rem; color: var(--text-muted); border-top: 1px solid var(--border-color); padding-top: 20px; }

        @media (max-width: 960px) {
          .editorial-row, .editorial-curr-row, .editorial-plat-row, .arch-split-container { grid-template-columns: 1fr; gap: 32px; }
          .v2-sticky-bg-text { display: none; }
        }
        @media (max-width: 768px) {
          .v1-stats-row { gap: 32px; }
          .v1-nav { gap: 12px; }
          .v1-footer-columns { grid-template-columns: 1fr; }
          .v1-hero { padding: 140px 24px 100px; }
          .v1-cta-headline { line-height: 1.0; }
        }
      `}</style>
    </div>
  );
}

export { AnimatedCounter };
