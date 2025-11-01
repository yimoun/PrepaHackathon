import { createContext, useState } from "react";
import IUser from "../data_interfaces/IUser";
import UserDS from "../data_services/UserDS";
import { storageAccessTokenKey } from "../data_services/CustomAxios";

export interface IUserContext {
  initialized: boolean;
  user: IUser | null;
  token: string;
  setUser: (user: IUser | null) => void;
  setToken: (token: string) => void;
  refreshUser: () => void;
  logoutUser: () => void;
}

const defaultUserContext: IUserContext = {
  initialized: false,
  user: null,
  token: "",
  setUser: () => {},
  setToken: () => {},
  refreshUser: () => {},
  logoutUser: () => {},
};

export const UserContextState = (): IUserContext => {
  const [userContext, setUserContext] = useState<IUserContext>(defaultUserContext);

  userContext.setUser = (user: IUser | null): void => {
    setUserContext((prev) => {
      if (!prev.initialized) {
        prev.initialized = true;
      }
      prev.user = user;
      return { ...prev };
    });
  };

  userContext.setToken = (token: string): void => {
    setUserContext((prev) => {
      prev.token = token;
      return { ...prev };
    });
  };

  userContext.refreshUser = (): void => {
    const token = localStorage.getItem(storageAccessTokenKey);
    if (token) {
      console.log("Tentative de récupération de l'utilisateur...");
      userContext.setToken(token);
      UserDS.get()
        .then((response) => {
          console.log("Utilisateur récupéré :", response.data);
          userContext.setUser(response.data);
        })
        .catch((error) => {
          console.error("Erreur lors de la récupération de l'utilisateur :", error);
          userContext.setUser(null);
        });
    } else {
      console.log("⚠️ Aucun token trouvé, utilisateur non connecté.");
      userContext.setUser(null);
    }
  };

  userContext.logoutUser = (): void => {
    UserDS.logout().then(() => {
      console.log(" Déconnexion réussie");
      userContext.setUser(null);
      userContext.setToken("");
    });
  };

  return userContext;
};

const UserContext = createContext<IUserContext>(defaultUserContext);
export default UserContext;
