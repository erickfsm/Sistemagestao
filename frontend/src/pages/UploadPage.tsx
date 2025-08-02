import ExcelUploader from '../components/ExcelUploader.tsx';

const UploadPage = () => {
  return (
    <div className="p-8 max-w-2xl mx-auto">
      <h2 className="text-3xl font-bold mb-6 text-center">Importar Planilha Excel</h2>
      <ExcelUploader />
    </div>
  );
};

export default UploadPage;