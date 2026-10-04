# Capstone Data Science 

##  Busca Semântica em Artigos Científicos

## O que é este projeto?

Pipeline completo que transforma artigos científicos em PDF em um sistema de **busca semântica**. Você carrega documentos, o sistema gera embeddings (representações matemáticas do significado), indexa tudo em um banco vetorial e permite buscar por sentido, não por palavra exata.

**Exemplo:** Se você buscar "efeitos do tempo de tela em crianças", o sistema encontrará automaticamente documentos que falam sobre "impacto de mídias digitais em menores de idade", mesmo que não usem as mesmas palavras.

## Domínio escolhido

**Efeitos do uso de telas em crianças e adolescentes**

Temas cobertos nos artigos:
- Tempo de tela (screen time) e saúde mental
- Relação entre mídia digital e obesidade infantil
- Impacto no sono e qualidade do repouso
- Desenvolvimento cognitivo e aprendizagem
- Comportamento e socialização
- Intervenções e recomendações clínicas

**Fonte dos dados:** 30 artigos científicos de acesso aberto do **PubMed Central (PMC)**, coletados em 2026. Os nomes dos PDFs são seus identificadores PMC (ex.: `PMC13532691.pdf`).

## Pipeline (fluxo dos dados)

```
PDFs (data/raw/)
    ↓
[loader.py] — Extração de texto + chunking
    ↓
chunks.jsonl (data/processed/) — 6000+ trechos de texto
    ↓
[clean.py] — Remoção de trechos vazios, curtos ou inválidos
    ↓
chunks.jsonl (filtrado)
    ↓
[embedder.py] — Conversão em vetores (all-MiniLM-L6-v2) + ChromaDB
    ↓
ChromaDB (data/chroma/) — Banco vetorial persistido
    ↓
[search.py] — Busca por sentido
    ↓
Resultados com distância de similaridade
```

## Estrutura do projeto

```
capstone/
├── data/
│   ├── raw/                 # PDFs originais (~30 artigos)
│   ├── processed/
│   │   └── chunks.jsonl     # Trechos de texto extraídos e limpos
│   └── chroma/              # Banco vetorial ChromaDB (SQLite)
├── src/
│   ├── loader.py            # Lê PDFs → chunks.jsonl
│   ├── clean.py             # Filtra chunks.jsonl (sem lixo)
│   ├── embedder.py          # Gera embeddings → ChromaDB
│   ├── search.py            # CLI para busca semântica
│   ├── test_search.py       # Valida a busca (domínio vs fora-domínio)
│   ├── main.py              # Menu interativo
│   ├── demo.py              # Demonstração com perguntas do domínio
│   ├── logging_config.py    # Configuração de logs
│   
├── requirements.txt         # Dependências Python
├── .gitignore               # Arquivos a ignorar no Git
└── README.md                # Este arquivo
```

## Instalação

### Pré-requisitos
- Python 3.8+
- Windows, macOS ou Linux
- Git (opcional, para versionamento)

### Passo 1: Clonar ou preparar o projeto

```bash
# Se tiver Git:
git clone <seu-repositorio>
cd capstone

```

### Passo 2: Criar ambiente virtual

```bash
python -m venv venv
```

Ativar:
- **Windows (PowerShell):** `.\venv\Scripts\Activate.ps1`
- **Windows (CMD):** `venv\Scripts\activate.bat`
- **Linux/macOS:** `source venv/bin/activate`

### Passo 3: Instalar dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Dependências:**
- `pypdf` — leitura de PDFs
- `chromadb` — banco vetorial
- `sentence-transformers` — geração de embeddings

## Como rodar

### Execução completa (do zero)

Execute **nesta ordem**:

```bash
python src/loader.py      # Lê PDFs, gera chunks (~ 1 min)
python src/clean.py       # Remove trechos inválidos (< 1 min)
python src/embedder.py    # Gera embeddings, carrega ChromaDB (~ 20 min)
```

Depois, faça buscas:

```bash
python src/search.py "screen time and obesity in children"
python src/search.py "does mobile use affect sleep?"
```

### Teste rápido (validação)

Compara busca **dentro do domínio** vs **fora do domínio**:

```bash
python src/test_search.py
```

Esperado:
```
Query: "screen time and obesity" → distâncias baixas (~0.2–0.4)
Query: "chocolate cake recipe"   → distâncias altas (~0.8–1.0)
```

Se as distâncias forem diferentes, o índice está funcionando ✅


### Demonstração (várias buscas do domínio)

```bash
python src/demo.py
```

Executa buscas pré-configuradas relacionadas ao domínio e mostra resultados.

## Entender a busca semântica

### Como funciona?

1. **Embeddings:** Cada trecho de texto é convertido em um vetor de números (384 dimensões, no caso do all-MiniLM-L6-v2). Esse vetor captura o *significado* do texto.

2. **Índice:** Todos os vetores são armazenados em um banco vetorial (ChromaDB). Isso permite buscar rapidamente.

3. **Busca:** Quando você digita uma pergunta, ela também é convertida em um vetor. O sistema então encontra os vetores mais próximos (mais parecidos) usando distância de cosseno.

4. **Resultado:** O sistema retorna os trechos mais similares à sua pergunta, junto com uma distância que indica a relevância (0 = idêntico, 1 = oposto).

### Por que é melhor que busca por palavra-chave?

| Busca | "screen time" | Busca semântica |
|-------|---|---|
| Procura pela palavra exata | Procura pelo significado |
| "tablet use" ≠ "screen time" | "tablet use" ≈ "screen time" |
| Resultado: nada | Resultado: documentos relevantes |

### Exemplo prático

```
Você busca:   "How does digital media affect children's sleep?"

Documento 1:  "Screen exposure before bedtime suppresses melatonin..."
              → Distância: 0.18 ✅ (muito relevante)

Documento 2:  "The metabolic syndrome includes obesity and hypertension..."
              → Distância: 0.65 (menos relevante)

Documento 3:  "How to make a chocolate cake"
              → Distância: 0.92 (não relevante)
```

## Dependências principais

```
pypdf==4.0.1                    # Leitura de PDFs
chromadb==0.4.14                # Banco vetorial
sentence-transformers==2.2.2    # Geração de embeddings (all-MiniLM-L6-v2)
```

Veja `requirements.txt` para a lista completa.

## Dados de origem

Os 30 PDFs foram baixados do **PubMed Central**, um repositório de artigos científicos de **acesso aberto** (open access). Cada um tem uma licença que permite reuso (tipicamente CC-BY 4.0).

**Como estão organizados:**
- `data/raw/PMC13532691.pdf` — Artigo sobre "Screen time and childhood obesity"
- `data/raw/PMC13540691.pdf` — Artigo sobre "Digital media and sleep disorders"
- ... (30 no total)

Para consultar o artigo original, use o ID PMC:
```
https://www.ncbi.nlm.nih.gov/pmc/articles/PMC13532691/
```

## Limitações desta entrega (parcial)

❌ Sem clustering (agrupamento de temas)
❌ Sem detecção de anomalias
❌ Sem classificação de qualidade de texto
❌ Sem interface gráfica (Streamlit/Flask)

Estes itens estão previstos para a **entrega final**.

## Troubleshooting

### "Collection not found" ao rodar search.py

**Causa:** O embedder.py ainda não foi executado.

**Solução:**
```bash
python src/embedder.py
```

Aguarde ~20 minutos.

### Erro ao ler PDFs (DLL bloqueada no Windows)

**Causa:** Política de Controle de Aplicativo do Windows bloqueando torch.dll.

**Solução:**
1. Abra o arquivo `venv\Lib\site-packages\torch\lib\shm.dll`
2. Clique direito → Properties → **Unblock** → Apply → OK
3. Ou: Execute PowerShell como Administrator

### O pipeline está muito lento

**Normal.** A geração de embeddings é a operação mais cara:
- loader.py: ~1–5 min (depende do volume de PDFs)
- clean.py: <1 min
- embedder.py: **15–30 min** (primeira execução; cache depois)


## Autor

**Grazielle Nascimento Ferreira**  Capstone Data Science, 2026.

**Email:** Grazielle.Nascimento0724@jala.university

## Licença

Este projeto usa dados de **PubMed Central** (open access, CC-BY 4.0).

---

**Última atualização:** 2 de outubro de 2026
