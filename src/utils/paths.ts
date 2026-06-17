export function withBase(path: string): string {
  if (
    !path ||
    path.startsWith("http://") ||
    path.startsWith("https://") ||
    path.startsWith("mailto:") ||
    path.startsWith("tel:") ||
    path.startsWith("#")
  ) {
    return path;
  }

  const base = import.meta.env.BASE_URL || "/";
  if (base === "/") {
    return path;
  }

  const cleanBase = base.endsWith("/") ? base.slice(0, -1) : base;
  if (path === "/") {
    return `${cleanBase}/`;
  }

  return path.startsWith("/") ? `${cleanBase}${path}` : `${cleanBase}/${path}`;
}

export function withoutBase(path: string): string {
  const base = import.meta.env.BASE_URL || "/";
  const cleanBase = base.endsWith("/") ? base.slice(0, -1) : base;

  if (cleanBase !== "/" && path.startsWith(cleanBase)) {
    return path.slice(cleanBase.length) || "/";
  }

  return path;
}
