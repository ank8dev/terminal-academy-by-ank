import React, { useEffect, useRef } from 'react';
import { useMotion } from '../providers/MotionProvider';

export const ScrollCanvas: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const { velocity, scrollProgress } = useMotion();

  // Keep a mutable ref of the scroll progress and velocity to avoid re-triggering the useEffect loop
  const scrollRef = useRef({ progress: 0, velocity: 0 });
  
  useEffect(() => {
    scrollRef.current = { progress: scrollProgress, velocity };
  }, [scrollProgress, velocity]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    // ── MASSIVE 3D SYSTEM INFRASTRUCTURE CYLINDER GRID ──
    interface Point3D {
      x: number;
      y: number;
      z: number;
    }

    const points: Point3D[] = [];
    const ringCount = 8;
    const pointsPerRing = 16;
    
    // Visually expanded scale, depth, and visibility mapping user requests
    const baseRadius = 580; 
    const cylinderLength = 1200;

    for (let r = 0; r < ringCount; r++) {
      const cy = (r / (ringCount - 1) - 0.5) * cylinderLength;
      for (let p = 0; p < pointsPerRing; p++) {
        const theta = (p / pointsPerRing) * Math.PI * 2;
        points.push({
          x: Math.cos(theta) * baseRadius,
          y: cy,
          z: Math.sin(theta) * baseRadius
        });
      }
    }

    let currentProgress = 0;
    let currentVelocity = 0;
    let currentDamp = 1.0;
    let currentTransition = 0;
    let time = 0;

    const handleResize = () => {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };
    window.addEventListener('resize', handleResize);

    const project = (pt: Point3D, rotX: number, rotY: number, scrollOffset: number) => {
      const ry = rotY + scrollOffset * 2.5;
      
      let x1 = pt.x * Math.cos(ry) - pt.z * Math.sin(ry);
      let y1 = pt.y;
      let z1 = pt.x * Math.sin(ry) + pt.z * Math.cos(ry);

      const rx = rotX + scrollOffset * 1.1;
      
      let x2 = x1;
      let y2 = y1 * Math.cos(rx) - z1 * Math.sin(rx);
      let z2 = y1 * Math.sin(rx) + z1 * Math.cos(rx);

      // Increased camera depth and perspective mapping
      const zoom = 1.35 + scrollOffset * 1.8;
      x2 *= zoom;
      y2 *= zoom;
      z2 *= zoom;

      // 3D to 2D perspective math with near clipping to prevent NaN/Infinity
      const fov = 850;
      const nearClip = -fov + 50;
      const isBehindCamera = z2 <= nearClip;
      
      const projScale = isBehindCamera ? 0 : fov / (fov + z2);

      const px = x2 * projScale + width / 2;
      const centerY = height * 0.42 + (scrollOffset * 110);
      const py = y2 * projScale + centerY;

      return { 
        x: px, 
        y: py, 
        z: z2, 
        scale: projScale, 
        visible: !isBehindCamera && projScale > 0 && px >= -500 && px <= width + 500 && py >= -500 && py <= height + 500
      };
    };

    const animate = () => {
      const targetProgress = scrollRef.current.progress || 0;
      const targetVelocity = scrollRef.current.velocity || 0;

      currentProgress += (targetProgress - currentProgress) * 0.05;
      currentVelocity += (targetVelocity - currentVelocity) * 0.05;

      // ── DETECT LIFECYCLE & ARCHITECTURE PINNED RANGES ──
      const lifecycleEl = document.getElementById('lifecycle');
      const architectureEl = document.getElementById('architecture');
      let targetDamp = 1.0;
      let targetTransition = 0;

      if (lifecycleEl) {
        const rect = lifecycleEl.getBoundingClientRect();
        const vh = window.innerHeight;
        const scrollRange = Math.max(1, rect.height - vh);
        const rawProgress = -rect.top / scrollRange;

        if (rect.top > 0 && rect.top < vh * 1.5) {
          // Pre-approach: start morphing 1.5 viewports before pinning
          targetTransition = (1 - rect.top / (vh * 1.5)) * 0.85;
        } else if (rawProgress >= 0 && rawProgress <= 1) {
          // Pinned: full freeze + complete atmospheric transition
          targetDamp = 0.0;
          if (rawProgress < 0.1) {
            targetTransition = 0.85 + (rawProgress / 0.1) * 0.15;
          } else if (rawProgress > 0.85) {
            targetTransition = (1 - rawProgress) / 0.15;
          } else {
            targetTransition = 1.0;
          }
        }
      }

      // Also freeze cylinder during architecture chapter (stays dark, just freeze rotation)
      if (architectureEl) {
        const rect = architectureEl.getBoundingClientRect();
        const vh = window.innerHeight;
        const scrollRange = Math.max(1, rect.height - vh);
        const rawProgress = -rect.top / scrollRange;
        if (rawProgress >= 0 && rawProgress <= 1) {
          targetDamp = 0.0;
        }
      }

      currentDamp += (targetDamp - currentDamp) * 0.08;
      currentTransition += (targetTransition - currentTransition) * 0.05;
      
      // Decelerate time steps inside the pinned range
      time += 0.005 * currentDamp;

      const baseRotY = time * 0.04;
      const baseRotX = 0.55 + Math.sin(time * 0.06) * 0.04;

      ctx.clearRect(0, 0, width, height);

      // ── DYNAMIC SCENE BACKDROP TRANSITION ──
      // Morph background color smoothly between dark black (#050506) and bright warm white (#ffffff)
      const bgR = Math.round(5 + 250 * currentTransition);
      const bgG = Math.round(5 + 250 * currentTransition);
      const bgB = Math.round(6 + 249 * currentTransition);
      ctx.fillStyle = `rgb(${bgR}, ${bgG}, ${bgB})`;
      ctx.fillRect(0, 0, width, height);

      // Draw backdrop glow - Shifted to the bottom-right corner mapping Lenis reference
      const glowX = width * 0.85;
      const glowY = height * 0.85;
      const backdropGlow = ctx.createRadialGradient(
        glowX, glowY, 50,
        glowX, glowY, baseRadius * 2.5
      );
      
      // Animate glows based on transition states
      const alphaGlow1 = (0.26 - currentTransition * 0.16);
      const alphaGlow2 = (0.12 - currentTransition * 0.06);
      const alphaGlow3 = (0.04 - currentTransition * 0.02);

      backdropGlow.addColorStop(0, `rgba(255, 85, 0, ${alphaGlow1})`);     
      backdropGlow.addColorStop(0.45, `rgba(245, 158, 11, ${alphaGlow2})`); 
      backdropGlow.addColorStop(0.8, `rgba(251, 191, 36, ${alphaGlow3})`);  
      backdropGlow.addColorStop(1, 'rgba(0, 0, 0, 0)');

      ctx.fillStyle = backdropGlow;
      ctx.beginPath();
      ctx.arc(glowX, glowY, baseRadius * 2.8, 0, Math.PI * 2);
      ctx.fill();

      // Project vertices
      const projected = points.map(pt => project(pt, baseRotX, baseRotY, currentProgress));

      // Draw Rings with increased expressiveness (higher visibility and thicker paths)
      for (let r = 0; r < ringCount; r++) {
        const startIdx = r * pointsPerRing;
        const progressZ = r / (ringCount - 1);
        
        // Interpolate stroke opacity and line colors based on light theme transitionT
        const ringAlpha = (1 - currentTransition) * (0.24 - progressZ * 0.1) + currentTransition * (0.15 - progressZ * 0.06);
        ctx.strokeStyle = currentTransition > 0.5 
          ? `rgba(15, 23, 42, ${ringAlpha})` 
          : `rgba(245, 158, 11, ${ringAlpha})`;

        ctx.lineWidth = 1.8; 
        ctx.beginPath();
        let first = true;
        for (let p = 0; p < pointsPerRing; p++) {
          const idx = startIdx + p;
          const pt = projected[idx];

          if (pt.visible) {
            if (first) {
              ctx.moveTo(pt.x, pt.y);
              first = false;
            } else {
              ctx.lineTo(pt.x, pt.y);
            }
          }
        }
        ctx.closePath();
        ctx.stroke();
      }

      // Draw Vertical paths
      ctx.lineWidth = 1.2;
      for (let r = 0; r < ringCount - 1; r++) {
        const startIdx = r * pointsPerRing;
        const nextRingStart = (r + 1) * pointsPerRing;

        for (let p = 0; p < pointsPerRing; p++) {
          const idx1 = startIdx + p;
          const idx2 = nextRingStart + p;
          const p1 = projected[idx1];
          const p2 = projected[idx2];

          if (p1.visible && p2.visible) {
            const angleRatio = p / pointsPerRing;
            const rVal = Math.floor(255 - angleRatio * 4);
            const gVal = Math.floor(85 + angleRatio * 106);

            const vertAlpha = (1 - currentTransition) * 0.15 + currentTransition * 0.08;
            ctx.strokeStyle = currentTransition > 0.5
              ? `rgba(15, 23, 42, ${vertAlpha})`
              : `rgba(${rVal}, ${gVal}, 24, ${vertAlpha})`;

            ctx.beginPath();
            ctx.moveTo(p1.x, p1.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.stroke();
          }
        }
      }

      // Draw Glowing Transistor Nodes (Much larger and brighter, colored inside TA palette)
      for (let i = 0; i < projected.length; i++) {
        const pt = projected[i];
        if (!pt.visible) continue;

        const pulse = Math.sin(time * 2.5 + i * 0.45) * 0.5 + 0.5;
        const depthFade = Math.max(0, 1 - pt.z / 1200);

        ctx.beginPath();
        ctx.arc(pt.x, pt.y, 4 + pulse * 3.5, 0, Math.PI * 2); 

        const nodeAlpha = depthFade * ((1 - currentTransition) * (0.35 + pulse * 0.45) + currentTransition * (0.45 + pulse * 0.45));
        const rNode = Math.round((1 - currentTransition) * 251 + currentTransition * 255);
        const gNode = Math.round((1 - currentTransition) * 191 + currentTransition * 85);
        const bNode = Math.round((1 - currentTransition) * 36 + currentTransition * 0);
        ctx.fillStyle = `rgba(${rNode}, ${gNode}, ${bNode}, ${nodeAlpha})`;

        ctx.fill();
      }

      animationFrameId = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
        zIndex: 0,
      }}
    />
  );
};
