import { useEffect } from 'react';

// Token-guarded requestAnimationFrame loop: stop() cancels in-flight callbacks
export function createAnimationFrameLoop(onFrame: (timestamp: number) => boolean | void) {
  let animationFrameId: number | null = null;
  let isLoopRunning = false;
  let runToken = 0;

  const stop = () => {
    if (!isLoopRunning && animationFrameId === null) return;
    isLoopRunning = false;
    runToken += 1;
    if (animationFrameId !== null) {
      window.cancelAnimationFrame(animationFrameId);
      animationFrameId = null;
    }
  };

  const scheduleNextFrame = (token: number) => {
    animationFrameId = window.requestAnimationFrame((timestamp) => {
      animationFrameId = null;
      if (!isLoopRunning || token !== runToken) return;
      if (onFrame(timestamp) === false) {
        if (token === runToken) isLoopRunning = false;
        return;
      }
      if (!isLoopRunning || token !== runToken) return;
      scheduleNextFrame(token);
    });
  };

  const start = () => {
    if (isLoopRunning) return;
    isLoopRunning = true;
    runToken += 1;
    scheduleNextFrame(runToken);
  };

  return { isRunning: () => isLoopRunning, start, stop };
}

// Batches the scroll/resize callback to exactly one call per animation frame
export function useScheduledOnScroll(callback: () => void, enabled = true) {
  useEffect(() => {
    if (!enabled) return;

    const frameTask = createAnimationFrameLoop(() => {
      callback();
      return false; // Run once per trigger, do not self-loop
    });
    
    const schedule = frameTask.start;

    callback();
    window.addEventListener('scroll', schedule, { passive: true });
    window.addEventListener('resize', schedule);
    return () => {
      window.removeEventListener('scroll', schedule);
      window.removeEventListener('resize', schedule);
      frameTask.stop();
    };
  }, [callback, enabled]);
}
