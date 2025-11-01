import { useState, useEffect, useContext } from "react";
import {
  Container,
  Typography,
  Paper,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from "@mui/material";
import { Rating } from "@mui/material";
import UserContext from "../../contexts/UserContext";
import IAlerte from "../../data_interfaces/IAlerte";
import AlerteDS from "../../data_services/AlerteDS";
function AlertesList() {
  const { user } = useContext(UserContext);
  const [alertes, setAlertes] = useState<IAlerte[]>([]);
  const [newRating, setNewRating] = useState<number | null>(0);
  const [newComment, setNewComment] = useState("");
  const [userAlerte, setUserAlerte] = useState<IAlerte | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [confirmDeleteOpen, setConfirmDeleteOpen] = useState(false); // Dialog de confirmation

  const userEvaluation = alertes.find((a) => user && a.employe.username === user.username) || null;

  useEffect(() => {
    fetchAlertes();
  }, []);

  const fetchAlertes = async () => {
    try {
      const data = await AlerteDS.fetchAlertes();
      setAlertes(data);
      if (user) {
        const userAlerte = data.find((a) => a.employe.username === user.username);
        setUserAlerte(userAlerte || null);
      }
    } catch (error) {
      console.error("Erreur de récupération des alertes", error);
    }
  };

  const handleSubmit = async () => {
    // try {
    //   if (!newRating) return;
    //   if (userEvaluation) {
    //     await EvaluationDS.updateEvaluation(userEvaluation.id, userEvaluation);
    //   } else {
    //     await EvaluationDS.createEvaluation(userEvaluation);
    //   }
    //   fetchEvaluations();
    //   setDialogOpen(false);
    // } catch (error) {
    //   console.error("Erreur lors de l'envoi de l'évaluation", error);
    // }
  };

  // Ouvre la boîte de dialogue de confirmation avant de supprimer
  const handleOpenDeleteDialog = () => {
    setConfirmDeleteOpen(true);
  };

  const handleDelete = async () => {
    // try {
    //   if (userEvaluation) {
    //     await EvaluationDS.deleteEvaluation(userEvaluation.id);
    //     setUserEvaluation(null);
    //     fetchEvaluations();
    //   }
    // } catch (error) {
    //   console.error("Erreur lors de la suppression de l'évaluation", error);
    // } finally {
    //   setConfirmDeleteOpen(false);
    //   setDialogOpen(false);
    // }
  };

  return (
    <Container maxWidth="sm" sx={{ marginY: "1rem" }}>
      <Paper style={{ padding: "1rem", textAlign: "center" }}>
        <Typography variant="h5">Avis des joueurs</Typography>
        {alertes.map((alerte) => (
          <Paper key={alerte.id} sx={{ padding: "1rem", marginY: "0.5rem" }}>
            <Typography variant="subtitle1">{alerte.employe.username}</Typography>
            <Rating value={Number(alerte.niveau ?? 0)} precision={0.5} readOnly />
            <Typography variant="body2">{alerte.commentaire}</Typography>
            <Typography variant="caption" color="textSecondary">
              {new Date(alerte.created_at).toLocaleString()}
            </Typography>
          </Paper>
        ))}
        {user && (
          <>
            <Button
              variant="contained"
              color="primary"
              onClick={() => setDialogOpen(true)}
            >
              {userEvaluation ? "Modifier ou supprimer mon évaluation" : "Laisser une évaluation"}
            </Button>
            <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
              <DialogTitle>
                {userEvaluation ? "Modifier ou supprimer votre évaluation" : "Laisser une évaluation"}
              </DialogTitle>
              <DialogContent>
                <Rating
                  value={newRating}
                  onChange={(_, newValue) => setNewRating(newValue)}
                  precision={0.5}
                />
                <TextField
                  fullWidth
                  label="Votre commentaire"
                  multiline
                  rows={3}
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                  sx={{ marginTop: "1rem" }}
                />
              </DialogContent>
              <DialogActions>
                <Button onClick={() => setDialogOpen(false)}>Annuler</Button>
                {userEvaluation && (
                  <Button onClick={handleOpenDeleteDialog} color="error">
                    Supprimer
                  </Button>
                )}
                <Button onClick={handleSubmit} color="primary">
                  {userEvaluation ? "Modifier" : "Soumettre"}
                </Button>
              </DialogActions>
            </Dialog>

            {/* Dialog de confirmation de suppression */}
            <Dialog open={confirmDeleteOpen} onClose={() => setConfirmDeleteOpen(false)}>
              <DialogTitle>Confirmer la suppression</DialogTitle>
              <DialogContent>
                <Typography>
                  Êtes-vous sûr de vouloir supprimer votre évaluation ? Cette action est
                  irréversible.
                </Typography>
              </DialogContent>
              <DialogActions>
                <Button onClick={() => setConfirmDeleteOpen(false)}>Annuler</Button>
                <Button onClick={handleDelete} color="error">
                  Supprimer
                </Button>
              </DialogActions>
            </Dialog>
          </>
        )}
      </Paper>
    </Container>
  );
}

export default AlertesList;
