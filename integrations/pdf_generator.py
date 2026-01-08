"""
Gerador de PDF para imóveis e demandas
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from typing import Dict, Optional
from datetime import datetime
import os


class PDFGenerator:
    """Classe para gerar PDFs formatados"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configura estilos customizados"""
        # Título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#283593'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        # Texto normal
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6
        ))
    
    def generate_property_pdf(
        self,
        form_data: Dict,
        analysis: Dict,
        response_id: str,
        output_path: Optional[str] = None
    ) -> str:
        """
        Gera PDF formatado com dados do imóvel
        
        Args:
            form_data: Dados do formulário
            analysis: Análise do ChatGPT
            response_id: ID da resposta
            output_path: Caminho para salvar PDF (opcional)
            
        Returns:
            Caminho do arquivo PDF gerado
        """
        if not output_path:
            os.makedirs('pdfs', exist_ok=True)
            output_path = f"pdfs/imovel_{response_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        # Título
        title = Paragraph("DADOS DO IMÓVEL", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.3*inch))
        
        # Informações básicas
        story.append(Paragraph("INFORMAÇÕES BÁSICAS", self.styles['CustomHeading']))
        
        answers = form_data.get('answers', {})
        info = analysis.get('informacoes_extraidas', {})
        
        # Tabela de dados básicos
        basic_data = [
            ['Campo', 'Valor'],
            ['ID do Cadastro', response_id],
            ['Data de Cadastro', datetime.now().strftime('%d/%m/%Y %H:%M:%S')],
            ['Tipo de Imóvel', answers.get('tipo_imovel', info.get('tipo_imovel', 'Não informado'))],
            ['Localização', answers.get('localizacao', info.get('localizacao', 'Não informado'))],
            ['Valor/Orçamento', answers.get('valor', answers.get('orcamento', info.get('orcamento', 'Não informado')))],
        ]
        
        basic_table = Table(basic_data, colWidths=[2*inch, 4*inch])
        basic_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3949ab')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        story.append(basic_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Detalhes do imóvel
        if answers.get('quartos') or answers.get('banheiro') or answers.get('garagem'):
            story.append(Paragraph("CARACTERÍSTICAS DO IMÓVEL", self.styles['CustomHeading']))
            
            characteristics = []
            if answers.get('quartos'):
                characteristics.append(['Quartos', str(answers.get('quartos'))])
            if answers.get('banheiro'):
                characteristics.append(['Banheiros', str(answers.get('banheiro'))])
            if answers.get('garagem'):
                characteristics.append(['Vagas de Garagem', str(answers.get('garagem'))])
            if answers.get('area_total'):
                characteristics.append(['Área Total', f"{answers.get('area_total')} m²"])
            if answers.get('area_util'):
                characteristics.append(['Área Útil', f"{answers.get('area_util')} m²"])
            
            if characteristics:
                char_table = Table(characteristics, colWidths=[2*inch, 4*inch])
                char_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#5c6bc0')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey)
                ]))
                story.append(char_table)
                story.append(Spacer(1, 0.2*inch))
        
        # Análise do ChatGPT
        story.append(Paragraph("ANÁLISE INTELIGENTE", self.styles['CustomHeading']))
        
        analysis_data = [
            ['Item', 'Informação'],
            ['Tipo de Lead', analysis.get('tipo_lead', 'N/A')],
            ['Prioridade', analysis.get('prioridade', 'N/A').upper()],
            ['Categoria', analysis.get('categoria', 'N/A')],
        ]
        
        if analysis.get('resumo'):
            analysis_data.append(['Resumo', analysis.get('resumo')])
        
        analysis_table = Table(analysis_data, colWidths=[2*inch, 4*inch])
        analysis_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7986cb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        story.append(analysis_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Observações
        observacoes = answers.get('observacoes') or info.get('observacoes')
        if observacoes:
            story.append(Paragraph("OBSERVAÇÕES", self.styles['CustomHeading']))
            story.append(Paragraph(str(observacoes), self.styles['CustomBody']))
            story.append(Spacer(1, 0.2*inch))
        
        # Ações sugeridas
        if analysis.get('acoes_sugeridas'):
            story.append(Paragraph("AÇÕES SUGERIDAS", self.styles['CustomHeading']))
            for i, acao in enumerate(analysis.get('acoes_sugeridas', []), 1):
                story.append(Paragraph(f"{i}. {acao}", self.styles['CustomBody']))
        
        # Rodapé
        story.append(Spacer(1, 0.3*inch))
        footer = Paragraph(
            f"Gerado automaticamente em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            ParagraphStyle(
                name='Footer',
                parent=self.styles['Normal'],
                fontSize=8,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
        )
        story.append(footer)
        
        # Gera PDF
        doc.build(story)
        return output_path
    
    def generate_demand_pdf(
        self,
        form_data: Dict,
        analysis: Dict,
        response_id: str,
        output_path: Optional[str] = None
    ) -> str:
        """
        Gera PDF formatado com dados da demanda do cliente
        
        Args:
            form_data: Dados do formulário
            analysis: Análise do ChatGPT
            response_id: ID da resposta
            output_path: Caminho para salvar PDF (opcional)
            
        Returns:
            Caminho do arquivo PDF gerado
        """
        if not output_path:
            os.makedirs('pdfs', exist_ok=True)
            output_path = f"pdfs/demanda_{response_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        # Título
        title = Paragraph("DEMANDA DO CLIENTE", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.3*inch))
        
        # Informações do cliente
        story.append(Paragraph("DADOS DO CLIENTE", self.styles['CustomHeading']))
        
        answers = form_data.get('answers', {})
        info = analysis.get('informacoes_extraidas', {})
        
        client_data = [
            ['Campo', 'Valor'],
            ['ID da Demanda', response_id],
            ['Data de Cadastro', datetime.now().strftime('%d/%m/%Y %H:%M:%S')],
            ['Nome', answers.get('nome', info.get('nome', 'Não informado'))],
            ['Telefone', answers.get('telefone', info.get('telefone', 'Não informado'))],
            ['Email', answers.get('email', info.get('email', 'Não informado'))],
        ]
        
        client_table = Table(client_data, colWidths=[2*inch, 4*inch])
        client_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3949ab')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        story.append(client_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Demanda
        story.append(Paragraph("INFORMAÇÕES DA DEMANDA", self.styles['CustomHeading']))
        
        demand_data = [
            ['Campo', 'Valor'],
            ['Tipo de Imóvel', answers.get('tipo_imovel', info.get('tipo_imovel', 'Não informado'))],
            ['Localização', answers.get('localizacao', info.get('localizacao', 'Não informado'))],
            ['Orçamento', answers.get('orcamento', info.get('orcamento', 'Não informado'))],
        ]
        
        if answers.get('quartos'):
            demand_data.append(['Quartos', str(answers.get('quartos'))])
        if answers.get('banheiro'):
            demand_data.append(['Banheiros', str(answers.get('banheiro'))])
        
        demand_table = Table(demand_data, colWidths=[2*inch, 4*inch])
        demand_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#5c6bc0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        story.append(demand_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Análise
        story.append(Paragraph("ANÁLISE INTELIGENTE", self.styles['CustomHeading']))
        
        analysis_data = [
            ['Item', 'Informação'],
            ['Tipo de Lead', analysis.get('tipo_lead', 'N/A')],
            ['Prioridade', analysis.get('prioridade', 'N/A').upper()],
        ]
        
        if analysis.get('resumo'):
            analysis_data.append(['Resumo', analysis.get('resumo')])
        
        analysis_table = Table(analysis_data, colWidths=[2*inch, 4*inch])
        analysis_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7986cb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        story.append(analysis_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Observações
        observacoes = answers.get('observacoes') or info.get('observacoes')
        if observacoes:
            story.append(Paragraph("OBSERVAÇÕES", self.styles['CustomHeading']))
            story.append(Paragraph(str(observacoes), self.styles['CustomBody']))
            story.append(Spacer(1, 0.2*inch))
        
        # Ações sugeridas
        if analysis.get('acoes_sugeridas'):
            story.append(Paragraph("AÇÕES SUGERIDAS", self.styles['CustomHeading']))
            for i, acao in enumerate(analysis.get('acoes_sugeridas', []), 1):
                story.append(Paragraph(f"{i}. {acao}", self.styles['CustomBody']))
        
        # Rodapé
        story.append(Spacer(1, 0.3*inch))
        footer = Paragraph(
            f"Gerado automaticamente em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            ParagraphStyle(
                name='Footer',
                parent=self.styles['Normal'],
                fontSize=8,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
        )
        story.append(footer)
        
        # Gera PDF
        doc.build(story)
        return output_path

