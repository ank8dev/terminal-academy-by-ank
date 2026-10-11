import React, { useState, useEffect, useRef } from 'react';
import { motion, useInView } from 'framer-motion';
import { Terminal, Download, Github, Package, Monitor, Shield, Sparkles, CheckCircle } from 'lucide-react';
import { MonitoringWidget } from '~/App';
import '~/App.css';

const MOCK_STATS = {
  cpu: '12%', ram: '256MB / 512MB', swap: '0MB', disk: '0.3ms',
  net: '1.2KB/s', load: '0.15', proc: '23', uptime: '00:14:22',
  latency: '4ms', sandbox: 'ACTIVE',
};

/* ── Animated counter ── */
function Counter({ end, suffix = '', label }: { end: number; suffix?: string; label: string }) {
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
    <div ref={ref} className="v5-counter">
      <span className="v5-counter-value">{count}{suffix}</span>
      <span className="v5-counter-label">{label}</span>
    </div>
  );
}

/* ── Fade-in section wrapper ── */
function FadeSection({ children, className = '', id = '' }: { children: React.ReactNode; className?: string; id?: string }) {
  return (
    <motion.section
      id={id}
      className={className}
      initial={{ opacity: 0, y: 40 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-80px' }}
      transition={{ duration: 0.6 }}
    >
      {children}
    </motion.section>
  );
}

/* ══════════════════════════════════════════════
   VARIANT 5 — BENTO BOX CAPABILITIES MATRIX
   ══════════════════════════════════════════════ */
export default function Variant5Bento() {
  return (
    <div className="v5-root">
      {/* ── HEADER ── */}
      <header className="v5-header">
        <div className="v5-header-inner">
          <div className="v5-logo">
            <Terminal size={18} style={{ color: 'var(--accent-primary)' }} />
            <span>t//a</span>
          </div>
          <nav className="v5-nav">
            <a href="#bento" className="v5-nav-link">Bento Grid</a>
            <a href="#expanded" className="v5-nav-link">Capabilities</a>
            <a href="#telemetry" className="v5-nav-link">Telemetry</a>
            <a href="#download" className="v5-nav-link">Download</a>
            <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="v5-nav-link">
              <Github size={16} />
            </a>
          </nav>
        </div>
      </header>

      {/* ── HERO ── */}
      <section className="v5-hero">
        <div className="v5-hero-mesh" />
        <div className="v5-hero-badge">
          <Sparkles size={12} style={{ color: 'var(--accent-primary)' }} /> Asymmetric Capabilities Matrix
        </div>
        <h1>Everything You Need to <span style={{ color: 'var(--accent-primary)' }}>Master Systems</span></h1>
        <p>A complete sandbox training environment packaged in a native client smaller than a single media file.</p>
        <div className="v5-hero-ctas">
          <motion.a href="#bento" className="v5-btn-primary" whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.97 }}>
            Explore Matrix
          </motion.a>
          <motion.a href="#download" className="v5-btn-secondary" whileHover={{ scale: 1.03 }}>
            Download Client
          </motion.a>
        </div>
      </section>

      {/* ── BENTO GRID ── */}
      <section className="v5-bento-section" id="bento">
        <div className="v5-bento-grid">
          {/* Cell 1: Terminal Sandbox (span 2) */}
          <div className="v5-bento-cell v5-bento-wide">
            <span className="v5-bento-label">Terminal Sandbox</span>
            <div className="v5-bento-terminal">
              <pre>{`\x1b[36mstudent@sandbox:~$\x1b[0m ls -la`}</pre>
              <pre style={{ color: 'var(--text-muted)' }}>{`-rw-r--r--  1 student  240 Jul 12 app.py
-rw-r--r--  1 student  105 Jul 12 config.txt
drwxr-xr-x  2 student 4096 Jul 12 src/`}</pre>
              <pre>{`\x1b[36mstudent@sandbox:~$\x1b[0m docker ps`}</pre>
              <pre style={{ color: 'var(--text-muted)' }}>{`CONTAINER ID  IMAGE         STATUS    PORTS
9e8d7c6b5a4f  alpine:latest Up 10min  80/tcp`}</pre>
            </div>
          </div>

          {/* Cell 2: AI Mentor */}
          <div className="v5-bento-cell">
            <span className="v5-bento-label">AI Mentor</span>
            <div className="v5-chat-bubble">
              <div className="v5-chat-avatar">A</div>
              <div className="v5-chat-text">
                Try running <code>chmod 644</code> on <code>config.txt</code> to set read permissions correctly.
              </div>
            </div>
          </div>

          {/* Cell 3: Curriculum */}
          <div className="v5-bento-cell">
            <span className="v5-bento-label">Curriculum</span>
            <div className="v5-curriculum-list">
              {[
                { name: 'Linux Core', done: true },
                { name: 'Networking', done: false },
                { name: 'DevOps', done: false },
                { name: 'Hosting', done: false },
              ].map((c, i) => (
                <div key={i} className="v5-curriculum-item">
                  <span className={`v5-check ${c.done ? 'v5-check-done' : ''}`}>{c.done ? '✓' : '○'}</span>
                  <span>{c.name}</span>
                </div>
              ))}
              <div className="v5-progress-bar">
                <div className="v5-progress-fill" style={{ width: '25%' }} />
              </div>
            </div>
          </div>

          {/* Cell 4: Live Telemetry (span 2) */}
          <div className="v5-bento-cell v5-bento-wide v5-bento-telemetry widget-container">
            <span className="v5-bento-label" style={{ padding: '0 12px' }}>Live Telemetry</span>
            <MonitoringWidget bindDrag={undefined} lang="en" stats={MOCK_STATS} />
          </div>

          {/* Cell 5: Lightweight */}
          <div className="v5-bento-cell">
            <span className="v5-bento-label">Lightweight</span>
            <div className="v5-size-chart">
              {[
                { os: 'macOS DMG', size: 6, max: 10 },
                { os: 'Windows MSI', size: 3, max: 10 },
                { os: 'Linux AppImage', size: 8, max: 10 },
              ].map((s, i) => (
                <div key={i} className="v5-size-row">
                  <span className="v5-size-label">{s.os}</span>
                  <div className="v5-size-bar-bg">
                    <div className="v5-size-bar-fill" style={{ width: `${(s.size / s.max) * 100}%` }} />
                  </div>
                  <span className="v5-size-value">~{s.size}MB</span>
                </div>
              ))}
            </div>
          </div>

          {/* Cell 6: Open Source */}
          <div className="v5-bento-cell">
            <span className="v5-bento-label">Open Source</span>
            <div className="v5-oss-content">
              <div className="v5-oss-badges">
                <span className="v5-oss-badge"><Github size={14} /> GitHub</span>
                <span className="v5-oss-badge">AGPL-3.0</span>
              </div>
              <motion.a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="v5-btn-outline"
                whileHover={{ scale: 1.03 }}
              >
                View Source →
              </motion.a>
            </div>
          </div>
        </div>
      </section>

      {/* ── CORE FEATURES EXPANDED ── */}
      <FadeSection className="v5-section" id="expanded">
        <h2 className="v5-section-title">Core capabilities designed for systems developers</h2>
        <p className="v5-section-subtitle">No browser approximations. Everything executes natively on your machine inside disposable virtualization hooks.</p>
        <div className="v5-expanded-features">
          {[
            { icon: Package, title: 'Zero Dependencies', desc: 'No cloud accounts, subscriptions, or network latency. All code compiles and runs locally on your engine workspace.' },
            { icon: Monitor, title: 'Multiplatform Client', desc: 'Fully responsive macOS, Linux, and Windows clients built with native Rust hooks.' },
            { icon: Shield, title: 'Isolated Workspace', desc: 'Secure Docker overlays preserve host storage. Break folders, alter configurations, or run loops safely.' },
          ].map((f, i) => (
            <motion.div key={i} className="v5-expanded-card" whileHover={{ y: -3 }}>
              <div className="v5-expanded-icon"><f.icon size={22} /></div>
              <h3>{f.title}</h3>
              <p>{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </FadeSection>

      {/* ── TELEMETRY ENGINE ── */}
      <FadeSection className="v5-section" id="telemetry">
        <h2 className="v5-section-title">Telemetry Engine</h2>
        <p className="v5-section-subtitle">The native dashboard monitors resources inside container scopes continuously.</p>
        <div className="v5-telemetry-visual widget-container">
          <MonitoringWidget bindDrag={undefined} lang="en" stats={MOCK_STATS} />
        </div>
      </FadeSection>

      {/* ── DELIBERATE SYSTEM PRACTICE ── */}
      <FadeSection className="v5-section">
        <div className="v5-deliberate-grid">
          <div className="v5-deliberate-text">
            <h2>Learn Systems by Practice</h2>
            <p>Static tutorials explain variables, but skip the complexity of diagnostics. We drop you directly into broken sandboxes so you can construct diagnostic strategies.</p>
            <div className="v5-deliberate-checks">
              <div className="v5-check-row">
                <CheckCircle size={16} className="v5-check-icon" />
                <span>Simulates real DevOps sysadmin incidents.</span>
              </div>
              <div className="v5-check-row">
                <CheckCircle size={16} className="v3-check-icon" />
                <span>Local verify commands check configurations instantly.</span>
              </div>
              <div className="v5-check-row">
                <CheckCircle size={16} className="v3-check-icon" />
                <span>100% self-contained workspace runtime.</span>
              </div>
            </div>
          </div>
          <div className="v5-deliberate-code">
            <pre className="v5-code-box">{`# Start learning track
agy run linux --incident permissions
# Terminal Academy compiler
Resolving syllabus dependencies...
Mounting local overlay files...
Sandbox active.`}</pre>
          </div>
        </div>
      </FadeSection>

      {/* ── PLATFORM SUPPORT ── */}
      <FadeSection className="v5-section">
        <h2 className="v5-section-title">Available Everywhere</h2>
        <p className="v5-section-subtitle">Tauri binaries are compiled for all three major operating systems.</p>
        <div className="v5-platforms-row">
          {['macOS', 'Windows', 'Linux'].map(os => (
            <motion.button key={os} className="v5-platform-pill" whileHover={{ scale: 1.04 }}>
              <Download size={14} /> {os} Client
            </motion.button>
          ))}
        </div>
      </FadeSection>

      {/* ── TRUST / METRICS ── */}
      <FadeSection className="v5-section">
        <div className="v5-counters-row">
          <Counter end={6} suffix="MB" label="Install Weight" />
          <Counter end={4} suffix="" label="Learning Tracks" />
          <Counter end={50} suffix="ms" label="Launch Speed" />
        </div>
      </FadeSection>

      {/* ── CTA ── */}
      <FadeSection className="v5-cta-section" id="download">
        <div className="v5-cta-card">
          <h2>Master command infrastructures today</h2>
          <p>Get the desktop installer and solve real systems incidents offline.</p>
          <div className="v5-cta-actions">
            <motion.button className="v5-btn-primary" whileHover={{ scale: 1.04 }}>
              <Download size={18} /> Download Client
            </motion.button>
            <motion.a href="https://github.com" target="_blank" rel="noopener noreferrer" className="v5-btn-outline" whileHover={{ scale: 1.03 }}>
              View on GitHub
            </motion.a>
          </div>
        </div>
      </FadeSection>

      {/* ── FOOTER ── */}
      <footer className="v5-footer">
        <div className="v5-footer-columns">
          <div className="v5-footer-col">
            <h4>Product</h4>
            <a href="#">Capabilities</a>
            <a href="#">Telemetry</a>
            <a href="#">Changelog</a>
          </div>
          <div className="v5-footer-col">
            <h4>Resources</h4>
            <a href="#">Documentation</a>
            <a href="https://github.com" target="_blank" rel="noopener noreferrer">GitHub Code</a>
            <a href="#">Syllabus MD</a>
          </div>
          <div className="v5-footer-col">
            <h4>About</h4>
            <a href="#">License (AGPL-3.0)</a>
            <a href="#">Privacy Policy</a>
          </div>
        </div>
        <div className="v5-footer-bottom">
          © 2025 Terminal Academy. All rights reserved. Offline-first system sandbox.
        </div>
      </footer>

      <style>{`
        .v5-root { background: var(--bg-base); color: var(--text-main); }
        .v5-header { position: sticky; top: 0; z-index: 100; background: var(--nav-bg); backdrop-filter: blur(20px); border-bottom: 1px solid var(--border-color); }
        .v5-header-inner { max-width: 1200px; margin: 0 auto; padding: 12px 24px; display: flex; align-items: center; justify-content: space-between; }
        .v5-logo { display: flex; align-items: center; gap: 8px; font-family: var(--font-mono); font-weight: 700; font-size: 1.1rem; }
        .v5-nav { display: flex; gap: 20px; align-items: center; }
        .v5-nav-link { color: var(--text-muted); font-size: 0.9rem; text-decoration: none; transition: color 0.2s; display: flex; align-items: center; }
        .v5-nav-link:hover { color: var(--accent-primary); }

        .v5-hero { text-align: center; padding: 120px 24px 80px; position: relative; overflow: hidden; }
        .v5-hero-mesh { position: absolute; top: -150px; left: 50%; transform: translateX(-50%); width: 750px; height: 350px; background: radial-gradient(circle, rgba(255,85,0,0.1) 0%, transparent 65%); filter: blur(60px); pointer-events: none; }
        .v5-hero-badge { display: inline-flex; align-items: center; gap: 6px; padding: 6px 14px; background: rgba(255,85,0,0.08); border: 1px solid rgba(255,85,0,0.15); border-radius: 20px; font-size: 0.8rem; color: var(--accent-primary); margin-bottom: 24px; font-family: var(--font-mono); }
        .v5-hero h1 { font-size: clamp(2.2rem, 5vw, 3.8rem); font-weight: 700; line-height: 1.15; margin-bottom: 16px; }
        .v5-hero p { color: var(--text-muted); font-size: 1.15rem; margin-bottom: 28px; max-width: 600px; margin-left: auto; margin-right: auto; line-height: 1.6; }
        .v5-hero-ctas { display: flex; gap: 16px; justify-content: center; flex-wrap: wrap; }

        .v5-btn-primary { display: inline-flex; align-items: center; gap: 8px; padding: 14px 28px; background: var(--accent-primary); color: #fff; border: none; border-radius: 12px; font-size: 1rem; font-weight: 600; cursor: pointer; text-decoration: none; font-family: var(--font-sans); box-shadow: 0 0 30px rgba(255,85,0,0.3); }
        .v5-btn-secondary { display: inline-flex; align-items: center; gap: 8px; padding: 14px 28px; background: transparent; color: var(--text-main); border: 1px solid var(--border-color); border-radius: 12px; font-size: 1rem; cursor: pointer; text-decoration: none; font-family: var(--font-sans); transition: border-color 0.2s; }
        .v5-btn-secondary:hover { border-color: var(--accent-primary); }

        .v5-bento-section { max-width: 1100px; margin: 0 auto; padding: 48px 24px 80px; }
        .v5-bento-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
        .v5-bento-wide { grid-column: span 2; }
        .v5-bento-cell { background: var(--bg-raised); backdrop-filter: blur(16px); border: 1px solid var(--border-color); border-radius: 16px; padding: 24px; transition: border-color 0.3s; overflow: hidden; }
        .v5-bento-cell:hover { border-color: var(--border-highlight); }
        .v5-bento-label { display: block; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-muted); margin-bottom: 14px; }

        .v5-bento-terminal { font-family: var(--font-mono); font-size: 0.82rem; line-height: 1.7; color: var(--term-text); background: var(--bg-base); border-radius: 10px; padding: 14px; }
        .v5-bento-terminal pre { margin: 0; white-space: pre-wrap; }

        .v5-chat-bubble { display: flex; gap: 12px; align-items: flex-start; }
        .v5-chat-avatar { width: 32px; height: 32px; border-radius: 50%; background: var(--accent-primary); color: #fff; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.9rem; flex-shrink: 0; }
        .v5-chat-text { background: rgba(255,85,0,0.06); border: 1px solid rgba(255,85,0,0.12); border-radius: 10px; padding: 12px 14px; font-size: 0.9rem; color: var(--text-muted); line-height: 1.5; }
        .v5-chat-text code { font-family: var(--font-mono); color: var(--accent-primary); background: rgba(255,85,0,0.08); padding: 1px 5px; border-radius: 3px; }

        .v5-curriculum-list { display: flex; flex-direction: column; gap: 8px; }
        .v5-curriculum-item { display: flex; align-items: center; gap: 8px; font-size: 0.9rem; }
        .v5-check { width: 20px; text-align: center; color: var(--text-muted); }
        .v5-check-done { color: #27c93f; }
        .v5-progress-bar { height: 5px; background: rgba(255,255,255,0.05); border-radius: 3px; margin-top: 8px; overflow: hidden; }
        .v5-progress-fill { height: 100%; background: var(--accent-primary); border-radius: 3px; }

        .v5-bento-telemetry .widget-content { height: 220px; }

        .v5-size-chart { display: flex; flex-direction: column; gap: 10px; }
        .v5-size-row { display: flex; align-items: center; gap: 10px; }
        .v5-size-label { width: 110px; font-size: 0.82rem; color: var(--text-muted); flex-shrink: 0; }
        .v5-size-bar-bg { flex: 1; height: 8px; background: rgba(255,255,255,0.05); border-radius: 4px; overflow: hidden; }
        .v5-size-bar-fill { height: 100%; background: var(--accent-primary); border-radius: 4px; }
        .v5-size-value { width: 50px; font-size: 0.82rem; color: var(--accent-primary); font-family: var(--font-mono); text-align: right; }

        .v5-oss-content { display: flex; flex-direction: column; gap: 14px; }
        .v5-oss-badges { display: flex; gap: 8px; flex-wrap: wrap; }
        .v5-oss-badge { display: inline-flex; align-items: center; gap: 5px; padding: 5px 12px; background: rgba(255,85,0,0.08); border: 1px solid rgba(255,85,0,0.12); border-radius: 16px; font-size: 0.8rem; color: var(--text-muted); }
        .v5-btn-outline { display: inline-flex; align-items: center; padding: 8px 16px; background: transparent; color: var(--accent-primary); border: 1px solid var(--border-color); border-radius: 8px; font-size: 0.85rem; text-decoration: none; font-family: var(--font-sans); cursor: pointer; transition: border-color 0.2s; }
        .v5-btn-outline:hover { border-color: var(--accent-primary); }

        .v5-section { max-width: 1100px; margin: 0 auto; padding: 100px 24px; }
        .v5-section-title { font-size: 2.2rem; font-weight: 700; text-align: center; margin-bottom: 12px; }
        .v5-section-subtitle { text-align: center; color: var(--text-muted); margin-bottom: 48px; font-size: 1.1rem; max-width: 600px; margin-left: auto; margin-right: auto; }

        .v5-expanded-features { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px; }
        .v5-expanded-card { padding: 32px; background: var(--bg-raised); border: 1px solid var(--border-color); border-radius: 16px; transition: border-color 0.3s; }
        .v5-expanded-card:hover { border-color: var(--border-highlight); }
        .v5-expanded-icon { width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; background: rgba(255,85,0,0.1); border-radius: 10px; color: var(--accent-primary); margin-bottom: 16px; }
        .v5-expanded-card h3 { font-size: 1.15rem; margin-bottom: 8px; font-weight: 600; }
        .v5-expanded-card p { color: var(--text-muted); font-size: 0.95rem; line-height: 1.6; }

        .v5-telemetry-visual { max-width: 600px; margin: 0 auto; border-radius: 16px; overflow: hidden; border: 1px solid var(--border-color); }
        .v5-telemetry-visual .widget-content { height: 320px; }

        .v5-deliberate-grid { display: grid; grid-template-columns: 1.2fr 1fr; gap: 48px; align-items: center; }
        .v5-deliberate-text h2 { font-size: 2rem; font-weight: 700; margin-bottom: 18px; }
        .v5-deliberate-text p { color: var(--text-muted); font-size: 1.05rem; line-height: 1.7; margin-bottom: 24px; }
        .v5-deliberate-checks { display: flex; flex-direction: column; gap: 14px; }
        .v5-check-row { display: flex; align-items: center; gap: 12px; font-size: 0.98rem; }
        .v5-check-icon { color: #27c93f; flex-shrink: 0; }
        .v5-deliberate-code { background: var(--term-bg); border: 1px solid var(--border-color); border-radius: 12px; padding: 24px; overflow-x: auto; }
        .v5-code-box { font-family: var(--font-mono); font-size: 0.85rem; color: var(--term-text); margin: 0; line-height: 1.6; }

        .v5-platforms-row { display: flex; justify-content: center; gap: 16px; flex-wrap: wrap; }
        .v5-platform-pill { display: inline-flex; align-items: center; gap: 8px; padding: 12px 24px; background: var(--bg-raised); border: 1px solid var(--border-color); border-radius: 20px; color: var(--text-main); font-size: 0.92rem; cursor: pointer; font-family: var(--font-sans); transition: border-color 0.2s; }
        .v5-platform-pill:hover { border-color: var(--accent-primary); }

        .v5-counters-row { display: flex; justify-content: center; gap: 64px; flex-wrap: wrap; }
        .v5-counter { text-align: center; }
        .v5-counter-value { display: block; font-size: 3rem; font-weight: 800; font-family: var(--font-mono); color: var(--accent-primary); line-height: 1; }
        .v5-counter-label { display: block; margin-top: 8px; font-size: 0.95rem; color: var(--text-muted); }

        .v5-cta-section { padding: 80px 24px 120px; }
        .v5-cta-card { max-width: 700px; margin: 0 auto; text-align: center; padding: 56px 36px; background: var(--bg-raised); border: 1px solid var(--accent-primary); border-radius: 20px; background-image: linear-gradient(var(--bg-raised), var(--bg-raised)), linear-gradient(135deg, rgba(255,85,0,0.3), rgba(180,83,9,0.3)); background-origin: border-box; background-clip: padding-box, border-box; }
        .v5-cta-card h2 { font-size: 2rem; margin-bottom: 12px; font-weight: 700; }
        .v5-cta-card p { color: var(--text-muted); margin-bottom: 32px; font-size: 1.05rem; }
        .v5-cta-actions { display: flex; gap: 16px; justify-content: center; flex-wrap: wrap; }
        .v5-btn-outline { display: inline-flex; align-items: center; gap: 8px; padding: 14px 28px; background: transparent; color: var(--text-main); border: 1px solid var(--border-color); border-radius: 12px; font-size: 1rem; cursor: pointer; text-decoration: none; font-family: var(--font-sans); transition: border-color 0.2s; }
        .v5-btn-outline:hover { border-color: var(--accent-primary); }

        .v5-footer { border-top: 1px solid var(--border-color); padding: 80px 24px 40px; }
        .v5-footer-columns { max-width: 900px; margin: 0 auto 48px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 40px; }
        .v5-footer-col { display: flex; flex-direction: column; gap: 10px; }
        .v5-footer-col h4 { font-size: 0.88rem; font-weight: 700; margin-bottom: 6px; color: var(--text-main); text-transform: uppercase; letter-spacing: 0.05em; }
        .v5-footer-col a { color: var(--text-muted); font-size: 0.9rem; text-decoration: none; transition: color 0.2s; }
        .v5-footer-col a:hover { color: var(--accent-primary); }
        .v5-footer-bottom { text-align: center; font-size: 0.85rem; color: var(--text-muted); border-top: 1px solid var(--border-color); padding-top: 24px; }

        @media (max-width: 768px) {
          .v5-bento-grid { grid-template-columns: 1fr; }
          .v5-bento-wide { grid-column: span 1; }
          .v5-footer-columns { grid-template-columns: 1fr; gap: 32px; }
          .v5-deliberate-grid { grid-template-columns: 1fr; gap: 32px; }
        }
      `}</style>
    </div>
  );
}
