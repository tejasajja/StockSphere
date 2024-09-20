import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import './App.css';
import Login from './pages/Login';
import Register from "./pages/Register";
import PrivateRoute from "./utils/PrivateRoute";
import Dashboad from './pages/Dashboad';

import { ThemeProvider } from "./components/ui/theme-provider";
import AdminTransactions from "./pages/AdminTransaction";
import AdminCustomers from "./pages/AdminCustomers";
import AdminStocks from "./pages/AdminStocks";
import AdminCrypto from "./pages/AdminCrypto";
import AdminAgent from "./pages/AdminAgent";
import CryptoDashboard from "./pages/CryptoDashboard";
import StockAnl from "./pages/StockAnaly";



function App() {
  
  // The token state is no longer necessary here since the validation is handled within PrivateRoute

  return (
    <ThemeProvider>
    <div className=""> {/* Use the container class */}
      <Router className="">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />


          
          <Route path="/stockdashboard" element={
            <PrivateRoute>
              <Dashboad/>
            </PrivateRoute>
          } />
                    <Route path="/cryptodashboard" element={
            <PrivateRoute>
              <CryptoDashboard/>
            </PrivateRoute>
          } />
          
          <Route path="/Crypto" element={
            <PrivateRoute>
              <CryptoDashboard/>
            </PrivateRoute>
            
          } />

<Route path="/stockanalysis" element={
            <PrivateRoute>
              <StockAnl/>
            </PrivateRoute>
            
          } />
                    <Route path="/admin/transactions" element={
            <PrivateRoute roleRequired="admin">
            <AdminTransactions/>
  </PrivateRoute>
  
          } />
                    <Route path="/admin/customers" element={
            <PrivateRoute roleRequired="admin">
            <AdminCustomers/>
  </PrivateRoute>
          } />
          <Route path="/admin/stocks" element={
            <PrivateRoute roleRequired="admin">
            <AdminStocks/>
  </PrivateRoute>
          } />
          <Route path="/admin/crypto" element={
            <PrivateRoute roleRequired="admin">
            <AdminCrypto/>
  </PrivateRoute>
          } />
          <Route path="/admin/agent" element={
            <PrivateRoute roleRequired="admin">
            <AdminAgent/>
  </PrivateRoute>

  
          } />
        </Routes>

      </Router>
     </div>
     </ThemeProvider>
  );
}

export default App;
