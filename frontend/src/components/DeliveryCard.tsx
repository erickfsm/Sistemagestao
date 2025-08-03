import React from 'react';

interface DeliveryCardProps {
  numeroNf: string;
  transportadora: string;
  dataPrevista: string;
  status: string;
  onClick: () => void;
}

const DeliveryCard: React.FC<DeliveryCardProps> = ({
  numeroNf,
  transportadora,
  dataPrevista,
  status,
  onClick,
}) => {
  return (
    <div
      className="bg-white p-4 rounded-lg shadow-md mb-4 border-l-4 border-blue-500 cursor-pointer hover:bg-gray-50 transition-colors"
      onClick={onClick}
    >
      <div className="flex justify-between items-center">
        <div>
          <p className="text-gray-500 text-sm">N. da Nota</p>
          <p className="font-bold text-lg text-gray-800">{numeroNf}</p>
        </div>
        <div className="text-center">
          <p className="text-gray-500 text-sm">Transportadora</p>
          <p className="font-semibold text-gray-800">{transportadora}</p>
        </div>
        <div className="text-right">
          <p className="text-gray-500 text-sm">Data Prevista</p>
          <p className="font-semibold text-gray-800">{dataPrevista}</p>
          <span
            className={`text-xs font-bold px-2 py-1 rounded-full ${
              status && status.includes('Concluída')
                ? 'bg-green-200 text-green-800'
                : 'bg-yellow-200 text-yellow-800'
            }`}
          >
            {status}
          </span>
        </div>
      </div>
    </div>
  );
};

export default DeliveryCard;