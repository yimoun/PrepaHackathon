import IUser from './IUser'

export default interface IAuthResponse {
  access: string
  refresh: string
  user: IUser
}
