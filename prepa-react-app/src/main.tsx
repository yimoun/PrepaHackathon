import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { Route, Routes, BrowserRouter } from "react-router-dom";
import "./assets/css/main.css";
import App from "./components/App";
import AuthContainer from "./components/auth/AuthContainer";
import IADetection from "./components/projectComponents/IADetection";
import LoginView from "./components/auth/LoginView";
import Logout from "./components/auth/Logout";
import NotFound from "./components/NotFound";
import PasswordEditView from "./components/user/PasswordEditView";
import ProtectedRoutes from "./components/ProtectedRoutes";
import SignUpView from "./components/auth/SignUpView";
import UserEditView from "./components/user/UserEditView";
import AlertesList from "./components/projectComponents/AlertesList"; 
import ModeleIAHistory from "./components/projectComponents/modeleIAHistory";



createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />}>          
           <Route path="" element={<IADetection />} />
           <Route path="/alertes" element={<AlertesList />} />
           <Route path="/game-history" element={<ModeleIAHistory />} />
           <Route path="" element={<ProtectedRoutes />}>
              <Route path="user-edit/me" element={<UserEditView />} />
              <Route path="password-edit/me" element={<PasswordEditView />} />
              
            </Route> 
        </Route>
        <Route path="" element={<AuthContainer />}>
              <Route path="login" element={<LoginView />} />
              <Route path="signup" element={<SignUpView />} />
        </Route>
          <Route path="logout" element={<Logout />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
    </BrowserRouter>
  </StrictMode>
);
