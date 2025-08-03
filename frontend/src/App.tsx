import React, { useState, useEffect } from 'react';
import Header from './components/Header.tsx';
import Dashboard from './pages/Dashboard.tsx';
import UploadPage from './pages/UploadPage.tsx';
import DeliveriesPage from './pages/DeliveriesPage.tsx';
import LoginPage from './pages/LoginPage.tsx';
import FinalizePage from './pages/FinalizePage.tsx';
import DevolutionsPage from './pages/DevolutionsPage.tsx';

function App() {
  const [currentPage, setCurrentPage] = useState('home');
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const storedToken = localStorage.getItem('accessToken');
    if (storedToken) {
      setIsLoggedIn(true);
    }
  }, []);

  const handleLoginSuccess = () => {
    setIsLoggedIn(true);
    setCurrentPage('home');
  };

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    setIsLoggedIn(false);
    setCurrentPage('home');
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'home':
        return <Dashboard />;
      case 'upload':
        return <UploadPage />;
      case 'deliveries':
        return <DeliveriesPage />;
      case 'finalize':
        return <FinalizePage />;
      case 'devolutions':
        return <DevolutionsPage />;
      default:
        return <Dashboard />;
    }
  };

  if (!isLoggedIn) {
    return <LoginPage onLogin={handleLoginSuccess} />;
  }

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