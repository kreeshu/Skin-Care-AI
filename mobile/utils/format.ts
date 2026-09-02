export function formatPrice(price: number | null): string {
  if (price === null || price === undefined) return "N/A";
  return `Rs. ${Math.round(price).toLocaleString()}`;
}

export function formatDiscount(price: number | null, discountedPrice: number | null): {
  original: string;
  discounted: string | null;
  percentage: string | null;
} {
  const original = formatPrice(price);
  if (!discountedPrice || !price || discountedPrice >= price) {
    return { original, discounted: null, percentage: null };
  }
  const pct = Math.round(((price - discountedPrice) / price) * 100);
  return {
    original,
    discounted: formatPrice(discountedPrice),
    percentage: `${pct}% off`,
  };
}

export function formatRating(rating: number | null): string {
  if (rating === null || rating === undefined) return "No rating";
  return `${rating.toFixed(1)}`;
}

export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return "Just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString();
}

export function capitalize(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}
