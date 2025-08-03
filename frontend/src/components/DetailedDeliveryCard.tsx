import React, { useState, useEffect } from 'react';
import {
  finalizeDelivery,
  fetchComprovantesPorEntrega,
  fetchDevolucoesPorEntrega,
  fetchRastreamentoPorEntrega,
  uploadComprovante,
  atualizarRastreamentoEntrega
} from '../services/api';

interface Comprovante {
  id: string;
  nome_arquivo: string;
}

interface Devolucao {
  id: string;
}

interface Rastreamento {
  id: string;
  timestamp: string;
  status_descricao: string;
  localizacao: string | null;
}

interface DetailedDeliveryCardProps {
  onClose: () => void;
  onUpdate: () => void;
  delivery: {
    id: string;
    numeroNf: string;
    transportadora: string;
    codFornecFrete: string;
    dataPrevista: string;
    status: string;
    municipioUf: string;
    vendedor: string;
    dataCarregamento: string | null;
    tipoVenda: string;
    prazo: string;
    dataFinalizacao: string | null;
    diasAtraso: string;
    prazoMedio: string;
    dataFaturamento: string;
    romaneio: string;
    valor: string;
    devolucao: boolean;
    agendamento: string | null;
    codCli: number;
    cliente: string;
  };
}

const DetailedDeliveryCard: React.FC<DetailedDeliveryCardProps> = ({
  onClose,
  onUpdate,
  delivery,
}) => {
  const [comprovantes, setComprovantes] = useState<Comprovante[]>([]);
  const [devolucoes, setDevolucoes] = useState<Devolucao[]>([]);
  const [rastreamento, setRastreamento] = useState<Rastreamento[]>([]);
  
  const [isRastreamentoVisible, setIsRastreamentoVisible] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isFinalizing, setIsFinalizing] = useState(false);
  
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [message, setMessage] = useState('');
  const [isError, setIsError] = useState(false);

  const loadAllData = async () => {
    if (!delivery?.id) return;
    try {
      const [comprovantesData, devolucoesData, rastreamentoData] = await Promise.all([
        fetchComprovantesPorEntrega(delivery.id),
        fetchDevolucoesPorEntrega(delivery.id),
        fetchRastreamentoPorEntrega(delivery.id)
      ]);
      setComprovantes(comprovantesData || []);
      setDevolucoes(devolucoesData || []);
      setRastreamento(rastreamentoData || []);
    } catch (error) {
      console.error("Erro ao carregar detalhes da entrega:", error);
      setMessage("Falha ao carregar dados. Tente novamente.");
      setIsError(true);
    }
  };

  useEffect(() => {
    loadAllData();
  }, [delivery]);

  const handleAtualizarViaApi = async () => {
    setIsUpdating(true);
    setMessage('');
    setIsError(false);
    try {
      const result = await atualizarRastreamentoEntrega(delivery.id);
      setMessage(result.mensagem || 'Dados atualizados via API.');
      await loadAllData();
    } catch (err: any) {
      setMessage(`Erro na API: ${err.message}`);
      setIsError(true);
    } finally {
      setIsUpdating(false);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files?.[0]) {
      setSelectedFile(event.target.files[0]);
    }
  };

  const handleUploadManual = async () => {
    if (!selectedFile) return;
    setIsUploading(true);
    setMessage('');
    setIsError(false);
    try {
      await uploadComprovante(delivery.id, selectedFile);
      setMessage('Anexo enviado com sucesso!');
      await loadAllData();
    } catch (err: any) {
      setMessage(`Erro no upload: ${err.message}`);
      setIsError(true);
    } finally {
      setIsUploading(false);
    }
  };

  const handleFinalize = async () => {
    setIsFinalizing(true);
    setMessage('');
    setIsError(false);
    try {
      await finalizeDelivery(delivery.id);
      setMessage("Entrega finalizada com sucesso!");
      setTimeout(() => {
        onUpdate();
        onClose();
      }, 1500);
    } catch (err: any) {
      setMessage(`Erro ao finalizar: ${err.message}`);
      setIsError(true);
    } finally {
      setIsFinalizing(false);
    }
  };
  
  const formatCurrency = (value: string | number) => {
    const numberValue = Number(value);
    return isNaN(numberValue) 
      ? 'R$ 0,00' 
      : new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(numberValue);
  };

  const temAnexo = comprovantes.length > 0;
  const podeFinalizar = temAnexo && !isFinalizing;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex justify-center items-center p-4 z-50">
      <div className="bg-white p-6 rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <h3 className="text-2xl font-bold mb-4">Detalhes da Entrega: NF {delivery.numeroNf}</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-sm mb-6">
            <p><span className="font-semibold">Transportadora:</span> {delivery.transportadora}</p>
            <p><span className="font-semibold">Cliente:</span> {delivery.cliente}</p>
            <p><span className="font-semibold">Valor Total:</span> {formatCurrency(delivery.valor)}</p>
            <p><span className="font-semibold">Status:</span> <span className="font-bold">{delivery.status}</span></p>
            <p><span className="font-semibold">Data Prevista:</span> {delivery.dataPrevista}</p>
            <p><span className="font-semibold">Data de Finalização:</span> {delivery.dataFinalizacao || 'Pendente'}</p>
            <p><span className="font-semibold">Devoluções Registradas:</span> {devolucoes.length}</p>
        </div>

        <div className="border-t pt-4 mt-4">
          <div className="flex justify-between items-center mb-2">
            <h4 className="font-bold text-lg">Histórico de Rastreamento</h4>
            <button onClick={handleAtualizarViaApi} disabled={isUpdating} className="bg-indigo-500 hover:bg-indigo-600 text-white px-3 py-1 rounded text-sm font-semibold disabled:bg-gray-400">
              {isUpdating ? 'Atualizando...' : 'Atualizar via API'}
            </button>
          </div>
          {isRastreamentoVisible && (
            <div className="text-sm max-h-40 overflow-y-auto border p-2 rounded bg-gray-50">
              {rastreamento.length > 0 ? rastreamento.map(evento => (
                <p key={evento.id} className="border-b last:border-b-0 py-1">{new Date(evento.timestamp).toLocaleString('pt-BR')} - {evento.status_descricao}</p>
              )) : <p>Nenhum histórico encontrado.</p>}
            </div>
          )}
          <button onClick={() => setIsRastreamentoVisible(!isRastreamentoVisible)} className="text-blue-500 text-sm mt-1">
            {isRastreamentoVisible ? 'Esconder Histórico' : 'Mostrar Histórico'}
          </button>
        </div>

        <div className="border-t pt-4 mt-4">
          <h4 className="font-bold text-lg mb-2">Comprovante de Entrega</h4>
          {temAnexo ? (
            <div>
              {comprovantes.map(comp => (
                <a key={comp.id} href={`${import.meta.env.VITE_API_BASE_URL}/comprovantes/${comp.id}/download`} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                  {comp.nome_arquivo || `Ver Comprovante (ID ${comp.id})`}
                </a>
              ))}
            </div>
          ) : (
            <div className="flex items-center space-x-2">
              <input type="file" onChange={handleFileSelect} className="text-sm border rounded p-1"/>
              <button onClick={handleUploadManual} disabled={isUploading || !selectedFile} className="bg-purple-500 hover:bg-purple-600 text-white px-3 py-1 rounded text-sm font-semibold disabled:bg-gray-400">
                {isUploading ? 'Enviando...' : 'Enviar Anexo'}
              </button>
            </div>
          )}
        </div>

        {message && <p className={`text-sm text-center font-bold mt-4 p-2 rounded ${isError ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>{message}</p>}

        <div className="flex justify-end gap-4 mt-6 border-t pt-4">
           <button onClick={onClose} className="bg-gray-500 hover:bg-gray-600 text-white font-bold py-2 px-4 rounded">Fechar</button>
           <button onClick={handleFinalize} disabled={!podeFinalizar} className={`bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded ${!podeFinalizar && 'opacity-50 cursor-not-allowed'}`}>
            {isFinalizing ? 'Finalizando...' : 'Finalizar Entrega'}
           </button>
        </div>
      </div>
    </div>
  );
};

export default DetailedDeliveryCard;