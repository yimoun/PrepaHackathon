import { useState, useEffect, useCallback} from "react";
import { Container, Typography, Paper, Button, ButtonGroup, Dialog, DialogTitle, 
DialogContent, DialogContentText, DialogActions,  Box } from "@mui/material";

import { useNavigate } from "react-router-dom";

import { storageAccessTokenKey } from "../../data_services/CustomAxios";  

//Récupération des images 
const allImages: string[] = []; 

// const allImages = Object.values(
//   import.meta.glob("/src/assets/img/*.{png,jpg,jpeg,svg}", { eager: true })
// ).map((img) => {
//   if (img && typeof img === "object" && "default" in img) {
//     return img.default as string;
//   }
//   return "";  // Retourne une chaîne vide si `img` est `null` ou `undefined`
// });

const getRandomImages = (count: number) => {
  let shuffled = allImages.sort(() => Math.random() - 0.5);
  return shuffled.slice(0, count);
};

const gridOptionsGuest = [{ label: "4x4", rows: 4, cols: 4 }];
const gridOptionsUser = [
  { label: "4x3", rows: 3, cols: 4 },
  { label: "4x4", rows: 4, cols: 4 },
  { label: "5x4", rows: 4, cols: 5 },
  { label: "6x4", rows: 4, cols: 6 },
  { label: "6x5", rows: 5, cols: 6 },
  { label: "6x6", rows: 6, cols: 6 },
];


// Fonction pour déterminer le niveau de difficulté en fonction de la taille de la grille
const getDifficultyLevel = (rows: number, cols: number): "easy" | "medium" | "hard" => {
  const totalCards = rows * cols;
  if (totalCards <= 12) return "easy";
  if (totalCards <= 20) return "medium";
  return "hard";
};

 function IADetection() {
  const navigate = useNavigate();

  const isLogged = localStorage.getItem(storageAccessTokenKey) !== null;

  
  const [matches, setMatches] = useState(0);
  const [attempts, setAttempts] = useState(0);
  const [backColor, setBackColor] = useState<string>("ghostwhite"); //État pour la couyleyur du dos des cartes.
  const [gridSize, setGridSize] = useState({ rows: 4, cols: 4 });  // État pour la taille de la grille par défaut : 4x4
  const [rulesOpen, setRulesOpen] = useState(false);
  const [startTime, setStartTime] = useState<number | null>(null); // Pour suivre la durée de la partie
  const [gameInProgress, setGameInProgress] = useState(false);

  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const [newGridSize, setNewGridSize] = useState({ rows: 4, cols: 4 }); // Pour stocker la nouvelle taille de grille choisie

  // Fonction pour sauvegarder le résultat d'une partie
  const saveGameResult = useCallback(async (completed: boolean) => {
    if (isLogged && startTime && attempts > 0) {
      const duration = Math.floor((Date.now() - startTime) / 1000);
      const level = getDifficultyLevel(gridSize.rows, gridSize.cols);
      
      try {
        // await GameHistoryDS.saveGameResult(
        //   level,
        //   duration,
        //   attempts,
        //   completed
        // );
        console.log(`Partie ${completed ? 'complétée' : 'non complétée'} sauvegardée`);
      } catch (error) {
        console.error("Erreur lors de la sauvegarde de la partie:", error);
      }
    }
  }, [isLogged, startTime, attempts, gridSize]);



  //Fonction pour générer les cartes en fonction de la taille choisie
  const generateCards = useCallback((rows: number, cols: number) => {
    const numPairs = (rows * cols) / 2;
    const selectedImages = getRandomImages(numPairs);

    // const newCards: IPlayingCard[] = [...selectedImages, ...selectedImages]
    //   .sort(() => Math.random() - 0.5)
    //   .map((emoji, index) => ({
    //     id: index,
    //     emoji,
    //     flipped: false,
    //     matched: false,
    //   } as IPlayingCard));

    //setCards(newCards);
    setMatches(0);
    setAttempts(0);
    //setSelectedCards([]);
    setStartTime(Date.now());
    setGameInProgress(true);
  }, [])

  // Effet pour générer une nouvelle partie quand la taille de la grille change
  useEffect(() => {
    if (gameInProgress && attempts > 0) {
      saveGameResult(false); // Sauvegarder la partie non complétée avant de changer de grille
    }
    generateCards(gridSize.rows, gridSize.cols);
  }, [gridSize]);

  // Gestion du changement de grille
  const handleGridSizeChange = (cols: number, rows: number) => {
    if (gameInProgress && attempts > 0) {
      setNewGridSize({ cols, rows }); // Stocker la nouvelle taille de grille
      setConfirmDialogOpen(true); // Ouvrir la boîte de dialogue
    } else {
      setGridSize({ cols, rows });
      generateCards(cols, rows);
    }
  };

  

  // useEffect(() => {
  //   if (selectedCards.length === 2) {
  //     const [firstCard, secondCard] = selectedCards;
  //     if (firstCard.emoji === secondCard.emoji) { //Quand deux cartes sont sélectionnées, si elles correspondent, elles deviennent "matched: true"
  //       setTimeout(() => {
  //         setCards((prev) =>
  //           prev.map((card) =>
  //             card.id === firstCard.id || card.id === secondCard.id
  //               ? { ...card, matched: true }
  //               : card
  //           )
  //         );
  //         setMatches((prev) => prev + 1); //Le nombre de paires trouvées augmentent.
  //       }, 600);
  //     } else {  //Sinon, elles se retournent après 1000ms
  //       setTimeout(() => {
  //         setCards((prev) =>
  //           prev.map((card) =>
  //             card.id === firstCard.id || card.id === secondCard.id
  //               ? { ...card, flipped: false }
  //               : card
  //           )
  //         );
  //       }, 1000);
  //     }
  //     setAttempts((prev) => prev + 1);  //Les tentatives sont comptées à chaque fois.
  //     setSelectedCards([]);
  //   }
  // }, [/*cards, */ selectedCards]);

  //  // Effet pour détecter quand une partie est gagnée
  //  useEffect(() => {
  //   if (gameInProgress && cards.length > 0 && attempts > 0) {
  //     const allMatched = cards.every((card) => card.matched);
  //     if (allMatched) {
  //       saveGameResult(true);
  //       setGameInProgress(false);
  //     }
  //   }
  // }, [matches, cards, gameInProgress, attempts, saveGameResult]);


  //  // Sauvegarder la partie non complétée quand l'utilisateur change de grille
  //  useEffect(() => {
  //   if (gameInProgress && isLogged && !cards.every((card) => card.matched)) {
  //     saveGameResult(false);
  //   }
  // }, [gridSize, gameInProgress, isLogged, cards, saveGameResult]);

 /*Empêche de retourner une carte déja retournée et limite le nombre de cartes retournées à 2 */
//  const tryFlipCard = useCallback((cardToFlip: IPlayingCard) => {
//   if (!cardToFlip.flipped && selectedCards.length < 2) {
//     setCards((prev) =>
//       prev.map((card) =>
//         card.id === cardToFlip.id ? { ...card, flipped: true } : card
//       )
//     );
//     setSelectedCards((prev) => [...prev, cardToFlip]);
//   }
// }, [selectedCards]);

//const gridOptions = useMemo(() => user ? gridOptionsUser : gridOptionsGuest, [user]);

return (
  <Container maxWidth="md" 
  sx={{
    marginY: "1rem",
    paddingX: { xs: 1, sm: 2 }, // Ajoute un petit padding latéral sur mobile
    aspectRatio: "1 / 1" // Forcer une forme carrée (largeur = hauteur)
}}>
    <Paper style={{ padding: "1rem", textAlign: "center" }}>
      <Typography variant="h4" gutterBottom>
       Outil de détection de port de casque et de lunettes de protection
      </Typography>
    

      <Box sx={{ display: "flex", flexDirection: "column", gap: 3, alignItems: "center", mb: 2, height: "100%"   }}>
            <Button
                variant="contained"
                color="secondary"
                onClick={() => setRulesOpen(true)}
            >
               Cliquez ici pour ouvrir la caméra et commencer la détection
            </Button>

            <Box
              sx={{
                  display: "flex",
                  justifyContent: "center",
                  gap: 2,
                  flexWrap: "wrap", // Si l’écran est trop étroit, ils passent l’un sous l’autre
                  alignItems: "center"
              }}
            >
              
            </Box>
        </Box>

        


       {/* Boutons pour changer la couleur du dos des cartes */}
       <Typography variant="body2" sx={{ marginBottom: "2rem" }}>
            Moifiier la couleur du dos des cartes
      </Typography>
       <ButtonGroup sx={{ marginBottom: "1rem" }}>
        <Button 
          onClick={() => setRulesOpen(true)} 
          sx={{ backgroundColor: "ghostwhite" }}>
          Blanc
        </Button>
      </ButtonGroup>

       {/*  Sélecteur de taille de grille */}
       <Typography variant="h6" sx={{ marginBottom: "1rem" }}>
        Sélectionnez la taille de la grille :
      </Typography>
    <Box
      sx={{
        display: "grid",
        gridTemplateRows: `repeat(${gridSize.cols}, 1fr)`, // définit le nombre de lignes
        gridTemplateColumns: `repeat(${gridSize.rows}, 1fr)`, // Définit les bonnes colonnes
        gap: "10px", // Espacement entre les cartes
        justifyContent: "center",
      }}
    >
   
    </Box>

    <Dialog open={rulesOpen} onClose={() => setRulesOpen(false)}>
        <DialogTitle>Règlements du jeu</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Le but du jeu est de retrouver toutes les paires de cartes en un minimum de coups.
            <br />
            - Retournez deux cartes à la fois.
            <br />
            - Si elles correspondent, elles restent visibles.
            <br />
            - Sinon, elles se retournent après un instant.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRulesOpen(false)}>Fermer</Button>
        </DialogActions>
      </Dialog>


    </Paper>
  </Container>
); 

}

export default IADetection;





