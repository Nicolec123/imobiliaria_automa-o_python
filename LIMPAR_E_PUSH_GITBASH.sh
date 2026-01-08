#!/bin/bash
echo "========================================"
echo "  LIMPAR HISTÓRICO E FAZER PUSH"
echo "========================================"
echo ""
echo "Este script vai:"
echo "  1. Remover .git (histórico antigo)"
echo "  2. Criar novo repositório limpo"
echo "  3. Fazer commit"
echo "  4. Fazer push forçado"
echo ""
echo "⚠️  ATENÇÃO: Isso vai substituir TUDO no GitHub!"
echo ""
read -p "Pressione ENTER para continuar..."

echo ""
echo "Removendo histórico antigo..."
if [ -d ".git" ]; then
    rm -rf .git
    echo "✅ Histórico removido"
else
    echo "ℹ️  Não havia histórico"
fi

echo ""
echo "Inicializando novo repositório..."
git init
git add .
git commit -m "Initial commit - Sistema de Integração Imobiliária (sem segredos)"

echo ""
echo "Adicionando remote..."
git remote add origin https://github.com/Nicolec123/imobiliaria_automa-o_python.git 2>/dev/null
git remote set-url origin https://github.com/Nicolec123/imobiliaria_automa-o_python.git

echo ""
echo "Fazendo push forçado..."
git push -u origin master --force

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SUCESSO! Push realizado!"
    echo ""
    echo "Agora você pode configurar o Railway."
else
    echo ""
    echo "❌ Erro no push"
    echo ""
    echo "Verifique:"
    echo "  - Se o repositório existe no GitHub"
    echo "  - Se você tem permissão"
    echo "  - Se não há mais segredos nos arquivos"
fi

echo ""
read -p "Pressione ENTER para sair..."
