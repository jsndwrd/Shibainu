const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

type ApiFetchOptions = RequestInit & {
  token?: string | null;
};

function getStoredToken(): string | null {
  if (typeof window === "undefined") return null;

  return (
    localStorage.getItem("token") ||
    localStorage.getItem("access_token") ||
    null
  );
}

export async function apiFetch<T>(
  route: string,
  options: ApiFetchOptions = {},
): Promise<T> {
  if (!API_BASE_URL) {
    throw new Error("NEXT_PUBLIC_API_URL belum diatur.");
  }

  const { token, headers, ...restOptions } = options;
  const activeToken = token ?? getStoredToken();

  const response = await fetch(`${API_BASE_URL}${route}`, {
    ...restOptions,
    headers: {
      "Content-Type": "application/json",
      ...(activeToken ? { Authorization: `Bearer ${activeToken}` } : {}),
      ...headers,
    },
  });

  const text = await response.text();
  const data = text ? JSON.parse(text) : null;

  if (!response.ok) {
    throw new Error(
      data?.detail ||
        data?.message ||
        `Request gagal dengan status ${response.status}`,
    );
  }

  return data as T;
}
