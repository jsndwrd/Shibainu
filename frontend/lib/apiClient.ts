const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL;

type ApiFetchOptions = RequestInit & {
  token?: string | null;
};

export async function apiFetch<T>(
  route: string,
  options: ApiFetchOptions = {},
): Promise<T> {
  if (!apiBaseUrl) {
    throw new Error("NEXT_PUBLIC_API_URL belum diatur.");
  }

  const { token, headers, ...restOptions } = options;

  const response = await fetch(`${apiBaseUrl}${route}`, {
    ...restOptions,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
  });

  const text = await response.text();
  const data = text ? JSON.parse(text) : null;

  if (!response.ok) {
    throw new Error(
      data?.detail ||
        data?.message ||
        `Permintaan gagal dengan status ${response.status}`,
    );
  }

  return data as T;
}
