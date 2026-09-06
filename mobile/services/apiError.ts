export type ApiErrorKind = "network" | "timeout" | "http";

export class ApiError extends Error {
  kind: ApiErrorKind;
  status?: number;
  url: string;
  baseUrl: string;

  constructor(opts: {
    kind: ApiErrorKind;
    url: string;
    baseUrl: string;
    status?: number;
    message: string;
  }) {
    super(opts.message);
    this.name = "ApiError";
    this.kind = opts.kind;
    this.url = opts.url;
    this.baseUrl = opts.baseUrl;
    this.status = opts.status;
  }

  get isOffline(): boolean {
    return this.kind === "network" || this.kind === "timeout";
  }
}

export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError;
}

export function toUserMessage(error: unknown): { title: string; message: string } {
  if (isApiError(error)) {
    if (error.kind === "network") {
      return {
        title: "Backend offline",
        message: `Can't reach the server. Is the backend running?`,
      };
    }
    if (error.kind === "timeout") {
      return {
        title: "Request timed out",
        message: "The server took too long to respond. Check your connection and try again.",
      };
    }
    if (error.status === 404) {
      return {
        title: "Not found",
        message: error.message || "The requested item was not found.",
      };
    }
    return {
      title: "Server error",
      message: error.message || "Something went wrong on the server. Please try again.",
    };
  }
  if (error instanceof Error) {
    return { title: "Something went wrong", message: error.message };
  }
  return { title: "Something went wrong", message: "An unexpected error occurred. Please try again." };
}
