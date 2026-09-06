import { Platform } from "react-native";
import { API_BASE_URL } from "../constants/config";
import { ApiError } from "./apiError";

const REQUEST_TIMEOUT_MS = 15000;

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  getBaseUrl(): string {
    return this.baseUrl;
  }

  private toUrl(path: string): string {
    return `${this.baseUrl}${path}`;
  }

  private async parseErrorBody(response: Response, fallback: string): Promise<string> {
    const data = await response.json().catch(() => null);
    if (data && typeof (data as any).detail === "string" && (data as any).detail) {
      return (data as any).detail;
    }
    return fallback;
  }

  private async request<T>(path: string, options?: RequestInit): Promise<T> {
    const url = this.toUrl(path);
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

    // Allow caller-provided signal to still work by forwarding abort.
    if (options?.signal) {
      if (options.signal.aborted) controller.abort();
      else options.signal.addEventListener("abort", () => controller.abort(), { once: true });
    }

    let response: Response;
    try {
      response = await fetch(url, {
        headers: {
          "Content-Type": "application/json",
          ...options?.headers,
        },
        ...options,
        signal: controller.signal,
      });
    } catch (error: any) {
      if (error?.name === "AbortError") {
        throw new ApiError({
          kind: "timeout",
          url,
          baseUrl: this.baseUrl,
          message: `Request timed out: ${url}`,
        });
      }
      throw new ApiError({
        kind: "network",
        url,
        baseUrl: this.baseUrl,
        message: `Failed to fetch: ${url}. Is the backend running at ${this.baseUrl}?`,
      });
    } finally {
      clearTimeout(timeoutId);
    }

    if (!response.ok) {
      const detail = await this.parseErrorBody(response, "Request failed");
      throw new ApiError({
        kind: "http",
        url,
        baseUrl: this.baseUrl,
        status: response.status,
        message: detail || `HTTP ${response.status}`,
      });
    }

    return response.json();
  }

  async analyzeImage(imageUri: string, useSlm: boolean = false) {
    const formData = new FormData();
    const filename = imageUri.split("/").pop() || "photo.jpg";
    const match = /\.(\w+)$/.exec(filename);
    const type = match ? `image/${match[1]}` : "image/jpeg";

    // Web fetch requires a real Blob; the {uri,name,type} object only
    // works on native (Expo handles it there). Plain objects get
    // stringified to "[object Object]" on web and FastAPI 422s.
    if (Platform.OS === "web") {
      const blobRes = await fetch(imageUri);
      formData.append("image", await blobRes.blob(), filename);
    } else {
      formData.append("image", {
        uri: imageUri,
        name: filename,
        type,
      } as any);
    }
    formData.append("use_slm", String(useSlm));

    const url = this.toUrl("/api/analyze");
    const controller = new AbortController();
    // Image analysis (esp. with SLM) can take a while — own 120s timeout.
    const timeoutId = setTimeout(() => controller.abort(), 120000);

    let response: Response;
    try {
      // NOTE: do not set Content-Type manually for FormData — fetch sets the
      // multipart boundary automatically. Setting it breaks uploads.
      response = await fetch(url, {
        method: "POST",
        body: formData,
        signal: controller.signal,
      });
    } catch (error: any) {
      if (error?.name === "AbortError") {
        throw new ApiError({
          kind: "timeout",
          url,
          baseUrl: this.baseUrl,
          message: `Analysis timed out: ${url}`,
        });
      }
      throw new ApiError({
        kind: "network",
        url,
        baseUrl: this.baseUrl,
        message: `Failed to fetch: ${url}. Is the backend running at ${this.baseUrl}?`,
      });
    } finally {
      clearTimeout(timeoutId);
    }

    if (!response.ok) {
      const detail = await this.parseErrorBody(response, "Analysis failed");
      throw new ApiError({
        kind: "http",
        url,
        baseUrl: this.baseUrl,
        status: response.status,
        message: detail || `HTTP ${response.status}`,
      });
    }

    return response.json();
  }

  async getProducts(params: {
    search?: string;
    category?: string;
    skin_type?: string;
    sort_by?: string;
    page?: number;
    page_size?: number;
  } = {}): Promise<any> {
    const query = new URLSearchParams();
    if (params.search) query.set("search", params.search);
    if (params.category) query.set("category", params.category);
    if (params.skin_type) query.set("skin_type", params.skin_type);
    if (params.sort_by) query.set("sort_by", params.sort_by);
    if (params.page) query.set("page", String(params.page));
    if (params.page_size) query.set("page_size", String(params.page_size));

    const qs = query.toString();
    return this.request(`/api/products${qs ? `?${qs}` : ""}`);
  }

  async getProduct(productId: string): Promise<any> {
    return this.request(`/api/products/${encodeURIComponent(productId)}`);
  }

  async getAnalysis(analysisId: string): Promise<any> {
    return this.request(`/api/analysis/${encodeURIComponent(analysisId)}`);
  }

  async getCategories(): Promise<{ categories: string[] }> {
    return this.request("/api/products/categories");
  }

  async getConditions(): Promise<{ conditions: any[] }> {
    return this.request("/api/conditions");
  }

  async getCondition(name: string): Promise<any> {
    return this.request(`/api/conditions/${encodeURIComponent(name)}`);
  }

  async getSkinTypes(): Promise<{ skin_types: any[] }> {
    return this.request("/api/conditions/skin-types");
  }

  async sendChatMessage(message: string, history: { role: string; content: string }[] = [], context?: {
    condition?: string;
    skin_type?: string;
    is_medical?: boolean;
    product_ids?: string[];
    recommendations?: Record<string, any>;
  }): Promise<any> {
    // CPU SLM needs far longer than the 15s default — own 120s timeout.
    const url = this.toUrl("/api/chat");
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 120000);
    try {
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, history, context }),
        signal: controller.signal,
      });
      if (!response.ok) {
        const detail = await this.parseErrorBody(response, "Chat failed");
        throw new ApiError({ kind: "http", url, baseUrl: this.baseUrl, status: response.status, message: detail });
      }
      return response.json();
    } catch (error: any) {
      if (error?.name === "AbortError") {
        throw new ApiError({ kind: "timeout", url, baseUrl: this.baseUrl, message: `Chat timed out: ${url}` });
      }
      throw error instanceof ApiError ? error : new ApiError({ kind: "network", url, baseUrl: this.baseUrl, message: `Failed to fetch: ${url}` });
    } finally {
      clearTimeout(timeoutId);
    }
  }

  async healthCheck(): Promise<any> {
    return this.request("/api/health");
  }
}

export const api = new ApiClient(API_BASE_URL);
