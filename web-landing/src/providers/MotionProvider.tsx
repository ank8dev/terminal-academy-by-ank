import React, { createContext, useContext, useEffect, useState, useRef } from 'react';
import Lenis from 'lenis';
import 'lenis/dist/lenis.css';

interface MotionContextType {
  scrollProgress: number;
  velocity: number;
  direction: number;
  viewport: { width: number; height: number };
  lenisInstance: Lenis | null;
}

const MotionContext = createContext<MotionContextType>({
  scrollProgress: 0,
  velocity: 0,
  direction: 0,
  viewport: { width: 0, height: 0 },
  lenisInstance: null,
});

export const useMotion = () => useContext(MotionContext);

export const MotionProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [motionState, setMotionState] = useState<MotionContextType>({
    scrollProgress: 0,
    velocity: 0,
    direction: 0,
    viewport: { width: 0, height: 0 },
    lenisInstance: null,
  });

  const lenisRef = useRef<Lenis | null>(null);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    // Respect reduced motion preference for accessibility
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    const lenis = new Lenis({
      smoothWheel: !prefersReduced,
      autoRaf: true,
      lerp: 0.1,
    });

    lenisRef.current = lenis;

    const handleScroll = () => {
      setMotionState({
        scrollProgress: lenis.progress,
        velocity: lenis.velocity,
        direction: lenis.direction,
        viewport: { width: window.innerWidth, height: window.innerHeight },
        lenisInstance: lenis,
      });
    };

    lenis.on('scroll', handleScroll);

    // Set initial layout details
    setMotionState({
      scrollProgress: 0,
      velocity: 0,
      direction: 0,
      viewport: { width: window.innerWidth, height: window.innerHeight },
      lenisInstance: lenis,
    });

    const handleResize = () => {
      setMotionState(prev => ({
        ...prev,
        viewport: { width: window.innerWidth, height: window.innerHeight },
      }));
    };

    window.addEventListener('resize', handleResize);

    return () => {
      lenis.destroy();
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return (
    <MotionContext.Provider value={motionState}>
      {children}
    </MotionContext.Provider>
  );
};
