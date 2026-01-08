"""
Gerador de XML para Chaves na Mão
Gera XML a partir dos dados do formulário/análise
"""
from typing import Dict, List, Optional
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom


class ChavesNaMaoXMLGenerator:
    """Gera XML do Chaves na Mão a partir dos dados processados"""
    
    def __init__(self):
        """Inicializa o gerador de XML"""
        pass
    
    def generate_property_xml(self, property_data: Dict) -> str:
        """
        Gera XML de um imóvel a partir dos dados
        
        Args:
            property_data: Dados do imóvel (vindos do formulário/análise)
            
        Returns:
            String XML formatada
        """
        # Cria estrutura XML
        root = ET.Element('Document')
        imoveis = ET.SubElement(root, 'imoveis')
        imovel = ET.SubElement(imoveis, 'imovel')
        
        # Campos básicos
        self._add_element(imovel, 'referencia', property_data.get('codigo', property_data.get('referencia', 'AUTO_' + datetime.now().strftime('%Y%m%d%H%M%S'))))
        self._add_element(imovel, 'codigo_cliente', property_data.get('codigo_cliente', property_data.get('codigo', '')))
        self._add_element(imovel, 'link_cliente', property_data.get('link_cliente', ''))
        self._add_element(imovel, 'titulo', property_data.get('titulo', property_data.get('nome_imovel', 'Imóvel')))
        
        # Transação e finalidade
        transacao = property_data.get('transacao', 'V')  # V=venda, L=locacao
        self._add_element(imovel, 'transacao', transacao)
        self._add_element(imovel, 'transacao2', property_data.get('transacao2', ''))
        self._add_element(imovel, 'finalidade', property_data.get('finalidade', 'RE'))  # RE=residencial
        self._add_element(imovel, 'finalidade2', property_data.get('finalidade2', ''))
        self._add_element(imovel, 'destaque', property_data.get('destaque', '0'))
        
        # Tipo
        self._add_element(imovel, 'tipo', property_data.get('tipo', property_data.get('tipo_imovel', 'Apartamento')))
        self._add_element(imovel, 'tipo2', property_data.get('tipo2', ''))
        
        # Valores
        valor = property_data.get('valor', '')
        if not valor:
            orcamento = property_data.get('orcamento', '0')
            # Se orcamento é um dict, extrai valor_total ou valor_minimo
            if isinstance(orcamento, dict):
                valor = orcamento.get('valor_total', orcamento.get('valor_minimo', '0'))
            else:
                valor = orcamento
        
        # Converte para string e limpa formato
        valor_str = str(valor)
        if isinstance(valor, str):
            valor_str = valor_str.replace('R$', '').replace('.', '').replace(',', '.').strip()
        self._add_element(imovel, 'valor', valor_str)
        self._add_element(imovel, 'valor_locacao', str(property_data.get('valor_locacao', '')))
        self._add_element(imovel, 'valor_iptu', str(property_data.get('valor_iptu', '')))
        self._add_element(imovel, 'valor_condominio', str(property_data.get('valor_condominio', '')))
        
        # Áreas
        self._add_element(imovel, 'area_total', str(property_data.get('area_total', property_data.get('area', ''))))
        self._add_element(imovel, 'area_util', str(property_data.get('area_util', '')))
        self._add_element(imovel, 'conservacao', property_data.get('conservacao', ''))
        
        # Características
        self._add_element(imovel, 'quartos', str(property_data.get('quartos', '')))
        self._add_element(imovel, 'suites', str(property_data.get('suites', '')))
        self._add_element(imovel, 'garagem', str(property_data.get('garagem', property_data.get('vagas', ''))))
        self._add_element(imovel, 'banheiro', str(property_data.get('banheiro', property_data.get('banheiros', ''))))
        self._add_element(imovel, 'closet', str(property_data.get('closet', '')))
        self._add_element(imovel, 'salas', str(property_data.get('salas', '')))
        self._add_element(imovel, 'despensa', str(property_data.get('despensa', '')))
        self._add_element(imovel, 'bar', str(property_data.get('bar', '')))
        self._add_element(imovel, 'cozinha', str(property_data.get('cozinha', '')))
        self._add_element(imovel, 'quarto_empregada', str(property_data.get('quarto_empregada', '')))
        self._add_element(imovel, 'escritorio', str(property_data.get('escritorio', '')))
        self._add_element(imovel, 'area_servico', str(property_data.get('area_servico', '')))
        self._add_element(imovel, 'lareira', str(property_data.get('lareira', '')))
        self._add_element(imovel, 'varanda', str(property_data.get('varanda', '')))
        self._add_element(imovel, 'lavanderia', str(property_data.get('lavanderia', '')))
        self._add_element(imovel, 'aceita_pet', '1' if property_data.get('aceita_pet', False) else '0')
        
        # Endereço
        self._add_element(imovel, 'estado', property_data.get('estado', ''))
        self._add_element(imovel, 'cidade', property_data.get('cidade', property_data.get('localizacao', '').split('-')[0].strip() if property_data.get('localizacao') else ''))
        self._add_element(imovel, 'bairro', property_data.get('bairro', property_data.get('localizacao', '').split('-')[1].strip() if property_data.get('localizacao') and '-' in property_data.get('localizacao', '') else ''))
        self._add_element(imovel, 'cep', property_data.get('cep', ''))
        self._add_element(imovel, 'endereco', property_data.get('endereco', ''))
        self._add_element(imovel, 'numero', str(property_data.get('numero', '')))
        self._add_element(imovel, 'complemento', property_data.get('complemento', ''))
        self._add_element(imovel, 'esconder_endereco_imovel', str(property_data.get('esconder_endereco', '0')))
        
        # Descrição
        descritivo = property_data.get('descritivo', property_data.get('descricao', property_data.get('observacoes', '')))
        descritivo_elem = ET.SubElement(imovel, 'descritivo')
        descritivo_elem.text = descritivo
        descritivo_elem.set('xml:space', 'preserve')
        
        # Fotos
        fotos_imovel = ET.SubElement(imovel, 'fotos_imovel')
        fotos = property_data.get('fotos', property_data.get('foto_urls', []))
        if isinstance(fotos, str):
            fotos = [fotos]
        elif not isinstance(fotos, list):
            fotos = []
        
        for foto_url in fotos:
            if foto_url:
                foto = ET.SubElement(fotos_imovel, 'foto')
                self._add_element(foto, 'url', foto_url)
                self._add_element(foto, 'data_atualizacao', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        # Outros campos
        self._add_element(imovel, 'data_atualizacao', property_data.get('data_atualizacao', datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        self._add_element(imovel, 'latitude', property_data.get('latitude', ''))
        self._add_element(imovel, 'longitude', property_data.get('longitude', ''))
        self._add_element(imovel, 'video', property_data.get('video', ''))
        self._add_element(imovel, 'tour_360', property_data.get('tour_360', ''))
        
        # Áreas comuns e privativas
        area_comum = ET.SubElement(imovel, 'area_comum')
        areas_comuns = property_data.get('area_comum', property_data.get('areas_comuns', []))
        if isinstance(areas_comuns, str):
            areas_comuns = [areas_comuns]
        for area in areas_comuns:
            if area:
                self._add_element(area_comum, 'item', area)
        
        area_privativa = ET.SubElement(imovel, 'area_privativa')
        areas_privativas = property_data.get('area_privativa', property_data.get('areas_privativas', []))
        if isinstance(areas_privativas, str):
            areas_privativas = [areas_privativas]
        for area in areas_privativas:
            if area:
                self._add_element(area_privativa, 'item', area)
        
        self._add_element(imovel, 'aceita_troca', str(property_data.get('aceita_troca', '')))
        self._add_element(imovel, 'periodo_locacao', property_data.get('periodo_locacao', ''))
        
        # Formata XML
        xml_string = ET.tostring(root, encoding='unicode')
        # Formata com indentação
        dom = minidom.parseString(xml_string)
        return dom.toprettyxml(indent="    ", encoding='utf-8').decode('utf-8')
    
    def generate_feed_xml(self, properties: List[Dict]) -> str:
        """
        Gera XML feed completo com múltiplos imóveis
        
        Args:
            properties: Lista de dados de imóveis
            
        Returns:
            String XML formatada
        """
        root = ET.Element('Document')
        imoveis = ET.SubElement(root, 'imoveis')
        
        for property_data in properties:
            # Gera XML de cada imóvel
            property_xml = self.generate_property_xml(property_data)
            # Parse e adiciona ao feed
            prop_root = ET.fromstring(property_xml)
            for imovel in prop_root.findall('.//imovel'):
                imoveis.append(imovel)
        
        # Formata XML
        xml_string = ET.tostring(root, encoding='unicode')
        dom = minidom.parseString(xml_string)
        return dom.toprettyxml(indent="    ", encoding='utf-8').decode('utf-8')
    
    def generate_xml_from_form_data(self, form_data: Dict, analysis: Dict) -> str:
        """
        Gera XML a partir de dados do formulário e análise do ChatGPT
        
        Args:
            form_data: Dados do formulário
            analysis: Análise do ChatGPT
            
        Returns:
            String XML formatada
        """
        # Combina dados do formulário e análise
        info = analysis.get('informacoes_extraidas', {})
        answers = form_data.get('answers', {})
        
        # Trata orcamento que pode ser dict ou string
        orcamento = info.get('orcamento', '0')
        if isinstance(orcamento, dict):
            valor_default = orcamento.get('valor_total', orcamento.get('valor_minimo', '0'))
        else:
            valor_default = orcamento
        
        property_data = {
            # Dados básicos
            'codigo': form_data.get('response_id', ''),
            'titulo': answers.get('titulo', info.get('tipo_imovel', 'Imóvel')),
            'tipo': answers.get('tipo', info.get('tipo_imovel', 'Apartamento')),
            'transacao': answers.get('transacao', 'V'),
            'finalidade': answers.get('finalidade', 'RE'),
            
            # Valores
            'valor': answers.get('valor', valor_default),
            'valor_locacao': answers.get('valor_locacao', ''),
            'valor_condominio': answers.get('valor_condominio', ''),
            
            # Localização
            'cidade': answers.get('cidade', info.get('localizacao', '').split('-')[0].strip() if info.get('localizacao') else ''),
            'bairro': answers.get('bairro', info.get('localizacao', '').split('-')[1].strip() if info.get('localizacao') and '-' in info.get('localizacao', '') else ''),
            'estado': answers.get('estado', ''),
            'endereco': answers.get('endereco', ''),
            'numero': answers.get('numero', ''),
            'cep': answers.get('cep', ''),
            
            # Características
            'quartos': answers.get('quartos', ''),
            'suites': answers.get('suites', ''),
            'banheiro': answers.get('banheiro', ''),
            'garagem': answers.get('garagem', ''),
            'area_total': answers.get('area_total', ''),
            'area_util': answers.get('area_util', ''),
            
            # Descrição
            'descritivo': answers.get('observacoes', info.get('observacoes', '')),
            
            # Fotos
            'fotos': answers.get('fotos', []) if isinstance(answers.get('fotos'), list) else [],
        }
        
        return self.generate_property_xml(property_data)
    
    def _add_element(self, parent, tag: str, value: str):
        """Adiciona elemento XML se valor não for vazio"""
        elem = ET.SubElement(parent, tag)
        if value:
            elem.text = str(value).strip()


