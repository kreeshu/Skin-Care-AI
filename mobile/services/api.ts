import { Platform } from "react-native";
import { File, UploadType, type UploadResult } from "expo-file-system";
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

  async analyzeImage(imageUri: string, fileInfo?: { fileSize?: number; mimeType?: string }, skinType?: string | null) {
    const url = this.toUrl("/api/analyze");
    if (fileInfo?.fileSize && fileInfo.fileSize > 10 * 1024 * 1024) {
      throw new ApiError({
        kind: "http",
        url,
        baseUrl: this.baseUrl,
        status: 400,
        message: "Photo is too large (max 10MB). Retake with lower quality and try again.",
      });
    }
    // Expo Go cache URIs may be single- or double-encoded (%40/@, %2F//).
    // Android resolves %2F as a literal dirname, so probe each decoding
    // level and upload with the first one that exists on disk.
    const candidates = [imageUri];
    try {
      if (imageUri.includes("%25")) candidates.push(decodeURI(imageUri));
    } catch {}
    try {
      candidates.push(decodeURIComponent(candidates[candidates.length - 1]));
    } catch {}
    let fileUri = candidates[0];
    let resolved = false;
    for (const c of candidates) {
      try {
        const f = new File(c);
        if (f.exists && !resolved) {
          fileUri = c;
          resolved = true;
        }
      } catch {}
    }
    if (!resolved) {
      throw new ApiError({
        kind: "http",
        url,
        baseUrl: this.baseUrl,
        status: 400,
        message: "Photo file not found on this device. Please retake the photo and try again.",
      });
    }
    const filename = (fileUri.split("/").pop() || "photo.jpg").split("?")[0] || "photo.jpg";
    const match = /\.(\w+)$/.exec(filename);
    const type = fileInfo?.mimeType || (match ? `image/${match[1].toLowerCase()}` : "image/jpeg");
    console.log("[analyze] uploading:", fileUri.split("?")[0].slice(0, 100), `${Math.round((fileInfo?.fileSize ?? 0) / 1024)}KB`, type);

    // Web uploads a real Blob; native uploads the file directly (see below).
    if (Platform.OS === "web") {
      const formData = new FormData();
      const blobRes = await fetch(imageUri);
      formData.append("image", await blobRes.blob(), filename);
      if (skinType) formData.append("skin_type", skinType);

      const controller = new AbortController();
      // Image analysis can take a while — own 120s timeout.
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
    // Native: RN's fetch can't stream Expo cache files (rejects with a
    // network error while the backend stays silent). Upload natively.
    const controller = new AbortController();
    // Image analysis can take a while — own 120s timeout.
    const timeoutId = setTimeout(() => controller.abort(), 120000);
    let result: UploadResult;
    try {
      result = await new File(fileUri).upload(url, {
        uploadType: UploadType.MULTIPART,
        fieldName: "image",
        mimeType: type,
        parameters: skinType ? { skin_type: skinType } : {},
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

    if (result.status < 200 || result.status >= 300) {
      let detail = "Analysis failed";
      try {
        const data = JSON.parse(result.body);
        if (data && typeof data.detail === "string" && data.detail) detail = data.detail;
      } catch {
        if (result.body) detail = result.body.slice(0, 200);
      }
      throw new ApiError({
        kind: "http",
        url,
        baseUrl: this.baseUrl,
        status: result.status,
        message: detail,
      });
    }

    try {
      return JSON.parse(result.body);
    } catch {
      throw new ApiError({
        kind: "http",
        url,
        baseUrl: this.baseUrl,
        status: result.status,
        message: "Invalid response from server.",
      });
    }
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

  async getCategories(): Promise<{ categories: string[] }> {
    return this.request("/api/products/categories");
  }

  async sendChatMessage(message: string, history: { role: string; content: string }[] = [], context?: {
    concerns?: any[];
    analysis_quality?: Record<string, any>;
    skin_type?: string;
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
