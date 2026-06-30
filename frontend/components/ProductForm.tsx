"use client";

import { useEffect, useMemo, useState } from "react";
import type { Category, Product, ProductPayload } from "@/types/product";
import { ErrorMessage } from "./ErrorMessage";

type ProductFormProps = {
  categories: Category[];
  initialProduct?: Product;
  submitLabel: string;
  isSubmitting: boolean;
  error: string | null;
  onSubmit: (payload: ProductPayload) => Promise<void>;
};

type FormState = {
  name: string;
  description: string;
  category_id: string;
  brand: string;
  price: string;
  rating: string;
  stock: string;
  weight_g: string;
  battery_hours: string;
  screen_size: string;
  memory_gb: string;
  storage_gb: string;
  tags: string;
  thumbnail_url: string;
};

function numberToString(value: number | null | undefined) {
  return value === null || value === undefined ? "" : String(value);
}

function initialState(product: Product | undefined, categories: Category[]): FormState {
  return {
    name: product?.name ?? "",
    description: product?.description ?? "",
    category_id: product?.category.id ? String(product.category.id) : String(categories[0]?.id ?? ""),
    brand: product?.brand ?? "",
    price: numberToString(product?.price),
    rating: numberToString(product?.rating),
    stock: numberToString(product?.stock),
    weight_g: numberToString(product?.weight_g),
    battery_hours: numberToString(product?.battery_hours),
    screen_size: numberToString(product?.screen_size),
    memory_gb: numberToString(product?.memory_gb),
    storage_gb: numberToString(product?.storage_gb),
    tags: product?.tags.join(", ") ?? "",
    thumbnail_url: product?.thumbnail_url ?? "",
  };
}

function optionalNumber(value: string) {
  const trimmed = value.trim();
  return trimmed === "" ? null : Number(trimmed);
}

function optionalString(value: string) {
  const trimmed = value.trim();
  return trimmed === "" ? null : trimmed;
}

export function ProductForm({
  categories,
  initialProduct,
  submitLabel,
  isSubmitting,
  error,
  onSubmit,
}: ProductFormProps) {
  const nextInitialState = useMemo(() => initialState(initialProduct, categories), [initialProduct, categories]);
  const [form, setForm] = useState<FormState>(nextInitialState);
  const [localError, setLocalError] = useState<string | null>(null);

  useEffect(() => {
    setForm(nextInitialState);
  }, [nextInitialState]);

  function updateField(field: keyof FormState, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLocalError(null);

    const categoryId = Number(form.category_id);
    const price = Number(form.price);

    if (!form.name.trim() || !form.description.trim() || !categoryId || Number.isNaN(price)) {
      setLocalError("商品名、説明、カテゴリ、価格を入力してください。");
      return;
    }

    await onSubmit({
      name: form.name.trim(),
      description: form.description.trim(),
      category_id: categoryId,
      brand: optionalString(form.brand),
      price,
      rating: optionalNumber(form.rating),
      stock: optionalNumber(form.stock),
      weight_g: optionalNumber(form.weight_g),
      battery_hours: optionalNumber(form.battery_hours),
      screen_size: optionalNumber(form.screen_size),
      memory_gb: optionalNumber(form.memory_gb),
      storage_gb: optionalNumber(form.storage_gb),
      tags: form.tags
        .split(",")
        .map((tag) => tag.trim())
        .filter(Boolean),
      thumbnail_url: optionalString(form.thumbnail_url),
    });
  }

  return (
    <form className="form-panel" onSubmit={handleSubmit}>
      <ErrorMessage message={localError ?? error} />

      <div className="form-grid two-columns">
        <label className="field wide">
          <span>商品名</span>
          <input value={form.name} onChange={(event) => updateField("name", event.target.value)} required />
        </label>

        <label className="field wide">
          <span>説明</span>
          <textarea
            rows={5}
            value={form.description}
            onChange={(event) => updateField("description", event.target.value)}
            required
          />
        </label>

        <label className="field">
          <span>カテゴリ</span>
          <select
            value={form.category_id}
            onChange={(event) => updateField("category_id", event.target.value)}
            required
          >
            <option value="">選択してください</option>
            {categories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
        </label>

        <label className="field">
          <span>ブランド</span>
          <input value={form.brand} onChange={(event) => updateField("brand", event.target.value)} />
        </label>

        <label className="field">
          <span>価格</span>
          <input min="0" type="number" value={form.price} onChange={(event) => updateField("price", event.target.value)} required />
        </label>

        <label className="field">
          <span>評価</span>
          <input
            max="5"
            min="0"
            step="0.1"
            type="number"
            value={form.rating}
            onChange={(event) => updateField("rating", event.target.value)}
          />
        </label>

        <label className="field">
          <span>在庫</span>
          <input min="0" type="number" value={form.stock} onChange={(event) => updateField("stock", event.target.value)} />
        </label>

        <label className="field">
          <span>重量(g)</span>
          <input min="0" type="number" value={form.weight_g} onChange={(event) => updateField("weight_g", event.target.value)} />
        </label>

        <label className="field">
          <span>バッテリー時間</span>
          <input min="0" type="number" value={form.battery_hours} onChange={(event) => updateField("battery_hours", event.target.value)} />
        </label>

        <label className="field">
          <span>画面サイズ</span>
          <input
            min="0"
            step="0.1"
            type="number"
            value={form.screen_size}
            onChange={(event) => updateField("screen_size", event.target.value)}
          />
        </label>

        <label className="field">
          <span>メモリ(GB)</span>
          <input min="0" type="number" value={form.memory_gb} onChange={(event) => updateField("memory_gb", event.target.value)} />
        </label>

        <label className="field">
          <span>ストレージ(GB)</span>
          <input min="0" type="number" value={form.storage_gb} onChange={(event) => updateField("storage_gb", event.target.value)} />
        </label>

        <label className="field wide">
          <span>タグ</span>
          <input value={form.tags} onChange={(event) => updateField("tags", event.target.value)} />
        </label>

        <label className="field wide">
          <span>サムネイルURL</span>
          <input value={form.thumbnail_url} onChange={(event) => updateField("thumbnail_url", event.target.value)} />
        </label>
      </div>

      <div className="form-actions">
        <button className="button" type="submit" disabled={isSubmitting || categories.length === 0}>
          {isSubmitting ? "保存中" : submitLabel}
        </button>
      </div>
    </form>
  );
}
