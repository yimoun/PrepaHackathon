import { Box, Container, Typography } from "@mui/material";

function Footer() {
  return (
    <Box component="footer" >
      <Container disableGutters={true}>
        <Typography align="center" paddingBottom={3}>
          &copy; Nelson&Jordan - PrépaHackathon
        </Typography>
      </Container>
    </Box>
  );
}

export default Footer;
