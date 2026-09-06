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
  detected_condition: string;
  condition_confidence: number;
  skin_type: string;
  skin_type_confidence: number;
  is_medical: boolean;
  title: string;
  description: string;
  skin_type_title: string | null;
  recommendations: Record<string, ProductRecommendation[]>;
  routine_suggestion: string[];
  total_products_found: number;
  disclaimer: string;
  slm: SlmResult | null;
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
  condition: string;
  skin_type: string;
  date: string;
  result: AnalysisResult;
}

export type ChatTurn =
  | { role: "user"; content: string }
  | { role: "assistant"; content: string }
  | { role: "user"; kind: "photo"; imageUri: string; status: "analyzing" | "done" | "error" }
  | { role: "assistant"; kind: "result"; result: AnalysisResult };

export interface ChatContext {
  condition?: string;
  skin_type?: string;
  is_medical?: boolean;
  product_ids?: string[];
  recommendations?: Record<string, ProductRecommendation[]>;
}

export interface ChatReply {
  reply: string;
  product_cards: { product_id: string; name: string; brand: string }[];
  disclaimer: string;
  generated_by?: string;
}
