import { Briefcase, BookOpen, FolderGit2, Award } from 'lucide-react';

export default function CandidateResumeTimeline({ resume }) {
  if (!resume) return null;

  const experience = resume.experience || [];
  const education = resume.education || [];
  const projects = resume.projects || [];
  const certifications = resume.certifications || [];

  return (
    <div className="space-y-6 font-sans">
      {/* 1. Experience Timeline */}
      <div className="bg-bg-surface border border-border rounded-lg p-5 space-y-4">
        <h3 className="text-xs font-mono uppercase tracking-wider text-text-muted flex items-center space-x-2">
          <Briefcase className="w-3.5 h-3.5 text-accent" />
          <span>WORK EXPERIENCE RECORD ({experience.length})</span>
        </h3>

        {experience.length > 0 ? (
          <div className="space-y-4 relative before:absolute before:inset-0 before:left-2 before:w-px before:bg-border/60">
            {experience.map((exp, idx) => {
              const title = exp.job_title || 'Position';
              const company = exp.company || 'Company not specified';
              const dates =
                exp.start_date || exp.end_date
                  ? `${exp.start_date || 'N/A'} — ${exp.end_date || 'Present'}`
                  : 'Dates not specified';

              return (
                <div key={idx} className="relative pl-6 space-y-1">
                  <div className="absolute left-1 top-1.5 h-2 w-2 rounded-full bg-accent shrink-0" />
                  
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between">
                    <h4 className="text-xs font-medium text-text-primary">{title}</h4>
                    <span className="text-[11px] font-mono text-text-muted">{dates}</span>
                  </div>

                  <p className="text-xs font-mono text-accent">{company}</p>

                  {exp.description && (
                    <p className="text-xs text-text-secondary leading-relaxed pt-1">
                      {exp.description}
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        ) : (
          <p className="text-xs text-text-muted italic">No work experience entries listed.</p>
        )}
      </div>

      {/* 2. Education Section */}
      <div className="bg-bg-surface border border-border rounded-lg p-5 space-y-4">
        <h3 className="text-xs font-mono uppercase tracking-wider text-text-muted flex items-center space-x-2">
          <BookOpen className="w-3.5 h-3.5 text-accent" />
          <span>EDUCATION CREDENTIALS ({education.length})</span>
        </h3>

        {education.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {education.map((edu, idx) => {
              const degree = edu.degree || 'Degree';
              const field = edu.field ? `in ${edu.field}` : '';
              const inst = edu.institution || 'Institution not specified';
              const years =
                edu.start_year || edu.end_year
                  ? `${edu.start_year || ''} — ${edu.end_year || ''}`
                  : '';

              return (
                <div
                  key={idx}
                  className="bg-bg-base border border-border/60 rounded p-3.5 space-y-1"
                >
                  <h4 className="text-xs font-medium text-text-primary">
                    {degree} {field}
                  </h4>
                  <p className="text-xs text-accent font-mono">{inst}</p>
                  {years && <p className="text-[11px] font-mono text-text-muted">{years}</p>}
                </div>
              );
            })}
          </div>
        ) : (
          <p className="text-xs text-text-muted italic">No education entries listed.</p>
        )}
      </div>

      {/* 3. Projects Section */}
      {projects.length > 0 && (
        <div className="bg-bg-surface border border-border rounded-lg p-5 space-y-4">
          <h3 className="text-xs font-mono uppercase tracking-wider text-text-muted flex items-center space-x-2">
            <FolderGit2 className="w-3.5 h-3.5 text-accent" />
            <span>NOTABLE PROJECTS ({projects.length})</span>
          </h3>

          <div className="space-y-3">
            {projects.map((proj, idx) => (
              <div
                key={idx}
                className="bg-bg-base border border-border/60 rounded p-3.5 space-y-1.5"
              >
                <h4 className="text-xs font-medium text-text-primary">
                  {proj.name || 'Project'}
                </h4>
                {proj.description && (
                  <p className="text-xs text-text-secondary leading-relaxed">{proj.description}</p>
                )}
                {proj.technologies?.length > 0 && (
                  <div className="flex flex-wrap gap-1 pt-1 font-mono text-[10px]">
                    {proj.technologies.map((tech, tIdx) => (
                      <span
                        key={tIdx}
                        className="px-2 py-0.5 bg-bg-surface text-text-secondary border border-border rounded"
                      >
                        {tech}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 4. Certifications Section */}
      <div className="bg-bg-surface border border-border rounded-lg p-5 space-y-3">
        <h3 className="text-xs font-mono uppercase tracking-wider text-text-muted flex items-center space-x-2">
          <Award className="w-3.5 h-3.5 text-accent" />
          <span>CERTIFICATIONS ({certifications.length})</span>
        </h3>

        {certifications.length > 0 ? (
          <div className="flex flex-wrap gap-2 font-mono text-xs">
            {certifications.map((cert, idx) => (
              <span
                key={idx}
                className="px-2.5 py-1 text-xs text-text-primary bg-bg-base border border-border rounded"
              >
                {cert}
              </span>
            ))}
          </div>
        ) : (
          <p className="text-xs text-text-muted italic">No certifications listed.</p>
        )}
      </div>
    </div>
  );
}
