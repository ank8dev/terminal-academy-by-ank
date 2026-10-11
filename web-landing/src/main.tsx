import { createRoot } from 'react-dom/client';
import { MotionProvider } from '@/providers/MotionProvider';
import { ScrollCanvas } from '@/components/ScrollCanvas';
import { Terminal, LayoutGrid, BookOpen, Network, Box } from 'lucide-react';
import './index.css';

function ProtoHub() {
  const prototypes = [
    {
      id: 'variant-1.html',
      name: 'Variant 1: Classic Redux',
      philosophy: 'High-density tech developer hub with scrambled headers, mesh backgrounds, glow card matrices, and direct terminal interactive inputs.',
      inspiration: 'MaximeHeckel, Appwrite, ElysiaJS',
      typography: 'JetBrains Mono + Fira Code (strict monospaced developer look)',
      features: ['Scrambled text animation', 'Hover glow borders', 'Full terminal widget embed', 'Tauri/React architecture layers', 'Downloader script CTA'],
      icon: Terminal,
      color: '#ff5500'
    },
    {
      id: 'variant-2.html',
      name: 'Variant 2: Workspace Simulator',
      philosophy: 'Dashboard-first simulation displaying the real lesson, terminal, chat, and monitoring panels side-by-side inside the landing flow.',
      inspiration: 'Appwrite console, Lenis documentation',
      typography: 'Inter + Roboto Mono (clean, industrial-scientific look)',
      features: ['Full multi-pane simulator', 'Active incident switching support', 'Telemetry charts & specs table', 'Offline installation profiles'],
      icon: LayoutGrid,
      color: '#b45309'
    },
    {
      id: 'variant-3.html',
      name: 'Variant 3: Playground & Docs',
      philosophy: 'Interactive developer documentation with a split terminal playground, chmod command validation alert, and lesson syllabus accordions.',
      inspiration: 'Trigger.dev, Twenty.com',
      typography: 'Outfit + Ubuntu Mono (premium product marketing look)',
      features: ['Documentation & terminal split', 'Permissions validation triggers', 'Syllabus accordion expand loops', 'Chat widget integration'],
      icon: BookOpen,
      color: '#ea580c'
    },
    {
      id: 'variant-4.html',
      name: 'Variant 4: Network Flow',
      philosophy: 'Visual infrastructure map displaying interactive SVG nodes, bezier line connections, and scroll-responsive path morphing.',
      inspiration: 'Lenis scroll, ElysiaJS homepage',
      typography: 'Lexend + DM Mono (futuristic, high-tech animated look)',
      features: ['Interactive SVG network topology', 'Scroll-morphing paths (useMotion)', 'Isolated sandbox details', 'Monitoring engine charts'],
      icon: Network,
      color: '#f97316'
    },
    {
      id: 'variant-5.html',
      name: 'Variant 5: Bento Matrix',
      philosophy: 'Asymmetric grid layout displaying terminal logs, AI mentor bubbles, curriculum checkmarks, download bars, and metrics rows.',
      inspiration: 'Twenty, Trigger.dev',
      typography: 'Plus Jakarta Sans + IBM Plex Mono (modern editorial clean look)',
      features: ['Bento Grid UI blocks', 'Pre-rendered terminal ANSI sessions', 'Lightweight size comparison bars', 'Multi-column specifications'],
      icon: Box,
      color: '#ff6b00'
    }
  ];

  return (
    <div className="hub-root">
      <div className="hub-header">
        <div className="hub-logo">
          <Terminal size={22} style={{ color: 'var(--accent-primary)' }} />
          <span>Terminal Academy</span>
          <span className="hub-badge">Independent Prototypes Portal</span>
        </div>
      </div>

      <div className="hub-content">
        <div className="hub-title-section">
          <h1>Clean Slate Overhaul Prototypes</h1>
          <p>
            We have generated five completely separate landing pages as independent entry points. 
            Each landing page is a complete website with custom typography, natural vertical scrolling, and interactive sandbox code blocks.
          </p>
        </div>

        <div className="hub-grid">
          {prototypes.map(proto => (
            <div key={proto.id} className="hub-card">
              <div className="hub-card-header">
                <div className="hub-card-icon" style={{ backgroundColor: `${proto.color}15`, color: proto.color }}>
                  <proto.icon size={24} />
                </div>
                <h2>{proto.name}</h2>
              </div>
              <p className="hub-card-desc">{proto.philosophy}</p>
              <div className="hub-card-meta">
                <div><strong>Typography:</strong> <code>{proto.typography}</code></div>
                <div style={{ marginTop: '6px' }}><strong>Inspiration:</strong> {proto.inspiration}</div>
              </div>
              <div className="hub-card-features">
                <h4>Key Features:</h4>
                <ul>
                  {proto.features.map((f, i) => (
                    <li key={i}>{f}</li>
                  ))}
                </ul>
              </div>
              <a href={`/${proto.id}`} className="hub-card-btn" style={{ borderColor: proto.color, color: '#fff', background: `linear-gradient(135deg, ${proto.color}20, transparent)` }}>
                Launch Independent Page →
              </a>
            </div>
          ))}
        </div>
      </div>

      <footer className="hub-footer">
        © 2025 Terminal Academy · Multi-Page Architecture Evaluated Locally
      </footer>

      <style>{`
        .hub-root { min-height: 100vh; background: #050506; color: var(--text-main); font-family: var(--font-sans); position: relative; z-index: 10; padding-bottom: 80px; }
        .hub-header { border-bottom: 1px solid var(--border-color); background: rgba(5,5,6,0.8); backdrop-filter: blur(20px); position: sticky; top: 0; z-index: 50; }
        .hub-logo { max-width: 1200px; margin: 0 auto; padding: 16px 24px; display: flex; align-items: center; gap: 10px; font-family: var(--font-mono); font-weight: 700; font-size: 1.25rem; }
        .hub-badge { font-size: 0.72rem; padding: 3px 10px; background: rgba(255,85,0,0.15); color: var(--accent-primary); border-radius: 12px; font-weight: 500; font-family: var(--font-sans); }
        
        .hub-content { max-width: 1200px; margin: 0 auto; padding: 80px 24px; }
        .hub-title-section { text-align: center; max-width: 750px; margin: 0 auto 64px; }
        .hub-title-section h1 { font-size: clamp(2.2rem, 5vw, 3.2rem); font-weight: 800; margin-bottom: 16px; letter-spacing: -0.02em; }
        .hub-title-section p { color: var(--text-muted); font-size: 1.15rem; line-height: 1.6; }

        .hub-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 24px; }
        .hub-card { background: var(--bg-raised); border: 1px solid var(--border-color); border-radius: 20px; padding: 32px; display: flex; flex-direction: column; transition: border-color 0.3s, transform 0.3s; }
        .hub-card:hover { border-color: var(--border-highlight); transform: translateY(-4px); }
        .hub-card-header { display: flex; align-items: center; gap: 14px; margin-bottom: 16px; }
        .hub-card-header h2 { font-size: 1.25rem; font-weight: 700; margin: 0; }
        .hub-card-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; }
        .hub-card-desc { color: var(--text-muted); font-size: 0.95rem; line-height: 1.6; margin-bottom: 16px; flex-grow: 1; }
        .hub-card-meta { font-size: 0.85rem; color: var(--text-muted); margin-bottom: 20px; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 12px; }
        .hub-card-meta strong { color: var(--text-main); }
        .hub-card-meta code { font-family: var(--font-mono); color: var(--accent-primary); }
        
        .hub-card-features { margin-bottom: 28px; }
        .hub-card-features h4 { font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 10px; color: var(--text-main); }
        .hub-card-features ul { padding-left: 18px; margin: 0; display: flex; flex-direction: column; gap: 6px; }
        .hub-card-features li { font-size: 0.88rem; color: var(--text-muted); }

        .hub-card-btn { display: block; text-align: center; padding: 12px 24px; border: 1px solid; border-radius: 10px; font-size: 0.95rem; font-weight: 600; text-decoration: none; cursor: pointer; transition: filter 0.2s; }
        .hub-card-btn:hover { filter: brightness(1.2); }

        .hub-footer { border-top: 1px solid var(--border-color); padding: 40px 24px; text-align: center; font-size: 0.88rem; color: var(--text-muted); background: #050506; }

        @media (max-width: 600px) {
          .hub-content { padding: 48px 16px; }
          .hub-grid { grid-template-columns: 1fr; }
        }
      `}</style>
    </div>
  );
}

const rootEl = document.getElementById('root');
if (rootEl) {
  createRoot(rootEl).render(
    <MotionProvider>
      <ScrollCanvas />
      <ProtoHub />
    </MotionProvider>
  );
}
