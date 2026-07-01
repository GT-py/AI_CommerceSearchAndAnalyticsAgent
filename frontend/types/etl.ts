export type ETLRunResponse = {
  message: string;
  daily_search_metrics_count: number;
  product_features_count: number;
};

export type DailySearchMetric = {
  id: number;
  date: string;
  keyword: string;
  search_count: number;
  click_count: number;
  ctr: number;
  created_at: string;
};

export type DailySearchMetricListResponse = {
  items: DailySearchMetric[];
  page: number;
  limit: number;
  total: number;
  has_next: boolean;
};

export type ProductFeature = {
  id: number;
  product_id: number;
  product_name: string;
  date: string;
  view_count_7d: number;
  click_count_7d: number;
  favorite_count_7d: number;
  ctr_7d: number;
  created_at: string;
};

export type ProductFeatureListResponse = {
  items: ProductFeature[];
  page: number;
  limit: number;
  total: number;
  has_next: boolean;
};
