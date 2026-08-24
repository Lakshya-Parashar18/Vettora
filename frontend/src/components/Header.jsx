import { useTheme } from '../context/ThemeContext';
import HallmarkLogo from './HallmarkLogo';

export default function Header() {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="sticky top-0 z-30 bg-bg-surface border-b border-border/80 px-4 sm:px-8 py-3 transition-colors">
      <div className="app-container flex items-center justify-between">
        <div className="flex items-center space-x-3.5">
          <HallmarkLogo size={34} />
          <div>
            <div className="flex items-center space-x-2.5">
              <span className="font-display font-medium text-xl tracking-tight text-text-primary">
                Vettora
              </span>
              <span className="text-[10px] font-mono font-medium tracking-wider text-accent border border-accent/40 px-1.5 py-0.2 rounded uppercase">
                Assay v1.0
              </span>
            </div>
            <p className="text-xs font-mono text-text-muted mt-0.5 tracking-tight uppercase">
              evidence-based candidate screening
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {/* Simple Bordered Pill Switch (Requirement 1) */}
          <button
            type="button"
            onClick={toggleTheme}
            className="flex items-center space-x-1 p-0.5 rounded-full border border-border bg-bg-base font-mono text-[10px] uppercase transition-colors"
            aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
            title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
          >
            <span
              className={`px-2 py-0.5 rounded-full transition-colors ${
                theme === 'dark'
                  ? 'bg-accent text-bg-base font-medium'
                  : 'text-text-muted hover:text-text-primary'
              }`}
            >
              DARK
            </span>
            <span
              className={`px-2 py-0.5 rounded-full transition-colors ${
                theme === 'light'
                  ? 'bg-accent text-bg-base font-medium'
                  : 'text-text-muted hover:text-text-primary'
              }`}
            >
              LIGHT
            </span>
          </button>
        </div>
      </div>
    </header>
  );
}
