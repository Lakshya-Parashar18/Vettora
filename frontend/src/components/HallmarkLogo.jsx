export default function HallmarkLogo({ size = 32, className = '' }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 40 40"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={`shrink-0 ${className}`}
      aria-hidden="true"
    >
      {/* Outer Hallmark Ring */}
      <circle cx="20" cy="20" r="18.25" stroke="var(--accent)" strokeWidth="1.25" />
      {/* Inner Dash Ring */}
      <circle
        cx="20"
        cy="20"
        r="14.75"
        stroke="var(--accent)"
        strokeWidth="0.75"
        strokeDasharray="2 1.5"
      />
      {/* Centered Monogram "V" in Fraunces */}
      <text
        x="20"
        y="25.5"
        textAnchor="middle"
        fill="var(--accent)"
        fontFamily="Fraunces, serif"
        fontSize="17"
        fontWeight="500"
      >
        V
      </text>
    </svg>
  );
}
