import { useState } from "react";
import { NavigateFunction, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";  //Hook de la bibliothèque react-hook-form pour la gestion des formulaires
import { yupResolver } from "@hookform/resolvers/yup";  //Intégration de yup avec react-hook-form pour la validation des champs.
import * as yup from "yup"; //Bibliothèque de validation des données.
import {
  Alert,
  Box,
  Button,
  IconButton,
  InputAdornment,
  Link,
  Typography,
} from "@mui/material";
//Icônes pour afficher/cacher le mot de passe.
import VisibilityIcon from "@mui/icons-material/Visibility";
import VisibilityOffIcon from "@mui/icons-material/VisibilityOff";
import FormTextField from "../controls/FormTextField";
import ProgressBackdrop from "../controls/ProgressBackdrop";
import UserDS from "../../data_services/UserDS";
import ReCAPTCHA from "react-google-recaptcha";



//Définit un type TypeScript FormLoginFields contenant les champs du formulaire
type FormLoginFields = {
  username: string;
  password: string;
};

function LoginView() {
  const navigate: NavigateFunction = useNavigate();

  const [showPassword, setShowPassword] = useState(false);  //Gère l’affichage du mot de passe
  const [submitWarning, setSubmitWarning] = useState("");   //Stocke un message d’avertissement si l’utilisateur n’a pas de compte actif.
  const [submitError, setSubmitError] = useState("");       //Stocke un message d’erreur en cas d’échec de la connexion
  const [submitting, setSubmitting] = useState(false);      // Indique si le formulaire est en train d’être soumis (utilisé pour afficher un chargement).
  const [recaptchaToken, setRecaptchaToken] = useState<string | null>(null);


  //Définition du schéma de validation avec la bibliothèque yup
  const formSchema = yup.object().shape({
    username: yup.string().required("Le nom d'utilisateur est obligatoire"),
    password: yup.string().required("Le mot de passe est obligatoire"),
  });

  
  //Initialisation du formulaire
  const {
    formState: { errors },  //Contient les erreurs de validation.
    handleSubmit, //Une fonction pour gérer la soumission du formulaire.
    register, //Permet d’enregistrer les champs du formulaire.
  } = useForm<FormLoginFields>({
    resolver: yupResolver(formSchema),
  });

  //Fonction pour afficher/masquer le mot de passe
  const handleShowPasswordClick = (): void => {
    setShowPassword((prev) => !prev);
  };

  //Gestion de la soumission du formulaire, Ici data est de type TypeScript FormLoginFields définit plus haut.
  const handleFormSubmit = (data: FormLoginFields): void => {
    //Réinitialisation des messages d'erreur
    setSubmitWarning("");
    setSubmitError("");
    setSubmitting(true);

    UserDS.login(data.username, data.password, recaptchaToken)
      .then(() => {
        navigate("/"); //En cas de succes l’utilisateur est redirigé vers la route de path /.
      })
      .catch((err) => {
        if (
          err.response.status === 401 &&
          err.response.data === "no_active_account"
        ) {
          setSubmitWarning("Aucun compte actif n'a été trouvé.");
        } else {
          setSubmitError(
            "Une erreur s'est produite lors de la connexion, veuillez réessayer."
          );
        }
      })
      .finally(() => {
        setSubmitting(false); //assure que submitting est remis à false après la requête.
      });
  };

  //Gestion du clic sur "S'inscrire": quand l'utilisateur clique sur ce bouton il est redirigé vers la page d'inscription
  const handleSignUpClick = () => {
    navigate("/signup/");
  };

  return (
    <>
      <Typography component="h1" variant="h5">
        S'identifier
      </Typography>
      {/* Box agit comme un <form>, sans validation HTML (noValidate). */}
      <Box 
        component="form"
        noValidate
        onSubmit={handleSubmit(handleFormSubmit)}
        sx={{ mt: 1, width: "100%" }}
      >
        <FormTextField
          autoComplete="username"
          autoFocus
          errorText={errors.username?.message}  //affiche un message d’erreur en cas de champ vide
          label="Nom d'utilisateur"
          registerReturn={register("username")}
        />
        <FormTextField
          autoComplete="current-password"
          errorText={errors.password?.message}  //affiche un message d’erreur en cas de champ vide
          label="Mot de passe"
          slotProps={{
            input: {
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton //Affiche/cache le mot de passe avec IconButton.
                    aria-label="toggle password visibility"
                    onClick={() => handleShowPasswordClick()}
                    onMouseDown={(e) => e.preventDefault()}
                    edge="end"
                  >
                    {showPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
                  </IconButton>
                </InputAdornment>
              ),
            },
          }}
          registerReturn={register("password")}
          type={showPassword ? "text" : "password"}
        />

{/* Affiche un message d'avertissement ou d'erreur. */}
        {submitWarning !== "" && (
          <Alert severity="warning" sx={{ mt: 2 }}>
            {submitWarning}
          </Alert>
        )}
        {submitError !== "" && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {submitError}
          </Alert>
        )}

        <ReCAPTCHA
            sitekey="6LfwcOUqAAAAAE5ZymKUfkCTrdVO8_X_SDg1Msqt"
            onChange={(token: string | null) => setRecaptchaToken(token)}
            onExpired={() => setRecaptchaToken(null)}
        />


        <Button
          color="primary"
          fullWidth
          sx={{ mb: 2, mt: 3 }}
          type="submit"
          variant="contained"
        >
          Se connecter
        </Button>
        <Link
          component="div"
          onClick={handleSignUpClick}
          sx={{ cursor: "pointer" }}
          textAlign="right"
          variant="body2"
        >
          Vous n'avez pas de compte? S'inscrire
        </Link>
      </Box>
      {/* Affichage du chargement: Affiche un "loader" lorsque submitting est true */}
      <ProgressBackdrop open={submitting} />
    </>
  );
}

export default LoginView;
