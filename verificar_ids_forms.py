"""
Script para verificar se os IDs dos formulários estão corretos
"""
import json
import re

# Links fornecidos pelo usuário
links_fornecidos = {
    "C.I - Vitacon": "https://docs.google.com/forms/d/e/1FAIpQLScjeo68Y9uzap5FFOYpCN0Jt9e0rq1fGl3GL12X_kcz70LIXg/viewform?usp=dialog",
    "C.I - Compact Home's - Studios, Flats e Lofts": "https://docs.google.com/forms/d/e/1FAIpQLSejcWTIXyPLmV12Vtocwa_idahZRFmDzbgWVDViI5vKVGKDcg/viewform?usp=dialog",
    "C.I - Terras e Investimentos": "https://docs.google.com/forms/d/e/1FAIpQLSczrCo8gGYKa1FYRLX9cVluFpsH8mMWt-QXKCv_zPRUjZzTBw/viewform?usp=dialog",
    "C.I - Signature - Alto Padrão": "https://docs.google.com/forms/d/e/1FAIpQLSeXt_q6Cyjp9oNm1BTJZGYwuTl5l3s0u8EdBMk4lg3dQz8aZw/viewform?usp=dialog",
    "C.I - Urban Living – Médio Padrão": "https://docs.google.com/forms/d/e/1FAIpQLScfFCz0aFdTnRe6lKEBqW1nmSZ4N6IQKgVXSO5ZgrmY1L7IUA/viewform?usp=dialog",
    "C.I - Smart Key - Imóveis Econômicos": "https://docs.google.com/forms/d/e/1FAIpQLSced8d4W_V0OvY2dxcmk4bgbcBOdqyvufkyYqdfxiCJZkGpmg/viewform?usp=dialog",
    "C.I - Corporate": "https://docs.google.com/forms/d/e/1FAIpQLSclmHp4eRsoeP8RyQZGAdZq0_Tm_Yc5N7uB07fGDWfkXUZpNA/viewform?usp=dialog",
    "C.I - Business Spaces - Espaços Empresariais": "https://docs.google.com/forms/d/e/1FAIpQLSfJH_Nb6bTc7LymRLTvfJ_IA96Y9xOYHawrDT5RMXE0CeBR7A/viewform?usp=dialog"
}

def extrair_id_do_link(link):
    """Extrai o ID do formulário do link"""
    match = re.search(r'/d/e/([^/]+)', link)
    if match:
        return match.group(1)
    return None

def verificar_ids():
    """Verifica se os IDs estão corretos"""
    print("="*70)
    print("  VERIFICAÇÃO DE IDs DOS FORMULÁRIOS")
    print("="*70)
    
    # Carrega forms_config.json
    try:
        with open('forms_config.json', 'r', encoding='utf-8') as f:
            forms_config = json.load(f)
    except Exception as e:
        print(f"❌ Erro ao carregar forms_config.json: {e}")
        return
    
    forms = forms_config.get('forms', [])
    
    print(f"\n📋 Comparando {len(forms)} formulários...\n")
    
    todos_corretos = True
    
    for form in forms:
        nome = form.get('name', '')
        id_config = form.get('id', '')
        url_config = form.get('url', '')
        
        # Extrai ID do link fornecido
        link_fornecido = links_fornecidos.get(nome)
        if link_fornecido:
            id_fornecido = extrair_id_do_link(link_fornecido)
            
            if id_config == id_fornecido:
                print(f"✅ {nome}")
                print(f"   ID correto: {id_config}")
            else:
                print(f"❌ {nome}")
                print(f"   ID no config: {id_config}")
                print(f"   ID no link:   {id_fornecido}")
                print(f"   ⚠️  IDs DIFERENTES!")
                todos_corretos = False
        else:
            print(f"⚠️  {nome}")
            print(f"   Link não fornecido")
    
    print("\n" + "="*70)
    
    if todos_corretos:
        print("✅ TODOS OS IDs ESTÃO CORRETOS!")
        print("\n💡 O problema pode ser:")
        print("   1. Conta autorizada não tem acesso aos formulários")
        print("   2. Formulários precisam ser compartilhados com a conta")
        print("   3. Permissões insuficientes (precisa ser Editor, não apenas Visualizador)")
    else:
        print("❌ ALGUNS IDs ESTÃO INCORRETOS!")
        print("   Atualize o forms_config.json com os IDs corretos")
    
    print("="*70)

if __name__ == '__main__':
    verificar_ids()

