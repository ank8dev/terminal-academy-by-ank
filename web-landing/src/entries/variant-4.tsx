import { createRoot } from 'react-dom/client';
import { MotionProvider } from '@/providers/MotionProvider';
import { ScrollCanvas } from '@/components/ScrollCanvas';
import Variant4MotionFlow from '@/variants/Variant4MotionFlow';
import '../index.css';

// Apply specific typography and native scrolling overrides for V4
const style = document.createElement('style');
style.textContent = `
  :root {
    --font-sans: 'Lexend', sans-serif;
    --font-mono: 'DM Mono', monospace;
  }
  html, body, #root {
    width: 100% !important;
    height: auto !important;
    min-height: 100% !important;
    overflow: visible !important;
    overflow-x: hidden !important;
    user-select: text !important;
    -webkit-user-drag: auto !important;
  }
  body {
    font-family: var(--font-sans);
  }
`;
document.head.appendChild(style);

const rootEl = document.getElementById('root');
if (rootEl) {
  createRoot(rootEl).render(
    <MotionProvider>
      <ScrollCanvas />
      <Variant4MotionFlow />
    </MotionProvider>
  );
}
