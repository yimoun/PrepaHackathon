import { useState, useContext } from "react";
import { NavigateFunction, useNavigate } from "react-router-dom";
import UserContext from "../contexts/UserContext";
import UserDS from "../data_services/UserDS";
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Divider,
  IconButton,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
  Tooltip,
  Typography,
} from "@mui/material";
import {
  AccountCircle as AccountCircleIcon,
  Logout as LogoutIcon,
  PersonOutlineOutlined as PersonOutlineOutlinedIcon,
  DeleteOutline as DeleteOutlineIcon,
} from "@mui/icons-material";

function BannerUserMenu(): React.JSX.Element {
  const navigate: NavigateFunction = useNavigate();
  const { user, logoutUser } = useContext(UserContext);
  const [userAnchorEl, setUserAnchorEl] = useState<HTMLElement | null>(null);
  const [deleteOpen, setDeleteOpen] = useState(false);

  const handleOpenUserMenu = (e: React.MouseEvent<HTMLElement>) => {
    setUserAnchorEl(e.currentTarget);
  };

  const handleCloseUserMenu = () => {
    setUserAnchorEl(null);
  };

  const handleUserEditClick = (): void => {
    setUserAnchorEl(null);
    navigate("/user-edit/me/");
  };

  const handleLogoutClick = (): void => {
    setUserAnchorEl(null);
    logoutUser();
    navigate("/");
  };

  const handleOpenDeleteDialog = (): void => {
    setUserAnchorEl(null);
    setDeleteOpen(true);
  };

  const handleCloseDeleteDialog = (): void => {
    setDeleteOpen(false);
  };

  const handleConfirmDelete = async (): Promise<void> => {
    setDeleteOpen(false);
    try {
      await UserDS.deleteUser();
      logoutUser();
      navigate("/");
    } catch (error) {
      console.error("Erreur lors de la suppression du compte", error);
    }
  };

  return (
    <>
      <Box>
        <Tooltip title={"Ouvrir le menu utilisateur"}>
          <IconButton
            aria-controls="user-menu-appbar"
            aria-haspopup="true"
            color="inherit"
            onClick={handleOpenUserMenu}
            sx={{ px: 0 }}
          >
            <AccountCircleIcon fontSize="large" />
          </IconButton>
        </Tooltip>
        <Menu
          anchorEl={userAnchorEl}
          anchorOrigin={{
            vertical: "top",
            horizontal: "right",
          }}
          id="user-menu-appbar"
          keepMounted
          onClose={handleCloseUserMenu}
          open={Boolean(userAnchorEl)}
          sx={{ mt: "30px" }}
          transformOrigin={{
            vertical: "top",
            horizontal: "right",
          }}
        >
          {user && (
            <MenuItem onClick={handleUserEditClick} sx={{ py: "4px" }}>
              <ListItemIcon>
                <PersonOutlineOutlinedIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText>
                <Typography sx={{ fontSize: "0.95rem" }}>{user.username}</Typography>
              </ListItemText>
            </MenuItem>
          )}
          <Divider />
          <MenuItem onClick={handleLogoutClick} sx={{ py: "4px" }}>
            <ListItemIcon>
              <LogoutIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText>
              <Typography sx={{ fontSize: "0.95rem" }}>Se déconnecter</Typography>
            </ListItemText>
          </MenuItem>
          <MenuItem onClick={handleOpenDeleteDialog} sx={{ py: "4px" }}>
            <ListItemIcon>
              <DeleteOutlineIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText>
              <Typography sx={{ fontSize: "0.95rem" }}>Supprimer mon profil</Typography>
            </ListItemText>
          </MenuItem>
        </Menu>
      </Box>
      <Dialog
        aria-describedby="delete-dialog-description"
        aria-labelledby="delete-dialog-title"
        onClose={handleCloseDeleteDialog}
        open={deleteOpen}
      >
        <DialogTitle id="delete-dialog-title">Confirmer la suppression</DialogTitle>
        <Divider />
        <DialogContent>
          <DialogContentText id="delete-dialog-description">
            Êtes-vous sûr de vouloir supprimer votre profil ? Cette action est irréversible.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDeleteDialog} color="primary">Annuler</Button>
          <Button onClick={handleConfirmDelete} color="error">Supprimer</Button>
        </DialogActions>
      </Dialog>
    </>
  );
}

export default BannerUserMenu;
