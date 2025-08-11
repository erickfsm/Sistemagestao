import { Routes, Route, useLocation } from 'react-router-dom';
import Header from './components/Header.tsx';
import ProtectedRoute from './components/ProtectedRoute.tsx';
import DashboardPage from './pages/Dashboard.tsx';
import UploadPage from './pages/UploadPage.tsx';
import DeliveriesPage from './pages/DeliveriesPage.tsx';
import LoginPage from './pages/LoginPage.tsx';
import FinalizePage from './pages/FinalizePage.tsx';
import DevolutionsPage from './pages/DevolutionsPage.tsx';

function App() {
  const location = useLocation();
  const showHeader = location.pathname !== '/login';

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    window.location.href = '/login';
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {showHeader && <Header onLogout={handleLogout} />}
      
      <main>
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/entregas" element={<DeliveriesPage />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/devolucoes" element={<DevolutionsPage />} />
            <Route path="/finalizar" element={<FinalizePage />} />
          </Route>
        </Routes>
      </main>
    </div>
  );
}

export default App;