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
        // Smooth sine wave breathing opacity (0.10 to 0.55)
        const alpha = ((Math.sin(star.phase) + 1) / 2) * 0.45 + 0.10;

        ctx.beginPath();
        ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${star.color}, ${alpha})`;
        ctx.shadowColor = `rgba(${star.color}, ${alpha * 0.7})`;
        ctx.shadowBlur = 10;
        ctx.fill();
        ctx.shadowBlur = 0;
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
      {/* High Density Soothing Micro-Star Constellation Canvas */}
      <canvas
        ref={canvasRef}
        aria-hidden="true"
        className="w-full h-full opacity-90 transition-opacity duration-500"
      />

      {/* Ultra-Soft Breathing Ambient Glow Orbs */}
      <div className="absolute -top-40 -left-40 w-[650px] h-[650px] rounded-full bg-[var(--accent)]/08 dark:bg-[var(--accent)]/06 blur-[140px] animate-ambient-pulse" />
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-[550px] h-[550px] rounded-full bg-amber-500/06 dark:bg-amber-500/04 blur-[160px] animate-ambient-pulse" />
      <div className="absolute top-2/3 left-1/4 w-[450px] h-[450px] rounded-full bg-emerald-500/06 dark:bg-emerald-500/04 blur-[150px] animate-ambient-pulse" />
      <div className="absolute -bottom-40 -right-40 w-[600px] h-[600px] rounded-full bg-[var(--accent-2)]/08 dark:bg-[var(--accent-2)]/05 blur-[150px] animate-ambient-pulse" />
    </div>
  );
}
