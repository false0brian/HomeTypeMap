// Minimal RN/TS integration sample for HomeTypeMap API.

export type WorkScopeType = "kitchen" | "bathroom" | "partial" | "full_remodeling";

export interface ComplexPin {
  complex_id: number;
  name: string;
  latitude: number;
  longitude: number;
  portfolio_count: number;
}

export interface ClusterPin {
  cluster_key: string;
  center_latitude: number;
  center_longitude: number;
  count: number;
}

export interface MapPinsResponse {
  clusters: ClusterPin[];
  complexes: ComplexPin[];
}

export interface UnitTypeChip {
  unit_type_id: number;
  exclusive_area_m2: number;
  type_code?: string;
  room_count?: number;
  bathroom_count?: number;
  structure_keyword?: string;
  portfolio_count: number;
}

export interface ComplexDetailResponse {
  complex_id: number;
  name: string;
  address: string;
  built_year?: number;
  household_count?: number;
  unit_types: UnitTypeChip[];
}

export interface PortfolioCard {
  portfolio_id: number;
  title: string;
  before_image_url?: string;
  after_image_url?: string;
  work_scope: WorkScopeType;
  style: string;
  budget_min_krw?: number;
  budget_max_krw?: number;
  duration_days?: number;
  vendor_id?: number;
  vendor_name?: string;
}

export interface PortfolioListResponse {
  items: PortfolioCard[];
  total: number;
}

const API_BASE = "http://127.0.0.1:8000/api/v1";

export async function fetchMapPins(params: {
  south: number;
  west: number;
  north: number;
  east: number;
  zoom: number;
}): Promise<MapPinsResponse> {
  const qs = new URLSearchParams({
    south: String(params.south),
    west: String(params.west),
    north: String(params.north),
    east: String(params.east),
    zoom: String(params.zoom),
  });
  const res = await fetch(`${API_BASE}/map/pins?${qs.toString()}`);
  if (!res.ok) throw new Error("failed to fetch map pins");
  return res.json();
}

export async function fetchComplexDetail(complexId: number): Promise<ComplexDetailResponse> {
  const res = await fetch(`${API_BASE}/complexes/${complexId}`);
  if (!res.ok) throw new Error("failed to fetch complex detail");
  return res.json();
}

export async function fetchPortfoliosByType(
  complexId: number,
  unitTypeId: number,
  filters?: {
    min_area?: number;
    max_area?: number;
    budget_min_krw?: number;
    budget_max_krw?: number;
    work_scope?: WorkScopeType;
    style?: string;
    limit?: number;
    offset?: number;
  },
): Promise<PortfolioListResponse> {
  const params = new URLSearchParams({
    unit_type_id: String(unitTypeId),
    limit: String(filters?.limit ?? 20),
    offset: String(filters?.offset ?? 0),
  });

  if (filters?.min_area !== undefined) params.set("min_area", String(filters.min_area));
  if (filters?.max_area !== undefined) params.set("max_area", String(filters.max_area));
  if (filters?.budget_min_krw !== undefined) params.set("budget_min_krw", String(filters.budget_min_krw));
  if (filters?.budget_max_krw !== undefined) params.set("budget_max_krw", String(filters.budget_max_krw));
  if (filters?.work_scope) params.set("work_scope", filters.work_scope);
  if (filters?.style) params.set("style", filters.style);

  const res = await fetch(`${API_BASE}/complexes/${complexId}/portfolios?${params.toString()}`);
  if (!res.ok) throw new Error("failed to fetch portfolios");
  return res.json();
}

export async function addFavorite(userKey: string, portfolioId: number) {
  const res = await fetch(`${API_BASE}/favorites`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_key: userKey, portfolio_id: portfolioId }),
  });
  if (!res.ok) throw new Error("failed to add favorite");
  return res.json();
}

export async function requestQuote(payload: {
  user_key: string;
  vendor_id?: number;
  portfolio_id?: number;
  preferred_date?: string;
  message?: string;
}) {
  const res = await fetch(`${API_BASE}/quote-requests`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("failed to request quote");
  return res.json();
}
