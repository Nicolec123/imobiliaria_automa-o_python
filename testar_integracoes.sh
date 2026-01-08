#!/bin/bash

echo "========================================"
echo "  TESTE DE INTEGRAÇÕES - IMOBILIÁRIA"
echo "========================================"
echo ""

# Verifica se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "[ERRO] Python não encontrado!"
    echo "Por favor, instale Python 3.8 ou superior."
    exit 1
fi

echo "[OK] Python encontrado"
python3 --version
echo ""

# Verifica se as dependências estão instaladas
echo "Verificando dependências..."
if ! python3 -c "import flask" &> /dev/null; then
    echo "[AVISO] Dependências não encontradas. Instalando..."
    echo ""
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[ERRO] Falha ao instalar dependências!"
        exit 1
    fi
    echo ""
    echo "[OK] Dependências instaladas!"
    echo ""
else
    echo "[OK] Dependências já instaladas"
    echo ""
fi

# Executa o teste
echo "========================================"
echo "  Executando testes de integrações..."
echo "========================================"
echo ""
python3 testar_integracoes_individualmente.py

echo ""
echo "========================================"
echo "  Teste concluído!"
echo "========================================"
echo ""
read -p "Pressione Enter para fechar..."

