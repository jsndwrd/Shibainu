export function getBriefTitle(content: unknown, fallback = "Policy Brief") {
  if (!content) return fallback;

  const text =
    typeof content === "string" ? content : JSON.stringify(content, null, 2);

  const lines = text.split("\n");

  const heading = lines.find((line) => line.trim().startsWith("# "));

  if (!heading) return fallback;

  return heading
    .replace(/^#\s*/, "")
    .replace(/^Policy Brief:\s*/i, "")
    .trim();
}
