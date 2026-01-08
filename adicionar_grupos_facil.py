"""
Script interativo para adicionar grupos facilmente ao wasseller_config.json
"""
import json
import os

def adicionar_grupos():
    """Adiciona grupos de forma interativa"""
    
    print("="*70)
    print("📱 ADICIONAR GRUPOS AO WASSELLER")
    print("="*70)
    
    config_path = 'wasseller_config.json'
    
    # Carrega configuração existente
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"\n❌ Arquivo {config_path} não encontrado!")
        return
    except json.JSONDecodeError:
        print(f"\n❌ Erro ao ler {config_path}. Verifique se o JSON está válido.")
        return
    
    grupos = config.get('notificacoes', {}).get('grupos', [])
    
    print(f"\n📋 Grupos atuais: {len(grupos)}")
    if grupos:
        print("\nGrupos configurados:")
        for i, grupo in enumerate(grupos, 1):
            print(f"   {i}. {grupo.get('nome', 'Sem nome')} - {grupo.get('id', 'Sem ID')}")
    
    print("\n" + "="*70)
    print("ADICIONAR NOVO GRUPO")
    print("="*70)
    
    while True:
        print("\n--- Novo Grupo ---")
        
        nome = input("Nome do grupo (ex: Equipe de Vendas): ").strip()
        if not nome:
            print("❌ Nome é obrigatório!")
            continue
        
        grupo_id = input("ID do grupo (ex: 5511999999999@g.us ou número): ").strip()
        if not grupo_id:
            print("❌ ID é obrigatório!")
            continue
        
        # Remove caracteres não numéricos se for só número
        grupo_id_limpo = ''.join(filter(str.isdigit, grupo_id))
        if grupo_id_limpo and not '@' in grupo_id:
            # Se for só número, formata como grupo WhatsApp
            if not grupo_id_limpo.startswith('55'):
                grupo_id_limpo = '55' + grupo_id_limpo
            grupo_id = grupo_id_limpo + '@g.us'
        
        novo_grupo = {
            "id": grupo_id,
            "nome": nome,
            "ativo": True
        }
        
        grupos.append(novo_grupo)
        print(f"\n✅ Grupo '{nome}' adicionado!")
        
        continuar = input("\nAdicionar outro grupo? (s/N): ").strip().lower()
        if continuar != 's':
            break
    
    # Atualiza configuração
    if 'notificacoes' not in config:
        config['notificacoes'] = {}
    config['notificacoes']['grupos'] = grupos
    
    # Salva arquivo
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Configuração salva em {config_path}!")
        print(f"📊 Total de grupos: {len(grupos)}")
    except Exception as e:
        print(f"\n❌ Erro ao salvar: {e}")

def remover_grupos():
    """Remove grupos da configuração"""
    
    print("="*70)
    print("🗑️  REMOVER GRUPOS")
    print("="*70)
    
    config_path = 'wasseller_config.json'
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"\n❌ Arquivo {config_path} não encontrado!")
        return
    
    grupos = config.get('notificacoes', {}).get('grupos', [])
    
    if not grupos:
        print("\n⚠️  Nenhum grupo configurado!")
        return
    
    print("\nGrupos configurados:")
    for i, grupo in enumerate(grupos, 1):
        print(f"   {i}. {grupo.get('nome', 'Sem nome')} - {grupo.get('id', 'Sem ID')}")
    
    try:
        indice = int(input("\nDigite o número do grupo para remover (0 para cancelar): "))
        if indice == 0:
            return
        if 1 <= indice <= len(grupos):
            grupo_removido = grupos.pop(indice - 1)
            config['notificacoes']['grupos'] = grupos
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ Grupo '{grupo_removido.get('nome')}' removido!")
        else:
            print("❌ Número inválido!")
    except ValueError:
        print("❌ Digite um número válido!")
    except Exception as e:
        print(f"\n❌ Erro: {e}")

def menu():
    """Menu principal"""
    while True:
        print("\n" + "="*70)
        print("MENU - GERENCIAR GRUPOS")
        print("="*70)
        print("\nEscolha uma opção:")
        print("  1. Adicionar grupos")
        print("  2. Remover grupos")
        print("  3. Ver grupos atuais")
        print("  4. Sair")
        
        opcao = input("\nOpção: ").strip()
        
        if opcao == '1':
            adicionar_grupos()
        elif opcao == '2':
            remover_grupos()
        elif opcao == '3':
            try:
                with open('wasseller_config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
                grupos = config.get('notificacoes', {}).get('grupos', [])
                print(f"\n📋 Total: {len(grupos)} grupos")
                for i, grupo in enumerate(grupos, 1):
                    status = "✅ Ativo" if grupo.get('ativo', True) else "❌ Inativo"
                    print(f"   {i}. {grupo.get('nome', 'Sem nome')} - {grupo.get('id', 'Sem ID')} [{status}]")
            except Exception as e:
                print(f"\n❌ Erro: {e}")
        elif opcao == '4':
            print("\n👋 Até logo!")
            break
        else:
            print("\n❌ Opção inválida!")

if __name__ == '__main__':
    try:
        menu()
    except KeyboardInterrupt:
        print("\n\n👋 Interrompido pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro: {e}")

