export type ExtractedConditions = {
  category: string | null;
  max_price: number | null;
  sort: string | null;
  tags: string[];
  min_battery_hours: number | null;
  max_weight_g: number | null;
  min_memory_gb: number | null;
  min_storage_gb: number | null;
};

export type RecommendedProduct = {
  id: number;
  name: string;
  price: number;
  reason: string;
};

export type AssistantChatRequest = {
  conversation_id?: number;
  message: string;
};

export type AssistantChatResponse = {
  conversation_id: number;
  assistant_message_id: number;
  reply: string;
  extracted_conditions: ExtractedConditions;
  recommended_products: RecommendedProduct[];
};

export type AssistantFeedbackRequest = {
  message_id: number;
  rating: "good" | "bad";
  comment?: string | null;
};

export type AssistantFeedbackResponse = {
  id: number;
  message_id: number;
  user_id: number | null;
  rating: string;
  comment: string | null;
  created_at: string;
};

export type AIEvaluation = {
  id: number;
  created_at: string;
  user_id: number | null;
  question: string | null;
  assistant_reply: string;
  rating: "good" | "bad";
  comment: string | null;
};

export type AIEvaluationListResponse = {
  items: AIEvaluation[];
  page: number;
  limit: number;
  total: number;
  has_next: boolean;
};
