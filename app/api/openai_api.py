import os
from openai import OpenAI
from google import genai
from dotenv import load_dotenv

load_dotenv()  # Carrega as variáveis de ambiente
    

def partial_request(prompt: str, context: str):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    system = f"""
Você é um assistente especializados em análise de currículos acadêmicos e profissionais.

Responda a pergunta do usuário com base no trecho de currículo fornecido.

Para isso, você receberá duas informações:
1. O prompt original enviado pelo usuário (que expressa o que ele deseja saber).
2. Um trecho do currículo acadêmico (seção).

Sua tarefa é:
- Analisar o trecho do currículo levando em consideração a pergunta.
- Responder com base apenas nas informações que estão explícitas ou fortemente implícitas nesse trecho.
- Ignorar informações que não sejam pertinentes a pergunta.
- Não extrapolar para além do conteúdo disponível na seção fornecida.

Apresente sua análise de forma clara, objetiva e bem estruturada.

---  

## Prompt do Usuário ##
{prompt}

## Trecho do Currículo ##
{context}
---

"""

    completion = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        max_tokens=3000,
        messages=[
            {"role": "developer", "content": system}
        ]
    )
    return completion.choices[0].message.content


def final_request(prompt: str, respostas: str):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    system = f"""
Você é um assistente especializado na análise de currículos acadêmicos.

Você receberá um conjunto de respostas parciais. Cada uma foi gerada a partir de uma análise de trecho específico do currículo de um acadêmico. Todas as análises seguem o mesmo prompt original, enviado por um usuário que deseja obter informações sobre o currículo.

Sua tarefa é gerar uma resposta única, clara, precisa e bem estruturada que atenda completamente ao prompt do usuário, utilizando apenas as informações fornecidas nas respostas parciais.

Instruções:

- Leia com atenção todas as respostas parciais fornecidas.
- Consolide as informações relevantes, eliminando repetições e redundâncias.
- Respeite o conteúdo: não invente ou assuma nada que não esteja explícito nas respostas parciais.
- Se houver contradições ou ambiguidade, destaque com cautela.
- A resposta final deve ser coerente, fluida e adequada ao nível de detalhe e linguagem esperados em uma análise acadêmica.
- Caso as respostas parciais sejam insuficientes, você pode incluir uma observação final indicando a limitação.

---

🔹 Prompt original do usuário:
{prompt}

🔹 Respostas parciais:
{respostas}
"""

    completion = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        max_tokens=3000,
        messages=[
            {"role": "developer", "content": system}
        ]
    )
    return completion.choices[0].message.content


def prompt_categorizer(user_input: str):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    system = """
Você é um classificador inteligente de entradas textuais segundo categorias acadêmicas. Dada uma entrada de texto (prompt do usuário), sua tarefa é identificar a categoria mais apropriada entre uma lista de categorias.

Cada categoria representa um conjunto específico de informações dentro de um currículo acadêmico. Analise cuidadosamente o conteúdo, propósito e foco da entrada para decidir 
em qual categoria ela se encaixa melhor.

### Lista de categorias ###

1. **Identificação Pessoal e Profissional**  
   **Significado:**  
   Reúne informações básicas e de contato do acadêmico, como nome completo, CPF, data de nascimento, nacionalidade, endereço, e-mail institucional, telefone, e também vínculos institucionais e cargos ocupados.  
   **Tags associadas:**  
   ["#DADOS-GERAIS"]

2. **Áreas de Atuação e Conhecimento**  
    **Significado:**  
    Define os campos científicos, tecnológicos ou artísticos nos quais o profissional atua, baseando-se em classificações como a da CAPES ou do CNPq.
    **Tags associadas:**
    ["#AREAS-DE-ATUACAO", "#PREMIOS-E-TITULOS", "#PREMIOS-TITULOS"]
    
3. **Formação Acadêmica e Qualificações**  
    **Significado:**  
    Descreve a trajetória educacional formal do profissional, incluindo cursos de graduação, pós-graduação (mestrado, doutorado), prêmios, especializações e outros certificados relevantes.  
    **Tags associadas:**
    ["#CURSO-TECNICO-PROFISSIONALIZANTE", "#ENSINO-FUNDAMENTAL-PRIMEIRO-GRAU", "#ENSINO-MEDIO-SEGUNDO-GRAU", "#GRADUACAO", "#APERFEICOAMENTO", "#ESPECIALIZACAO", "#MESTRADO", "#MESTRADO-PROFISSIONALIZANTE", "#DOUTORADO", "#RESIDENCIA-MEDICA", "#LIVRE-DOCENCIA", "#POS-DOUTORADO", "#FORMACAO-COMPLEMENTAR", "#FORMACAO-COMPLEMENTAR-DE-EXTENSAO-UNIVERSITARIA", "#MBA", "#PREMIOS-TITULOS"]
    
4. **Pesquisa e Projetos Acadêmicos**  
    **Significado:**  
    Abarca a participação e coordenação em projetos de pesquisa, linhas de pesquisa, bolsas recebidas, grupos de pesquisa e financiamento acadêmico.  
    **Tags associadas:**
    ["#ATUACAO-PROFISSIONAL"]
      
5. **Orientações e Treinamentos**  
    **Significado:**  
    Diz respeito à atuação como orientador ou supervisor de estudantes, abrangendo orientações de TCC, iniciação científica, mestrado, doutorado e pós-doutorado, além de estágios e treinamentos supervisionados. Bem como a relação da produção acadêmica de seus orientandos.  
    **Tags associadas:**
    ["#ORIENTACOES", "#TREINAMENTO", "#ORIENTACOES-CONCLUIDAS", "#ORIENTACOES-EM-ANDAMENTO", "#PARTICIPACAO-EM-BANCA-TRABALHOS-CONCLUSAO", "#OUTRAS-PARTICIPACOES-EM-BANCA"]
    
6. **Experiência Profissional**  
    **Significado:**  
    Inclui experiências em instituições públicas ou privadas, tanto no ensino quanto fora dele, como consultorias, empresas, atuação clínica, entre outras atividades profissionais.  
    **Tags associadas:**
    ["#ATUACOES-PROFISSIONAIS"]
     
7. **Atividades Acadêmicas e Administrativas**  
    **Significado:**  
    Refere-se à participação em comissões, coordenações de cursos, chefias de departamento, organização de eventos, entre outras responsabilidades dentro da estrutura acadêmica.
    **Tags associadas:**
    ["#ATUACOES-PROFISSIONAIS", "#OUTRAS-ATIVIDADES-TECNICO-CIENTIFICA", "#ORGANIZACAO-DE-EVENTO","CURSO-DE-CURTA-DURACAO-MINISTRADO", "#PARTICIPACAO-EM-BANCA-TRABALHOS-CONCLUSAO","#PARTICIPACAO-EM-BANCA-JULGADORA", "#PARTICIPACAO-EM-EVENTOS-CONGRESSOS", "#ORIENTACOES-EM-ANDAMENTO", "#INFORMACOES-ADICIONAIS-INSTITUICOES", "#INFORMACOES-ADICIONAIS-CURSOS", "ORIENTACOES-CONCLUIDAS"]
    
8. **Produção Bibliográfica**  
    **Significado:**  
    Abrange publicações acadêmicas como artigos científicos, livros, capítulos de livros, resumos em anais, trabalhos completos, entre outros materiais bibliográficos.  
    **Tags associadas:**
    ["#TRABALHOS-EM-EVENTOS", "#ARTIGOS-PUBLICADOS","#ARTIGOS-ACEITOS-PARA-PUBLICACAO","#LIVROS-E-CAPITULOS", "#CAPITULOS-DE-LIVROS-PUBLICADOS", "#TEXTOS-EM-JORNAIS-OU-REVISTAS", "#DEMAIS-TIPOS-DE-PRODUCAO-BIBLIOGRAFICA"]
    
9. **Produção Técnica e Tecnológica**  
    **Significado:**  
    Diz respeito à produção aplicada, como desenvolvimento de softwares, patentes, protótipos, relatórios técnicos, pareceres e produtos tecnológicos.  
    **Tags associadas:
    ["#PRODUCAO-TECNICA", "#REGISTRO-OU-PATENTE", "#SOFTWARE", "#PRODUTO-TECNOLOGICO", "#PATENTE", "#CULTIVAR-PROTEGIDA", "#CULTIVAR-REGISTRADA", "#DESENHO-INDUSTRIAL", "#MARCA", "#TOPOGRAFIA-DE-CIRCUITO-INTEGRADO", "#PROCESSOS-OU-TECNICAS", "#TRABALHO-TECNICO", "#DEMAIS-TIPOS-DE-PRODUCAO-TECNICA", "#CARTA-MAPA-OU-SIMILAR", "#DESENVOLVIMENTO-DE-MATERIAL-DIDATICO-OU-INSTRUCIONAL", "#EDITORACAO", "#MANUTENCAO-DE-OBRA-ARTISTICA", "#MAQUETE", "#PROGRAMA-DE-RADIO-OU-TV", "#MIDIA-SOCIAL-WEBSITE-BLOG"]
     
10. **Produção Artística e Cultural**  
    **Significado:**  
    Inclui obras artísticas, exposições, performances, composições, curadorias e demais produções voltadas à expressão cultural e artística.  
    **Tags associadas:**
    ["#PRODUCAO-ARTISTICA-CULTURAL", "#APRESENTACAO-DE-OBRA-ARTISTICA", "#APRESENTACAO-EM-RADIO-OU-TV", "#ARRANJO-MUSICAL", "#COMPOSICAO-MUSICAL", "#OBRA-DE-ARTES-VISUAIS", "#OUTRA-PRODUCAO-ARTISTICA-CULTURAL", "#SONOPLASTIA", "#ARTES-CENICAS", "#ARTES-VISUAIS", "#MUSICA", "#PARTITURA-MUSICAL"]
    

### Fim da Lista de categorias ###

## Instruções: ##

- Escolha apenas uma das Categorias.
- Responda a categoria com todas as informações relacionadas a categoria provenientes da lista de categorias.
- Caso a entrada seja ambígua ou genérica, escolha a categoria mais provável com base no conteúdo principal.
- 
## Fim das Instruções ##

## Exemplo de uso ##

Entrada: Qual a experiência do pesquisador na produção de artigos na área de Inteligência Artificial?

Saída: 
8. **Produção Bibliográfica**  
    **Significado:**  
    Abrange publicações acadêmicas como artigos científicos, livros, capítulos de livros, resumos em anais, trabalhos completos, entre outros materiais bibliográficos.  
    **Tags associadas:**
    ["#TRABALHOS-EM-EVENTOS", "#ARTIGOS-PUBLICADOS","#ARTIGOS-ACEITOS-PARA-PUBLICACAO","#LIVROS-E-CAPITULOS", "#CAPITULOS-DE-LIVROS-PUBLICADOS", "#TEXTOS-EM-JORNAIS-OU-REVISTAS", "#DEMAIS-TIPOS-DE-PRODUCAO-BIBLIOGRAFICA"]

## Fim dos Exemplos de Uso ##
"""

    completion = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {"role": "developer", "content": system},
            {"role": "user", "content": f"Prompt a ser analisado: {user_input}"}
        ]
    )
    
    return completion.choices[0].message.content

def gpt_request(prompt: str, curriculo: str):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    system = f"""
Você é um assistente especializado na análise de currículos acadêmicos.

Sua tarefa é gerar uma resposta única, clara, precisa e bem estruturada que atenda completamente ao prompt do usuário, utilizando apenas as informações fornecidas no currículo.

Instruções:

- Leia com atenção o currículo.
- Consolide as informações relevantes, eliminando repetições e redundâncias.
- Respeite o conteúdo: não invente ou assuma nada que não esteja explícito no currículo.
- Se houver contradições ou ambiguidade, destaque com cautela.
- A resposta final deve ser coerente, fluida e adequada ao nível de detalhe e linguagem esperados em uma análise acadêmica.
- Caso os dados do currículo sejam insuficientes, você pode incluir uma observação final indicando a limitação.

---

🔹 Prompt original do usuário:
{prompt}

🔹 Currículo:
{curriculo}
"""

    completion = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {"role": "developer", "content": system}
        ]
    )
    return completion.choices[0].message.content



def gemini_request(prompt: str, curriculo: str):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    system = f"""
Você é um assistente especializado na análise de currículos acadêmicos.

Sua tarefa é gerar uma resposta única, clara, precisa e bem estruturada que atenda completamente ao prompt do usuário, utilizando apenas as informações fornecidas no currículo.

Instruções:

- Leia com atenção o currículo.
- Consolide as informações relevantes, eliminando repetições e redundâncias.
- Respeite o conteúdo: não invente ou assuma nada que não esteja explícito no currículo.
- Se houver contradições ou ambiguidade, destaque com cautela.
- A resposta final deve ser coerente, fluida e adequada ao nível de detalhe e linguagem esperados em uma análise acadêmica.
- Caso os dados do currículo sejam insuficientes, você pode incluir uma observação final indicando a limitação.
- Se precisar pesquise na internet
---

🔹 Prompt original do usuário:
{prompt}

🔹 Currículo:
{curriculo}
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=system
    )
    return response.text