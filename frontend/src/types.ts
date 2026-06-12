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
  componentType?: ProductComponentType;
  socket?: string | null;
  supportedSockets?: string[];
  ramType?: string | null;
  gpuTdp?: number;
  cpuTdp?: number;
  psuWatts?: number;
  supportsWifi?: boolean;
  scoreGaming?: number;
  scoreWork?: number;
  scoreStudy?: number;
  scoreGeneral?: number;
  notes?: string[];
  inStock: boolean;
  stockQuantity: number;
  category: Category;
};

export type ProductComponentType =
  | "CPU"
  | "GPU"
  | "MOTHERBOARD"
  | "RAM"
  | "STORAGE"
  | "PSU"
  | "CASE"
  | "OTHER";

export type ProductCreateRequest = {
  name: string;
  description?: string | null;
  brand: string;
  price: number;
  currency: string;
  inStock: boolean;
  stockQuantity: number;
  categoryId: number;
  componentType: ProductComponentType;
  socket?: string | null;
  supportedSockets?: string[];
  ramType?: string | null;
  gpuTdp: number;
  cpuTdp: number;
  psuWatts: number;
  supportsWifi: boolean;
  scoreGaming: number;
  scoreWork: number;
  scoreStudy: number;
  scoreGeneral: number;
  notes?: string | null;
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

export type CartResponse = {
  items: CartItem[];
  totalAmount: number;
  currency: string;
};

export type ConfigurationHistory = {
  id: number;
  userId: number;
  username: string;
  purpose: string;
  budget: number;
  totalPrice: number;
  currency: string;
  performanceEstimate: string;
  createdAt: string;
};

export type Purpose = "gaming" | "work" | "study" | "general";

export type ConfiguratorRequest = {
  budget: number;
  purpose: Purpose;
  preferred_brand: "intel" | "amd" | "nvidia" | "any";
  needs_wifi: boolean;
  target_resolution: "1080p" | "1440p" | "4k";
  minimum_performance?: "entry" | "mid" | "high" | null;
  cpu_brand_preference?: "intel" | "amd" | "any";
  gpu_brand_preference?: "nvidia" | "amd" | "intel" | "any";
  min_ram_gb?: number;
  min_vram_gb?: number;
};

export type SelectedComponent = {
  product_id?: number | null;
  type: string;
  model: string;
  brand: string;
  price: number;
  score: number;
  notes: string[];
};

export type ConfigurationVariant = {
  purpose: Purpose;
  budget: number;
  total_price: number;
  currency: "RUB";
  performance_estimate: "entry" | "mid" | "high";
  ml_score: number;
  components: SelectedComponent[];
  compatibility_checks: string[];
  explanation: string[];
};

export type ConfiguratorResponse = ConfigurationVariant & {
  alternatives?: {
    cheaper?: ConfigurationVariant | null;
    pricier?: ConfigurationVariant | null;
  } | null;
};

export type ConfiguratorAssistantRequest = {
  message: string;
  history?: Array<{
    role: "user" | "assistant";
    content: string;
  }>;
};

export type ConfiguratorAssistantResponse = {
  mode: "chat" | "recommendation";
  answer: string;
  extracted_request?: ConfiguratorRequest | null;
  recommendation?: ConfiguratorResponse | null;
  llm_model?: string | null;
  llm_used: boolean;
};

export type ProblemDetail = {
  type?: string;
  title?: string;
  status?: number;
  detail?: unknown;
  instance?: string;
};
