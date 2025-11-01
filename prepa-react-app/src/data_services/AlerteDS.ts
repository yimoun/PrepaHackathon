import { AxiosResponse, AxiosError } from "axios";
import IAlerte from "../data_interfaces/IAlerte";
import CustomAxios from "./CustomAxios"; // Importez votre instance CustomAxios

const API_URL = "alertes/"; // Utilisez le chemin relatif car l'URL de base est déjà définie dans CustomAxios

export default class AlerteDS {
  static async fetchAlertes(): Promise<IAlerte[]> {
    try {
      // Utilisez CustomAxios pour effectuer la requête
      const response: AxiosResponse<IAlerte[]> = await CustomAxios.get(API_URL);
      return response.data; // Retourne les données des alertes
    } catch (error) {
      const axiosError = error as AxiosError; // Typage explicite de l'erreur

      if (axiosError.response) {
        console.error("Erreur côté serveur :", axiosError.response.data);
      } else if (axiosError.request) {
        console.error("Pas de réponse du serveur :", axiosError.request);
      } else {
        console.error("Erreur lors de la configuration de la requête :", axiosError.message);
      }

      return []; // Retourne un tableau vide en cas d'erreur
    }
  }

  static async createAlerte(data: Partial<IAlerte> | null): Promise<IAlerte> {
    try {
      // Utilisez CustomAxios pour effectuer la requête
      const response: AxiosResponse<IAlerte> = await CustomAxios.post(API_URL, data);
      return response.data; // Retourne l'alerte créée
    } catch (error) {
      const axiosError = error as AxiosError; // Typage explicite de l'erreur

      if (axiosError.response) {
        console.error("Erreur côté serveur :", axiosError.response.data);
      } else if (axiosError.request) {
        console.error("Pas de réponse du serveur :", axiosError.request);
      } else {
        console.error("Erreur lors de la configuration de la requête :", axiosError.message);
      }

      throw error; // Propage l'erreur pour la gestion ultérieure
    }
  }

//TODO: Je ne pense que nous aurons besoin de modifier un modèle IA, donc ce code est commenté pour l'instant.
  // static async updateModelIA(id: number, data: Partial<IModelIA>): Promise<IModelIA> {
  //   try {
  //     // Utilisez CustomAxios pour effectuer la requête
  //     const response: AxiosResponse<IModelIA> = await CustomAxios.put(`${API_URL}${id}/`, data);
  //     return response.data; // Retourne le modèle IA mis à jour
  //   } catch (error) {
  //     const axiosError = error as AxiosError; // Typage explicite de l'erreur

  //     if (axiosError.response) {
  //       console.error("Erreur côté serveur :", axiosError.response.data);
  //     } else if (axiosError.request) {
  //       console.error("Pas de réponse du serveur :", axiosError.request);
  //     } else {
  //       console.error("Erreur lors de la configuration de la requête :", axiosError.message);
  //     }

  //     throw error; // Propage l'erreur pour la gestion ultérieure
  //   }
  // }

  static async deleteAlerte(id: number): Promise<void> {
    try {
      // Utilisez CustomAxios pour effectuer la requête
      await CustomAxios.delete(`${API_URL}${id}/`);
    } catch (error) {
      const axiosError = error as AxiosError; // Typage explicite de l'erreur

      if (axiosError.response) {
        console.error("Erreur côté serveur :", axiosError.response.data);
      } else if (axiosError.request) {
        console.error("Pas de réponse du serveur :", axiosError.request);
      } else {
        console.error("Erreur lors de la configuration de la requête :", axiosError.message);
      }

      throw error; // Propage l'erreur pour la gestion ultérieure
    }
  }
}