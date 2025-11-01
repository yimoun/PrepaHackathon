import { useEffect } from "react";
import { Navigate } from "react-router-dom";
import UserDS from "../../data_services/UserDS";

function Logout() {
  useEffect(() => {
    UserDS.logout();
  });

  return <Navigate to="/" />;
}

export default Logout;
