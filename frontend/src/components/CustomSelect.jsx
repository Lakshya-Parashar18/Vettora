import { useState, useRef, useEffect } from 'react';
import { ChevronDown, Check } from 'lucide-react';

export default function CustomSelect({
  id,
  value,
  onChange,
  options = [],
  icon: Icon,
  ariaLabel,
}) {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef(null);

  const selectedOption = options.find((opt) => opt.value === value) || options[0];

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') setIsOpen(false);
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  const handleSelect = (val) => {
    onChange(val);
    setIsOpen(false);
  };

  return (
    <div ref={containerRef} className="relative inline-block text-left font-mono text-xs">
      <button
        id={id}
        type="button"
        onClick={() => setIsOpen((prev) => !prev)}
        aria-label={ariaLabel}
        aria-expanded={isOpen}
        className="inline-flex items-center space-x-2 bg-bg-surface border border-border hover:border-accent/40 text-text-primary px-2.5 py-1.5 rounded focus:outline-none focus:ring-2 focus:ring-[var(--accent)] transition-all cursor-pointer select-none"
      >
        {Icon && <Icon className="w-3.5 h-3.5 text-accent shrink-0" />}
        <span className="truncate">{selectedOption?.label || ''}</span>
        <ChevronDown
          className={`w-3.5 h-3.5 text-accent shrink-0 transition-transform duration-200 ${
            isOpen ? 'rotate-180' : ''
          }`}
        />
      </button>

      {isOpen && (
        <div
          role="listbox"
          aria-labelledby={id}
          className="absolute left-0 mt-1.5 w-max min-w-[180px] bg-bg-surface border border-border rounded-lg shadow-2xl py-1 z-50 animate-in fade-in zoom-in-95 duration-150 backdrop-blur-md"
        >
          {options.map((opt) => {
            const isSelected = opt.value === value;
            return (
              <div
                key={opt.value}
                role="option"
                aria-selected={isSelected}
                onClick={() => handleSelect(opt.value)}
                className={`px-3 py-2 text-xs flex items-center justify-between cursor-pointer transition-colors ${
                  isSelected
                    ? 'bg-accent/15 text-accent font-medium'
                    : 'text-text-primary hover:bg-accent/10 hover:text-accent'
                }`}
              >
                <span className="truncate">{opt.label}</span>
                {isSelected && <Check className="w-3.5 h-3.5 text-accent shrink-0 ml-2" />}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
