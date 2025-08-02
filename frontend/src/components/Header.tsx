const Header = ({ onNavigate, onLogout }: { onNavigate: (page: string) => void, onLogout: () => void }) => {
  return (
    <header className="bg-slate-900 text-white p-4 shadow-md flex justify-between items-center">
      <div className="text-xl font-bold">Sistema de Gestão</div>
      <nav className="flex items-center space-x-4">
        <ul className="flex space-x-4">
          <li><a href="#" onClick={() => onNavigate('home')} className="hover:text-blue-400 transition-colors">Home</a></li>
          <li><a href="#" onClick={() => onNavigate('upload')} className="hover:text-blue-400 transition-colors">Upload</a></li>
          <li><a href="#" onClick={() => onNavigate('deliveries')} className="hover:text-blue-400 transition-colors">Entregas</a></li>
        </ul>
        <button onClick={onLogout} className="bg-red-500 hover:bg-red-600 text-white font-bold py-1 px-3 rounded">
          Sair
        </button>
      </nav>
    </header>
  );
};

export default Header;