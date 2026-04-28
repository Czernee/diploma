import type { ProblemDetail } from "../types";

export class ApiError extends Error {
  status: number;
  problem: ProblemDetail | null;

  constructor(status: number, message: string, problem: ProblemDetail | null = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.problem = problem;
  }
}

type RequestOptions = {
  method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  token?: string;
  body?: unknown;
};

function formatStructuredDetail(detail: Record<string, unknown>): string {
  const message = typeof detail.message === "string" ? detail.message : null;
  const minimum = typeof detail.minimumRequiredBudget === "number" ? detail.minimumRequiredBudget : null;
  const provided = typeof detail.providedBudget === "number" ? detail.providedBudget : null;

  if (message && minimum !== null && provided !== null) {
    return `${message}. Минимальный бюджет: ${minimum} RUB, указанный: ${provided} RUB.`;
  }

  if (message) {
    return message;
  }

  return Object.entries(detail)
    .map(([key, value]) => `${key}: ${String(value)}`)
    .join(", ");
}

function extractProblemMessage(problem: ProblemDetail | null, status: number): string {
  const detail = problem?.detail;

  if (typeof detail === "string" && detail.trim().length > 0) {
    return detail;
  }

  if (detail && typeof detail === "object" && !Array.isArray(detail)) {
    return formatStructuredDetail(detail as Record<string, unknown>);
  }

  if (typeof problem?.title === "string" && problem.title.trim().length > 0) {
    return problem.title;
  }

  return `Ошибка запроса (статус ${status})`;
}

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers: HeadersInit = {
    Accept: "application/json"
  };

  if (options.body !== undefined) {
    headers["Content-Type"] = "application/json";
  }

  if (options.token) {
    headers.Authorization = `Bearer ${options.token}`;
  }

  const response = await fetch(path, {
    method: options.method ?? "GET",
    headers,
    body: options.body !== undefined ? JSON.stringify(options.body) : undefined
  });

  if (!response.ok) {
    let problem: ProblemDetail | null = null;
    try {
      problem = (await response.json()) as ProblemDetail;
    } catch {
      problem = null;
    }
    const message = extractProblemMessage(problem, response.status);
    throw new ApiError(response.status, message, problem);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}
