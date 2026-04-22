const b = { width:16, height:16, viewBox:"0 0 16 16", fill:"none", stroke:"currentColor", strokeWidth:1.5, strokeLinecap:"round", strokeLinejoin:"round" };

export const Icon = {
  Overview:   (p) => <svg {...b} {...p}><rect x="2" y="2" width="5" height="5" rx="1"/><rect x="9" y="2" width="5" height="5" rx="1"/><rect x="2" y="9" width="5" height="5" rx="1"/><rect x="9" y="9" width="5" height="5" rx="1"/></svg>,
  Upload:     (p) => <svg {...b} {...p}><path d="M8 10V2.5M4.5 6 8 2.5 11.5 6"/><path d="M2.5 10v2.5A1.5 1.5 0 0 0 4 14h8a1.5 1.5 0 0 0 1.5-1.5V10"/></svg>,
  Reconcile:  (p) => <svg {...b} {...p}><path d="M2 5h9M8 2.5 11 5 8 7.5"/><path d="M14 11H5M8 8.5 5 11l3 2.5"/></svg>,
  Calculator: (p) => <svg {...b} {...p}><rect x="3" y="2" width="10" height="12" rx="1.5"/><path d="M5.5 5h5M5.5 8.5h.01M8 8.5h.01M10.5 8.5h.01M5.5 11.5h.01M8 11.5h.01M10.5 11.5h.01"/></svg>,
  Document:   (p) => <svg {...b} {...p}><path d="M9 1.5H4a1.5 1.5 0 0 0-1.5 1.5v10A1.5 1.5 0 0 0 4 14.5h8a1.5 1.5 0 0 0 1.5-1.5V6"/><path d="M9 1.5 13.5 6H9z"/><path d="M5.5 9h5M5.5 11.5h3"/></svg>,
  Analytics:  (p) => <svg {...b} {...p}><path d="M2.5 13.5v-4M6 13.5v-8M9.5 13.5v-5M13 13.5v-10"/></svg>,
  Check:      (p) => <svg {...b} {...p}><path d="m3 8.5 3 3 7-7"/></svg>,
  Alert:      (p) => <svg {...b} {...p}><path d="M8 1.5 14.5 13h-13z"/><path d="M8 6v3M8 11.25h.005"/></svg>,
  Lock:       (p) => <svg {...b} {...p}><rect x="3" y="7" width="10" height="7" rx="1.5"/><path d="M5 7V5a3 3 0 0 1 6 0v2"/></svg>,
  Download:   (p) => <svg {...b} {...p}><path d="M8 2v8M4.5 6.5 8 10l3.5-3.5"/><path d="M2.5 12v1A1.5 1.5 0 0 0 4 14.5h8a1.5 1.5 0 0 0 1.5-1.5v-1"/></svg>,
  Play:       (p) => <svg {...b} {...p}><path d="M4.5 3v10l8-5z" fill="currentColor" stroke="none"/></svg>,
  ArrowUp:    (p) => <svg {...b} {...p}><path d="M8 13V3M4 7l4-4 4 4"/></svg>,
  ArrowDown:  (p) => <svg {...b} {...p}><path d="M8 3v10M4 9l4 4 4-4"/></svg>,
  ChevronDown:(p) => <svg {...b} {...p}><path d="m4 6 4 4 4-4"/></svg>,
  Database:   (p) => <svg {...b} {...p}><ellipse cx="8" cy="3.5" rx="5.5" ry="2"/><path d="M2.5 3.5v9c0 1.1 2.5 2 5.5 2s5.5-.9 5.5-2v-9M2.5 8c0 1.1 2.5 2 5.5 2s5.5-.9 5.5-2"/></svg>,
  Cpu:        (p) => <svg {...b} {...p}><rect x="4" y="4" width="8" height="8" rx="1"/><path d="M6 1.5v2M10 1.5v2M6 12.5v2M10 12.5v2M1.5 6h2M1.5 10h2M12.5 6h2M12.5 10h2"/></svg>,
  Pulse:      (p) => <svg {...b} {...p}><path d="M1.5 8h3l2-5 2 10 2-5h4"/></svg>,
  Search:     (p) => <svg {...b} {...p}><circle cx="7" cy="7" r="4.5"/><path d="m10.5 10.5 3 3"/></svg>,
  Sun:        (p) => <svg {...b} {...p}><circle cx="8" cy="8" r="3"/><path d="M8 1.5v1.5M8 13v1.5M1.5 8H3M13 8h1.5M3.2 3.2l1 1M11.8 11.8l1 1M3.2 12.8l1-1M11.8 4.2l1-1"/></svg>,
  Moon:       (p) => <svg {...b} {...p}><path d="M13.5 9.5A5.5 5.5 0 0 1 6.5 2.5a5.5 5.5 0 1 0 7 7z"/></svg>,
  File:       (p) => <svg {...b} {...p}><path d="M10 1.5H4a1.5 1.5 0 0 0-1.5 1.5v10A1.5 1.5 0 0 0 4 14.5h8a1.5 1.5 0 0 0 1.5-1.5V6L10 1.5z"/><path d="M10 1.5V6h4.5"/></svg>,
  Refresh:    (p) => <svg {...b} {...p}><path d="M13.5 8A5.5 5.5 0 1 1 10.5 3"/><path d="M10.5 1v2h2"/></svg>,
};

export function BrandMark({ size = 26 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 28 28" fill="none">
      <rect x="0.5" y="0.5" width="27" height="27" rx="6.5" fill="var(--ok-bg)" stroke="var(--ok-border)"/>
      <path d="M18.5 10.5a5 5 0 1 0 0 7" stroke="var(--accent)" strokeWidth="1.8" strokeLinecap="round" fill="none"/>
    </svg>
  );
}
