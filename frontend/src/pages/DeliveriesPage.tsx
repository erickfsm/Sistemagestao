import DeliveryCard from '../components/DeliveryCard.tsx';

const mockDeliveries = [
  { id: '1', trackingId: 'BR123456789BR', carrier: 'Correios', estimatedDate: '05/08/2025', status: 'Em trânsito' },
  { id: '2', trackingId: 'FED987654321', carrier: 'FedEx', estimatedDate: '02/08/2025', status: 'Entregue' },
  { id: '3', trackingId: 'DHL555888333', carrier: 'DHL', estimatedDate: '07/08/2025', status: 'Aguardando coleta' },
];

const DeliveriesPage = () => {
  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h2 className="text-3xl font-bold mb-6 text-center">Monitoramento de Entregas</h2>
      <div className="space-y-4">
        {mockDeliveries.map(delivery => (
          <DeliveryCard
            key={delivery.id}
            id={delivery.id}
            trackingId={delivery.trackingId}
            carrier={delivery.carrier}
            estimatedDate={delivery.estimatedDate}
            status={delivery.status}
          />
        ))}
      </div>
    </div>
  );
};

export default DeliveriesPage;