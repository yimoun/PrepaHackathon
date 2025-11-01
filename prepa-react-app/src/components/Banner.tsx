import { useContext } from "react";
import { useNavigate } from "react-router-dom";
import UserContext, { IUserContext } from "../contexts/UserContext";
import { AppBar, Button, Container, Link, Toolbar, Typography } from "@mui/material";
import BannerUserMenu from "./BannerUserMenu";


function Banner() {
  const navigate = useNavigate();
  const userContext: IUserContext = useContext(UserContext);
  console.log("UserContext dans Banner :", userContext);

  const handleHomeClick = () => navigate("/");
  const handleLoginClick = () => navigate("/login/");

  return (
    <AppBar position="fixed">
      <Container component="nav" disableGutters={true}>
        <Toolbar>
          <Link
            color="inherit"
            onClick={handleHomeClick}
            sx={{ cursor: "pointer", flexGrow: 1, textDecoration: "none" }}
          >
            <Typography variant="h6">PrépaHackathon</Typography>
          </Link>

          {userContext.user ? (
            <>
              <Typography variant="body1" sx={{ marginRight: 2 }}>
                Bonjour, {userContext.user.username}
              </Typography>
              <BannerUserMenu />
            </>
          ) : (
            <Button color="primary" variant="contained" onClick={handleLoginClick}>
              Se connecter
            </Button>
          )}
        </Toolbar>
      </Container>
    </AppBar>
  );
}

export default Banner;
