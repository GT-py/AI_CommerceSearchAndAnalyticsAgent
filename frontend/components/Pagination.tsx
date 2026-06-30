type PaginationProps = {
  page: number;
  limit: number;
  total: number;
  hasNext: boolean;
  onPageChange: (page: number) => void;
};

export function Pagination({ page, limit, total, hasNext, onPageChange }: PaginationProps) {
  const totalPages = Math.max(1, Math.ceil(total / limit));

  return (
    <div className="pagination" aria-label="ページ移動">
      <button
        className="button button-secondary"
        type="button"
        disabled={page <= 1}
        onClick={() => onPageChange(page - 1)}
      >
        前へ
      </button>
      <span className="page-indicator">
        {page} / {totalPages} ページ
      </span>
      <button
        className="button button-secondary"
        type="button"
        disabled={!hasNext}
        onClick={() => onPageChange(page + 1)}
      >
        次へ
      </button>
    </div>
  );
}
