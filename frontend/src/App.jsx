import Header from './components/Header';
import ScreeningDashboard from './pages/ScreeningDashboard';
import { ThemeProvider } from './context/ThemeContext';
import SmoothScroll from './components/SmoothScroll';
import AnimatedBackground from './components/AnimatedBackground';

export default function App() {
  return (
    <ThemeProvider>
      <SmoothScroll>
        <div className="relative min-h-[100dvh] bg-bg-primary text-text-primary flex flex-col antialiased transition-colors overflow-x-hidden">
          <AnimatedBackground />
          <Header />
          <main className="relative z-10 flex-1">
            <ScreeningDashboard />
          </main>
          <footer className="border-t border-border py-4 px-6 text-center text-xs text-text-muted font-mono bg-bg-surface transition-colors mt-auto z-10 relative">
            Vettora • AI-Powered Resume Screening UI
          </footer>
        </div>
      </SmoothScroll>
    </ThemeProvider>
  );
}
