import React from 'react';

interface DeliveryCardProps {
  id: string;
  trackingId: string;
  carrier: string;
  estimatedDate: string;
  status: string;
}

const DeliveryCard: React.FC<DeliveryCardProps> = ({ id, trackingId, carrier, estimatedDate, status }) => {
  return (
    <div className="bg-white p-4 rounded-lg shadow-md flex justify-between items-center mb-4">
      <div>
        <p className="text-sm text-gray-500">ID da Entrega: {id}</p>
        <p className="font-semibold">Rastreamento: {trackingId}</p>
        <p className="text-sm">Transportadora: {carrier}</p>
      </div>
      <div className="text-right">
        <p className="text-sm text-gray-500">Data Prevista</p>
        <p className="font-semibold">{estimatedDate}</p>
        <span className={`text-xs font-bold px-2 py-1 rounded-full ${
          status === 'Entregue' ? 'bg-green-200 text-green-800' : 'bg-yellow-200 text-yellow-800'
        }`}>
          {status}
        </span>
      </div>
    </div>
  );
};

export default DeliveryCard;