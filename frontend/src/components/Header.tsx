import { useState } from 'react';

const Header = ({ onNavigate, onLogout }: { onNavigate: (page: string) => void, onLogout: () => void }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const toggleMenu = () => setIsMenuOpen(!isMenuOpen);

  return (
    <header className="bg-white text-gray-800 p-4 shadow-md flex justify-between items-center sticky top-0 z-10">
      <div className="flex items-center gap-2">
        <img src="/1000282714.jpg" alt="Logo da Global Hospitalar" className="h-10" />
        <div className="text-xl font-bold text-gh-orange">GLOBAL HOSPITALAR</div>
      </div>
      
      <div className="md:hidden">
        <button onClick={toggleMenu} className="text-gray-600 focus:outline-none">
          <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      </div>

      <nav className="hidden md:flex items-center space-x-4">
        <ul className="flex space-x-4">
          <li><a href="#" onClick={() => onNavigate('home')} className="hover:text-gh-orange transition-colors">Home</a></li>
          <li><a href="#" onClick={() => onNavigate('upload')} className="hover:text-gh-orange transition-colors">Upload</a></li>
          <li><a href="#" onClick={() => onNavigate('deliveries')} className="hover:text-gh-orange transition-colors">Entregas</a></li>
          <li><a href="#" onClick={() => onNavigate('finalize')} className="hover:text-gh-orange transition-colors">Finalizar Entrega</a></li>
          <li><a href="#" onClick={() => onNavigate('devolutions')} className="hover:text-gh-orange transition-colors">Devoluções</a></li>
        </ul>
        <button onClick={onLogout} className="bg-red-500 hover:bg-red-600 text-white font-bold py-1 px-3 rounded transition-colors">
          Sair
        </button>
      </nav>

      {isMenuOpen && (
        <div className="absolute top-0 right-0 w-64 bg-white shadow-lg h-screen flex flex-col p-4 md:hidden">
          <div className="text-right">
            <button onClick={toggleMenu} className="text-gray-600 focus:outline-none">
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <ul className="flex flex-col space-y-4 mt-4">
            <li><a href="#" onClick={() => onNavigate('home')} className="block py-2 text-gray-800 hover:text-gh-orange transition-colors">Home</a></li>
            <li><a href="#" onClick={() => onNavigate('upload')} className="block py-2 text-gray-800 hover:text-gh-orange transition-colors">Upload</a></li>
            <li><a href="#" onClick={() => onNavigate('deliveries')} className="block py-2 text-gray-800 hover:text-gh-orange transition-colors">Entregas</a></li>
            <li><a href="#" onClick={() => onNavigate('finalize')} className="block py-2 text-gray-800 hover:text-gh-orange transition-colors">Finalizar Entrega</a></li>
            <li><a href="#" onClick={() => onNavigate('devolutions')} className="block py-2 text-gray-800 hover:text-gh-orange transition-colors">Devoluções</a></li>
            <li><a href="#" onClick={onLogout} className="block py-2 bg-red-500 text-white rounded text-center">Sair</a></li>
          </ul>
        </div>
      )}
    </header>
  );
};

export default Header;