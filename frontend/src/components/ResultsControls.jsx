import { Search, Filter, ArrowUpDown, X, Download } from 'lucide-react';
import CustomSelect from './CustomSelect';

const FILTER_OPTIONS = [
  { value: 'ALL', label: 'ALL TIERS' },
  { value: 'STRONG', label: 'STRONG MATCH' },
  { value: 'GOOD', label: 'GOOD MATCH' },
  { value: 'PARTIAL', label: 'PARTIAL MATCH' },
  { value: 'WEAK', label: 'WEAK MATCH' },
];

const SORT_OPTIONS = [
  { value: 'SCORE_DESC', label: 'SCORE: HIGH TO LOW' },
  { value: 'SCORE_ASC', label: 'SCORE: LOW TO HIGH' },
  { value: 'NAME_ASC', label: 'NAME: A TO Z' },
];

export default function ResultsControls({
  searchQuery,
  onSearchChange,
  recommendationFilter,
  onFilterChange,
  sortBy,
  onSortChange,
  totalResultsCount,
  filteredCount,
  onExportCsv,
  onExportJson,
}) {
  const isFiltered = searchQuery.trim() !== '' || recommendationFilter !== 'ALL';

  const clearFilters = () => {
    onSearchChange('');
    onFilterChange('ALL');
    onSortChange('SCORE_DESC');
  };

  return (
    <div className="bg-bg-surface border border-border rounded-lg p-4 space-y-3 font-mono text-xs transition-colors">
      <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
        
        {/* Search Input (Requirement 4) */}
        <div className="relative flex-1">
          <Search className="w-3.5 h-3.5 text-text-muted absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search candidates by name or email..."
            className="w-full bg-bg-surface text-text-primary border border-border rounded pl-8 pr-8 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-[var(--accent)] font-sans"
            aria-label="Search candidates by name or email"
          />
          {searchQuery && (
            <button
              type="button"
              onClick={() => onSearchChange('')}
              className="btn-ghost absolute right-2 top-1/2 -translate-y-1/2 p-0.5"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Filter, Sort & Export Controls */}
        <div className="flex items-center space-x-2.5 flex-wrap sm:flex-nowrap">
          <CustomSelect
            id="recommendation-filter"
            value={recommendationFilter}
            onChange={onFilterChange}
            options={FILTER_OPTIONS}
            icon={Filter}
            ariaLabel="Filter candidates by match tier"
          />

          <CustomSelect
            id="sort-by-select"
            value={sortBy}
            onChange={onSortChange}
            options={SORT_OPTIONS}
            icon={ArrowUpDown}
            ariaLabel="Sort candidates"
          />

          {/* Export CSV Button */}
          {onExportCsv && (
            <button
              type="button"
              onClick={onExportCsv}
              className="inline-flex items-center space-x-1 px-2.5 py-1.5 bg-bg-base border border-accent/40 text-accent hover:bg-accent/15 rounded transition-colors font-mono text-xs font-medium"
              title="Export candidate ranking ledger to CSV file"
            >
              <Download className="w-3.5 h-3.5" />
              <span>CSV</span>
            </button>
          )}

          {/* Export JSON Button */}
          {onExportJson && (
            <button
              type="button"
              onClick={onExportJson}
              className="inline-flex items-center space-x-1 px-2.5 py-1.5 bg-bg-base border border-border text-text-secondary hover:text-text-primary hover:border-border-strong rounded transition-colors font-mono text-xs"
              title="Export candidate evaluation dataset to JSON file"
            >
              <Download className="w-3.5 h-3.5 text-text-muted" />
              <span>JSON</span>
            </button>
          )}

          {isFiltered && (
            <button
              type="button"
              onClick={clearFilters}
              className="btn-ghost text-xs text-text-muted hover:text-[var(--danger-muted)]"
            >
              <X className="w-3 h-3" />
              <span>RESET</span>
            </button>
          )}
        </div>
      </div>

      {/* Requirement 4: Mono caption in --text-muted */}
      <div className="flex items-center justify-between text-[10px] text-text-muted pt-1 uppercase font-mono">
        <span>
          SHOWING {filteredCount} OF {totalResultsCount} CANDIDATES
        </span>
        {isFiltered && <span className="text-accent">FILTER ACTIVE</span>}
      </div>
    </div>
  );
}
