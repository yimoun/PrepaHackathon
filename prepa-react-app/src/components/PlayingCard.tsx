import ReactCardFlip from "react-card-flip"; // Une bibliothèque React pour gérer le retournement des cartes.
import IPlayingCard from "../data_interfaces/IPlayingCard";
import PlayingCardSide from "./PlayingCardSide";
import { Box } from "@mui/material"; // Utilisation de MUI pour remplacer les balises HTML

type PlayingCardProps = {
  card: IPlayingCard;
  onSelect?: (card: IPlayingCard) => void; // Lorsqu'on sélectionne la carte jouable.
  backColor: string;  //Pour la couleur du dos de la carte.
};

/* Ce composant est une carte jouable du jeu de mémoire. Il gère l'affichage recto/verso et l'interaction quand on clique dessus. */
export default function PlayingCard({ card, onSelect, backColor }: PlayingCardProps) {
  const handleBackClick = () => {
    if (onSelect) {
      onSelect(card);
    }
  };

  return (
    <ReactCardFlip isFlipped={card.flipped}>
      {/* Recto (dos de la carte) */}
      <Box key="front">
        <PlayingCardSide
         bgColor={backColor}
          emoji="❓"
          onClick={handleBackClick}
        />
      </Box>

      {/* Verso (face visible de la carte) */}
      <Box key="back">
        <PlayingCardSide emoji={card.emoji} />
      </Box>
    </ReactCardFlip>
  );
}
