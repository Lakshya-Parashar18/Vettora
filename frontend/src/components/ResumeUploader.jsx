import { useRef, useState } from 'react';
import { Upload, AlertTriangle, X } from 'lucide-react';

const MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024;
const ALLOWED_EXTENSIONS = ['.pdf', '.txt', '.doc', '.docx'];
const ALLOWED_MIME_TYPES = [
  'application/pdf',
  'text/plain',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
];

const SAMPLE_POOLS = [
  // Pool 1: Full-Stack & Core Web Systems
  [
    {
      name: 'aarav_sharma_senior_fullstack.txt',
      content: `Aarav Sharma
Email: aarav.sharma@example.com | Phone: +91 98765 43210 | Location: Bengaluru, India

PROFESSIONAL SUMMARY
Senior Full Stack Engineer with 6 years of experience building high-performance web applications, scalable microservices, and database systems using React, TypeScript, Python, and FastAPI.

WORK EXPERIENCE
Senior Full Stack Engineer | CloudTech Solutions, Bengaluru (July 2021 - Present)
- Architected modular React 18 frontend dashboard serving 100,000+ monthly active recruiters.
- Implemented high-throughput Python FastAPI microservices handling 2,000 requests/sec with MongoDB.
- Reduced API response latency by 45% using Redis caching and asynchronous query execution.

Software Engineer | Apex Systems, Hyderabad (June 2018 - June 2021)
- Developed responsive web interfaces using React, Redux, and Tailwind CSS.
- Built RESTful endpoints using Python and Flask for candidate tracking and authentication.
- Managed PostgreSQL schemas, written complex SQL queries, and setup Docker CI/CD pipelines.

TECHNICAL SKILLS
- Languages & Frameworks: React, JavaScript, TypeScript, Python, FastAPI, Node.js, Express, HTML5, CSS3, Tailwind CSS
- Databases & Tools: MongoDB, PostgreSQL, Docker, Git, REST APIs, PyTest

EDUCATION
Master of Technology (M.Tech) in Computer Science | IIT Delhi (2018)
Bachelor of Technology (B.Tech) in Computer Science | BITS Pilani (2016)`,
    },
    {
      name: 'ananya_iyer_frontend_lead.txt',
      content: `Ananya Iyer
Email: ananya.iyer@example.com | Phone: +91 98123 45678 | Location: Pune, India

SUMMARY
Frontend Specialist with 4 years of experience building accessible, pixel-perfect user interfaces with React, JavaScript, TypeScript, and modern CSS architecture.

EXPERIENCE
Frontend Developer | WebVibe Studios, Pune (Jan 2022 - Present)
- Built interactive client dashboards with React 18, Next.js, and Tailwind CSS.
- Improved Lighthouse performance scores from 65 to 98 across 15 production web pages.
- Collaborated with UI/UX designers to implement design systems and responsive components.

Junior Web Developer | DevCorp Tech, Mumbai (May 2020 - Dec 2021)
- Developed reusable UI components using JavaScript (ES6+), HTML5, and CSS3.
- Integrated third-party REST APIs into single-page web applications.

SKILLS
- Core Skills: React, JavaScript, TypeScript, HTML/CSS, Tailwind CSS, Redux, Vite
- Tools: Git, Webpack, Figma, Jest

EDUCATION
Bachelor of Engineering (B.E.) in Information Technology | Pune University (2020)`,
    },
    {
      name: 'vikram_patel_junior_backend.txt',
      content: `Vikram Patel
Email: vikram.patel@example.com | Phone: +91 97234 56789 | Location: Ahmedabad, India

OBJECTIVE
Motivated Associate Software Developer with 1 year of internship experience seeking a position to apply Python, Django, REST API, and basic SQL knowledge.

WORK EXPERIENCE
Software Developer Intern | DataStart Inc, Ahmedabad (June 2023 - Present)
- Assisted backend team with Python bug fixes, Django model migrations, and API documentation updates.
- Wrote unit tests and maintained internal technical documentation.

EDUCATION
Bachelor of Technology (B.Tech) in Information Technology | GTU Ahmedabad (2023)

SKILLS
- Programming: Python, Django, REST API, Basic SQL, HTML/CSS, Git`,
    },
  ],

  // Pool 2: Cloud, DevOps & Infrastructure Systems
  [
    {
      name: 'rohan_verma_devops_architect.txt',
      content: `Rohan Verma
Email: rohan.verma@example.com | Phone: +91 99887 65432 | Location: Gurugram, India

PROFESSIONAL SUMMARY
DevOps Infrastructure Architect with 5 years of experience managing multi-cluster Kubernetes on AWS, Terraform automation, and CI/CD pipelines.

EXPERIENCE
DevOps Lead | InfraCloud Systems, Gurugram (Aug 2021 - Present)
- Managed production Kubernetes (EKS) clusters on AWS serving 5M+ daily requests.
- Built automated Terraform modules and Helm charts for zero-downtime microservice deployments.
- Implemented Prometheus & Grafana monitoring stack with 99.99% system availability.

Cloud Engineer | CyberNet Solutions, Noida (Feb 2019 - July 2021)
- Automated deployment pipelines using GitHub Actions, Docker, and Shell scripting.
- Configured AWS VPC, EC2, IAM, and Security Groups following cloud best practices.

SKILLS
- Cloud & DevOps: AWS, Kubernetes, Terraform, Docker, CI/CD, Helm, Linux, Python, Bash
- Databases: PostgreSQL, Redis, MongoDB

EDUCATION
B.Tech in Computer Science | NIT Trichy (2019)`,
    },
    {
      name: 'neha_kulkarni_backend_engineer.txt',
      content: `Neha Kulkarni
Email: neha.kulkarni@example.com | Phone: +91 98450 12345 | Location: Hyderabad, India

SUMMARY
Backend Engineer with 3 years of experience developing RESTful APIs, async task pipelines, and database optimizations using Python, FastAPI, and PostgreSQL.

EXPERIENCE
Backend Developer | NexaTech, Hyderabad (Oct 2021 - Present)
- Developed FastAPI backend endpoints processing 500k daily database transactions.
- Integrated Celery & Redis task queues for background async processing.
- Optimized SQL query execution plans, reducing database latency by 35%.

SKILLS
- Backend: Python, FastAPI, Django, PostgreSQL, Redis, REST APIs, PyTest, Docker

EDUCATION
B.Tech in Computer Science | IIIT Hyderabad (2021)`,
    },
    {
      name: 'siddharth_rao_fullstack_dev.txt',
      content: `Siddharth Rao
Email: siddharth.rao@example.com | Phone: +91 97112 34567 | Location: Bengaluru, India

SUMMARY
Full Stack Developer with 2 years of experience building modern web applications with React, Node.js, Express, and MongoDB.

EXPERIENCE
Software Engineer | CodeCraft, Bengaluru (May 2022 - Present)
- Developed responsive web portals using React, JavaScript, and Tailwind CSS.
- Implemented Node.js / Express REST microservices with JWT authentication.

SKILLS
- Web Dev: React, Node.js, Express, JavaScript, MongoDB, HTML5, CSS3, Git

EDUCATION
B.E. in Computer Science | RVCE Bengaluru (2022)`,
    },
  ],

  // Pool 3: AI / ML & Data Engineering Focus
  [
    {
      name: 'kavya_nair_ai_ml_lead.txt',
      content: `Kavya Nair
Email: kavya.nair@example.com | Phone: +91 99001 12233 | Location: Bengaluru, India

PROFESSIONAL SUMMARY
Senior AI / ML Engineer with 5 years of experience building LLM fine-tuning, RAG semantic search pipelines, and vector database architectures using PyTorch, Python, and FastAPI.

EXPERIENCE
Lead ML Engineer | AI Dynamics, Bengaluru (Nov 2020 - Present)
- Designed Retrieval-Augmented Generation (RAG) system with Pinecone vector database and Gemini API.
- Deployed scalable PyTorch inference endpoints using FastAPI and Docker on AWS.
- Fine-tuned transformer models on domain datasets, improving response accuracy by 28%.

AI Developer | DeepMind Analytics, Chennai (July 2019 - Oct 2020)
- Implemented NLP preprocessing and feature engineering pipelines in Python and Pandas.

SKILLS
- AI & ML: Python, PyTorch, Transformers, LLMs, RAG, LangChain, Vector DBs, FastAPI, Docker, AWS

EDUCATION
M.Tech in Artificial Intelligence | IISc Bangalore (2019)
B.Tech in CS | Anna University (2017)`,
    },
    {
      name: 'aditya_deshmukh_data_scientist.txt',
      content: `Aditya Deshmukh
Email: aditya.deshmukh@example.com | Phone: +91 98334 55667 | Location: Mumbai, India

SUMMARY
Data Scientist with 3 years of experience in statistical analysis, predictive modeling, and Python data pipelines.

EXPERIENCE
Data Scientist | FinAnalytics, Mumbai (Jan 2022 - Present)
- Built classification and regression models using Python, Scikit-Learn, and XGBoost.
- Automated data processing pipelines using Pandas, NumPy, and SQL.

SKILLS
- Data Science: Python, SQL, Pandas, NumPy, Scikit-Learn, Statistics, Git

EDUCATION
B.E. in Computer Engineering | VJTI Mumbai (2021)`,
    },
    {
      name: 'pooja_gupta_software_intern.txt',
      content: `Pooja Gupta
Email: pooja.gupta@example.com | Phone: +91 97554 32100 | Location: New Delhi, India

OBJECTIVE
Junior Associate Engineer with 1 year of hands-on experience in Java, Python, and web fundamentals.

EXPERIENCE
Software Intern | TechStart, New Delhi (June 2023 - Present)
- Wrote unit tests in JUnit and Python pytest framework for backend modules.

SKILLS
- Languages: Java, Python, HTML, CSS, SQL, Git

EDUCATION
B.Tech in CS | DTU Delhi (2023)`,
    },
  ],

  // Pool 4: Cloud Architecture & High-Scale Backend
  [
    {
      name: 'devansh_mehta_principal_architect.txt',
      content: `Devansh Mehta
Email: devansh.mehta@example.com | Phone: +91 99665 44332 | Location: Mumbai, India

PROFESSIONAL SUMMARY
Senior Backend Architect with 7 years of experience engineering high-scale distributed microservices, database architectures, and cloud platforms using Python, FastAPI, PostgreSQL, and Docker.

EXPERIENCE
Principal Backend Engineer | FinTech Infra, Mumbai (March 2020 - Present)
- Led backend engineering team building high-throughput financial transaction processing engine in Python.
- Designed database schemas and connection pooling for PostgreSQL & Redis handling 10,000 queries/sec.

Senior Software Engineer | Enterprise Cloud, Pune (June 2017 - Feb 2020)
- Built REST microservices using Python FastAPI and Flask with MongoDB persistence.

SKILLS
- Core Tech: Python, FastAPI, Django, PostgreSQL, Redis, MongoDB, Microservices, Docker, AWS, System Design

EDUCATION
B.Tech in Computer Science | IIT Bombay (2017)`,
    },
    {
      name: 'rhea_kapoor_frontend_engineer.txt',
      content: `Rhea Kapoor
Email: rhea.kapoor@example.com | Phone: +91 98776 55443 | Location: Bengaluru, India

SUMMARY
UI/UX Frontend Engineer with 4 years of experience crafting modern, accessible web interfaces in React, TypeScript, Next.js, and Tailwind CSS.

EXPERIENCE
Senior Frontend Developer | PixelCraft, Bengaluru (Jan 2021 - Present)
- Developed reusable component design system in React 18 and Storybook.
- Optimized client bundle sizes by 40% through code splitting and tree shaking.

SKILLS
- Frontend: React, TypeScript, Next.js, Redux, Tailwind CSS, HTML5, CSS3, Jest

EDUCATION
B.Tech in Information Technology | Manipal University (2020)`,
    },
    {
      name: 'tarun_malhotra_devops_associate.txt',
      content: `Tarun Malhotra
Email: tarun.malhotra@example.com | Phone: +91 96543 21098 | Location: Noida, India

OBJECTIVE
DevOps Engineer with 1 year of experience in Linux server management, Docker containerization, and Git CI/CD scripting.

EXPERIENCE
DevOps Trainee | CloudLabs, Noida (July 2023 - Present)
- Maintained Docker build scripts and Linux deployment server configurations.

SKILLS
- Infrastructure: Linux, Bash, Docker, Git, Python, Basic AWS

EDUCATION
B.Tech in CS | Amity University (2023)`,
    },
  ],
];

export default function ResumeUploader({ onFilesSelected, validationError, setValidationError }) {
  const fileInputRef = useRef(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [poolIndex, setPoolIndex] = useState(0);

  const handleLoadSampleResumes = (e) => {
    e.stopPropagation();
    setValidationError(null);
    const activePool = SAMPLE_POOLS[poolIndex % SAMPLE_POOLS.length];
    const files = activePool.map(
      (item) => new File([item.content], item.name, { type: 'text/plain' })
    );
    setPoolIndex((prev) => prev + 1);
    onFilesSelected(files);
  };

  const validateFiles = (fileList) => {
    const validFiles = [];
    const errors = [];

    Array.from(fileList).forEach((file) => {
      const extension = '.' + file.name.split('.').pop().toLowerCase();
      const isValidType = ALLOWED_EXTENSIONS.includes(extension) || ALLOWED_MIME_TYPES.includes(file.type);
      const isValidSize = file.size <= MAX_FILE_SIZE_BYTES;

      if (!isValidType) {
        errors.push(`"${file.name}" format unsupported. Upload PDF, TXT, DOC, or DOCX files.`);
      } else if (!isValidSize) {
        errors.push(`"${file.name}" exceeds 5MB size limit.`);
      } else {
        validFiles.push(file);
      }
    });

    if (errors.length > 0) {
      setValidationError(errors.join(' '));
    } else {
      setValidationError(null);
    }

    if (validFiles.length > 0) {
      onFilesSelected(validFiles);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateFiles(e.dataTransfer.files);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      validateFiles(e.target.files);
      e.target.value = '';
    }
  };

  return (
    <div className="flex flex-col font-sans">
      {/* Requirement 3: 1px dashed border switching to solid --accent border on drag-over */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        tabIndex={0}
        role="button"
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            fileInputRef.current?.click();
          }
        }}
        aria-label="Upload PDF or TXT resumes"
        className={`relative rounded p-6 sm:p-8 text-center cursor-pointer transition-colors font-mono text-xs bg-bg-surface ${
          isDragOver
            ? 'border border-solid border-accent text-accent'
            : 'border border-dashed border-border hover:border-border-strong text-text-secondary'
        }`}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept=".pdf,.txt,.doc,.docx,application/pdf,text/plain,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          multiple
          className="hidden"
          id="resume-file-input"
        />

        <div className="flex flex-col items-center justify-center space-y-3">
          <Upload className="w-6 h-6 text-accent" />

          <div>
            <p className="text-xs font-medium text-text-primary">
              <span className="text-accent font-medium">Upload resumes to begin</span> — Vettora reads PDF, DOC, DOCX, and TXT.
            </p>
            <p className="text-[11px] text-text-muted mt-1">
              Drag &amp; drop files or click to browse (Max 5MB each)
            </p>
          </div>

          <div className="flex items-center space-x-3 text-[10px] text-text-muted pt-1">
            <span>MULTIPLE RESUMES PERMITTED</span>
            <span>•</span>
            <span>AUTOMATIC TEXT EXTRACTION</span>
          </div>

          <div className="pt-2">
            <button
              type="button"
              onClick={handleLoadSampleResumes}
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 bg-bg-base border border-accent/40 text-accent hover:bg-accent/15 rounded transition-colors text-xs font-mono font-medium"
              title="Auto-load 3 candidate resumes for instant 1-click screening demo"
            >
              <img
                src="https://img.icons8.com/pulsar-line/48/lightning-bolt.png"
                alt="Lightning icon"
                className="w-3.5 h-3.5 object-contain shrink-0 icon-theme-adaptive"
              />
              <span>LOAD SAMPLE BATCH #{ (poolIndex % SAMPLE_POOLS.length) + 1 } (1-CLICK DEMO)</span>
            </button>
          </div>
        </div>
      </div>

      {validationError && (
        <div className="mt-3 bg-bg-surface border border-[var(--danger-muted)]/40 rounded p-3 text-xs font-mono text-[var(--danger-muted)] flex items-start justify-between">
          <div className="flex items-start space-x-2">
            <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
            <p className="leading-normal">{validationError}</p>
          </div>
          <button
            type="button"
            onClick={() => setValidationError(null)}
            className="text-[var(--danger-muted)] p-0.5 ml-2 rounded"
            aria-label="Dismiss error"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      )}
    </div>
  );
}
