import React, { useState, useEffect, useRef } from 'react';
import { motion, useInView } from 'framer-motion';
import { Terminal, Download, Github, Shield, Network, Activity, Server, ChevronRight } from 'lucide-react';
import { MonitoringWidget } from '~/App';
import { useMotion } from '@/providers/MotionProvider';
import '~/App.css';

const MOCK_STATS = {
  cpu: '12%', ram: '256MB / 512MB', swap: '0MB', disk: '0.3ms',
  net: '1.2KB/s', load: '0.15', proc: '23', uptime: '00:14:22',
  latency: '4ms', sandbox: 'ACTIVE',
};

const NODES = [
  { id: 'pty', label: 'Alpine PTY', x: 180, y: 80 },
  { id: 'docker', label: 'Docker Sandbox', x: 620, y: 80 },
  { id: 'nginx', label: 'Nginx Proxy', x: 180, y: 380 },
  { id: 'pg', label: 'PostgreSQL', x: 620, y: 380 },
];
const CENTER = { x: 400, y: 230 };

function nodePath(nx: number, ny: number, cx: number, cy: number, scrollOffset: number) {
  const mx = (nx + cx) / 2 + scrollOffset * 20;
  const my = (ny + cy) / 2 - scrollOffset * 15;
  return `M ${nx},${ny} Q ${mx},${my} ${cx},${cy}`;
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
    <div ref={ref} className="v4-metric">
      <span className="v4-metric-value">{count}{suffix}</span>
      <span className="v4-metric-label">{label}</span>
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
   VARIANT 4 — NETWORK TOPOLOGY / MOTION FLOW
   ══════════════════════════════════════════════ */
export default function Variant4MotionFlow() {
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);
  const { scrollProgress } = useMotion();

  return (
    <div className="v4-root">
      {/* ── HEADER ── */}
      <header className="v4-header">
        <div className="v4-header-inner">
          <div className="v4-logo">
            <Terminal size={18} style={{ color: 'var(--accent-primary)' }} />
            <span>t//a</span>
          </div>
          <nav className="v4-nav">
            <a href="#topology" className="v4-nav-link">Topology</a>
            <a href="#features" className="v4-nav-link">Capabilities</a>
            <a href="#layers" className="v4-nav-link">Architecture</a>
            <a href="#security" className="v4-nav-link">Security</a>
            <a href="#download" className="v4-nav-link">Download</a>
            <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="v4-nav-link">
              <Github size={16} />
            </a>
          </nav>
        </div>
      </header>

      {/* ── HERO ── */}
      <section className="v4-hero">
        <div className="v4-hero-glow" />
        <h1 className="v4-hero-title">
          Visualize Your <span className="v4-gradient-text">Infrastructure</span>
        </h1>
        <p className="v4-hero-sub">
          Every exercise executes inside an isolated runtime. Monitor resources, trace traffic pathways, 
          and examine system topologies interactively as you learn.
        </p>
        <div className="v4-hero-ctas">
          <motion.a href="#topology" className="v4-btn-primary" whileHover={{ scale: 1.03 }}>
            Explore Sandbox Topology
          </motion.a>
          <motion.button className="v4-btn-ghost" whileHover={{ scale: 1.03 }}>
            <Download size={16} /> Download Launcher
          </motion.button>
        </div>
      </section>

      {/* ── NETWORK TOPOLOGY ── */}
      <section className="v4-topology-section" id="topology">
        <h2 className="v4-section-title">Sandbox System Topology</h2>
        <p className="v4-section-sub">Hover over outer nodes to trace data bridges. Scroll down to see network paths morph dynamically.</p>
        <div className="v4-topology-container">
          <svg viewBox="0 0 800 460" className="v4-topology-svg">
            {/* Connection paths */}
            {NODES.map(n => {
              const isActive = hoveredNode === n.id;
              return (
                <path
                  key={`path-${n.id}`}
                  d={nodePath(n.x, n.y, CENTER.x, CENTER.y, scrollProgress)}
                  fill="none"
                  stroke={isActive ? '#ff5500' : 'rgba(255,85,0,0.2)'}
                  strokeWidth={isActive ? 3 : 1.5}
                  filter={isActive ? 'url(#glow)' : undefined}
                  style={{ transition: 'stroke 0.3s, stroke-width 0.3s' }}
                />
              );
            })}

            {/* Glow filter */}
            <defs>
              <filter id="glow">
                <feGaussianBlur stdDeviation="4" result="coloredBlur" />
                <feMerge>
                  <feMergeNode in="coloredBlur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
            </defs>

            {/* Center node */}
            <circle cx={CENTER.x} cy={CENTER.y} r="36" fill="var(--bg-raised)" stroke="var(--accent-primary)" strokeWidth="2" filter="url(#glow)" />
            <text x={CENTER.x} y={CENTER.y - 6} textAnchor="middle" fill="var(--accent-primary)" fontSize="11" fontWeight="700" fontFamily="var(--font-mono)">t//a</text>
            <text x={CENTER.x} y={CENTER.y + 10} textAnchor="middle" fill="var(--text-muted)" fontSize="9" fontFamily="var(--font-mono)">ENGINE</text>

            {/* Outer nodes */}
            {NODES.map(n => {
              const isActive = hoveredNode === n.id;
              return (
                <g
                  key={n.id}
                  onMouseEnter={() => setHoveredNode(n.id)}
                  onMouseLeave={() => setHoveredNode(null)}
                  style={{ cursor: 'pointer' }}
                >
                  <circle
                    cx={n.x} cy={n.y} r="28"
                    fill="var(--bg-raised)"
                    stroke={isActive ? 'var(--accent-primary)' : 'var(--border-color)'}
                    strokeWidth={isActive ? 2 : 1}
                    style={{ transition: 'stroke 0.3s, stroke-width 0.3s' }}
                  />
                  <text
                    x={n.x} y={n.y + 4}
                    textAnchor="middle"
                    fill={isActive ? 'var(--accent-primary)' : 'var(--text-muted)'}
                    fontSize="10"
                    fontWeight="600"
                    fontFamily="var(--font-mono)"
                    style={{ transition: 'fill 0.3s' }}
                  >
                    {n.label}
                  </text>
                </g>
              );
            })}
          </svg>
        </div>
      </section>

      {/* ── CORE CAPABILITIES ── */}
      <FadeSection className="v4-section" id="features">
        <h2 className="v4-section-title">Telemetry & Infrastructure</h2>
        <p className="v4-section-sub">A production-grade environment optimized for terminal testing.</p>
        <div className="v4-features-grid">
          {[
            { icon: Shield, title: 'Network Sandbox Isolation', desc: 'Each exercise generates complete container boundaries, ensuring hosts remain protected.' },
            { icon: Network, title: 'Virtual Bridges & Links', desc: 'Set ip links, examine bridges, build rules, and modify interfaces safely.' },
            { icon: Activity, title: 'Telemetry Metrics Stream', desc: 'Real-time CPU and Memory allocations read directly from system resources.' },
            { icon: Server, title: 'Automated State Recovery', desc: 'A single click resets the sandbox overlay. Recover from full directory bricks instantly.' },
          ].map((f, i) => (
            <motion.div key={i} className="v4-feature-card" whileHover={{ y: -3 }}>
              <div className="v4-feature-icon"><f.icon size={22} /></div>
              <h3>{f.title}</h3>
              <p>{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </FadeSection>

      {/* ── ARCHITECTURE LAYERS ── */}
      <FadeSection className="v4-section" id="layers">
        <h2 className="v4-section-title">The Three-Tier Architecture</h2>
        <p className="v4-section-sub">A lightweight native desktop wrapper communicating with standard container engines.</p>
        <div className="v4-stack-row">
          {[
            { label: 'Host Interface', tech: 'Tauri Desktop Wrapper', desc: 'Native operating system shells executing Webview windows with minimal resource footprints.' },
            { label: 'Sandbox Control', tech: 'Docker / Podman Overlay', desc: 'Alpine Linux system bases generating ephemeral containers with restricted host resources.' },
            { label: 'Telemetry Pipeline', tech: 'Sysctl Socket Intercept', desc: 'Unix socket interfaces reporting system process trees and hardware usage loops.' },
          ].map((s, i) => (
            <div key={i} className="v4-stack-card">
              <span className="v4-stack-label">{s.label}</span>
              <span className="v4-stack-tech">{s.tech}</span>
              <p>{s.desc}</p>
            </div>
          ))}
        </div>
      </FadeSection>

      {/* ── SECURITY DEEP DIVE ── */}
      <FadeSection className="v4-section" id="security">
        <div className="v4-sec-split">
          <div className="v4-sec-left">
            <h2>Zero-Trust Sandbox Isolation</h2>
            <p>Every terminal prompt links to a container runtime isolated from the native filesystem. Users can partition directories, destroy libraries, or load services without affecting their computer.</p>
            <ul className="v4-sec-list">
              <li>
                <ChevronRight size={16} className="v4-sec-bullet-icon" />
                <span>Docker-backed user namespace mappings prevent root escalation.</span>
              </li>
              <li>
                <ChevronRight size={16} className="v4-sec-bullet-icon" />
                <span>CPU and memory limits guard against runaway system scripts.</span>
              </li>
              <li>
                <ChevronRight size={16} className="v4-sec-bullet-icon" />
                <span>Isolated bridges route socket requests within the sandbox network only.</span>
              </li>
            </ul>
          </div>
          <div className="v4-sec-right">
            <div className="v4-sec-code-box">
              <pre className="v4-sec-pre">{`# Security Rules (iptables)
iptables -A FORWARD -i eth0 -o docker0 -j REJECT
iptables -A FORWARD -i docker0 -o eth0 -j ACCEPT
# CPU Share constraints
docker run --cpus="0.5" --memory="512m"`}</pre>
            </div>
          </div>
        </div>
      </FadeSection>

      {/* ── LIVE MONITORING DEMO ── */}
      <FadeSection className="v4-section">
        <h2 className="v4-section-title">Telemetry Engine Preview</h2>
        <p className="v4-section-sub">Below is the exact monitoring dashboard panel running in the client.</p>
        <div className="v4-monitor-container widget-container">
          <MonitoringWidget bindDrag={undefined} lang="en" stats={MOCK_STATS} />
        </div>
      </FadeSection>

      {/* ── TRUST / METRICS ── */}
      <FadeSection className="v4-section">
        <div className="v4-metrics-row">
          <AnimatedCounter end={99} suffix="%" label="Sandbox Availability" />
          <AnimatedCounter end={5} suffix="ms" label="Backend Latency" />
          <AnimatedCounter end={4} suffix="" label="Isolated Network Zones" />
        </div>
      </FadeSection>

      {/* ── CLIENT DOWNLOAD OPTIONS ── */}
      <FadeSection className="v4-section" id="download">
        <h2 className="v4-section-title">Supported Desktop Platforms</h2>
        <p className="v4-section-sub">Choose the target client launcher for your local developer machine.</p>
        <div className="v4-platform-grid">
          {[
            { name: 'macOS Client', arch: 'Apple Silicon & Intel', weight: '~6.4 MB', ext: '.dmg' },
            { name: 'Windows Client', arch: 'x64 & x86 Architectures', weight: '~3.2 MB', ext: '.msi' },
            { name: 'Linux Client', arch: 'AppImage & Flatpak binaries', weight: '~8.1 MB', ext: '.AppImage' }
          ].map((plat, idx) => (
            <motion.div 
              key={idx} 
              className="v4-plat-card"
              whileHover={{ y: -4, borderColor: 'var(--accent-primary)' }}
            >
              <h3>{plat.name}</h3>
              <div className="v4-plat-meta">
                <span>{plat.arch}</span>
                <span className="v4-plat-weight">{plat.weight} ({plat.ext})</span>
              </div>
              <button className="v4-plat-btn"><Download size={14} /> Get installer</button>
            </motion.div>
          ))}
        </div>
      </FadeSection>

      {/* ── CTA ── */}
      <FadeSection className="v4-cta-section">
        <div className="v4-cta-card">
          <h2>Master system engineering safely</h2>
          <p>Get the desktop installer and start writing local container operations.</p>
          <button className="v4-btn-primary"><Download size={18} /> Download Desktop Client</button>
        </div>
      </FadeSection>

      {/* ── FOOTER ── */}
      <footer className="v4-footer">
        <div className="v4-footer-inner">
          <span>© 2025 Terminal Academy</span>
          <span style={{ opacity: 0.3 }}>·</span>
          <a href="https://github.com" target="_blank" rel="noopener noreferrer">GitHub repository</a>
          <span style={{ opacity: 0.3 }}>·</span>
          <span>Tauri Engine Runtime</span>
        </div>
      </footer>

      <style>{`
        .v4-root { background: var(--bg-base); color: var(--text-main); }
        .v4-header { position: sticky; top: 0; z-index: 100; background: var(--nav-bg); backdrop-filter: blur(20px); border-bottom: 1px solid var(--border-color); box-shadow: 0 0 20px rgba(255,85,0,0.05); }
        .v4-header-inner { max-width: 1200px; margin: 0 auto; padding: 12px 24px; display: flex; align-items: center; justify-content: space-between; }
        .v4-logo { display: flex; align-items: center; gap: 8px; font-family: var(--font-mono); font-weight: 700; font-size: 1.1rem; }
        .v4-nav { display: flex; gap: 20px; align-items: center; }
        .v4-nav-link { color: var(--text-muted); font-size: 0.9rem; text-decoration: none; transition: color 0.2s; display: flex; align-items: center; }
        .v4-nav-link:hover { color: var(--accent-primary); }

        .v4-hero { text-align: center; padding: 120px 24px 80px; position: relative; overflow: hidden; }
        .v4-hero-glow { position: absolute; top: -150px; left: 50%; transform: translateX(-50%); width: 750px; height: 350px; background: radial-gradient(circle, rgba(255,85,0,0.1) 0%, transparent 65%); filter: blur(60px); pointer-events: none; }
        .v4-hero-title { font-size: clamp(2.5rem, 6vw, 4rem); font-weight: 700; line-height: 1.1; margin-bottom: 16px; }
        .v4-gradient-text { background: linear-gradient(135deg, #ff5500, #f59e0b, #ff5500); background-size: 200% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; animation: v4-gradient-shift 3s linear infinite; }
        @keyframes v4-gradient-shift { to { background-position: 200% center; } }
        .v4-hero-sub { color: var(--text-muted); font-size: 1.15rem; max-width: 600px; margin: 0 auto 32px; line-height: 1.6; }
        .v4-hero-ctas { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; }

        .v4-btn-primary { display: inline-flex; align-items: center; gap: 8px; padding: 13px 26px; background: var(--accent-primary); color: #fff; border: none; border-radius: 10px; font-size: 0.95rem; font-weight: 600; cursor: pointer; text-decoration: none; font-family: var(--font-sans); box-shadow: 0 0 30px rgba(255,85,0,0.3); }
        .v4-btn-ghost { display: inline-flex; align-items: center; gap: 8px; padding: 13px 26px; background: transparent; color: var(--text-main); border: 1px solid var(--border-color); border-radius: 10px; font-size: 0.95rem; cursor: pointer; font-family: var(--font-sans); transition: border-color 0.2s; }
        .v4-btn-ghost:hover { border-color: var(--accent-primary); }

        .v4-topology-section { padding: 48px 24px 80px; }
        .v4-section { max-width: 1100px; margin: 0 auto; padding: 100px 24px; }
        .v4-section-title { font-size: 2.2rem; font-weight: 700; text-align: center; margin-bottom: 12px; }
        .v4-section-sub { text-align: center; color: var(--text-muted); margin-bottom: 48px; font-size: 1.1rem; }

        .v4-topology-container { max-width: 800px; margin: 0 auto; background: var(--bg-raised); border: 1px solid var(--border-color); border-radius: 20px; padding: 24px; }
        .v4-topology-svg { width: 100%; height: auto; }

        .v4-features-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 20px; }
        .v4-feature-card { padding: 28px; background: var(--bg-raised); border: 1px solid var(--border-color); border-radius: 14px; transition: border-color 0.3s; }
        .v4-feature-card:hover { border-color: var(--border-highlight); }
        .v4-feature-icon { width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; background: rgba(255,85,0,0.1); border-radius: 10px; color: var(--accent-primary); margin-bottom: 16px; }
        .v4-feature-card h3 { font-size: 1.1rem; margin-bottom: 8px; font-weight: 600; }
        .v4-feature-card p { color: var(--text-muted); font-size: 0.92rem; line-height: 1.6; }

        .v4-stack-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px; }
        .v4-stack-card { padding: 32px; background: var(--bg-raised); border: 1px solid var(--border-color); border-radius: 14px; }
        .v4-stack-label { display: block; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--accent-primary); margin-bottom: 6px; }
        .v4-stack-tech { display: block; font-family: var(--font-mono); font-size: 0.98rem; font-weight: 600; margin-bottom: 12px; }
        .v4-stack-card p { color: var(--text-muted); font-size: 0.92rem; line-height: 1.6; }

        .v4-sec-split { display: grid; grid-template-columns: 1.2fr 1fr; gap: 48px; align-items: center; }
        .v4-sec-left h2 { font-size: 2rem; font-weight: 700; margin-bottom: 18px; }
        .v4-sec-left p { color: var(--text-muted); font-size: 1.05rem; line-height: 1.7; margin-bottom: 24px; }
        .v4-sec-list { display: flex; flex-direction: column; gap: 14px; padding: 0; list-style-type: none; }
        .v4-sec-list li { display: flex; align-items: center; gap: 10px; font-size: 0.96rem; color: var(--text-main); }
        .v4-sec-bullet-icon { color: var(--accent-primary); flex-shrink: 0; }
        .v4-sec-code-box { background: var(--term-bg); border: 1px solid var(--border-color); border-radius: 12px; padding: 20px; overflow-x: auto; }
        .v4-sec-pre { font-family: var(--font-mono); font-size: 0.85rem; color: var(--term-text); margin: 0; line-height: 1.6; }

        .v4-monitor-container { max-width: 600px; margin: 0 auto; border-radius: 16px; overflow: hidden; background: var(--bg-raised); border: 1px solid var(--border-color); }
        .v4-monitor-container .widget-content { height: 320px; }

        .v4-metrics-row { display: flex; justify-content: center; gap: 64px; flex-wrap: wrap; }
        .v4-metric { text-align: center; }
        .v4-metric-value { display: block; font-size: 3.2rem; font-weight: 800; font-family: var(--font-mono); color: var(--accent-primary); line-height: 1; }
        .v4-metric-label { display: block; margin-top: 8px; font-size: 0.95rem; color: var(--text-muted); }

        .v4-platform-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px; }
        .v4-plat-card { padding: 36px 28px; background: var(--bg-raised); border: 1px solid var(--border-color); border-radius: 16px; text-align: center; transition: border-color 0.3s; }
        .v4-plat-meta { display: flex; flex-direction: column; gap: 4px; margin: 8px 0 20px; font-size: 0.88rem; color: var(--text-muted); }
        .v4-plat-weight { color: var(--accent-primary); font-family: var(--font-mono); font-size: 0.85rem; margin-top: 4px; }
        .v4-plat-btn { display: inline-flex; align-items: center; gap: 8px; padding: 10px 24px; background: transparent; border: 1px solid var(--border-color); border-radius: 8px; color: var(--text-main); font-size: 0.9rem; cursor: pointer; font-family: var(--font-sans); transition: border-color 0.2s; }
        .v4-plat-btn:hover { border-color: var(--accent-primary); }

        .v4-cta-section { padding: 80px 24px 120px; }
        .v4-cta-card { max-width: 650px; margin: 0 auto; text-align: center; padding: 56px 36px; background: var(--bg-raised); border: 1px solid var(--accent-primary); border-radius: 20px; box-shadow: 0 0 40px rgba(255,85,0,0.1); }
        .v4-cta-card h2 { font-size: 1.8rem; margin-bottom: 12px; font-weight: 700; }
        .v4-cta-card p { color: var(--text-muted); margin-bottom: 28px; }

        .v4-footer { border-top: 1px solid var(--border-color); padding: 32px 24px; }
        .v4-footer-inner { max-width: 1200px; margin: 0 auto; display: flex; justify-content: center; gap: 12px; font-size: 0.88rem; color: var(--text-muted); flex-wrap: wrap; }
        .v4-footer-inner a { color: var(--text-muted); text-decoration: none; }
        .v4-footer-inner a:hover { color: var(--accent-primary); }

        @media (max-width: 960px) {
          .v4-sec-split { grid-template-columns: 1fr; gap: 32px; }
        }
      `}</style>
    </div>
  );
}
