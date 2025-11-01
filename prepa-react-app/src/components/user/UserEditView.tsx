import { useEffect, useState } from "react";
import { NavigateFunction, useNavigate } from "react-router-dom";
import { storageUsernameKey } from "../../data_services/CustomAxios";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as yup from "yup";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Container,
  Typography,
} from "@mui/material";
import FormTextField from "../controls/FormTextField";
import ProgressBackdrop from "../controls/ProgressBackdrop";
import IUser from "../../data_interfaces/IUser";
import UserDS from "../../data_services/UserDS";

type FormUserEditFields = {
  firstname: string;
  lastname: string;
  email: string;
  username: string;
};

function UserEditView() {
  const navigate: NavigateFunction = useNavigate();
  const [isValidUser, setIsValidUser] = useState<boolean | null>(null);
  const [submitWarning, setSubmitWarning] = useState("");
  const [submitError, setSubmitError] = useState("");
  const [submitting, setSubmitting] = useState(false);

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
  });

  const {
    formState: { errors, isDirty },
    handleSubmit,
    register,
    reset,
  } = useForm<FormUserEditFields>({
    resolver: yupResolver(formSchema),
  });

  useEffect(() => {
    UserDS.get()
      .then((response) => {
        const formFields: FormUserEditFields = {
          firstname: response.data.first_name,
          lastname: response.data.last_name,
          email: response.data.email,
          username: response.data.username,
        };
        reset(formFields);
        setIsValidUser(true);
      })
      .catch((err) => {
        console.log(
          "ERROR: An error occurred while getting user info",
          err,
          err.response
        );
        setIsValidUser(false);
      });
  }, [reset]);

  const handleFormSubmit = (data: FormUserEditFields): void => {
    setSubmitWarning("");
    setSubmitError("");

    if (isDirty) {
      setSubmitting(true);

      const userToSave: IUser = {
        first_name: data.firstname,
        last_name: data.lastname,
        email: data.email,
        username: data.username,
      };

      UserDS.save(userToSave)
        .then((response) => {
          localStorage.setItem(storageUsernameKey, response.data.first_name);
          navigate("/");
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
              "Une erreur s'est produite lors de la modification de votre utilisateur, veuillez réessayer."
            );
          }
        })
        .finally(() => {
          setSubmitting(false);
        });
    } else {
      navigate("/");
    }
  };

  const handlePasswordEditClick = (): void => {
    navigate("/password-edit/me/");
  };

  return (
    <Container maxWidth="xs">
      <Typography component="h1" textAlign="center" variant="h5">
        Modification de votre profil
      </Typography>
      <Box
        component="form"
        noValidate
        onSubmit={handleSubmit(handleFormSubmit)}
        sx={{ mt: 3, width: "100%" }}
      >
        <Box sx={{ mb: 2, textAlign: "center" }}>
          {isValidUser === null && <CircularProgress sx={{ p: 0.5 }} />}
          {isValidUser === false && (
            <Alert severity="error" sx={{ textAlign: "left" }}>
              Une erreur s'est produite lors de l'obtention des informations
              utilisateur, le formulaire est désactivé.
            </Alert>
          )}
        </Box>
        <FormTextField
          autoComplete="firstname"
          autoFocus
          disabled={isValidUser !== true}
          errorText={errors.firstname?.message}
          label="Prénom"
          registerReturn={register("firstname")}
          slotProps={{
            inputLabel: {
              shrink: true,
            },
          }}
        />
        <FormTextField
          autoComplete="lastname"
          disabled={isValidUser !== true}
          errorText={errors.lastname?.message}
          label="Nom de famille"
          registerReturn={register("lastname")}
          slotProps={{
            inputLabel: {
              shrink: true,
            },
          }}
        />
        <FormTextField
          autoComplete="email"
          disabled={isValidUser !== true}
          errorText={errors.email?.message}
          label="Courriel"
          registerReturn={register("email")}
          slotProps={{
            inputLabel: {
              shrink: true,
            },
          }}
        />
        <FormTextField
          autoComplete="username"
          disabled={isValidUser !== true}
          errorText={errors.username?.message}
          label="Nom d'utilisateur"
          registerReturn={register("username")}
          slotProps={{
            inputLabel: {
              shrink: true,
            },
          }}
        />
        <Box sx={{ color: "#999", fontSize: "11px" }}>
          Lettres, chiffres et @/./+/-/_ uniquement.
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
        <Button
          color="primary"
          disabled={isValidUser !== true}
          fullWidth
          sx={{ mb: 2, mt: 3 }}
          type="submit"
          variant="contained"
        >
          Enregistrer
        </Button>
        <Box sx={{ display: "flex", justifyContent: "flex-end" }}>
          <Button
            disabled={isValidUser !== true}
            onClick={handlePasswordEditClick}
            size="small"
            sx={{ fontSize: "14px", textTransform: "none" }}
            variant="text"
          >
            Cliquez ici pour changer votre mot de passe
          </Button>
        </Box>
      </Box>
      <ProgressBackdrop open={submitting} />
    </Container>
  );
}

export default UserEditView;
