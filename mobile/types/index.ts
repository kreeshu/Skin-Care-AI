export interface Product {
  product_id: string;
  name: string;
  brand: string;
  price: number | null;
  discounted_price: number | null;
  rating: number | null;
  review_count: number;
  availability: string;
  image_url: string;
  source: string;
  category: string[];
  skin_types: string[];
  skin_concerns: string[];
  ingredients: string[];
}

export interface ProductRecommendation {
  product_id: string;
  name: string;
  brand: string;
  price: number | null;
  discounted_price: number | null;
  rating: number | null;
  review_count: number;
  score: number;
  matching_ingredients: string[];
  image_url: string;
  source: string;
}

export interface SlmChosen {
  category: string;
  product_id: string;
  name: string;
  reason: string;
}

export interface SlmResult {
  chosen: SlmChosen[];
  routine: {
    am: string[];
    pm: string[];
  };
  summary: string;
  generated_by?: string;
}

export interface AnalysisResult {
  id: string;
  schema_version: 2;
  model_version: string;
  analysis_quality: { status: "usable" | "rejected" | "uncertain"; reasons: string[] };
  concerns: ConcernResult[];
  skin_type: string | null;
  title: string;
  description: string;
  skin_type_title: string | null;
  recommendations: Record<string, ProductRecommendation[]>;
  routine_suggestion: string[];
  total_products_found: number;
  disclaimer: string;
  slm: SlmResult | null;
}

export interface ConcernResult {
  name: "blemishes" | "dark_spots" | "redness" | "visible_pores" | "fine_lines";
  score: number;
  threshold: number;
  status: "present" | "absent" | "uncertain";
}

export interface Condition {
  name: string;
  title: string;
  description: string;
  is_medical: boolean;
  color: string;
  recommended_ingredients: string[];
  recommended_categories: string[];
  avoid_ingredients: string[];
  routine_steps: string[];
  causes: string[];
  tips: string[];
}

export interface SkinType {
  name: string;
  title: string;
  description: string;
  recommended_ingredients: string[];
  texture_preferences: string[];
  tips: string[];
}

export interface ProductsResponse {
  products: Product[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ScanHistoryItem {
  id: string;
  summary: string;
  skin_type: string;
  date: string;
  result: AnalysisResult;
}

export type ChatTurn =
  | { role: "user"; content: string; product_cards?: never }
  | { role: "assistant"; content: string; product_cards?: ChatReply["product_cards"] }
  | { role: "user"; kind: "photo"; imageUri: string; status: "analyzing" | "done" | "error"; fileSize?: number; mimeType?: string }
  | { role: "assistant"; kind: "result"; result: AnalysisResult };

export interface ChatContext {
  concerns?: ConcernResult[];
  analysis_quality?: AnalysisResult["analysis_quality"];
  skin_type?: string;
  product_ids?: string[];
  recommendations?: Record<string, ProductRecommendation[]>;
}

export interface ChatReply {
  reply: string;
  product_cards: { product_id: string; name: string; brand: string }[];
  disclaimer: string;
  generated_by?: string;
}
