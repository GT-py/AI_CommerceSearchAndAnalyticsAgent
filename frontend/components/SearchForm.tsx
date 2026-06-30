"use client";

import { useEffect, useState } from "react";
import type { Category, ProductQuery, ProductSort } from "@/types/product";

const sortOptions: { label: string; value: ProductSort }[] = [
  { label: "価格が安い順", value: "price_asc" },
  { label: "価格が高い順", value: "price_desc" },
  { label: "評価が高い順", value: "rating_desc" },
  { label: "新しい順", value: "newest" },
];

type SearchFormProps = {
  categories: Category[];
  initialQuery: ProductQuery;
  isLoading: boolean;
  onSearch: (query: ProductQuery) => void;
};

function toInputValue(value: number | string | undefined) {
  return value === undefined ? "" : String(value);
}

function toNumberOrUndefined(value: string) {
  const trimmed = value.trim();
  return trimmed === "" ? undefined : Number(trimmed);
}

export function SearchForm({ categories, initialQuery, isLoading, onSearch }: SearchFormProps) {
  const [keyword, setKeyword] = useState(initialQuery.keyword ?? "");
  const [categoryId, setCategoryId] = useState(toInputValue(initialQuery.category_id));
  const [minPrice, setMinPrice] = useState(toInputValue(initialQuery.min_price));
  const [maxPrice, setMaxPrice] = useState(toInputValue(initialQuery.max_price));
  const [sort, setSort] = useState<ProductSort | "">(initialQuery.sort ?? "");

  useEffect(() => {
    setKeyword(initialQuery.keyword ?? "");
    setCategoryId(toInputValue(initialQuery.category_id));
    setMinPrice(toInputValue(initialQuery.min_price));
    setMaxPrice(toInputValue(initialQuery.max_price));
    setSort(initialQuery.sort ?? "");
  }, [
    initialQuery.keyword,
    initialQuery.category_id,
    initialQuery.min_price,
    initialQuery.max_price,
    initialQuery.sort,
  ]);

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSearch({
      keyword: keyword.trim() || undefined,
      category_id: toNumberOrUndefined(categoryId),
      min_price: toNumberOrUndefined(minPrice),
      max_price: toNumberOrUndefined(maxPrice),
      sort: sort || undefined,
      page: 1,
      limit: initialQuery.limit ?? 20,
    });
  }

  function handleReset() {
    setKeyword("");
    setCategoryId("");
    setMinPrice("");
    setMaxPrice("");
    setSort("");
    onSearch({ page: 1, limit: initialQuery.limit ?? 20 });
  }

  return (
    <form className="search-form" onSubmit={handleSubmit}>
      <label className="field">
        <span>キーワード</span>
        <input value={keyword} onChange={(event) => setKeyword(event.target.value)} placeholder="LiteBook" />
      </label>

      <label className="field">
        <span>カテゴリ</span>
        <select value={categoryId} onChange={(event) => setCategoryId(event.target.value)}>
          <option value="">すべて</option>
          {categories.map((category) => (
            <option key={category.id} value={category.id}>
              {category.name}
            </option>
          ))}
        </select>
      </label>

      <label className="field">
        <span>最低価格</span>
        <input min="0" type="number" value={minPrice} onChange={(event) => setMinPrice(event.target.value)} />
      </label>

      <label className="field">
        <span>最高価格</span>
        <input min="0" type="number" value={maxPrice} onChange={(event) => setMaxPrice(event.target.value)} />
      </label>

      <label className="field">
        <span>並び替え</span>
        <select value={sort} onChange={(event) => setSort(event.target.value as ProductSort | "")}>
          <option value="">標準</option>
          {sortOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </label>

      <div className="form-actions align-end">
        <button className="button" type="submit" disabled={isLoading}>
          検索
        </button>
        <button className="button button-secondary" type="button" onClick={handleReset} disabled={isLoading}>
          クリア
        </button>
      </div>
    </form>
  );
}
