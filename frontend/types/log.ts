import type { Product } from "./product";

export type FavoriteItem = {
  id: number;
  product: Product;
  created_at: string;
};

export type FavoriteListResponse = {
  items: FavoriteItem[];
};

export type ClickSource = "search" | "assistant" | "favorite";

export type ClickLogResponse = {
  id: number;
  user_id: number | null;
  product_id: number;
  source: ClickSource;
  created_at: string;
};

export type SearchLog = {
  id: number;
  user_id: number | null;
  keyword: string | null;
  category_id: number | null;
  min_price: number | null;
  max_price: number | null;
  sort: string | null;
  page: number;
  limit: number;
  result_count: number;
  created_at: string;
};

export type SearchLogListResponse = {
  items: SearchLog[];
  page: number;
  limit: number;
  total: number;
  has_next: boolean;
};

export type ClickLog = {
  id: number;
  user_id: number | null;
  product_id: number;
  product: {
    id: number;
    name: string;
  };
  source: ClickSource;
  created_at: string;
};

export type ClickLogListResponse = {
  items: ClickLog[];
  page: number;
  limit: number;
  total: number;
  has_next: boolean;
};
