import React, { useState, useEffect, useRef } from 'react';
import { motion, useInView } from 'framer-motion';
import { BookOpen, CheckCircle, Lightbulb, Terminal, Download, Github, ChevronDown, ChevronRight, Zap, Star } from 'lucide-react';
import { TerminalWidget, ChatWidget, parseSyllabus } from '~/App';
import '~/App.css';

const COURSES = [
  { id: 'linux', name: 'Linux Core & SysAdmin', file: '/curriculum_linux.md' },
  { id: 'network', name: 'Networking & Security', file: '/curriculum_network.md' },
  { id: 'devops', name: 'DevOps & Containers', file: '/curriculum_devops.md' },
  { id: 'hosting', name: 'App Hosting', file: '/curriculum_hosting.md' },
];

/* ── Accordion item ── */
function AccordionItem({ title, children }: { title: string; children: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="v3-accordion-item">
      <button className="v3-accordion-header" onClick={() => setOpen(!open)}>
        {open ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
        <span>{title}</span>
      </button>
      <div className="v3-accordion-body" style={{ maxHeight: open ? '500px' : '0', opacity: open ? 1 : 0 }}>
        {children}
      </div>
    </div>
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
    <div ref={ref} className="v3-counter">
      <span className="v3-counter-value">{count}{suffix}</span>
      <span className="v3-counter-label">{label}</span>
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
   VARIANT 3 — PLAYGROUND & INTERACTIVE DOCS
   ══════════════════════════════════════════════ */
export default function Variant3Playground() {
  const [taskComplete, setTaskComplete] = useState(false);
  const [syllabusData, setSyllabusData] = useState<Record<string, any[]>>({});

  // Fetch syllabus for accordion preview
  useEffect(() => {
    COURSES.forEach(c => {
      fetch(c.file).then(r => r.text()).then(text => {
        const parsed = parseSyllabus(text);
        setSyllabusData(prev => ({ ...prev, [c.id]: parsed }));
      }).catch(() => {});
    });
  }, []);

  const handleTerminalData = (data: string) => {
    if (data && data.includes('Verification Success')) {
      setTaskComplete(true);
    }
  };

  return (
    <div className="v3-root">
      {/* ── HEADER ── */}
      <header className="v3-header">
        <div className="v3-header-inner">
          <div className="v3-logo">
            <Terminal size={18} style={{ color: 'var(--accent-primary)' }} />
            <span>t//a</span>
          </div>
          <nav className="v3-nav">
            <a href="#playground" className="v3-nav-link">Interactive Docs</a>
            <a href="#syllabus" className="v3-nav-link">Curriculum</a>
            <a href="#mentor" className="v3-nav-link">AI Mentor</a>
            <a href="#limits" className="v3-nav-link">Capabilities</a>
            <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="v3-nav-link">
              <Github size={16} />
            </a>
          </nav>
        </div>
      </header>

      {/* ── HERO ── */}
      <section className="v3-hero">
        <div className="v3-hero-gradient" />
        <div className="v3-hero-content">
          <div className="v3-badge"><Star size={12} /> Interactive Sandbox Tutorials</div>
          <h1>Learn Systems by <span style={{ color: 'var(--accent-primary)' }}>Breaking</span> Them</h1>
          <p>
            Skip the passive videos. Master Linux administration, container virtualization, network sockets, 
            and hosting configuration inside real sandbox terminals embedded alongside production documentation.
          </p>
          <div className="v3-hero-ctas">
            <motion.a href="#playground" className="v3-btn-primary" whileHover={{ scale: 1.03 }}>
              Try Interactive Playground
            </motion.a>
            <motion.button className="v3-btn-ghost" whileHover={{ scale: 1.03 }}>
              <Download size={16} /> Get Desktop App
            </motion.button>
          </div>
        </div>
      </section>

      {/* ── SPLIT LAYOUT: DOCS + TERMINAL ── */}
      <section className="v3-split-section" id="playground">
        <div className="v3-split-grid">
          {/* LEFT: Documentation */}
          <div className="v3-docs-panel">
            <div className="v3-docs-content">
              <h2>Understanding File Permissions</h2>
              <p>
                Unix systems use a three-tier permission model that controls who can read, write, and execute files.
                Each file has permissions for three categories: <strong>owner</strong>, <strong>group</strong>, and <strong>others</strong>.
              </p>
              <p>Running <code>ls -la</code> reveals the permission string for each file:</p>
              <div className="v3-code-block">
                <pre>{`$ ls -la
-rwxrwxrwx  1 student student  105 Jul 12 config.txt
-rw-r--r--  1 student student  240 Jul 12 app.py
drwxr-xr-x  2 student student 4096 Jul 12 src/`}</pre>
              </div>

              <h3>The <code>chmod</code> Command</h3>
              <p>
                Numeric notation uses three digits, each representing a permission set.
                The values are: <strong>4</strong> = read, <strong>2</strong> = write, <strong>1</strong> = execute.
              </p>
              <p>
                For example, <code>chmod 644 config.txt</code> sets:
              </p>
              <ul className="v3-perm-list">
                <li><strong>6</strong> (4+2) → Owner: read + write</li>
                <li><strong>4</strong> → Group: read only</li>
                <li><strong>4</strong> → Others: read only</li>
              </ul>

              <div className="v3-callout">
                <Lightbulb size={18} style={{ color: 'var(--accent-primary)', flexShrink: 0 }} />
                <span>Try it yourself → Type <code>chmod 644 config.txt</code> in the terminal on the right to fix the permissions.</span>
              </div>
            </div>
          </div>

          {/* RIGHT: Terminal */}
          <div className="v3-terminal-panel">
            <div className="v3-terminal-chrome">
              <div className="v3-terminal-dots">
                <span style={{ background: '#ff5f56' }} />
                <span style={{ background: '#ffbd2e' }} />
                <span style={{ background: '#27c93f' }} />
              </div>
              <span className="v3-terminal-title">sandbox@terminal</span>
            </div>
            <div className="v3-terminal-body">
              <TerminalWidget
                bindDrag={undefined}
                lang="en"
                onTerminalData={handleTerminalData}
                dockerStatus="running"
                onCommandBeforeExec={() => {}}
                onCommandAfterExec={() => {}}
                jwtToken="demo"
                blacklist={[]}
              />
            </div>

            {/* Verification indicator */}
            <motion.div
              className="v3-verification"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={taskComplete ? { opacity: 1, scale: 1 } : {}}
              transition={{ type: 'spring', stiffness: 300, damping: 20 }}
              style={{ display: taskComplete ? 'flex' : 'none' }}
            >
              <CheckCircle size={20} style={{ color: '#27c93f' }} />
              <span>Task Complete! Permissions set to 644 (rw-r--r--)</span>
            </motion.div>
          </div>
        </div>
      </section>

      {/* ── CORE FEATURES ── */}
      <FadeSection className="v3-section">
        <h2 className="v3-section-title">Designed for active retention</h2>
        <p className="v3-section-subtitle">How Terminal Academy helps you bridge the gap between reading documentation and production mastery.</p>
        <div className="v3-features-row">
          {[
            { icon: BookOpen, title: 'Guided Side-by-Side Docs', desc: 'Read documentation directly next to the sandbox. Apply commands as you read to solidify concepts.' },
            { icon: CheckCircle, title: 'Autonomous Shell Verification', desc: 'No manually graded quizzes. The sandbox actively tests filesystem outputs and states.' },
            { icon: Lightbulb, title: 'Adaptive AI Mentor Ank', desc: 'No spoon-fed solutions. Query Mentor Ank to receive guiding questions and tips.' },
          ].map((f, i) => (
            <motion.div key={i} className="v3-feature-card" whileHover={{ y: -3 }}>
              <div className="v3-feature-icon"><f.icon size={22} /></div>
              <h3>{f.title}</h3>
              <p>{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </FadeSection>

      {/* ── SYLLABUS PREVIEW ── */}
      <FadeSection className="v3-section" id="syllabus">
        <h2 className="v3-section-title">Explore the Core Syllabus</h2>
        <p className="v3-section-subtitle">Select any track to preview available incidents. Desktop app features the full tree structure.</p>
        <div className="v3-accordion">
          {COURSES.map(c => (
            <AccordionItem key={c.id} title={c.name}>
              <ul className="v3-module-list">
                {(syllabusData[c.id] || []).slice(0, 4).map((node: any, i: number) => (
                  <li key={i}>
                    <div className="v3-module-item-row">
                      <Zap size={12} className="v3-module-item-icon" />
                      <span>{node.title}</span>
                    </div>
                  </li>
                ))}
                {(syllabusData[c.id]?.length || 0) > 4 && (
                  <li style={{ color: 'var(--text-muted)', fontStyle: 'italic', listStyleType: 'none', paddingLeft: '20px' }}>
                    +{(syllabusData[c.id]?.length || 0) - 4} more modules in client...
                  </li>
                )}
              </ul>
            </AccordionItem>
          ))}
        </div>
      </FadeSection>

      {/* ── AI MENTOR SECTION ── */}
      <FadeSection className="v3-section" id="mentor">
        <h2 className="v3-section-title">Query Mentor Ank</h2>
        <p className="v3-section-subtitle">Use the live mentor interface below to get tips about Unix permissions, processes, or command execution.</p>
        <div className="v3-chat-container widget-container">
          <ChatWidget
            bindDrag={undefined}
            activeCourse={COURSES[0]}
            activeNode={null}
            activeIncident={null}
            lang="en"
            terminalBuffer=""
            systemStats={null}
            explainCommand=""
            setExplainCommand={() => {}}
            terminalEvent=""
            setTerminalEvent={() => {}}
            defaultApiKey=""
            blacklist={[]}
          />
        </div>
      </FadeSection>

      {/* ── WEB PLAYGROUND VS DESKTOP LIMITS ── */}
      <FadeSection className="v3-section" id="limits">
        <h2 className="v3-section-title">Playground vs. Native App</h2>
        <p className="v3-section-subtitle">Compare the browser playground capabilities with the full native Tauri desktop client experience.</p>
        <div className="v3-compare-table-wrapper">
          <table className="v3-compare-table">
            <thead>
              <tr>
                <th>Feature Capability</th>
                <th>Browser Playground</th>
                <th>Tauri Desktop Client</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>PTY Sandbox Isolation</strong></td>
                <td>Simulated browser shell intercept</td>
                <td>Real local Docker / Podman containers</td>
              </tr>
              <tr>
                <td><strong>Network Port Bindings</strong></td>
                <td>Disabled</td>
                <td>Supported (bind and load web servers)</td>
              </tr>
              <tr>
                <td><strong>Offline Mode</strong></td>
                <td>Requires internet connection</td>
                <td>100% offline runtime capability</td>
              </tr>
              <tr>
                <td><strong>Custom API Integrations</strong></td>
                <td>Restricted backend</td>
                <td>Local keys, custom LLM models support</td>
              </tr>
              <tr>
                <td><strong>Incident Curriculums</strong></td>
                <td>Basic demo modules</td>
                <td>Full 50+ incident syllabus suite</td>
              </tr>
            </tbody>
          </table>
        </div>
      </FadeSection>

      {/* ── TRUST / METRICS ── */}
      <FadeSection className="v3-section">
        <div className="v3-progress-row">
          <AnimatedCounter end={4} label="Tracks Supported" />
          <AnimatedCounter end={50} suffix="+" label="Incident Solutions" />
          <AnimatedCounter end={6} suffix="MB" label="Client Size" />
        </div>
      </FadeSection>

      {/* ── CTA ── */}
      <FadeSection className="v3-cta-section">
        <div className="v3-cta-card">
          <h2>Ready to master system internals?</h2>
          <p>Get the lightweight client and execute containers directly on your own machine.</p>
          <div className="v3-cta-actions">
            <button className="v3-btn-primary"><Download size={16} /> Download Desktop App</button>
            <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="v3-btn-ghost"><Github size={16} /> View Github</a>
          </div>
        </div>
      </FadeSection>

      {/* ── FOOTER ── */}
      <footer className="v3-footer">
        <div className="v3-footer-inner">
          <div className="v3-footer-left">
            <span>© 2025 Terminal Academy</span>
            <span style={{ opacity: 0.3 }}>·</span>
            <a href="https://github.com" target="_blank" rel="noopener noreferrer">GitHub Base</a>
          </div>
          <div className="v3-footer-right">
            <span>Built with Tauri + React + Lenis</span>
          </div>
        </div>
      </footer>

      <style>{`
        .v3-root { background: var(--bg-base); color: var(--text-main); }
        .v3-header { position: sticky; top: 0; z-index: 100; background: var(--nav-bg); backdrop-filter: blur(20px); border-bottom: 1px solid var(--border-color); }
        .v3-header-inner { max-width: 1200px; margin: 0 auto; padding: 12px 24px; display: flex; align-items: center; justify-content: space-between; }
        .v3-logo { display: flex; align-items: center; gap: 8px; font-family: var(--font-mono); font-weight: 700; font-size: 1.1rem; }
        .v3-nav { display: flex; gap: 20px; align-items: center; }
        .v3-nav-link { color: var(--text-muted); font-size: 0.9rem; cursor: pointer; text-decoration: none; transition: color 0.2s; display: flex; align-items: center; }
        .v3-nav-link:hover { color: var(--accent-primary); }

        .v3-hero { position: relative; text-align: center; padding: 120px 24px 80px; overflow: hidden; }
        .v3-hero-gradient { position: absolute; top: -150px; left: 50%; transform: translateX(-50%); width: 750px; height: 350px; background: radial-gradient(circle, rgba(255,85,0,0.1) 0%, transparent 65%); filter: blur(60px); pointer-events: none; }
        .v3-hero-content { position: relative; z-index: 1; max-width: 800px; margin: 0 auto; }
        .v3-hero-content .v3-badge { display: inline-flex; align-items: center; gap: 6px; padding: 6px 14px; background: rgba(255,85,0,0.08); border: 1px solid rgba(255,85,0,0.15); border-radius: 20px; font-size: 0.8rem; color: var(--accent-primary); margin-bottom: 24px; }
        .v3-hero h1 { font-size: clamp(2.2rem, 6vw, 3.8rem); font-weight: 700; margin-bottom: 16px; line-height: 1.15; }
        .v3-hero p { color: var(--text-muted); font-size: 1.15rem; max-width: 620px; margin: 0 auto 32px; line-height: 1.6; }
        .v3-hero-ctas { display: flex; gap: 16px; justify-content: center; flex-wrap: wrap; }

        .v3-btn-primary { display: inline-flex; align-items: center; gap: 8px; padding: 13px 26px; background: var(--accent-primary); color: #fff; border: none; border-radius: 10px; font-size: 0.95rem; font-weight: 600; cursor: pointer; text-decoration: none; font-family: var(--font-sans); box-shadow: 0 0 24px rgba(255,85,0,0.3); }
        .v3-btn-ghost { display: inline-flex; align-items: center; gap: 8px; padding: 13px 26px; background: transparent; color: var(--text-main); border: 1px solid var(--border-color); border-radius: 10px; font-size: 0.95rem; cursor: pointer; text-decoration: none; font-family: var(--font-sans); transition: border-color 0.2s; }
        .v3-btn-ghost:hover { border-color: var(--accent-primary); }

        .v3-split-section { max-width: 1300px; margin: 0 auto; padding: 48px 24px 80px; }
        .v3-split-grid { display: grid; grid-template-columns: 1fr 1.1fr; gap: 32px; }

        .v3-docs-panel { background: var(--bg-raised); border: 1px solid var(--border-color); border-radius: 16px; padding: 36px; max-height: 620px; overflow-y: auto; }
        .v3-docs-content h2 { font-size: 1.6rem; margin-bottom: 16px; font-weight: 700; }
        .v3-docs-content h3 { font-size: 1.2rem; margin: 24px 0 12px; font-weight: 600; }
        .v3-docs-content p { color: var(--text-muted); line-height: 1.7; margin-bottom: 14px; font-size: 0.96rem; }
        .v3-docs-content code { font-family: var(--font-mono); background: rgba(255,85,0,0.08); color: var(--accent-primary); padding: 2px 6px; border-radius: 4px; font-size: 0.9em; }
        .v3-docs-content strong { color: var(--text-main); }
        .v3-code-block { background: var(--bg-base); border: 1px solid var(--border-color); border-radius: 10px; padding: 16px; margin: 16px 0; overflow-x: auto; }
        .v3-code-block pre { font-family: var(--font-mono); font-size: 0.85rem; color: var(--term-text); margin: 0; line-height: 1.6; }
        .v3-perm-list { padding-left: 20px; margin: 12px 0 18px; color: var(--text-muted); line-height: 1.8; font-size: 0.96rem; }
        .v3-callout { display: flex; align-items: flex-start; gap: 12px; padding: 16px 20px; background: rgba(255,85,0,0.06); border: 1px solid rgba(255,85,0,0.15); border-radius: 10px; margin-top: 24px; font-size: 0.95rem; color: var(--text-muted); line-height: 1.5; }

        .v3-terminal-panel { display: flex; flex-direction: column; border-radius: 16px; border: 1px solid var(--border-color); overflow: hidden; background: var(--term-bg); height: 620px; }
        .v3-terminal-chrome { display: flex; align-items: center; gap: 12px; padding: 12px 16px; background: var(--term-header); border-bottom: 1px solid var(--border-color); }
        .v3-terminal-dots { display: flex; gap: 6px; }
        .v3-terminal-dots span { width: 12px; height: 12px; border-radius: 50%; }
        .v3-terminal-title { font-size: 0.8rem; color: var(--text-muted); font-family: var(--font-mono); }
        .v3-terminal-body { flex: 1; padding: 8px; overflow: hidden; }
        .v3-terminal-body .widget-content { height: 100%; }
        .v3-verification { display: flex; align-items: center; gap: 8px; padding: 14px 18px; background: rgba(39,201,63,0.08); border-top: 1px solid rgba(39,201,63,0.2); font-size: 0.92rem; font-weight: 500; color: #27c93f; }

        .v3-section { max-width: 1100px; margin: 0 auto; padding: 100px 24px; }
        .v3-section-title { font-size: 2.2rem; font-weight: 700; text-align: center; margin-bottom: 12px; }
        .v3-section-subtitle { text-align: center; color: var(--text-muted); margin-bottom: 48px; font-size: 1.1rem; max-width: 600px; margin-left: auto; margin-right: auto; }

        .v3-features-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px; }
        .v3-feature-card { padding: 32px; background: var(--bg-raised); border: 1px solid var(--border-color); border-radius: 16px; transition: border-color 0.3s; }
        .v3-feature-card:hover { border-color: var(--border-highlight); }
        .v3-feature-icon { width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; background: rgba(255,85,0,0.1); border-radius: 10px; color: var(--accent-primary); margin-bottom: 16px; }
        .v3-feature-card h3 { font-size: 1.1rem; margin-bottom: 8px; font-weight: 600; }
        .v3-feature-card p { color: var(--text-muted); font-size: 0.92rem; line-height: 1.6; }

        .v3-accordion { max-width: 800px; margin: 0 auto; display: flex; flex-direction: column; gap: 12px; }
        .v3-accordion-item { background: var(--bg-raised); border: 1px solid var(--border-color); border-radius: 14px; overflow: hidden; }
        .v3-accordion-header { width: 100%; display: flex; align-items: center; gap: 12px; padding: 18px 24px; background: transparent; border: none; color: var(--text-main); font-size: 1.05rem; font-weight: 600; cursor: pointer; font-family: var(--font-sans); text-align: left; }
        .v3-accordion-body { overflow: hidden; transition: max-height 0.3s ease, opacity 0.3s ease; padding: 0 24px; }
        .v3-module-list { padding: 0 0 18px 28px; color: var(--text-muted); font-size: 0.95rem; display: flex; flex-direction: column; gap: 10px; }
        .v3-module-item-row { display: flex; align-items: center; gap: 8px; }
        .v3-module-item-icon { color: var(--accent-primary); }

        .v3-chat-container { max-width: 800px; margin: 0 auto; border-radius: 16px; overflow: hidden; background: var(--bg-raised); border: 1px solid var(--border-color); }
        .v3-chat-container .widget-content { height: 350px; }

        .v3-compare-table-wrapper { border: 1px solid var(--border-color); border-radius: 16px; overflow: hidden; background: var(--bg-raised); }
        .v3-compare-table { width: 100%; border-collapse: collapse; text-align: left; font-size: 0.95rem; }
        .v3-compare-table th { background: rgba(255,255,255,0.02); padding: 16px 24px; font-weight: 700; border-bottom: 1px solid var(--border-color); color: var(--accent-primary); }
        .v3-compare-table td { padding: 18px 24px; border-bottom: 1px solid var(--border-color); color: var(--text-muted); }
        .v3-compare-table tr:last-child td { border-bottom: none; }

        .v3-progress-row { display: flex; justify-content: center; gap: 64px; flex-wrap: wrap; }
        .v3-counter { text-align: center; }
        .v3-counter-value { display: block; font-size: 3rem; font-weight: 800; font-family: var(--font-mono); color: var(--accent-primary); line-height: 1; }
        .v3-counter-label { display: block; margin-top: 8px; font-size: 0.95rem; color: var(--text-muted); }

        .v3-cta-section { padding: 80px 24px 120px; }
        .v3-cta-card { max-width: 750px; margin: 0 auto; text-align: center; padding: 56px 36px; background: var(--bg-raised); border: 1px solid var(--border-color); border-radius: 24px; }
        .v3-cta-card h2 { font-size: 2rem; margin-bottom: 12px; font-weight: 700; }
        .v3-cta-card p { color: var(--text-muted); margin-bottom: 32px; font-size: 1.05rem; }
        .v3-cta-actions { display: flex; gap: 16px; justify-content: center; flex-wrap: wrap; }

        .v3-footer { border-top: 1px solid var(--border-color); padding: 32px 24px; }
        .v3-footer-inner { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; font-size: 0.88rem; color: var(--text-muted); flex-wrap: wrap; gap: 16px; }
        .v3-footer-left { display: flex; align-items: center; gap: 10px; }
        .v3-footer-inner a { color: var(--text-muted); text-decoration: none; }
        .v3-footer-inner a:hover { color: var(--accent-primary); }

        @media (max-width: 960px) {
          .v3-split-grid { grid-template-columns: 1fr; }
          .v3-docs-panel { max-height: none; }
          .v3-terminal-panel { height: 480px; }
          .v3-footer-inner { justify-content: center; }
        }
      `}</style>
    </div>
  );
}
