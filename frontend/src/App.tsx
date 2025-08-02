import { useState, useEffect } from 'react';
import Header from './components/Header.tsx';
import Dashboard from './pages/Dashboard.tsx';
import UploadPage from './pages/UploadPage.tsx';
import DeliveriesPage from './pages/DeliveriesPage.tsx';
import LoginPage from './pages/LoginPage.tsx';

function App() {
  const [currentPage, setCurrentPage] = useState('home');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const storedToken = localStorage.getItem('accessToken');
    if (storedToken) {
      setToken(storedToken);
      setIsLoggedIn(true);
    }
  }, []);

  const handleLoginSuccess = (newToken: string) => {
    localStorage.setItem('accessToken', newToken);
    setToken(newToken);
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    setToken(null);
    setIsLoggedIn(false);
    setCurrentPage('home');
  };

  if (!isLoggedIn) {
    return <LoginPage onLogin={handleLoginSuccess} />;
  }

  const renderPage = () => {
    switch (currentPage) {
      case 'home':
        return <Dashboard />;
      case 'upload':
        return <UploadPage />;
      case 'deliveries':
        return <DeliveriesPage />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Header onNavigate={setCurrentPage} onLogout={handleLogout} />
      <main>
        {renderPage()}
      </main>
    </div>
  );
}

export default App;