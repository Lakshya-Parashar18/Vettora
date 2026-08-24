import { useEffect, useRef } from 'react';

export default function AnimatedBackground() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationFrameId;

    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    const handleResize = () => {
      if (!canvas) return;
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };
    window.addEventListener('resize', handleResize);

    // Soothing micro-star dots (balanced density ~90 nodes)
    const STARS_COUNT = Math.min(Math.floor(width / 16), 90);
    const stars = [];

    for (let i = 0; i < STARS_COUNT; i++) {
      stars.push({
        x: Math.random() * width,
        y: Math.random() * height,
        size: Math.random() * 1.1 + 0.7,
        color: i % 3 === 0 ? '217, 119, 6' : i % 3 === 1 ? '16, 185, 129' : '234, 179, 8', // Amber, Sage, Gold
        phase: Math.random() * Math.PI * 2,
        speed: Math.random() * 0.008 + 0.003,
      });
    }

    const render = () => {
      ctx.clearRect(0, 0, width, height);

      // Render independent breathing micro-star dots
      stars.forEach((star) => {
        star.phase += star.speed;
        const alpha = ((Math.sin(star.phase) + 1) / 2) * 0.45 + 0.10;

        ctx.beginPath();
        ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${star.color}, ${alpha})`;
        ctx.fill();
      });

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <div
      aria-hidden="true"
      className="pointer-events-none fixed inset-0 z-0 overflow-hidden select-none"
    >
      {/* 60FPS Micro-Star Canvas */}
      <canvas
        ref={canvasRef}
        aria-hidden="true"
        className="w-full h-full opacity-90 transition-opacity duration-500"
      />
    </div>
  );
}
