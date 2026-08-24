import { Edit3, Briefcase, Clock, GraduationCap, Award } from 'lucide-react';

export default function JobSummaryCard({ job, jobId, onEdit }) {
  if (!job) return null;

  const requiredSkills = job.required_skills || [];
  const preferredSkills = job.preferred_skills || [];
  const minYears = job.experience?.minimum_years;

  const eduDegrees = job.education?.degrees || [];
  const eduFields = job.education?.fields || [];
  const educationBadges = [...eduDegrees, ...eduFields];

  const preferredQuals = job.preferred_qualifications || [];
  const allPreferred = [...preferredSkills, ...preferredQuals];

  return (
    <div className="bg-bg-surface border border-border rounded-lg p-5 flex flex-col justify-between h-full font-sans transition-colors">
      <div>
        <div className="flex items-center justify-between mb-3 border-b border-border/60 pb-3">
          <div className="flex items-center space-x-2 font-mono text-xs">
            <span className="flex items-center space-x-1.5 text-text-primary font-medium">
              <span className="w-2 h-2 rounded-full bg-[var(--accent-2)] inline-block" />
              <span>JOB READY</span>
            </span>
            <span className="text-text-secondary font-mono text-[11px] font-medium">
              | ID: {jobId ? `${jobId.substring(0, 8)}...` : 'stored'}
            </span>
          </div>

          <button
            type="button"
            onClick={onEdit}
            className="btn-secondary text-xs"
          >
            <Edit3 className="w-3 h-3" />
            <span>EDIT SPEC</span>
          </button>
        </div>

        <h3 className="text-base font-medium text-text-primary mb-2 flex items-center space-x-2">
          <Briefcase className="w-4 h-4 text-accent shrink-0" />
          <span className="truncate">{job.title || 'Decomposed Job Specification'}</span>
        </h3>

        {minYears !== null && minYears !== undefined && (
          <div className="flex items-center space-x-1.5 text-xs text-text-secondary mb-3 font-mono">
            <Clock className="w-3.5 h-3.5 text-accent" />
            <span>MIN EXPERIENCE: {minYears > 0 ? `${minYears}+ YEARS` : 'ENTRY LEVEL / INTERN'}</span>
          </div>
        )}

        {/* Required Skills & Technical Tracks */}
        {requiredSkills.length > 0 && (
          <div className="mb-3 font-mono">
            <span className="text-[10px] text-text-muted uppercase tracking-wider block mb-1.5">
              REQUIRED SKILLS &amp; TRACKS · {requiredSkills.length}
            </span>
            <div className="flex flex-wrap gap-1.5">
              {requiredSkills.map((skill, idx) => (
                <span
                  key={idx}
                  className="px-2.5 py-1 text-xs text-text-primary bg-transparent border border-border rounded"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Education & Eligibility Criteria */}
        {educationBadges.length > 0 && (
          <div className="mb-3 font-mono">
            <span className="text-[10px] text-text-muted uppercase tracking-wider flex items-center space-x-1 mb-1.5">
              <GraduationCap className="w-3 h-3 text-accent" />
              <span>EDUCATION &amp; ELIGIBILITY · {educationBadges.length}</span>
            </span>
            <div className="flex flex-wrap gap-1.5">
              {educationBadges.map((badge, idx) => (
                <span
                  key={idx}
                  className="px-2 py-0.5 text-xs text-accent bg-accent/10 border border-accent/30 rounded"
                >
                  {badge}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Preferred Skills & Traits */}
        {allPreferred.length > 0 && (
          <div className="font-mono">
            <span className="text-[10px] text-text-muted uppercase tracking-wider flex items-center space-x-1 mb-1.5">
              <Award className="w-3 h-3 text-text-muted" />
              <span>PREFERRED QUALIFICATIONS &amp; TRAITS · {allPreferred.length}</span>
            </span>
            <div className="flex flex-wrap gap-1.5">
              {allPreferred.map((item, idx) => (
                <span
                  key={idx}
                  className="px-2.5 py-1 text-xs text-text-secondary bg-transparent border border-border/60 rounded"
                >
                  {item}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="mt-4 pt-3 border-t border-border/60 flex items-center justify-between text-[10px] text-text-muted font-mono uppercase">
        <span>SPECIFICATION DECOMPOSED</span>
        <span>READY FOR CANDIDATES</span>
      </div>
    </div>
  );
}
