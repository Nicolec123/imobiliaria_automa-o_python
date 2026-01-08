"""
Integração com Chaves na Mão
"""
from typing import Dict, List, Optional
import requests
import xml.etree.ElementTree as ET
from config import Config


class ChavesNaMaoIntegration:
    """Classe para integração com Chaves na Mão"""
    
    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
        """
        Inicializa a integração com Chaves na Mão
        
        Args:
            api_key: Chave da API (usa a configurada se não fornecida)
            api_url: URL base da API (usa a configurada se não fornecida)
        """
        self.api_key = api_key or Config.CHAVES_NA_MAO_API_KEY
        self.api_url = (api_url or Config.CHAVES_NA_MAO_API_URL).rstrip('/')
        
        if not self.api_key:
            raise ValueError("Chave da API Chaves na Mão não configurada")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def create_lead(self, lead_data: Dict) -> Dict:
        """
        Cria um novo lead na plataforma Chaves na Mão
        
        Args:
            lead_data: Dados do lead contendo informações do cliente
            
        Returns:
            Dados do lead criado
        """
        url = f"{self.api_url}/api/leads"
        
        try:
            response = requests.post(url, json=lead_data, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao criar lead no Chaves na Mão: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Resposta do servidor: {e.response.text}")
            raise
    
    def create_lead_from_analysis(self, analysis: Dict, form_data: Optional[Dict] = None) -> Dict:
        """
        Cria um lead baseado na análise do ChatGPT
        
        Args:
            analysis: Análise gerada pelo ChatGPT
            form_data: Dados originais do formulário (opcional)
            
        Returns:
            Dados do lead criado
        """
        info = analysis.get('informacoes_extraidas', {})
        
        lead_data = {
            "nome": info.get('nome', 'Cliente'),
            "telefone": info.get('telefone', ''),
            "email": info.get('email', ''),
            "tipo_lead": analysis.get('tipo_lead', 'Lead'),
            "tipo_imovel": info.get('tipo_imovel', ''),
            "localizacao": info.get('localizacao', ''),
            "orcamento": info.get('orcamento', ''),
            "observacoes": info.get('observacoes', ''),
            "prioridade": analysis.get('prioridade', 'média'),
            "origem": "Google Forms"
        }
        
        if form_data:
            lead_data["dados_originais"] = form_data
        
        return self.create_lead(lead_data)
    
    def update_lead(self, lead_id: str, updates: Dict) -> Dict:
        """
        Atualiza um lead existente
        
        Args:
            lead_id: ID do lead
            updates: Dicionário com campos a atualizar
            
        Returns:
            Dados atualizados do lead
        """
        url = f"{self.api_url}/api/leads/{lead_id}"
        
        try:
            response = requests.put(url, json=updates, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao atualizar lead no Chaves na Mão: {e}")
            raise
    
    def get_lead(self, lead_id: str) -> Dict:
        """
        Obtém dados de um lead
        
        Args:
            lead_id: ID do lead
            
        Returns:
            Dados do lead
        """
        url = f"{self.api_url}/api/leads/{lead_id}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao obter lead do Chaves na Mão: {e}")
            raise
    
    def search_properties(self, filters: Dict) -> List[Dict]:
        """
        Busca imóveis na plataforma
        
        Args:
            filters: Filtros de busca (tipo, localização, preço, etc.)
            
        Returns:
            Lista de imóveis encontrados
        """
        url = f"{self.api_url}/api/properties/search"
        
        try:
            response = requests.post(url, json=filters, headers=self.headers)
            response.raise_for_status()
            return response.json().get('properties', [])
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar imóveis no Chaves na Mão: {e}")
            return []
    
    def parse_xml_property(self, xml_content: str) -> Dict:
        """
        Parse um imóvel do formato XML do Chaves na Mão
        
        Args:
            xml_content: Conteúdo XML do imóvel
            
        Returns:
            Dicionário com dados do imóvel formatado
        """
        try:
            root = ET.fromstring(xml_content)
            
            # Busca o elemento imovel
            imovel_elem = root.find('.//imovel')
            if imovel_elem is None:
                raise ValueError("Elemento 'imovel' não encontrado no XML")
            
            # Extrai todos os campos do XML
            property_data = {}
            
            # Campos básicos
            for field in ['referencia', 'codigo_cliente', 'link_cliente', 'titulo', 
                         'transacao', 'transacao2', 'finalidade', 'finalidade2', 
                         'destaque', 'tipo', 'tipo2']:
                elem = imovel_elem.find(field)
                if elem is not None and elem.text:
                    property_data[field] = elem.text.strip()
            
            # Valores numéricos
            for field in ['valor', 'valor_locacao', 'valor_iptu', 'valor_condominio']:
                elem = imovel_elem.find(field)
                if elem is not None and elem.text:
                    try:
                        property_data[field] = float(elem.text.strip())
                    except ValueError:
                        property_data[field] = elem.text.strip()
            
            # Áreas
            for field in ['area_total', 'area_util']:
                elem = imovel_elem.find(field)
                if elem is not None and elem.text:
                    try:
                        property_data[field] = float(elem.text.strip())
                    except ValueError:
                        property_data[field] = elem.text.strip()
            
            # Características (booleanos e numéricos)
            boolean_fields = ['aceita_pet', 'esconder_endereco_imovel', 'aceita_troca']
            numeric_fields = ['quartos', 'suites', 'garagem', 'banheiro', 'closet', 
                            'salas', 'despensa', 'bar', 'cozinha', 'quarto_empregada',
                            'escritorio', 'area_servico', 'lareira', 'varanda', 'lavanderia']
            
            for field in boolean_fields + numeric_fields:
                elem = imovel_elem.find(field)
                if elem is not None and elem.text:
                    if field in boolean_fields:
                        property_data[field] = elem.text.strip() == '1'
                    else:
                        try:
                            property_data[field] = int(elem.text.strip())
                        except ValueError:
                            property_data[field] = elem.text.strip()
            
            # Endereço
            address_fields = ['estado', 'cidade', 'bairro', 'cep', 'endereco', 
                            'numero', 'complemento']
            for field in address_fields:
                elem = imovel_elem.find(field)
                if elem is not None and elem.text:
                    property_data[field] = elem.text.strip()
            
            # Descrição
            descritivo_elem = imovel_elem.find('descritivo')
            if descritivo_elem is not None:
                property_data['descritivo'] = descritivo_elem.text.strip() if descritivo_elem.text else ''
            
            # Fotos
            fotos = []
            fotos_elem = imovel_elem.find('fotos_imovel')
            if fotos_elem is not None:
                for foto_elem in fotos_elem.findall('foto'):
                    foto_data = {}
                    url_elem = foto_elem.find('url')
                    data_elem = foto_elem.find('data_atualizacao')
                    if url_elem is not None and url_elem.text:
                        foto_data['url'] = url_elem.text.strip()
                    if data_elem is not None and data_elem.text:
                        foto_data['data_atualizacao'] = data_elem.text.strip()
                    if foto_data:
                        fotos.append(foto_data)
            property_data['fotos'] = fotos
            
            # Áreas comuns e privativas
            area_comum = []
            area_comum_elem = imovel_elem.find('area_comum')
            if area_comum_elem is not None:
                for item in area_comum_elem.findall('item'):
                    if item.text:
                        area_comum.append(item.text.strip())
            property_data['area_comum'] = area_comum
            
            area_privativa = []
            area_privativa_elem = imovel_elem.find('area_privativa')
            if area_privativa_elem is not None:
                for item in area_privativa_elem.findall('item'):
                    if item.text:
                        area_privativa.append(item.text.strip())
            property_data['area_privativa'] = area_privativa
            
            # Outros campos
            for field in ['data_atualizacao', 'latitude', 'longitude', 'video', 
                         'tour_360', 'periodo_locacao', 'conservacao']:
                elem = imovel_elem.find(field)
                if elem is not None and elem.text:
                    property_data[field] = elem.text.strip()
            
            return property_data
            
        except ET.ParseError as e:
            raise ValueError(f"Erro ao fazer parse do XML: {e}")
        except Exception as e:
            raise ValueError(f"Erro ao processar XML do imóvel: {e}")
    
    def import_property_from_xml(self, xml_content: str) -> Dict:
        """
        Importa um imóvel a partir de XML e cria na plataforma
        
        Args:
            xml_content: Conteúdo XML do imóvel
            
        Returns:
            Dados do imóvel criado
        """
        # Parse do XML
        property_data = self.parse_xml_property(xml_content)
        
        # Cria o imóvel via API
        url = f"{self.api_url}/api/properties"
        
        try:
            response = requests.post(url, json=property_data, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao importar imóvel no Chaves na Mão: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Resposta do servidor: {e.response.text}")
            raise
    
    def import_properties_from_xml_file(self, xml_file_path: str) -> List[Dict]:
        """
        Importa múltiplos imóveis a partir de um arquivo XML
        
        Args:
            xml_file_path: Caminho do arquivo XML
            
        Returns:
            Lista de imóveis importados
        """
        try:
            tree = ET.parse(xml_file_path)
            root = tree.getroot()
            
            imported_properties = []
            
            # Processa cada imóvel no XML
            for imovel_elem in root.findall('.//imovel'):
                # Converte elemento para string XML
                xml_string = ET.tostring(imovel_elem, encoding='unicode')
                # Adiciona tags raiz para parse
                xml_content = f'<?xml version="1.0" encoding="UTF-8"?><Document><imoveis>{xml_string}</imoveis></Document>'
                
                try:
                    property_data = self.parse_xml_property(xml_content)
                    # Importa via API
                    result = self.import_property_from_xml(xml_content)
                    imported_properties.append({
                        'success': True,
                        'property': result,
                        'referencia': property_data.get('referencia', 'N/A')
                    })
                except Exception as e:
                    imported_properties.append({
                        'success': False,
                        'error': str(e),
                        'referencia': imovel_elem.find('referencia').text if imovel_elem.find('referencia') is not None else 'N/A'
                    })
            
            return imported_properties
            
        except ET.ParseError as e:
            raise ValueError(f"Erro ao fazer parse do arquivo XML: {e}")
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo não encontrado: {xml_file_path}")
        except Exception as e:
            raise ValueError(f"Erro ao processar arquivo XML: {e}")


