import { useState } from "react";
import { NavigateFunction, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as yup from "yup";
import { Alert, Box, Button, Link, Typography } from "@mui/material";
import FormTextField from "../controls/FormTextField";
import ProgressBackdrop from "../controls/ProgressBackdrop";
import IUser from "../../data_interfaces/IUser";
import UserDS from "../../data_services/UserDS";
// @ts-ignore: no types for react-google-recaptcha available
import ReCAPTCHA from "react-google-recaptcha";


type FormSignUpFields = {
  firstname: string;
  lastname: string;
  email: string;
  username: string;
  password: string;
  confirmPassword: string;
};

function SignUpView() {
  const navigate: NavigateFunction = useNavigate();
  const [submitWarning, setSubmitWarning] = useState("");
  const [submitError, setSubmitError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [recaptchaToken, setRecaptchaToken] = useState<string | null>(null);


  const formSchema = yup.object().shape({
    firstname: yup
      .string()
      .required("Le prénom est obligatoire")
      .max(50, "Le prénom doit contenir au plus 50 caractères"),
    lastname: yup
      .string()
      .required("Le nom de famille est obligatoire")
      .max(50, "Le nom de famille doit contenir au plus 50 caractères"),
    username: yup
      .string()
      .required("Le nom d'utilisateur est obligatoire")
      .max(150, "Le nom d'utilisageur doit contenir au plus 150 caractères"),
    email: yup
      .string()
      .required("Le courriel est obligatoire")
      .email("Le courriel doit être valide")
      .max(100, "Le courriel doit contenir au plus 100 caractères"),
    password: yup
      .string()
      .required("Le mot de passe est obligatoire")
      .max(100, "Le mot de passe doit contenir au plus 100 caractères")
      .min(8, "Le mot de passe doit contenir au moins 8 caractères"),
    confirmPassword: yup
      .string()
      .required("La confirmation du mot de passe est obligatoire")
      .oneOf([yup.ref("password")], "Les mots de passe ne correspondent pas"),
  });

  const {
    formState: { errors },
    handleSubmit,
    register,
  } = useForm<FormSignUpFields>({
    resolver: yupResolver(formSchema),
  });

  const handleFormSubmit = (data: FormSignUpFields): void => {
    console.log("Données du formulaire :", data);
    setSubmitWarning("");
    setSubmitError("");
    setSubmitting(true);

    const newUser: IUser = {
      first_name: data.firstname,
      last_name: data.lastname,
      username: data.username,
      email: data.email,
    };

    UserDS.register(newUser, data.password, recaptchaToken)
      .then(() => {
        navigate("/login/");
      })
      .catch((err) => {
        if (
          err.response.status === 400 &&
          err.response.data === "username_already_exists"
        ) {
          setSubmitWarning(
            "Ce nom d'utilisateur est déjà utilisé, veuillez en choisir un autre."
          );
        } else if (
          err.response.status === 400 &&
          err.response.data === "email_already_exists"
        ) {
          setSubmitWarning(
            "Ce courriel est déjà utilisé, veuillez en choisir un autre."
          );
        } else {
          setSubmitError(
            "Une erreur s'est produite lors de l'inscription, veuillez réessayer."
          );
        }
      })
      .finally(() => {
        setSubmitting(false);
      });
  };

  const handleLoginClick = () => {
    navigate("/login/");
  };

  return (
    <>
      <Typography component="h1" variant="h5">
        S'inscrire
      </Typography>
      <Box
        component="form"
        noValidate
        onSubmit={handleSubmit(handleFormSubmit)}
        sx={{ mt: 1, width: "100%" }}
      >
        <FormTextField
          autoComplete="firstname"
          autoFocus
          errorText={errors.firstname?.message}
          label="Prénom"
          registerReturn={register("firstname")}
        />
        <FormTextField
          autoComplete="lastname"
          errorText={errors.lastname?.message}
          label="Nom de famille"
          registerReturn={register("lastname")}
        />
        <FormTextField
          autoComplete="email"
          errorText={errors.email?.message}
          label="Courriel"
          registerReturn={register("email")}
        />
        <FormTextField
          autoComplete="username"
          errorText={errors.username?.message}
          label="Nom d'utilisateur"
          registerReturn={register("username")}
        />
        <Box sx={{ color: "#999", fontSize: "11px" }}>
          Lettres, chiffres et @/./+/-/_ uniquement.
        </Box>
        <FormTextField
          autoComplete="new-password"
          errorText={errors.password?.message}
          label="Mot de passe"
          registerReturn={register("password")}
          type="password"
        />
        <Box sx={{ color: "#999", fontSize: "11px" }}>
          Votre mot de passe doit contenir au moins 8 caractères.
        </Box>
        <FormTextField
          autoComplete="new-password"
          errorText={errors.confirmPassword?.message}
          label="Confirmation du mot de passe"
          registerReturn={register("confirmPassword")}
          type="password"
        />
        <Box sx={{ color: "#999", fontSize: "11px" }}>
          Entrez le même mot de passe que précédemment pour vérification.
        </Box>
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
            sitekey="6LfwcOUqAAAAAE5ZymKUfkCTrdVO8_X_SDg1Msqt"  // Remplace par ta vraie clé Site Key (donnée par Google)
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
          S'inscrire
        </Button>
        <Link
          component="div"
          onClick={handleLoginClick}
          sx={{ cursor: "pointer" }}
          textAlign="right"
          variant="body2"
        >
          Vous avez déjà un compte? Se connecter
        </Link>
      </Box>
      <ProgressBackdrop open={submitting} />
    </>
  );
}

export default SignUpView;
