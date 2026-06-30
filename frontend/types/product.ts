export type Category = {
  id: number;
  name: string;
  slug: string;
};

export type Product = {
  id: number;
  name: string;
  description: string;
  category: Category;
  brand: string | null;
  price: number;
  rating: number | null;
  stock: number | null;
  weight_g: number | null;
  battery_hours: number | null;
  screen_size: number | null;
  memory_gb: number | null;
  storage_gb: number | null;
  tags: string[];
  thumbnail_url: string | null;
};

export type ProductSort = "price_asc" | "price_desc" | "rating_desc" | "newest";

export type ProductQuery = {
  keyword?: string;
  category_id?: number;
  min_price?: number;
  max_price?: number;
  sort?: ProductSort;
  page?: number;
  limit?: number;
};

export type ProductListResponse = {
  items: Product[];
  page: number;
  limit: number;
  total: number;
  has_next: boolean;
};

export type ProductPayload = {
  name: string;
  description: string;
  category_id: number;
  brand: string | null;
  price: number;
  rating: number | null;
  stock: number | null;
  weight_g: number | null;
  battery_hours: number | null;
  screen_size: number | null;
  memory_gb: number | null;
  storage_gb: number | null;
  tags: string[];
  thumbnail_url: string | null;
};
