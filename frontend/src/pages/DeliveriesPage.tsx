import React, { useState, useEffect } from 'react';
import DeliveryCard from '../components/DeliveryCard.tsx';
import DetailedDeliveryCard from '../components/DetailedDeliveryCard.tsx';
import { fetchDeliveries } from '../services/api.ts';

interface Delivery {
  id: string;
  CODFILIAL: number;
  CHAVENFE: string;
  TRANSPORTADORA: string;
  CODFORNECFRETE: number;
  PREVISAOENTREGA: string;
  STATUS: string;
  NUMNOTA: number;
  MUNICIPIO: string;
  UF: string;
  VENDEDOR: string;
  DTCARREGAMENTO: string | null;
  TIPOVENDA: number;
  PRAZOENTREGA: number;
  DATAFINALIZACAO: string | null;
  DIASATRASO: number;
  PRAZOMEDIO: number;
  DTFAT: string;
  ROMANEIO: number;
  VLTOTAL: number;
  DEVOLUCAO: boolean;
  AGENDAMENTO: string | null;
  CODCLI: number;
  CLIENTE: string;
}

const DeliveriesPage = () => {
  const [deliveries, setDeliveries] = useState<Delivery[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedDelivery, setSelectedDelivery] = useState<Delivery | null>(null);
  const [filters, setFilters] = useState({
    status: '',
    num_nota: '',
    transportadora: '',
    data_inicial: '',
    data_final: '',
  });
  const [appliedFilters, setAppliedFilters] = useState({});
  const [showFilters, setShowFilters] = useState(false);

  const loadDeliveries = async (currentFilters: Record<string, any>) => {
    try {
      setIsLoading(true);
      const data = await fetchDeliveries(currentFilters);
      if (Array.isArray(data)) {
        setDeliveries(data);
      } else {
        setDeliveries([]);
      }
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Erro ao carregar as entregas.');
      setDeliveries([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDeliveries(appliedFilters);
  }, [appliedFilters]);

  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  const handleSearchClick = () => {
    setAppliedFilters(filters);
  };

  const handleCloseModal = () => {
    setSelectedDelivery(null);
  };

  const handleUpdateDeliveries = () => {
    loadDeliveries(appliedFilters);
  };

  if (isLoading) {
    return <div className="p-8 text-center">Carregando entregas...</div>;
  }

  if (error) {
    return <div className="p-8 text-center text-red-600">Erro: {error}</div>;
  }

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <h2 className="text-3xl font-bold mb-6 text-center">Monitoramento de Entregas</h2>
      
      <div className="mb-4 text-right">
        <button onClick={() => setShowFilters(!showFilters)} className="bg-gray-200 hover:bg-gray-300 py-2 px-4 rounded text-sm font-semibold transition-colors">
          {showFilters ? 'Esconder Filtros' : 'Mostrar Filtros'}
        </button>
      </div>
      
      {showFilters && (
        <div className="bg-white p-4 rounded-lg shadow-md mb-6 grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2">N. da Nota</label>
            <input type="text" name="num_nota" value={filters.num_nota} onChange={handleFilterChange} className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700"/>
          </div>
          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2">Transportadora</label>
            <input type="text" name="transportadora" value={filters.transportadora} onChange={handleFilterChange} className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700"/>
          </div>
          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2">Status</label>
            <select name="status" value={filters.status} onChange={handleFilterChange} className="shadow border rounded w-full py-2 px-3 text-gray-700">
              <option value="">Todos</option>
              <option value="Saida do CD Pendente">Saída do CD Pendente</option>
              <option value="Entrega Pendente - No prazo">No Prazo</option>
              <option value="Entrega Pendente - Fora do prazo">Fora do Prazo</option>
              <option value="Entrega Concluída - No prazo">Concluída No Prazo</option>
              <option value="Entrega Concluída - Fora do prazo">Concluída Fora do Prazo</option>
            </select>
          </div>
          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2">Data Inicial (Faturamento)</label>
            <input type="date" name="data_inicial" value={filters.data_inicial} onChange={handleFilterChange} className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700"/>
          </div>
          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2">Data Final (Faturamento)</label>
            <input type="date" name="data_final" value={filters.data_final} onChange={handleFilterChange} className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700"/>
          </div>
          <div className="md:col-span-4 text-right">
            <button onClick={handleSearchClick} className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded">
              Buscar
            </button>
          </div>
        </div>
      )}

      <div className="space-y-4">
        {deliveries.length > 0 ? (
          deliveries.map((delivery) => (
            delivery ? (
              <DeliveryCard
                key={delivery.id}
                numeroNf={String(delivery.NUMNOTA)}
                transportadora={delivery.TRANSPORTADORA}
                dataPrevista={delivery.PREVISAOENTREGA}
                status={delivery.STATUS}
                onClick={() => setSelectedDelivery(delivery)}
              />
            ) : null
          ))
        ) : (
          <div className="p-4 bg-yellow-100 text-yellow-800 rounded-lg text-center">
            Nenhuma entrega encontrada.
          </div>
        )}
      </div>
      
      {selectedDelivery && (
        <DetailedDeliveryCard
          onClose={handleCloseModal}
          onUpdate={handleUpdateDeliveries}
          delivery={{
            id: selectedDelivery.id,
            numeroNf: String(selectedDelivery.NUMNOTA),
            transportadora: selectedDelivery.TRANSPORTADORA,
            codFornecFrete: String(selectedDelivery.CODFORNECFRETE),
            dataPrevista: selectedDelivery.PREVISAOENTREGA,
            status: selectedDelivery.STATUS,
            municipioUf: `${selectedDelivery.MUNICIPIO} - ${selectedDelivery.UF}`,
            vendedor: selectedDelivery.VENDEDOR,
            dataCarregamento: selectedDelivery.DTCARREGAMENTO,
            tipoVenda: String(selectedDelivery.TIPOVENDA),
            prazo: String(selectedDelivery.PRAZOENTREGA),
            dataFinalizacao: selectedDelivery.DATAFINALIZACAO,
            diasAtraso: String(selectedDelivery.DIASATRASO),
            prazoMedio: String(selectedDelivery.PRAZOMEDIO),
            dataFaturamento: selectedDelivery.DTFAT,
            romaneio: String(selectedDelivery.ROMANEIO),
            valor: String(selectedDelivery.VLTOTAL),
            devolucao: selectedDelivery.DEVOLUCAO,
            agendamento: selectedDelivery.AGENDAMENTO,
            codCli: selectedDelivery.CODCLI,
            cliente: selectedDelivery.CLIENTE,
          }}
        />
      )}
    </div>
  );
};

export default DeliveriesPage;