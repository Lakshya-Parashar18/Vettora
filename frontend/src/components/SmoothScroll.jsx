import { useSmoothScroll } from '../hooks/useSmoothScroll';

export default function SmoothScroll({ children }) {
  useSmoothScroll();

  return (
    <div className="min-h-screen flex flex-col font-sans text-text-primary bg-bg-primary antialiased">
      {children}
    </div>
  );
}
