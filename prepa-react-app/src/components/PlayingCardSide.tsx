import { Card, CardActionArea, CardMedia, Typography } from "@mui/material";

type PlayingCardSideProps = {
  bgColor?: React.CSSProperties["backgroundColor"];
  emoji: string; // emoji représente maintenant une image pu un symbole
  onClick?: () => void; // Lorsqu'on clique sur la carte.
};

/* Ce composant représente une face d'une carte du jeu de mémoire affichant une image sur un fond coloré et peut être cliqué (retourner la carte) */

export default function PlayingCardSide({
  bgColor,
  emoji,
  onClick,
}: PlayingCardSideProps) {
  return (
    <Card onClick={onClick}>
      <CardActionArea
        sx={{
          alignItems: "center",
          backgroundColor: bgColor,
          display: "flex",
          height: 100,
          justifyContent: "center",
        }}
      >
        {/* <CardMedia
          component="img"
          image={emoji} // emoji est une image ici
          alt="playing card"
          sx={{ width: "80%", height: "auto" }}
        /> */}

        
        {/* Vérifie si l'emoji est une image ou un caractère */}
        {emoji.startsWith("http") || emoji.includes("/") ? (
          <CardMedia
            component="img"
            image={emoji} // emoji est une image ici
            alt="playing card"
            sx={{ width: "80%", height: "auto" }}
          />
        ) : (
          <Typography variant="h3">{emoji}</Typography> // Affiche "❓" en tant que texte
        )}


      </CardActionArea>

      
    </Card>
  );
}
