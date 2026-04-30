import { createContext, useContext, useMemo, useState } from "react";
import type { CartItem, Product } from "../types";

const CART_STORAGE_KEY = "diploma.cart.items";

type CartContextValue = {
  items: CartItem[];
  addProduct: (product: Product) => void;
  addItem: (item: Omit<CartItem, "quantity">, quantity?: number) => void;
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

  const updateItems = (updater: (prevItems: CartItem[]) => CartItem[]) => {
    setItems((prevItems) => {
      const nextItems = updater(prevItems);
      localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(nextItems));
      return nextItems;
    });
  };

  const upsertItem = (item: Omit<CartItem, "quantity">, quantityDelta: number) => {
    updateItems((prevItems) => {
      const existing = prevItems.find((entry) => entry.productId === item.productId);
      if (existing) {
        return prevItems.map((entry) =>
          entry.productId === item.productId ? { ...entry, quantity: entry.quantity + quantityDelta } : entry
        );
      }
      return [
        ...prevItems,
        {
          ...item,
          quantity: quantityDelta
        }
      ];
    });
  };

  const value = useMemo<CartContextValue>(
    () => ({
      items,
      addProduct: (product) => {
        upsertItem(
          {
            productId: product.id,
            productName: product.name,
            unitPrice: product.price,
            currency: product.currency
          },
          1
        );
      },
      addItem: (item, quantity = 1) => {
        if (quantity <= 0) {
          return;
        }
        upsertItem(item, quantity);
      },
      setQuantity: (productId, quantity) => {
        if (quantity <= 0) {
          updateItems((prevItems) => prevItems.filter((item) => item.productId !== productId));
          return;
        }
        updateItems((prevItems) =>
          prevItems.map((item) => (item.productId === productId ? { ...item, quantity } : item))
        );
      },
      removeItem: (productId) => {
        updateItems((prevItems) => prevItems.filter((item) => item.productId !== productId));
      },
      clear: () => {
        updateItems(() => []);
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
