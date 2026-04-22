export function useTooltipStyle() {
  const css = typeof window !== "undefined" ? getComputedStyle(document.documentElement) : null;
  const get = (v, fb) => css ? (css.getPropertyValue(v).trim() || fb) : fb;
  return {
    contentStyle: {
      background: get("--tooltip-bg", "#10141b"),
      border: `1px solid ${get("--border", "#1f2633")}`,
      borderRadius: 6,
      color: get("--text", "#e6e8ed"),
      fontSize: 11,
      fontFamily: "Inter, sans-serif",
      padding: "8px 10px",
    },
  };
}
