// src/components/GameHistory.tsx
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
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  CircularProgress,
} from "@mui/material";
import UserContext from "../../contexts/UserContext";
//import GameHistoryDS from "../../data_services/GameHistoryDS";
import IAlerte from "../../data_interfaces/IAlerte";

function ModeleIAHistory() {
  const { token } = useContext(UserContext);
  //const [gameHistory, setGameHistory] = useState<[]>([]);
  const [gameHistory, setGameHistory] = useState<IAlerte[]>([]);
  const [loading, setLoading] = useState(true);
  const [limit, setLimit] = useState(20);
  const [dialogOpen, setDialogOpen] = useState(false);

  useEffect(() => {
    if (token) {
      fetchHistory(limit);
    }
  }, [token, limit]);

  const fetchHistory = async (selectedLimit: number) => {
    setLoading(true);
    const data = []
    //const data = await GameHistoryDS.fetchUserGameHistory(selectedLimit);
    // Trier par date décroissante
    //data.sort((a, b) => new Date(b.date_played).getTime() - new Date(a.date_played).getTime());
    setGameHistory(data);
    setLoading(false);

    console.log(gameHistory)
  };

  return (
    <Container maxWidth="md" sx={{ marginY: "2rem" }}>
      <Paper style={{ padding: "1rem", textAlign: "center" }}>
        <Typography variant="h5" gutterBottom>
          Historique des Parties
        </Typography>

        {/* Sélection du nombre de parties à afficher */}
        <FormControl sx={{ marginBottom: "1rem", minWidth: 120 }}>
          <InputLabel>Nombre</InputLabel>
          <Select value={limit} onChange={(e) => setLimit(e.target.value as number)}>
            <MenuItem value={20}>20</MenuItem>
            <MenuItem value={50}>50</MenuItem>
            <MenuItem value={100}>100</MenuItem>
          </Select>
        </FormControl>

        {/* {loading ? (
          <CircularProgress />
        ) : gameHistory.length === 0 ? (
          <Typography>Aucun historique trouvé.</Typography>
        ) : (
          gameHistory.map((game) => (
            <Paper key={game.id} sx={{ padding: "1rem", marginY: "0.5rem" }}>
              <Typography variant="subtitle1">
                {new Date(game.date_played).toLocaleString()}
              
              </Typography>
              <Typography variant="body2">
                Niveau : <strong>{game.level}</strong> | Durée : {game.duration} sec | Tentatives : {game.attempts}
              </Typography>
              <Typography variant="caption" color={game.completed ? "success.main" : "error.main"}>
                {game.completed ? "Terminé ✅" : "Non complété ❌"}
              </Typography>
            </Paper>
          ))
        )} */}

        <Button variant="contained" color="primary" sx={{ marginTop: "1rem" }} onClick={() => setDialogOpen(true)}>
          Afficher l'historique
        </Button>

        {/* Dialog pour affichage détaillé */}
        <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
          <DialogTitle>Historique des Parties</DialogTitle>
          <DialogContent>
            {/* {gameHistory.map((game) => (
              <Paper key={game.id} sx={{ padding: "1rem", marginY: "0.5rem" }}>
                <Typography variant="subtitle1">
                  {new Date(game.date_played).toLocaleString()}
                </Typography>
                <Typography variant="body2">
                  Niveau : <strong>{game.level}</strong> | Durée : {game.duration} sec | Tentatives : {game.attempts}
                </Typography>
                <Typography variant="caption" color={game.completed ? "success.main" : "error.main"}>
                  {game.completed ? "Terminé ✅" : "Non complété ❌"}
                </Typography>
              </Paper>
            ))} */}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDialogOpen(false)} color="primary">
              Fermer
            </Button>
          </DialogActions>
        </Dialog>
      </Paper>
    </Container>
  );
}

export default ModeleIAHistory;
