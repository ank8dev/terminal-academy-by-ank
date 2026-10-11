import React, { useState, useEffect, useRef } from 'react';
import { motion, useInView } from 'framer-motion';
import { Terminal, Monitor, Bot, BookOpen, Download, Github, Activity, Shield, Cpu, Code, CheckCircle, HelpCircle } from 'lucide-react';
import { TerminalWidget, ChatWidget, LessonWidget, MonitoringWidget, parseSyllabus } from '~/App';
import '~/App.css';

const COURSES = [
  { id: 'linux', name: 'Linux Core & SysAdmin', file: '/curriculum_linux.md' },
  { id: 'network', name: 'Networking & Security', file: '/curriculum_network.md' },
  { id: 'devops', name: 'DevOps & Containers', file: '/curriculum_devops.md' },
  { id: 'hosting', name: 'App Hosting', file: '/curriculum_hosting.md' },
];

const MOCK_STATS = {
  cpu: '12%', ram: '256MB / 512MB', swap: '0MB', disk: '0.3ms',
  net: '1.2KB/s', load: '0.15', proc: '23', uptime: '00:14:22',
  latency: '4ms', sandbox: 'ACTIVE',
};

/* ── Animated counter ── */
function AnimatedCounter({ end, suffix = '', label }: { end: number; suffix?: string; label: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, margin: '-100px' });
  const [count, setCount] = useState(0);

  useEffect(() => {
    if (!isInView) return;
    let frame: number;
    const start = performance.now();
    const dur = 1200;
    const tick = (now: number) => {
      const p = Math.min((now - start) / dur, 1);
      const eased = 1 - Math.pow(1 - p, 3);
      setCount(Math.round(eased * end));
      if (p < 1) frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [isInView, end]);

  return (
    <div ref={ref} className="v2-stat-card">
      <span className="v2-stat-number">{count}{suffix}</span>
      <span className="v2-stat-label">{label}</span>
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
   VARIANT 2 — WORKSPACE SIMULATOR / DASHBOARD-FIRST
   ══════════════════════════════════════════════ */
export default function Variant2Dashboard() {
  const [activeCourse, setActiveCourse] = useState(COURSES[0]);
  const [nodes, setNodes] = useState<any[]>([]);
  const [activeNode, setActiveNode] = useState<any>(null);
  const [activeIncident, setActiveIncident] = useState<any>(null);
  const [skillTreeNodes, setSkillTreeNodes] = useState<any[]>([]);
  const [terminalBuffer] = useState('');
  const [explainCommand, setExplainCommand] = useState('');
  const [terminalEvent, setTerminalEvent] = useState('');

  useEffect(() => {
    fetch(activeCourse.file)
      .then(r => r.text())
      .then(text => {
        const parsed = parseSyllabus(text);
        setNodes(parsed);
        if (parsed.length > 0) {
          setActiveNode(parsed[0]);
          setActiveIncident(parsed[0].incidents?.[0] || null);
        }
      })
      .catch(() => {});
  }, [activeCourse]);

  useEffect(() => {
    fetch('/curriculum_graph.json')
      .then(r => r.json())
      .then(d => setSkillTreeNodes(d.nodes || []))
      .catch(() => {});
  }, []);

  return (
    <div className="v2-root">
      {/* ── HEADER ── */}
      <header className="v2-header">
        <div className="v2-header-inner">
          <div className="v2-logo">
            <Terminal size={20} style={{ color: 'var(--accent-primary)' }} />
            <span>t//a</span>
            <span className="v2-version-badge">v2.1.1</span>
          </div>
          <div className="v2-live-badge">
            <span className="v2-live-dot" />
            Workspace Live Preview
          </div>
          <nav className="v2-nav">
            <a href="#workspace" className="v2-nav-link">Live Workspace</a>
            <a href="#features" className="v2-nav-link">Platform Features</a>
            <a href="#specs" className="v2-nav-link">Technical Specs</a>
            <a href="#download" className="v2-nav-link">Download</a>
            <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="v2-nav-link">
              <Github size={18} />
            </a>
          </nav>
        </div>
      </header>

      {/* ── HERO ── */}
      <section className="v2-hero">
        <div className="v2-hero-glow" />
        <div className="v2-hero-content">
          <motion.div 
            className="v2-hero-tag"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4 }}
          >
            <Monitor size={14} /> Full Desktop Client Preview
          </motion.div>
          <motion.h1
            initial={{ opacity: 0, y: 25 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            The Ultimate Workspace for System Engineers
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 25 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="v2-hero-sub"
          >
            No mockups. No representations. Below is the exact multi-pane desktop client workspace running inside your browser. Navigate lessons, run real terminal commands, monitor metrics, and query the Socratic AI mentor.
          </motion.p>
          <motion.div
            className="v2-hero-ctas"
            initial={{ opacity: 0, y: 25 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <a href="#workspace" className="v2-btn-primary">Explore Workspace Demo</a>
            <a href="#download" className="v2-btn-secondary"><Download size={16} /> Download Installer</a>
          </motion.div>
        </div>
      </section>

      {/* ── PRODUCT DASHBOARD (THE LIVE SIMULATOR) ── */}
      <section className="v2-dashboard-section" id="workspace">
        <div className="v2-dashboard-label-container">
          <h2 className="v2-section-title">Interactive Workspace Simulator</h2>
          <p className="v2-section-subtitle">Click and drag inside any panel, select incidents on the left, execute diagnostics in the middle, and see monitoring graphs update.</p>
        </div>

        <div className="v2-dashboard-grid">
          {/* LEFT: Syllabus */}
          <div className="v2-panel v2-panel-syllabus widget-container">
            <LessonWidget
              bindDrag={undefined}
              courses={COURSES}
              activeCourse={activeCourse}
              setActiveCourse={setActiveCourse}
              nodes={nodes}
              activeNode={activeNode}
              setActiveNode={(n: any) => { setActiveNode(n); setActiveIncident(n?.incidents?.[0] || null); }}
              activeIncident={activeIncident}
              setActiveIncident={setActiveIncident}
              lang="en"
              skillTreeNodes={skillTreeNodes}
            />
          </div>

          {/* CENTER: Terminal */}
          <div className="v2-panel v2-panel-terminal widget-container">
            <div className="widget-content">
              <div className="widget-header">
                <div className="title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Terminal size={14} style={{ color: 'var(--accent-primary)' }} />
                  Sandbox Room (ank@sandbox)
                </div>
              </div>
              <div style={{ height: 'calc(100% - 38px)' }}>
                <TerminalWidget
                  bindDrag={undefined}
                  lang="en"
                  onTerminalData={() => {}}
                  dockerStatus="running"
                  onCommandBeforeExec={() => {}}
                  onCommandAfterExec={() => {}}
                  jwtToken="demo"
                  blacklist={[]}
                />
              </div>
            </div>
          </div>

          {/* RIGHT TOP: Chat */}
          <div className="v2-panel v2-panel-chat widget-container">
            <ChatWidget
              bindDrag={undefined}
              activeCourse={activeCourse}
              activeNode={activeNode}
              activeIncident={activeIncident}
              lang="en"
              terminalBuffer={terminalBuffer}
              systemStats={MOCK_STATS}
              explainCommand={explainCommand}
              setExplainCommand={setExplainCommand}
              terminalEvent={terminalEvent}
              setTerminalEvent={setTerminalEvent}
              defaultApiKey=""
              blacklist={[]}
            />
          </div>

          {/* RIGHT BOTTOM: Monitoring */}
          <div className="v2-panel v2-panel-monitor widget-container">
            <MonitoringWidget
              bindDrag={undefined}
              lang="en"
              stats={MOCK_STATS}
            />
          </div>
        </div>
      </section>

      {/* ── CORE PLATFORM FEATURES ── */}
      <FadeSection className="v2-section" id="features">
        <h2 className="v2-section-title">A Unified Suite for Systems Education</h2>
        <p className="v2-section-subtitle">No separate browser tabs or heavy VM configurations. Everything sits in a lightweight local client.</p>
        <div className="v2-features-grid">
          {[
            { icon: Terminal, title: 'Embedded Sandbox Shell', desc: 'Runs an authentic Unix terminal wrapper connected to an isolated container runtime environment.' },
            { icon: Bot, title: 'AI Mentor Ank Integrations', desc: 'Get Socratic dialogue, step-by-step diagnostic analysis, and incident breakdowns as you work.' },
            { icon: Activity, title: 'Live Container Telemetry', desc: 'Track real container CPU loads, memory allocation, virtual disk delays, and active process trees.' },
            { icon: BookOpen, title: 'Interactive Syllabus', desc: 'Expand node curriculums, choose branches, trace requirements, and track completed tasks offline.' },
            { icon: Shield, title: 'Host Safety Guarantee', desc: 'Your home folders are fully isolated. Execute recursive deletes or modify network interfaces without risk.' },
            { icon: Code, title: 'Suggested Diagnostic Helper', desc: 'Examine command definitions and syntax structures before applying changes in the sandbox.' }
          ].map((feat, idx) => (
            <motion.div 
              key={idx} 
              className="v2-feature-card"
              whileHover={{ y: -4, borderColor: 'var(--accent-primary)' }}
            >
              <div className="v2-feature-icon-wrapper">
                <feat.icon size={22} />
              </div>
              <h3>{feat.title}</h3>
              <p>{feat.desc}</p>
            </motion.div>
          ))}
        </div>
      </FadeSection>

      {/* ── SYSTEM SPECIFICATIONS / TECH STACK ── */}
      <FadeSection className="v2-section" id="specs">
        <h2 className="v2-section-title">Technical Specifications</h2>
        <p className="v2-section-subtitle">A deep dive into the technologies running under the hood of the Terminal Academy engine.</p>
        <div className="v2-specs-table-wrapper">
          <table className="v2-specs-table">
            <thead>
              <tr>
                <th>Component</th>
                <th>Standard Specs</th>
                <th>Architecture Detail</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>Desktop Runtime</strong></td>
                <td>Tauri Client Core v2.x</td>
                <td>Rust-based backend, WebView frontend, memory usage ~40MB total.</td>
              </tr>
              <tr>
                <td><strong>Sandbox Platform</strong></td>
                <td>Disposable Docker / Podman container</td>
                <td>Alpine Linux base system image. Virtual interfaces isolated from host.</td>
              </tr>
              <tr>
                <td><strong>Terminal Emulation</strong></td>
                <td>XTerm.js with PTY bindings</td>
                <td>High performance GPU rendering, complete ANSI escape support, screen buffer retention.</td>
              </tr>
              <tr>
                <td><strong>Telemetry Stream</strong></td>
                <td>Unix socket loopback</td>
                <td>Sub-millisecond latency telemetry stream reporting system resources continuously.</td>
              </tr>
              <tr>
                <td><strong>Curriculum Parser</strong></td>
                <td>Markdown parser engine</td>
                <td>Syllabus content compiled dynamically into graphs representing incident requirements.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </FadeSection>

      {/* ── WHY TERMINAL ACADEMY? ── */}
      <FadeSection className="v2-section">
        <div className="v2-why-split">
          <div className="v2-why-left">
            <h2>Why learn through terminal simulations?</h2>
            <p>Traditional tutorials explain theory, but skip the real panic of diagnosing incident errors. We drop you directly into a misconfigured system so you build authentic command instincts.</p>
            <div className="v2-why-points">
              <div className="v2-why-point">
                <CheckCircle size={16} className="v2-check-icon" />
                <span>Simulates real-world sysadmin and DevOps pager incidents.</span>
              </div>
              <div className="v2-why-point">
                <CheckCircle size={16} className="v2-check-icon" />
                <span>Immediate sandboxed loopback validation verifies your fixes.</span>
              </div>
              <div className="v2-why-point">
                <CheckCircle size={16} className="v2-check-icon" />
                <span>No complex setup or virtual machine software installations needed.</span>
              </div>
            </div>
          </div>
          <div className="v2-why-right">
            <div className="v2-sandbox-badge">
              <span className="v2-badge-title">Local Environment</span>
              <span className="v2-badge-status">SECURE & ISOLATED</span>
            </div>
            <div className="v2-sandbox-visual">
              <pre className="v2-code-visual">{`$ docker run --rm -it \\
  -v /var/run/docker.sock \\
  terminal-academy/sandbox:latest
[+] Container initialized.
[+] Mounting filesystem overlays...
[+] Network interfaces configured.
[+] Mentor Ank client connected.
sandbox# _`}</pre>
            </div>
          </div>
        </div>
      </FadeSection>

      {/* ── TRUST & NUMBERS ── */}
      <FadeSection className="v2-section">
        <div className="v2-numbers-row">
          <AnimatedCounter end={4} label="Tracks Offered" />
          <AnimatedCounter end={50} suffix="+" label="Practice Incidents" />
          <AnimatedCounter end={6} suffix="MB" label="Client Weight" />
          <AnimatedCounter end={100} suffix="%" label="Offline Capability" />
        </div>
      </FadeSection>

      {/* ── CLIENT DOWNLOAD OPTIONS ── */}
      <FadeSection className="v2-section" id="download">
        <h2 className="v2-section-title">Install Locally & Start Solving</h2>
        <p className="v2-section-subtitle">Download the package for your development platform. No signups or credit cards required.</p>
        <div className="v2-download-grid">
          {[
            { os: 'macOS Client', size: '6.4 MB', ext: '.dmg', label: 'Download for Apple Silicon / Intel' },
            { os: 'Windows Client', size: '3.2 MB', ext: '.msi', label: 'Download for Windows 10 / 11' },
            { os: 'Linux Client', size: '8.1 MB', ext: '.AppImage', label: 'Download for Debian / RHEL / Arch' }
          ].map((down, index) => (
            <motion.div 
              key={index}
              className="v2-download-card"
              whileHover={{ y: -4, borderColor: 'var(--accent-primary)' }}
            >
              <h3>{down.os}</h3>
              <div className="v2-download-meta">
                <span className="v2-meta-size">{down.size}</span>
                <span className="v2-meta-ext">{down.ext}</span>
              </div>
              <p>{down.label}</p>
              <button className="v2-download-btn"><Download size={14} /> Get Client</button>
            </motion.div>
          ))}
        </div>
      </FadeSection>

      {/* ── FOOTER ── */}
      <footer className="v2-footer">
        <div className="v2-footer-main">
          <div className="v2-footer-info">
            <div className="v2-logo">
              <Terminal size={18} style={{ color: 'var(--accent-primary)' }} />
              <span>t//a</span>
            </div>
            <p>Terminal Academy is a sandboxed system infrastructure playground built for developers, DevOps interns, and sysadmins looking to master system interactions.</p>
          </div>
          <div className="v2-footer-links">
            <div className="v2-link-column">
              <h4>Documentation</h4>
              <a href="#">Quick Start Guide</a>
              <a href="#">Tauri Sandbox Configuration</a>
              <a href="#">CLI Shell Commands</a>
            </div>
            <div className="v2-link-column">
              <h4>Community</h4>
              <a href="https://github.com" target="_blank" rel="noopener noreferrer">GitHub Codebase</a>
              <a href="#">Discord Server</a>
              <a href="#">Issue Tracker</a>
            </div>
          </div>
        </div>
        <div className="v2-footer-bottom">
          <span>© 2025 Terminal Academy. All rights reserved. Open source under the AGPL-3.0 License.</span>
        </div>
      </footer>

      <style>{`
        .v2-root { background: var(--bg-base); color: var(--text-main); }
        .v2-header { position: sticky; top: 0; z-index: 100; background: var(--nav-bg); backdrop-filter: blur(20px); border-bottom: 1px solid var(--border-color); }
        .v2-header-inner { max-width: 1400px; margin: 0 auto; padding: 12px 24px; display: flex; align-items: center; gap: 16px; }
        .v2-logo { display: flex; align-items: center; gap: 8px; font-family: var(--font-mono); font-weight: 700; font-size: 1.1rem; }
        .v2-version-badge { font-size: 0.65rem; padding: 2px 8px; background: rgba(255,85,0,0.15); color: var(--accent-primary); border-radius: 12px; }
        .v2-live-badge { display: flex; align-items: center; gap: 6px; font-size: 0.8rem; color: #27c93f; background: rgba(39,201,63,0.1); padding: 4px 12px; border-radius: 20px; margin-left: 8px; }
        .v2-live-dot { width: 8px; height: 8px; border-radius: 50%; background: #27c93f; animation: v2-pulse 2s infinite; }
        @keyframes v2-pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
        .v2-nav { margin-left: auto; display: flex; gap: 20px; align-items: center; }
        .v2-nav-link { color: var(--text-muted); text-decoration: none; font-size: 0.9rem; transition: color 0.2s; }
        .v2-nav-link:hover { color: var(--accent-primary); }

        .v2-hero { position: relative; text-align: center; padding: 120px 24px 80px; overflow: hidden; }
        .v2-hero-glow { position: absolute; top: -150px; left: 50%; transform: translateX(-50%); width: 700px; height: 350px; background: radial-gradient(circle, rgba(255,85,0,0.12) 0%, transparent 70%); filter: blur(60px); pointer-events: none; }
        .v2-hero-content { position: relative; z-index: 1; max-width: 800px; margin: 0 auto; }
        .v2-hero-tag { display: inline-flex; align-items: center; gap: 6px; padding: 6px 14px; background: rgba(255,85,0,0.08); border: 1px solid rgba(255,85,0,0.15); border-radius: 20px; font-size: 0.8rem; color: var(--accent-primary); margin-bottom: 24px; font-family: var(--font-mono); }
        .v2-hero h1 { font-size: clamp(2.4rem, 6vw, 4rem); font-weight: 700; margin-bottom: 16px; line-height: 1.1; }
        .v2-hero-sub { color: var(--text-muted); font-size: 1.15rem; line-height: 1.6; margin-bottom: 32px; max-width: 680px; margin-left: auto; margin-right: auto; }
        .v2-hero-ctas { display: flex; gap: 16px; justify-content: center; flex-wrap: wrap; }
        
        .v2-btn-primary { display: inline-flex; align-items: center; gap: 8px; padding: 14px 28px; background: var(--accent-primary); color: #fff; border: none; border-radius: 12px; font-size: 1rem; font-weight: 600; cursor: pointer; text-decoration: none; font-family: var(--font-sans); box-shadow: 0 0 30px rgba(255,85,0,0.3); }
        .v2-btn-secondary { display: inline-flex; align-items: center; gap: 8px; padding: 14px 28px; background: transparent; color: var(--text-main); border: 1px solid var(--border-color); border-radius: 12px; font-size: 1rem; font-weight: 500; cursor: pointer; text-decoration: none; font-family: var(--font-sans); transition: border-color 0.2s; }
        .v2-btn-secondary:hover { border-color: var(--accent-primary); }

        .v2-dashboard-section { padding: 48px 24px 80px; max-width: 1400px; margin: 0 auto; }
        .v2-dashboard-label-container { text-align: center; max-width: 800px; margin: 0 auto 36px; }
        .v2-section-title { font-size: 2.2rem; font-weight: 700; margin-bottom: 12px; }
        .v2-section-subtitle { color: var(--text-muted); font-size: 1.1rem; line-height: 1.6; }

        .v2-dashboard-grid { display: grid; grid-template-columns: 280px 1fr 320px; grid-template-rows: 1fr 200px; gap: 12px; height: 620px; }
        .v2-panel { border-radius: 16px; overflow: hidden; background: var(--bg-raised); border: 1px solid var(--border-color); backdrop-filter: blur(16px); }
        .v2-panel-syllabus { grid-row: 1 / 3; overflow-y: auto; }
        .v2-panel-terminal { grid-row: 1 / 3; }
        .v2-panel-chat { overflow-y: auto; }
        .v2-panel-monitor { overflow-y: auto; }
        .v2-panel .widget-content { height: 100%; }

        .v2-section { max-width: 1100px; margin: 0 auto; padding: 100px 24px; }
        
        .v2-features-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px; margin-top: 24px; }
        .v2-feature-card { padding: 32px; background: var(--bg-raised); border: 1px solid var(--border-color); border-radius: 16px; transition: border-color 0.3s, transform 0.3s; }
        .v2-feature-icon-wrapper { width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; background: rgba(255,85,0,0.1); border-radius: 10px; color: var(--accent-primary); margin-bottom: 18px; }
        .v2-feature-card h3 { font-size: 1.15rem; margin-bottom: 8px; font-weight: 600; }
        .v2-feature-card p { color: var(--text-muted); font-size: 0.95rem; line-height: 1.6; }

        .v2-specs-table-wrapper { margin-top: 24px; border: 1px solid var(--border-color); border-radius: 16px; overflow: hidden; background: var(--bg-raised); }
        .v2-specs-table { width: 100%; border-collapse: collapse; text-align: left; font-size: 0.95rem; }
        .v2-specs-table th { background: rgba(255,255,255,0.02); padding: 16px 24px; font-weight: 600; border-bottom: 1px solid var(--border-color); color: var(--accent-primary); }
        .v2-specs-table td { padding: 18px 24px; border-bottom: 1px solid var(--border-color); color: var(--text-muted); line-height: 1.5; }
        .v2-specs-table tr:last-child td { border-bottom: none; }

        .v2-why-split { display: grid; grid-template-columns: 1.2fr 1fr; gap: 48px; align-items: center; }
        .v2-why-left h2 { font-size: 2rem; font-weight: 700; margin-bottom: 18px; }
        .v2-why-left p { color: var(--text-muted); font-size: 1.05rem; line-height: 1.7; margin-bottom: 24px; }
        .v2-why-points { display: flex; flex-direction: column; gap: 14px; }
        .v2-why-point { display: flex; align-items: center; gap: 12px; font-size: 0.98rem; color: var(--text-main); }
        .v2-check-icon { color: #27c93f; flex-shrink: 0; }

        .v2-sandbox-badge { display: flex; justify-content: space-between; align-items: center; padding: 12px 18px; background: var(--bg-raised); border: 1px solid var(--border-color); border-bottom: none; border-radius: 12px 12px 0 0; font-family: var(--font-mono); font-size: 0.8rem; }
        .v2-badge-title { color: var(--text-muted); }
        .v2-badge-status { color: var(--accent-primary); font-weight: 700; }
        .v2-sandbox-visual { background: var(--term-bg); border: 1px solid var(--border-color); border-radius: 0 0 12px 12px; padding: 20px; overflow-x: auto; }
        .v2-code-visual { font-family: var(--font-mono); font-size: 0.85rem; color: var(--term-text); margin: 0; line-height: 1.6; }

        .v2-numbers-row { display: flex; justify-content: center; gap: 64px; flex-wrap: wrap; }
        .v2-stat-card { text-align: center; }
        .v2-stat-number { display: block; font-size: 3.2rem; font-weight: 800; font-family: var(--font-mono); color: var(--accent-primary); line-height: 1; }
        .v2-stat-label { display: block; margin-top: 8px; font-size: 0.95rem; color: var(--text-muted); }

        .v2-download-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px; margin-top: 24px; }
        .v2-download-card { padding: 36px 28px; background: var(--bg-raised); border: 1px solid var(--border-color); border-radius: 16px; text-align: center; transition: border-color 0.3s; }
        .v2-download-meta { display: flex; justify-content: center; gap: 10px; margin: 8px 0 16px; }
        .v2-meta-size { font-family: var(--font-mono); color: var(--accent-primary); font-size: 0.9rem; font-weight: 600; }
        .v2-meta-ext { font-family: var(--font-mono); color: var(--text-muted); font-size: 0.9rem; }
        .v2-download-card p { color: var(--text-muted); font-size: 0.9rem; margin-bottom: 24px; }
        .v2-download-btn { display: inline-flex; align-items: center; gap: 8px; padding: 10px 24px; background: transparent; border: 1px solid var(--border-color); border-radius: 8px; color: var(--text-main); font-size: 0.9rem; cursor: pointer; font-family: var(--font-sans); transition: border-color 0.2s; }
        .v2-download-btn:hover { border-color: var(--accent-primary); }

        .v2-footer { border-top: 1px solid var(--border-color); padding: 80px 24px 40px; }
        .v2-footer-main { max-width: 1200px; margin: 0 auto 48px; display: grid; grid-template-columns: 1.5fr 1fr; gap: 60px; }
        .v2-footer-info { display: flex; flex-direction: column; gap: 12px; }
        .v2-footer-info p { color: var(--text-muted); font-size: 0.9rem; line-height: 1.7; max-width: 500px; }
        .v2-footer-links { display: grid; grid-template-columns: repeat(2, 1fr); gap: 32px; }
        .v2-link-column { display: flex; flex-direction: column; gap: 10px; }
        .v2-link-column h4 { font-size: 0.88rem; font-weight: 700; color: var(--text-main); margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.05em; }
        .v2-link-column a { color: var(--text-muted); font-size: 0.9rem; text-decoration: none; transition: color 0.2s; }
        .v2-link-column a:hover { color: var(--accent-primary); }
        .v2-footer-bottom { text-align: center; border-top: 1px solid var(--border-color); padding-top: 24px; font-size: 0.85rem; color: var(--text-muted); }

        @media (max-width: 1100px) {
          .v2-dashboard-grid { grid-template-columns: 1fr; grid-template-rows: auto; height: auto; }
          .v2-panel { min-height: 320px; }
          .v2-why-split { grid-template-columns: 1fr; gap: 32px; }
          .v2-footer-main { grid-template-columns: 1fr; gap: 40px; }
        }
      `}</style>
    </div>
  );
}
