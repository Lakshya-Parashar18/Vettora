import { useEffect, useRef } from 'react';

export function useSmoothScroll(containerRef, enabled = true) {
  const scrollInstanceRef = useRef(null);

  useEffect(() => {
    if (!enabled || typeof window === 'undefined') return;

    // Disable smooth scrolling on touch devices
    if (window.innerWidth <= 768 || 'ontouchstart' in window) return;

    async function initScroll() {
      try {
        const LocomotiveScrollModule = await import('locomotive-scroll');
        const LocomotiveScroll = LocomotiveScrollModule.default || LocomotiveScrollModule;

        if (scrollInstanceRef.current) {
          try {
            scrollInstanceRef.current.destroy();
          } catch {
            // ignore
          }
        }

        scrollInstanceRef.current = new LocomotiveScroll({
          el: containerRef.current || document.querySelector('[data-scroll-container]'),
          smooth: true,
          smoothMobile: false,
          inertia: 0.8,
        });
      } catch {
        // fallback to native scroll
      }
    }

    initScroll();

    return () => {
      if (scrollInstanceRef.current) {
        try {
          scrollInstanceRef.current.destroy();
        } catch {
          // ignore
        }
        scrollInstanceRef.current = null;
      }
    };
  }, [containerRef, enabled]);

  return scrollInstanceRef;
}
