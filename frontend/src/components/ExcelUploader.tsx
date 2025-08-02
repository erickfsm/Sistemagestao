import React, { useState } from 'react';

const ExcelUploader = () => {
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setMessage('Por favor, selecione um arquivo.');
      return;
    }

    setIsLoading(true);
    setMessage('');

    setTimeout(() => {
      setIsLoading(false);
      setMessage(`Planilha "${file.name}" importada com sucesso!`);
      setFile(null);
    }, 2000);
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md max-w-lg mx-auto">
      <h3 className="text-2xl font-bold mb-4">Upload de Planilha</h3>
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center mb-4">
        {file ? (
          <p className="text-gray-700">Arquivo selecionado: <span className="font-semibold">{file.name}</span></p>
        ) : (
          <>
            <p className="text-gray-500 mb-2">Arraste e solte o arquivo aqui, ou</p>
            <label htmlFor="file-upload" className="cursor-pointer bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded transition-colors">
              Selecionar arquivo
            </label>
            <input id="file-upload" type="file" onChange={handleFileChange} className="hidden" accept=".xlsx, .xls" />
          </>
        )}
      </div>
      <button
        onClick={handleUpload}
        disabled={!file || isLoading}
        className={`w-full font-bold py-2 px-4 rounded transition-colors ${
          !file || isLoading
            ? 'bg-gray-400 cursor-not-allowed'
            : 'bg-green-500 hover:bg-green-600 text-white'
        }`}
      >
        {isLoading ? 'Importando...' : 'Importar'}
      </button>

      {message && (
        <p className="mt-4 text-center text-sm text-gray-600">
          {message}
        </p>
      )}
    </div>
  );
};

export default ExcelUploader;