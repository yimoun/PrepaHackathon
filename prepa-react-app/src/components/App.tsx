import { useEffect } from "react";
import { Outlet } from "react-router-dom";
import { Box } from "@mui/material";
import UserContext, { UserContextState, IUserContext } from "../contexts/UserContext";
import Banner from "./Banner";
import Footer from "./Footer";

function App() {
  const userContextState: IUserContext = UserContextState();

  useEffect(() => {
    console.log(" Chargement initial de l'utilisateur...");
    userContextState.refreshUser();
  }, []);  // <-- Charge l'utilisateur au démarrage

  return (
    <UserContext.Provider value={userContextState}>
  <Box
    sx={{
      display: "flex",
      flexDirection: "column",
      minHeight: "100vh", // Assure que le contenu prend toute la hauteur
      alignItems: "center", // Centre le contenu global
      padding:8
    }}
  >
    <Banner />
    <Box
      sx={{
        width: "100%",
        maxWidth: "1200px",   // Limite la largeur max (responsive pour desktop)
        flex: 1,               // Permet au contenu de remplir la hauteur restante
        padding: 2,             // Ajoute des marges internes
      }}
    >
      <Outlet />
    </Box>
    <Footer />
  </Box>
    </UserContext.Provider>

  );
}

export default App;
