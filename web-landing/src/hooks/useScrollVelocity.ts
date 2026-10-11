import { useMotion } from '../providers/MotionProvider';

export function useScrollVelocity() {
  const { velocity } = useMotion();
  return velocity;
}
