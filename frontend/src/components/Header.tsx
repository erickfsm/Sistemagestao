import { Link } from 'react-router-dom';

interface HeaderProps {
  onLogout: () => void;
}

const Header: React.FC<HeaderProps> = ({ onLogout }) => {
  const navLinks = [
    { name: 'Home', path: '/' },
    { name: 'Upload', path: '/upload' },
    { name: 'Entregas', path: '/entregas' },
    { name: 'Finalizar Entrega', path: '/finalizar' },
    { name: 'Devoluções', path: '/devolucoes' },
  ];

  return (
    <header className="bg-white shadow">
      <div className="container mx-auto px-4 py-4 flex justify-between items-center">
        <div className="flex items-center space-x-2">
            <img src="/logo.png" alt="TMS Global Logo" className="h-10 w-10" />
            <span className="text-xl font-bold">TMS GLOBAL</span>
        </div>
        <nav className="hidden md:flex items-center space-x-4">
          {navLinks.map((link) => (
            <Link
              key={link.name}
              to={link.path}
              className="text-gray-600 hover:text-blue-500 font-semibold"
            >
              {link.name}
            </Link>
          ))}
          <button
            onClick={onLogout}
            className="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded"
          >
            Sair
          </button>
        </nav>
      </div>
    </header>
  );
};

export default Header;