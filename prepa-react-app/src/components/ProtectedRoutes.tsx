import { Navigate, Outlet } from "react-router-dom";
import { storageAccessTokenKey } from "../data_services/CustomAxios";

function ProtectedRoutes() {
  return (
    <>
      {localStorage.getItem(storageAccessTokenKey) ? (
        <Outlet />
      ) : (
        <Navigate to="/login/" />
      )}
    </>
  );
}

export default ProtectedRoutes;
