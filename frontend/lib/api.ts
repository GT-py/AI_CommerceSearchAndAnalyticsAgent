import type {
  Category,
  Product,
  ProductListResponse,
  ProductPayload,
  ProductQuery,
} from "@/types/product";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

type ApiFetchOptions = RequestInit & {
  token?: string | null;
};

type ValidationDetail = {
  msg?: string;
  message?: string;
};

function detailToMessage(detail: unknown, fallback: string): string {
  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    const messages = detail
      .map((item: ValidationDetail) => item.msg ?? item.message)
      .filter(Boolean);

    if (messages.length > 0) {
      return messages.join(" / ");
    }
  }

  return fallback;
}

export async function apiFetch<T>(path: string, options: ApiFetchOptions = {}): Promise<T> {
  const { token, ...requestOptions } = options;
  const headers = new Headers(requestOptions.headers);
  headers.set("Accept", "application/json");

  if (requestOptions.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...requestOptions,
    headers,
    cache: requestOptions.cache ?? "no-store",
  });

  if (!response.ok) {
    const fallback = `Request failed with status ${response.status}`;
    let message = fallback;

    try {
      const body = (await response.json()) as { detail?: unknown; message?: unknown };
      message = detailToMessage(body.detail ?? body.message, fallback);
    } catch {
      message = response.statusText || fallback;
    }

    throw new ApiError(message, response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export function buildQueryString(params: Record<string, string | number | null | undefined>) {
  const searchParams = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      searchParams.set(key, String(value));
    }
  });

  const query = searchParams.toString();
  return query ? `?${query}` : "";
}

export function getProducts(query: ProductQuery = {}, token?: string | null) {
  return apiFetch<ProductListResponse>(`/products${buildQueryString(query)}`, { token });
}

export function getProduct(productId: number) {
  return apiFetch<Product>(`/products/${productId}`);
}

export function getCategories() {
  return apiFetch<Category[]>("/categories");
}

export function createProduct(payload: ProductPayload, token: string) {
  return apiFetch<Product>("/admin/products", {
    method: "POST",
    body: JSON.stringify(payload),
    token,
  });
}

export function updateProduct(productId: number, payload: ProductPayload, token: string) {
  return apiFetch<Product>(`/admin/products/${productId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
    token,
  });
}

export function deleteProduct(productId: number, token: string) {
  return apiFetch<{ message: string }>(`/admin/products/${productId}`, {
    method: "DELETE",
    token,
  });
}
