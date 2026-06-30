import type { SQLAgentQueryRequest, SQLAgentQueryResponse } from "@/types/sqlAgent";
import type {
  Category,
  Product,
  ProductListResponse,
  ProductPayload,
  ProductQuery,
} from "@/types/product";
import type {
  AnalyticsSummary,
  AssistantFeedbackAnalyticsResponse,
  ProductAnalyticsResponse,
  SearchKeywordAnalyticsResponse,
} from "@/types/analytics";
import type {
  AIEvaluationListResponse,
  AssistantChatRequest,
  AssistantChatResponse,
  AssistantFeedbackRequest,
  AssistantFeedbackResponse,
} from "@/types/assistant";
import type {
  ClickLogListResponse,
  ClickLogResponse,
  ClickSource,
  FavoriteListResponse,
  SearchLogListResponse,
} from "@/types/log";

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

export function getFavorites(token: string) {
  return apiFetch<FavoriteListResponse>("/favorites", { token });
}

export function addFavorite(productId: number, token: string) {
  return apiFetch<FavoriteListResponse["items"][number]>(`/favorites/${productId}`, {
    method: "POST",
    token,
  });
}

export function removeFavorite(productId: number, token: string) {
  return apiFetch<{ message: string }>(`/favorites/${productId}`, {
    method: "DELETE",
    token,
  });
}

export function createClickLog(productId: number, source: ClickSource, token?: string | null) {
  return apiFetch<ClickLogResponse>("/logs/click", {
    method: "POST",
    body: JSON.stringify({ product_id: productId, source }),
    token,
  });
}

export function getAdminSearchLogs(query: { page?: number; limit?: number }, token: string) {
  return apiFetch<SearchLogListResponse>(`/admin/logs/search${buildQueryString(query)}`, { token });
}

export function getAdminClickLogs(query: { page?: number; limit?: number }, token: string) {
  return apiFetch<ClickLogListResponse>(`/admin/logs/clicks${buildQueryString(query)}`, { token });
}

export function chatWithAssistant(payload: AssistantChatRequest, token?: string | null) {
  return apiFetch<AssistantChatResponse>("/assistant/chat", {
    method: "POST",
    body: JSON.stringify(payload),
    token,
  });
}

export function sendAssistantFeedback(payload: AssistantFeedbackRequest, token?: string | null) {
  return apiFetch<AssistantFeedbackResponse>("/assistant/feedback", {
    method: "POST",
    body: JSON.stringify(payload),
    token,
  });
}

export function getAdminEvaluations(query: { page?: number; limit?: number }, token: string) {
  return apiFetch<AIEvaluationListResponse>(`/admin/evaluations${buildQueryString(query)}`, { token });
}


export function getAdminAnalyticsSummary(token: string) {
  return apiFetch<AnalyticsSummary>("/admin/analytics/summary", { token });
}

export function getAdminAnalyticsSearchKeywords(
  query: { from_date?: string; to_date?: string; limit?: number },
  token: string,
) {
  return apiFetch<SearchKeywordAnalyticsResponse>(
    `/admin/analytics/search-keywords${buildQueryString(query)}`,
    { token },
  );
}

export function getAdminAnalyticsProducts(query: { limit?: number }, token: string) {
  return apiFetch<ProductAnalyticsResponse>(`/admin/analytics/products${buildQueryString(query)}`, { token });
}

export function getAdminAnalyticsAssistantFeedback(query: { recent_limit?: number }, token: string) {
  return apiFetch<AssistantFeedbackAnalyticsResponse>(
    `/admin/analytics/assistant-feedback${buildQueryString(query)}`,
    { token },
  );
}


export function querySqlAgent(payload: SQLAgentQueryRequest, token: string) {
  return apiFetch<SQLAgentQueryResponse>("/admin/sql-agent/query", {
    method: "POST",
    body: JSON.stringify(payload),
    token,
  });
}
