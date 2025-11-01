import {
  FormControl,
  FormHelperText,
  InputLabel,
  MenuItem,
  Select,
  SelectProps,
} from "@mui/material";

export type FormSelectMenuItemData = {
  value: string;
  text: string;
};

export type FormSelectProps = SelectProps<string> & {
  errorText?: string | null;
  label: string;
  options: FormSelectMenuItemData[];
};

function FormSelect({
  errorText = null,
  label,
  options,
  ...others
}: FormSelectProps): React.JSX.Element {
  return (
    <FormControl
      fullWidth
      sx={{ mt: 2 }}
      variant="outlined"
      {...(errorText && { errorText: true })}
    >
      <InputLabel>{label}</InputLabel>
      <Select label={label} {...others}>
        {/*<MenuItem sx={{ color: 'text.secondary' }} value="">
          <em>Aucun</em>
        </MenuItem>*/}
        {options.map((item: FormSelectMenuItemData) => (
          <MenuItem key={item.value} value={item.value}>
            {item.text}
          </MenuItem>
        ))}
      </Select>
      {errorText && <FormHelperText>{errorText}</FormHelperText>}
    </FormControl>
  );
}

export default FormSelect;
