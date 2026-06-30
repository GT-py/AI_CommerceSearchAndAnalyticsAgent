export type AnalyticsSummary = {
  total_products: number;
  total_users: number;
  total_searches: number;
  total_clicks: number;
  total_ai_conversations: number;
  total_ai_feedback: number;
  good_feedback_count: number;
  bad_feedback_count: number;
};

export type SearchKeywordAnalyticsItem = {
  keyword: string;
  search_count: number;
  total_result_count: number;
  avg_result_count: number;
};

export type SearchKeywordAnalyticsResponse = {
  items: SearchKeywordAnalyticsItem[];
};

export type ProductAnalyticsItem = {
  product_id: number;
  name: string;
  category: string;
  click_count: number;
  favorite_count: number;
  assistant_recommendation_clicks: number;
};

export type ProductAnalyticsResponse = {
  items: ProductAnalyticsItem[];
};

export type RecentBadFeedbackItem = {
  message_id: number;
  comment: string | null;
  created_at: string;
};

export type AssistantFeedbackAnalyticsResponse = {
  good: number;
  bad: number;
  good_rate: number;
  recent_bad_feedback: RecentBadFeedbackItem[];
};
