import IUser from "./IUser";

export default interface IAlerte {
    id: number;
    employe: IUser;
    modeleIA: number;
    typeEpiManquants: string;
    image: string;
    statut: string;
    created_at: string;
    updated_at: string;
    niveau: string;
    commentaire: string;
}
  