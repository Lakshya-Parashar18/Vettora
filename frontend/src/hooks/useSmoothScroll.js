import { useEffect, useRef } from 'react';

export function useSmoothScroll() {
  const scrollInstanceRef = useRef(null);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    let isMounted = true;

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

        if (isMounted) {
          scrollInstanceRef.current = new LocomotiveScroll({
            lenisOptions: {
              wrapper: window,
              content: document.documentElement,
              lerp: 0.1,
              duration: 1.2,
              smoothWheel: true,
            },
          });
        }
      } catch {
        // fallback
      }
    }

    initScroll();

    return () => {
      isMounted = false;
      if (scrollInstanceRef.current) {
        try {
          scrollInstanceRef.current.destroy();
        } catch {
          // ignore
        }
        scrollInstanceRef.current = null;
      }
    };
  }, []);

  return scrollInstanceRef;
}
