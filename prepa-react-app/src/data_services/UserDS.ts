import { AxiosResponse } from "axios"
import CustomAxios, { setLocalToken, unsetLocalToken } from "./CustomAxios"
import IUser from "../data_interfaces/IUser"


/*Envoie une requête PUT pour modifier le mot de passe de l’utilisateur actuel:Retourne une Promise
 contenant la réponse de l’API.*/
const changePassword = (password: string): Promise<AxiosResponse<IUser>> => (
  CustomAxios.put("auth/current-user-password/me/", { password })
)

//Récupère les informations de l’utilisateur connecté.
const get = (): Promise<AxiosResponse<IUser>> => (
  CustomAxios.get("auth/current-user/")
)


/*Envoie une requête POST pour obtenir un token JWT.Si la connexion réussit:Stocke le token
 via setLocalToken(response.data).Résout la Promise avec true.Sinon, rejette la Promise avec une erreur.*/
 const login = (username: string, password: string, recaptchaToken: string | null): Promise<boolean> => {
  const promise = new Promise<boolean>((resolve, reject) => {
    CustomAxios.post("auth/token/", { username, password, recaptcha_token: recaptchaToken })
      .then((response) => {
        setLocalToken(response.data)
        resolve(true)
      })
      .catch((err) => {
        reject(err)
      })
  })
  return promise
}

//Supprime le token JWT via unsetLocalToken(): Retourne true une fois déconnecté.
const logout = (): Promise<boolean> => {
  const promise = new Promise<boolean>((resolve) => {
    unsetLocalToken()
    resolve(true)
  });
  return promise;
}

//Fonction register (Créer un compte utilisateur)
const register = (user: IUser, password: string, recaptchaToken: string | null): Promise<AxiosResponse<IUser>> => (
  CustomAxios.post("auth/register/", {
    first_name: user.first_name,
    last_name: user.last_name,
    username: user.username,
    email: user.email,
    password,
    recaptcha_token: recaptchaToken
  })
)

//Fonction save (Modifier les infos utilisateur)
const save = (user: IUser): Promise<AxiosResponse<IUser>> => (
  CustomAxios.put("auth/current-user/me/", user)
)

// Supprimer l'utilisateur connecté
const deleteUser = (): Promise<AxiosResponse<void>> => (
  CustomAxios.delete("auth/user-delete/me/")
);

const UserDS = {
  changePassword,
  get,
  login,
  logout,
  register,
  save,
  deleteUser,
}

export default UserDS;
