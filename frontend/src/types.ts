export type UserProfile = {
  id: number;
  username: string;
  email: string;
  role: "USER" | "ADMIN" | string;
};

export type AuthResponse = {
  token: string;
  tokenType: string;
  expiresAt: string;
  user: UserProfile;
};

export type Category = {
  id: number;
  name: string;
  slug: string;
};

export type Product = {
  id: number;
  name: string;
  description: string;
  brand: string;
  price: number;
  currency: string;
  inStock: boolean;
  stockQuantity: number;
  category: Category;
};

export type ProductPage = {
  items: Product[];
  page: number;
  size: number;
  totalItems: number;
  totalPages: number;
};

export type OrderStatus =
  | "CREATED"
  | "CONFIRMED"
  | "PROCESSING"
  | "SHIPPED"
  | "DELIVERED"
  | "CANCELLED"
  | string;

export type OrderItem = {
  productId: number;
  productName: string;
  quantity: number;
  unitPrice: number;
  lineTotal: number;
};

export type Order = {
  id: number;
  userId: number;
  username: string;
  status: OrderStatus;
  totalAmount: number;
  currency: string;
  note: string | null;
  createdAt: string;
  items: OrderItem[];
};

export type CartItem = {
  productId: number;
  productName: string;
  quantity: number;
  unitPrice: number;
  currency: string;
};

export type Purpose = "gaming" | "work" | "study" | "general";

export type ConfiguratorRequest = {
  budget: number;
  purpose: Purpose;
  preferred_brand: "intel" | "amd" | "nvidia" | "any";
  needs_wifi: boolean;
  target_resolution: "1080p" | "1440p" | "4k";
};

export type SelectedComponent = {
  type: string;
  model: string;
  brand: string;
  price: number;
  score: number;
  notes: string[];
};

export type ConfiguratorResponse = {
  purpose: Purpose;
  budget: number;
  total_price: number;
  currency: "RUB";
  performance_estimate: "entry" | "mid" | "high";
  components: SelectedComponent[];
  compatibility_checks: string[];
  explanation: string[];
};

export type ProblemDetail = {
  type?: string;
  title?: string;
  status?: number;
  detail?: unknown;
  instance?: string;
};
