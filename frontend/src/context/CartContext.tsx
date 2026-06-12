import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { addCartItem, clearServerCart, deleteCartItem, fetchCart, updateCartItemQuantity } from "../api/orderApi";
import { useAuth } from "./AuthContext";
import type { CartItem, CartResponse, Product } from "../types";

const CART_STORAGE_KEY = "diploma.cart.items";

type CartContextValue = {
  items: CartItem[];
  addProduct: (product: Product) => Promise<void>;
  addItem: (item: Omit<CartItem, "quantity">, quantity?: number) => Promise<void>;
  setQuantity: (productId: number, quantity: number) => void;
  removeItem: (productId: number) => void;
  clear: () => void;
  totalAmount: number;
};

const CartContext = createContext<CartContextValue | undefined>(undefined);

function loadLocalCart(): CartItem[] {
  const raw = localStorage.getItem(CART_STORAGE_KEY);
  if (!raw) {
    return [];
  }
  try {
    return JSON.parse(raw) as CartItem[];
  } catch {
    return [];
  }
}

function toCartItems(response: CartResponse): CartItem[] {
  return response.items.map((item) => ({
    productId: item.productId,
    productName: item.productName,
    quantity: item.quantity,
    unitPrice: item.unitPrice,
    currency: item.currency
  }));
}

export function CartProvider({ children }: { children: React.ReactNode }) {
  const { token } = useAuth();
  const [items, setItems] = useState<CartItem[]>(loadLocalCart);

  useEffect(() => {
    let cancelled = false;

    async function syncServerCart() {
      if (!token) {
        setItems(loadLocalCart());
        return;
      }

      const localItems = loadLocalCart();
      try {
        for (const item of localItems) {
          await addCartItem(token, item);
        }
        const response = await fetchCart(token);
        if (!cancelled) {
          setItems(toCartItems(response));
          localStorage.removeItem(CART_STORAGE_KEY);
        }
      } catch {
        if (!cancelled) {
          setItems(localItems);
        }
      }
    }

    void syncServerCart();
    return () => {
      cancelled = true;
    };
  }, [token]);

  const updateItems = (updater: (prevItems: CartItem[]) => CartItem[]) => {
    setItems((prevItems) => {
      const nextItems = updater(prevItems);
      if (!token) {
        localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(nextItems));
      }
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
      addProduct: async (product) => {
        const item = {
          productId: product.id,
          productName: product.name,
          unitPrice: product.price,
          currency: product.currency
        };
        upsertItem(
          item,
          1
        );
        if (token) {
          const response = await addCartItem(token, { ...item, quantity: 1 });
          setItems(toCartItems(response));
        }
      },
      addItem: async (item, quantity = 1) => {
        if (quantity <= 0) {
          return;
        }
        upsertItem(item, quantity);
        if (token) {
          const response = await addCartItem(token, { ...item, quantity });
          setItems(toCartItems(response));
        }
      },
      setQuantity: (productId, quantity) => {
        if (quantity <= 0) {
          updateItems((prevItems) => prevItems.filter((item) => item.productId !== productId));
          if (token) {
            void updateCartItemQuantity(token, productId, 0).then((response) => setItems(toCartItems(response)));
          }
          return;
        }
        updateItems((prevItems) =>
          prevItems.map((item) => (item.productId === productId ? { ...item, quantity } : item))
        );
        if (token) {
          void updateCartItemQuantity(token, productId, quantity).then((response) => setItems(toCartItems(response)));
        }
      },
      removeItem: (productId) => {
        updateItems((prevItems) => prevItems.filter((item) => item.productId !== productId));
        if (token) {
          void deleteCartItem(token, productId).then((response) => setItems(toCartItems(response)));
        }
      },
      clear: () => {
        updateItems(() => []);
        if (token) {
          void clearServerCart(token).then((response) => setItems(toCartItems(response)));
        }
      },
      totalAmount: items.reduce((acc, item) => acc + item.quantity * item.unitPrice, 0)
    }),
    [items, token]
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
