import { UseFormRegisterReturn } from "react-hook-form";  //Type fourni par react-hook-form, utilisé pour lier un champ de formulaire à la gestion du formulaire.
import { TextField, TextFieldProps } from "@mui/material";

/*champ de saisie personnalisé basé sur TextField de MUI conçu pour s'intégrer avec react-hook-form. */

//Définition des types des props
export type FormTextFieldProps = TextFieldProps & {
  errorText?: string | null;
  registerReturn?: UseFormRegisterReturn; //Permet de connecter le champ à react-hook-form.
};


//Définition du composant FormTextField
function FormTextField({
  errorText,
  registerReturn,
  ...others
}: FormTextFieldProps) {
  return (
    <TextField
      fullWidth
      margin="normal"
      {...others}
      {...(errorText && { error: true, helperText: errorText })}
      {...(registerReturn && { ...registerReturn })}
    />
  );
}

export default FormTextField;
