import { API_BASE_URL } from "../constants/config";

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(path: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${path}`;
    const response = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Request failed" }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  async analyzeImage(imageUri: string, useSlm: boolean = false) {
    const formData = new FormData();
    const filename = imageUri.split("/").pop() || "photo.jpg";
    const match = /\.(\w+)$/.exec(filename);
    const type = match ? `image/${match[1]}` : "image/jpeg";

    formData.append("image", {
      uri: imageUri,
      name: filename,
      type,
    } as any);
    formData.append("use_slm", String(useSlm));

    const url = `${this.baseUrl}/api/analyze`;
    const response = await fetch(url, {
      method: "POST",
      body: formData,
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Analysis failed" }));
      throw new Error(error.detail || `HTTP ${response.status}`);
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
  } = {}) {
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

  async getProduct(productId: number) {
    return this.request(`/api/products/${productId}`);
  }

  async getCategories() {
    return this.request<{ categories: string[] }>("/api/products/categories");
  }

  async getConditions() {
    return this.request<{ conditions: any[] }>("/api/conditions");
  }

  async getCondition(name: string) {
    return this.request(`/api/conditions/${encodeURIComponent(name)}`);
  }

  async getSkinTypes() {
    return this.request<{ skin_types: any[] }>("/api/conditions/skin-types");
  }

  async healthCheck() {
    return this.request("/api/health");
  }
}

export const api = new ApiClient(API_BASE_URL);
