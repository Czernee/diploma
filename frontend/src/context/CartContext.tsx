import { createContext, useContext, useMemo, useState } from "react";
import type { CartItem, Product } from "../types";

const CART_STORAGE_KEY = "diploma.cart.items";

type CartContextValue = {
  items: CartItem[];
  addProduct: (product: Product) => void;
  setQuantity: (productId: number, quantity: number) => void;
  removeItem: (productId: number) => void;
  clear: () => void;
  totalAmount: number;
};

const CartContext = createContext<CartContextValue | undefined>(undefined);

export function CartProvider({ children }: { children: React.ReactNode }) {
  const [items, setItems] = useState<CartItem[]>(() => {
    const raw = localStorage.getItem(CART_STORAGE_KEY);
    if (!raw) {
      return [];
    }
    try {
      return JSON.parse(raw) as CartItem[];
    } catch {
      return [];
    }
  });

  const sync = (nextItems: CartItem[]) => {
    setItems(nextItems);
    localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(nextItems));
  };

  const value = useMemo<CartContextValue>(
    () => ({
      items,
      addProduct: (product) => {
        const existing = items.find((item) => item.productId === product.id);
        if (existing) {
          sync(
            items.map((item) =>
              item.productId === product.id ? { ...item, quantity: item.quantity + 1 } : item
            )
          );
          return;
        }
        sync([
          ...items,
          {
            productId: product.id,
            productName: product.name,
            quantity: 1,
            unitPrice: product.price,
            currency: product.currency
          }
        ]);
      },
      setQuantity: (productId, quantity) => {
        if (quantity <= 0) {
          sync(items.filter((item) => item.productId !== productId));
          return;
        }
        sync(items.map((item) => (item.productId === productId ? { ...item, quantity } : item)));
      },
      removeItem: (productId) => {
        sync(items.filter((item) => item.productId !== productId));
      },
      clear: () => {
        sync([]);
      },
      totalAmount: items.reduce((acc, item) => acc + item.quantity * item.unitPrice, 0)
    }),
    [items]
  );

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export function useCart() {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error("useCart must be used inside CartProvider");
  }
  return context;
}
