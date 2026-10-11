import { useMotion } from '../providers/MotionProvider';

export function useViewportMotion() {
  const { scrollProgress, direction, viewport } = useMotion();
  return { scrollProgress, direction, viewport };
}
