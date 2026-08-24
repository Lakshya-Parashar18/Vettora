import { useRef } from 'react';
import { useSmoothScroll } from '../hooks/useSmoothScroll';

export default function SmoothScroll({ children }) {
  const containerRef = useRef(null);
  useSmoothScroll(containerRef);

  return (
    <div ref={containerRef} data-scroll-container className="min-h-screen flex flex-col">
      {children}
    </div>
  );
}
