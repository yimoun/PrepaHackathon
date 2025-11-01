import { useState } from "react";
import { NavigateFunction, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as yup from "yup";
import { Alert, Box, Button, Container, Typography } from "@mui/material";
import FormTextField from "../controls/FormTextField";
import ProgressBackdrop from "../controls/ProgressBackdrop";
import UserDS from "../../data_services/UserDS";

type FormPasswordEditFields = {
  password: string;
  confirmPassword: string;
};

function PasswordEdit() {
  const navigate: NavigateFunction = useNavigate();
  const [submitError, setSubmitError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const formSchema = yup.object().shape({
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
  } = useForm<FormPasswordEditFields>({
    resolver: yupResolver(formSchema),
  });

  const handleFormSubmit = (data: FormPasswordEditFields): void => {
    setSubmitError("");
    setSubmitting(true);

    UserDS.changePassword(data.password)
      .then(() => {
        navigate("/");
      })
      .catch(() => {
        setSubmitError(
          "Une erreur s'est produite lors du changement de mot de passe, veuillez réessayer."
        );
      })
      .finally(() => {
        setSubmitting(false);
      });
  };

  const handlePasswordEditClick = (): void => {
    navigate("/user-edit/me/");
  };

  return (
    <Container maxWidth="xs">
      <Typography component="h1" textAlign="center" variant="h5">
        Changer votre mot de passe
      </Typography>
      <Box
        component="form"
        noValidate
        onSubmit={handleSubmit(handleFormSubmit)}
        sx={{ mt: 3, width: "100%" }}
      >
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
        {submitError !== "" && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {submitError}
          </Alert>
        )}
        <Button
          color="primary"
          fullWidth
          sx={{ mb: 2, mt: 3 }}
          type="submit"
          variant="contained"
        >
          Enregistrer
        </Button>
        <Box sx={{ display: "flex", justifyContent: "right" }}>
          <Button
            onClick={handlePasswordEditClick}
            size="small"
            sx={{ fontSize: "14px", textTransform: "none" }}
            variant="text"
          >
            Annuler
          </Button>
        </Box>
      </Box>
      <ProgressBackdrop open={submitting} />
    </Container>
  );
}

export default PasswordEdit;
