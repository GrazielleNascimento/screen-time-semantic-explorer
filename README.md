# Capstone Data Science

🇧🇷 Português · [🇺🇸 English](README-EN.md)

## Busca Semântica, Controle de Qualidade e Exploração de Clusters em Artigos Científicos

## O que é este projeto?

Um sistema completo que transforma artigos científicos em PDF em uma **aplicação interativa** para explorar um corpus de documentos usando embeddings e clusterização.

1. Os documentos são carregados e divididos em trechos (chunks).
2. Cada trecho vira um **embedding** (representação numérica do significado) guardado em um banco vetorial.
3. Você pode **buscar por sentido**, não por palavra exata.
4. Um **Isolation Forest** marca os trechos anômalos; o sistema gera um **relatório de qualidade** (antes e depois da limpeza) e remove esses trechos do banco.
5. Uma **interface web** (Streamlit) oferece busca, um **mapa interativo de clusters (K-Means / t-SNE)** e o relatório de qualidade.

**Exemplo:** se você buscar "efeitos do tempo de tela em crianças", o sistema também encontra trechos sobre "impacto de mídias digitais em menores de idade", mesmo que não usem as mesmas palavras.

Os relatórios técnicos (diagramas de arquitetura, decisões, resultados e trabalhos futuros) estão disponíveis em [português](docs/relatorio_projeto.md) e [inglês](docs/project_report.md).

## Domínio escolhido

**Efeitos do uso de telas em crianças e adolescentes**

Temas cobertos nos artigos:

- Tempo de tela (screen time) e saúde mental
- Mídia digital e obesidade infantil
- Impacto no sono e na qualidade do sono
- Desenvolvimento cognitivo e aprendizagem
- Comportamento e socialização
- Intervenções e recomendações clínicas

**Fonte dos dados:** 30 artigos científicos de acesso aberto do **PubMed Central (PMC)**, coletados em 2026. Os nomes dos PDFs são seus identificadores PMC (ex.: `PMC13589963.pdf`).

## Pipeline (fluxo dos dados)

```
PDFs / .txt (data/raw/)
    |
    v
[loader.py]   Extração de texto + chunking (250 caracteres, 50 de sobreposição)
    |
    v
chunks.jsonl (data/processed/)   6.165 trechos
    |
    v
[clean.py]    Remove trechos vazios, curtos, quase só números ou com muito lixo (regras, sem ML)
    |
    v
chunks.jsonl (filtrado)          6.069 trechos
    |
    v
[embedder.py] Embeddings (all-MiniLM-L6-v2, ONNX) + indexação no ChromaDB
    |
    v
ChromaDB (data/chroma/)          Banco vetorial persistido, 6.069 trechos
    |
    +--> [search.py]       Busca semântica (terminal e interface)
    |
    +--> [run_quality.py]  Isolation Forest -> reports/quality_report.md
    |                      remove 183 trechos anômalos -> 5.886 trechos
    |
    +--> [clustering.py]   K-Means (N escolhido pelo usuário) + mapa t-SNE
    |
    v
[app.py]  Interface Streamlit: Home | Search | Clusters | Quality report
```

Cada etapa lê a saída da anterior, então cada script pode ser rodado de forma independente.

## Interface web

Rode `streamlit run app.py` e abra http://localhost:8501. O menu lateral alterna entre quatro páginas:

| Página | O que faz |
|---|---|
| **Home** | Tela de abertura: número de trechos indexados, de documentos de origem e de trechos removidos pelo controle de qualidade; atalhos para as outras páginas; seis temas de pesquisa que abrem a busca com uma pergunta pronta. |
| **Search** | Digite uma pergunta e veja os 5 trechos mais parecidos (de 1 a 10 no controle deslizante). Cada resultado mostra o PDF de origem, o número do chunk, a **distância** de cosseno, a **similaridade** (1 − distância) e o texto. |
| **Clusters** | Escolha o número de clusters N (2 a 10). Os trechos são reagrupados com **K-Means** e desenhados em um mapa **t-SNE** interativo. Ao passar o mouse em um ponto aparecem PDF, número do chunk e um trecho do texto. Abaixo do mapa, cada cluster mostra tamanho, termos característicos (TF-IDF) e PDFs principais. Um botão exporta o gráfico atual em HTML para `reports/figures/`. |
| **Quality report** | Mostra `reports/quality_report.md`: o que o Isolation Forest encontrou e como o banco ficou antes e depois da limpeza. |

Se o índice não existir, todas as páginas mostram **"Index not found. Run the pipeline first"** em vez de quebrar.

### Capturas de tela

**Página inicial:**

![Home](docs/screenshots/home.png)

**Busca com resultados:**

![Página de busca com resultados](docs/screenshots/search.png)

**Busca sem resultados:**

![Página de busca sem resultados](docs/screenshots/search_empty.png)

**Clusters e relatório de qualidade:**

![Clusters](docs/screenshots/clusters.png)
![Relatório de qualidade](docs/screenshots/quality.png)

Os gráficos interativos de clusters também podem ser abertos diretamente no navegador:

- [Visualizar clusters com K=3](reports/figures/clusters_k3.html)
- [Visualizar clusters com K=5](reports/figures/clusters_k5.html)
- [Visualizar clusters com K=10](reports/figures/clusters_k10.html)

## Estrutura do projeto

```
CAPSTONE/
├── app.py                   # Interface Streamlit (ponto de entrada)
├── data/
│   ├── raw/                 # PDFs originais (30 artigos)
│   ├── processed/
│   │   ├── chunks.jsonl     # Trechos de texto extraídos e limpos
│   │   └── tsne_coords.npy  # Cache do t-SNE (gerado, não versionado)
│   └── chroma/              # Banco vetorial ChromaDB (gerado, não versionado)
├── src/
│   ├── loader.py            # Lê PDF / .txt -> chunks.jsonl
│   ├── clean.py             # Filtra chunks.jsonl (remove ruído)
│   ├── embedder.py          # Gera embeddings -> ChromaDB
│   ├── search.py            # Busca semântica (terminal e interface)
│   ├── store.py             # Lê o corpus / apaga ids no ChromaDB
│   ├── anomaly.py           # Isolation Forest
│   ├── quality_report.py    # Escreve reports/quality_report.md
│   ├── run_quality.py       # Roda o controle de qualidade (aceita --dry-run)
│   ├── clustering.py        # K-Means, t-SNE e resumos de cluster com TF-IDF
│   ├── test_search.py       # Valida a busca (domínio vs fora do domínio, usa o banco real)
│   ├── demo.py              # Demonstração com perguntas fixas
│   └── logging_config.py    # Configuração de logs
├── ui/                      # Código da interface (um arquivo por página + tema e componentes)
├── tests/                   # Testes automáticos (32, sem rede e sem o banco real)
├── reports/
│   ├── quality_report.md    # Gerado por run_quality.py
│   ├── removed_ids.json     # Ids removidos do banco (auditoria)
│   └── figures/             # Gráficos de clusters exportados (plano B para apresentações)
├── assets/topics/           # Ilustrações SVG dos temas de pesquisa
├── docs/
│   ├── relatorio_projeto.md # Relatório técnico (português)
│   ├── project_report.md    # Relatório técnico (inglês)
│   └── screenshots/         # Prints da interface
├── .streamlit/config.toml   # Tema da interface
├── Dockerfile, docker-compose.yml, .dockerignore
├── .gitlab-ci.yml           # CI: roda os testes
├── requirements.txt         # Dependências Python
└── README.md / README-EN.md # Documentação (português / inglês)
```

## Instalação

### Pré-requisitos

- Python 3.10+
- Windows, macOS ou Linux
- Git (opcional)
- Docker (opcional, para rodar a interface em contêiner)

### Passo 1: Obter o projeto

```bash
git clone <url-do-seu-repositorio>
cd CAPSTONE
```

### Passo 2: Criar um ambiente virtual

```bash
python -m venv venv
```

Ativar:

- **Windows (Git Bash):** `source venv/Scripts/activate`
- **Windows (PowerShell):** `.\venv\Scripts\Activate.ps1`
- **Windows (CMD):** `venv\Scripts\activate.bat`
- **Linux / macOS:** `source venv/bin/activate`

### Passo 3: Instalar as dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Bibliotecas principais: `pypdf` (leitura de PDF), `chromadb` (banco vetorial, que também traz o modelo de embeddings), `scikit-learn` (Isolation Forest, K-Means, t-SNE, TF-IDF), `streamlit` e `plotly` (interface e gráfico interativo). **Não há PyTorch**: o modelo de embeddings roda no ONNX Runtime dentro do ChromaDB.

## Como rodar

### 1. Construir o índice (do zero)

Execute **nesta ordem**:

```bash
python src/loader.py      # Lê os PDFs (e arquivos .txt) e gera os chunks
python src/clean.py       # Remove trechos inválidos
python src/embedder.py    # Gera embeddings e carrega o ChromaDB (leva alguns minutos)
```

O `embedder.py` baixa o modelo de embeddings (~80 MB) na primeira execução e o guarda em cache. Ele apaga e recria a collection, então sempre começa de um índice limpo.

### 2. Rodar o controle de qualidade

```bash
python src/run_quality.py --dry-run   # só detecta e escreve a seção "antes" (nada é removido)
python src/run_quality.py             # detecta, relata, remove as anomalias e escreve a seção "depois"
```

O segundo comando **altera o banco**. **Rode uma vez por índice**: rodar de novo analisa o banco já limpo e remove outros ~3%. Para recomeçar, rode `python src/embedder.py` antes.

### 3. Abrir a interface

```bash
streamlit run app.py
```

Depois abra http://localhost:8501. Na página Clusters, a primeira execução calcula o mapa t-SNE (cerca de um minuto) e o guarda em `data/processed/tsne_coords.npy`.

### 4. Buscar pelo terminal

```bash
python src/search.py "screen time and obesity in children"
python src/search.py "does screen time affect sleep in children?"
```

### 5. Rodar com Docker

```bash
docker compose up --build
```

A interface fica em http://localhost:8501. As pastas `data/` e `reports/` são montadas como volumes, então **`data/chroma/` precisa já existir** (rode o pipeline antes); senão a página mostra "Index not found". Na primeira busca o contêiner baixa o modelo de embeddings (~80 MB), então precisa de internet nessa vez. Para parar: `docker compose down`.

### 6. Rodar os testes

```bash
python -m unittest discover -s tests -t . -v
```

32 testes, cerca de 3 segundos. Usam dados sintéticos e um ChromaDB em memória: sem rede, sem baixar modelo e sem o banco real. O mesmo comando roda no CI do GitLab (`.gitlab-ci.yml`).

### Teste rápido de validação da busca

Compara uma busca **dentro do domínio** com uma **fora do domínio** (usa o banco real):

```bash
python src/test_search.py
```

Resultado obtido neste projeto:

```
Query: "screen time and obesity"   -> distância média 0.17
Query: "recipe for chocolate cake" -> distância média 0.78
OK: a busca do domínio retornou distâncias menores que a busca sem relação.
```

Se as distâncias do domínio forem claramente menores, o índice está funcionando.

### Demonstração (várias perguntas)

```bash
python src/demo.py
```

Roda uma lista fixa de perguntas (duas do domínio mais uma de controle fora do tema) e imprime, para cada resultado: distância, similaridade, PDF de origem e número do chunk. Cada resultado mostra a distância de cosseno (quanto menor, mais relevante) e a similaridade (1 − distância).

## Controle de qualidade com Isolation Forest

O controle de qualidade roda **depois** que o banco vetorial está carregado, sobre **todos os embeddings de uma vez**: um trecho só é anômalo *em relação ao restante do corpus*.

- **Isolation Forest** (`src/anomaly.py`): 200 árvores aleatórias. Um trecho que é isolado com poucos cortes recebe **nota baixa**, ou seja, é mais anômalo. `contamination = 0.03` significa que os 3% de menor nota são marcados.
- **Relatório** (`reports/quality_report.md`, gerado por `src/run_quality.py`, nunca escrito à mão): parâmetros, totais e estatísticas das notas antes da limpeza, os 15 trechos mais anômalos, anomalias por PDF e o banco depois da limpeza.
- **Auditoria:** os ids removidos são salvos em `reports/removed_ids.json` antes de qualquer remoção.

Resultado neste projeto:

| | Trechos |
|---|---|
| Antes da limpeza | 6.069 |
| Marcados como anômalos (3,02%) | 183 |
| Depois da limpeza | 5.886 |

**Nota de curadoria:** nem todo trecho marcado é lixo. Entre os mais anômalos há ruído de verdade (listas de países, um preâmbulo de LaTeX, uma lista de personagens de TV), mas também texto legítimo de métodos. O relatório mostra exemplos para que a remoção possa ser revisada antes de confiar nela.

## Clusters (K-Means + t-SNE)

- **K-Means** (`src/clustering.py`) agrupa os embeddings de 384 dimensões em N grupos; o N é escolhido na interface (2 a 10). O K-Means sempre devolve N grupos, mesmo quando os dados não têm grupos naturais, então os clusters devem ser lidos como uma referência.
- **t-SNE** projeta os embeddings em 2D (métrica de cosseno) só para **desenhar** o mapa; os clusters são calculados nos embeddings originais. A projeção é lenta, então fica em cache no disco e só é recalculada se o número de trechos mudar.
- Cada cluster é resumido com seus **termos característicos** (TF-IDF) e seus **PDFs principais**.

Exemplo com N = 3 (5.886 trechos):

| Cluster | Trechos | Termos característicos |
|---|---|---|
| 0 | 2.559 | study, children, data, intervention, health, family, school |
| 1 | 1.822 | screen, use, time, content, exposure, digital, television |
| 2 | 1.505 | sleep, obesity, time, activity, physical, screen, bmi |

## Entender a busca semântica

### Como funciona?

1. **Embeddings:** cada trecho de texto é convertido em um vetor de números (384 dimensões no all-MiniLM-L6-v2). Esse vetor captura o *significado* do texto.
2. **Índice:** todos os vetores ficam em um banco vetorial (ChromaDB), que permite achar os vizinhos mais próximos rapidamente.
3. **Busca:** a pergunta é convertida em vetor com o mesmo modelo. O sistema encontra os vetores mais próximos pela distância de cosseno.
4. **Resultado:** os trechos mais parecidos são devolvidos com sua distância: **0 significa mesmo sentido**, valores perto de **1 significam sem relação**, e quanto mais perto de 0, mais relevante. A interface também mostra a **similaridade** (1 − distância).

### Por que é melhor que busca por palavra-chave?

| Busca por palavra-chave | Busca semântica |
|---|---|
| Procura a palavra exata | Procura o significado |
| "tablet use" não casa com "screen time" | "tablet use" fica perto de "screen time" |
| Pode não retornar nada | Retorna trechos relevantes |

### Exemplo real deste projeto

```
Pergunta:  "is screen time associated with childhood obesity?"

Resultado #1: PMC13589963.pdf, chunk 0
              "The Association Between Daily Screen Time and Childhood
               Overweight and Obesity: Current Evidence and Potential Mechanisms..."
              Distância: 0.1167   Similaridade: 88%

Pergunta:  "what are the best recipes for chocolate cake?"   (controle fora do tema)

Resultado #1: distância 0.7166   Similaridade: 28%
```

O chunk 0 é o primeiro pedaço do artigo (título e autores), por isso casa com uma pergunta quase idêntica ao título.

Consultas curtas (por exemplo uma única palavra como "depression") tendem a ter distâncias maiores que perguntas completas, mesmo quando os resultados estão certos (melhor resultado: distância 0.4694, similaridade 53%). Compare distâncias dentro da mesma consulta, e não entre consultas muito diferentes.

## Dependências principais

- `pypdf`: extração de texto dos PDFs
- `chromadb`: banco vetorial, que também fornece a função de embeddings (all-MiniLM-L6-v2 rodando no ONNX Runtime)
- `scikit-learn`: Isolation Forest, K-Means, t-SNE e TF-IDF
- `streamlit`, `plotly`: interface e gráfico interativo
- `numpy`

Veja o `requirements.txt` para a lista completa.

## Dados de origem

Os 30 PDFs vêm do **PubMed Central**, um repositório de artigos científicos de **acesso aberto** (open access). A licença de cada artigo permite reuso (tipicamente CC-BY).

Exemplos de artigos da coleção:

- `data/raw/PMC13589963.pdf`: revisão sobre tempo de tela diário e sobrepeso e obesidade infantil
- `data/raw/PMC13570809.pdf`: interação com inteligência artificial vs. exposição tradicional a telas no desenvolvimento infantil
- `data/raw/PMC13589181.pdf`: tipos de tempo de tela e desfechos de desenvolvimento em crianças de 0 a 6 anos
- ... (30 no total)

Para consultar o artigo original, use o ID PMC:

```
https://www.ncbi.nlm.nih.gov/pmc/articles/PMC13589963/
```

## Limitações e trabalhos futuros

- **Corte do Isolation Forest:** `contamination = 0.03` fixa a fração de trechos marcados, haja ou não tanto ruído. Recomenda-se revisar à mão os trechos marcados.
- **Classificador supervisionado de qualidade (não implementado):** rotular ~20% dos trechos marcados como relevantes ou irrelevantes e treinar uma regressão logística para decidir quais remover ficou como trabalho futuro.
- **Modelo de embeddings:** o all-MiniLM-L6-v2 é pequeno; um modelo maior poderia melhorar a busca.
- **Clusters:** o K-Means precisa que o N seja escolhido pelo usuário e sempre devolve N grupos.
- **Ciclo de vida do índice:** a interface lê `reports/removed_ids.json`; se o índice for reconstruído com `embedder.py` sem repetir a limpeza, os números de "removidos" ficam desatualizados.
- Discussão completa: [`docs/relatorio_projeto.md`](docs/relatorio_projeto.md).

## Solução de problemas

### "Collection not found" ou "Index not found"

**Causa:** o `embedder.py` ainda não foi executado, então o índice não existe.

**Solução:**

```bash
python src/embedder.py
```

### Os resultados da busca parecem errados ou aleatórios

Verifique, nesta ordem:

1. O `embedder.py` rodou até o fim (a última linha do log mostra o total de trechos indexados, 6.069 aqui antes do controle de qualidade).
2. O `search.py` usa a mesma collection e a mesma função de embeddings do `embedder.py`.
3. O `clean.py` não removeu trechos demais nem deixou passar ruído.

### A interface ainda mostra números antigos depois de rodar o `run_quality.py`

O Streamlit guarda os dados em cache. Pare o app (Ctrl+C), inicie de novo com `streamlit run app.py` e recarregue a página.

### A porta 8501 já está em uso

Pare o outro processo `streamlit run` ou `docker compose`, ou rode `streamlit run app.py --server.port 8502`.

## Autor

**Grazielle Nascimento Ferreira**, Capstone Data Science, 2026.

**Email:** Grazielle.Nascimento0724@jala.university

## Licença

Este projeto usa dados do **PubMed Central** (acesso aberto, tipicamente CC-BY).

---

**Última atualização:** 16 de outubro de 2026
