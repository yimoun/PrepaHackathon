import { createContext, useState } from "react";

export interface IFavoriteContext {
  initialized: boolean
  productIds: number[]
  init: (productIds: number[]) => void
  contains: (productId: number) => boolean
  add: (productId: number) => void
  remove: (productId: number) => void
}

const defaultFavoriteContext: IFavoriteContext = {
  initialized: false,
  productIds: [],
  init: (): void => {},
  contains: (): boolean => false,
  add: (): void => {},
  remove: (): void => {},
}

export const FavoriteContextState = (): IFavoriteContext => {
  const [favoriteContext, setFavoriteContext] = useState<IFavoriteContext>(defaultFavoriteContext);

  favoriteContext.init = (productIds: number[]): void => {
    setFavoriteContext((prev) => {
      prev.initialized = true
      prev.productIds = [...productIds]
      return { ...prev }
    })
  }

  favoriteContext.contains = (productId: number): boolean => {
    const index = favoriteContext.productIds.indexOf(productId);
    return index >= 0;
  }

  favoriteContext.add = (productId: number): void => {
    const index = favoriteContext.productIds.indexOf(productId);
    if (index < 0) {
      setFavoriteContext((prev) => {
        prev.productIds.push(productId)
        return { ...prev }
      })
    }
  }

  favoriteContext.remove = (productId: number): void => {
    const index = favoriteContext.productIds.indexOf(productId);
    if (index >= 0) {
      setFavoriteContext((prev) => {
        prev.productIds.splice(index, 1)
        return { ...prev }
      })
    }
  }

  return favoriteContext;
}

const FavoriteContext = createContext<IFavoriteContext>(defaultFavoriteContext);
export default FavoriteContext;
