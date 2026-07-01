# Ticket Digital — Sistema de Controle de Refeições

Sistema web desenvolvido em Django para o **IFAM Campus Humaitá**, que controla a retirada de
refeições pelos alunos por meio de leitura de carteirinha (QR Code / código de barras).

Além do sistema web, o projeto conta com uma **automação BotCity** que lê listas de turma exportadas
em PDF (SIGAA) e gera automaticamente o CSV usado para cadastrar os alunos.

---

## Índice

1. [Como o sistema funciona](#como-o-sistema-funciona)
2. [Stack](#stack)
3. [Estrutura do projeto](#estrutura-do-projeto)
4. [Banco de dados](#banco-de-dados)
5. [Rotas](#rotas)
6. [Como executar o sistema web](#como-executar-o-sistema-web)
7. [Automação BotCity — PDF → CSV](#automação-botcity--pdf--csv)
8. [Observações](#observações)

---

## Como o sistema funciona

O sistema web tem 3 telas, cada uma resolvendo uma etapa do processo:

```
┌────────────────┐        ┌────────────────┐        ┌────────────────┐
│   Importar     │  ───▶  │     Leitor     │  ───▶  │   Relatório    │
│  (/importar/)  │        │   (/leitor/)   │        │ (/relatorio/)  │
├────────────────┤        ├────────────────┤        ├────────────────┤
│ Sobe um CSV e  │        │ Lê a matrícula │        │ Exporta em CSV │
│ cadastra os    │        │ e libera (ou   │        │ as refeições    │
│ alunos e       │        │ recusa) a      │        │ registradas em  │
│ turmas         │        │ refeição do dia│        │ um período      │
└────────────────┘        └────────────────┘        └────────────────┘
```

**Regra de negócio principal:** cada aluno só pode retirar uma refeição por dia. Na tela do leitor,
o resultado aparece por cor:

| Cor | Significado |
|---|---|
| 🟢 Verde | Refeição liberada e registrada |
| 🟡 Amarelo | Aluno já retirou a refeição hoje |
| 🔴 Vermelho | Matrícula não encontrada |

---

## Stack

- **Python 3** + **Django 6.0.6**
- **SQLite** — banco gerenciado diretamente via [`src/banco.py`](src/banco.py) (sem ORM do Django)
- **Bootstrap 5.3.8** — interface responsiva
- **pdfplumber** + **BotCity** (`botcity-maestro-sdk`) — automação de leitura de PDF (ver seção
  [Automação BotCity](#automação-botcity--pdf--csv))

---

## Estrutura do projeto

```
TICKET_DIGITAL/
│
├── manage.py                  # Ponto de entrada Django
├── requirements.txt           # Dependências Python
│
├── teste/                     # Configurações do projeto Django
│   ├── settings.py
│   ├── urls.py                # Roteamento de URLs
│   ├── views.py               # Lógica de todas as telas
│   ├── wsgi.py
│   └── asgi.py
│
├── src/
│   └── banco.py               # Camada de acesso ao SQLite (CRUD completo)
│
├── templates/                 # Templates HTML com Django Template Language
│   ├── base.html               # Layout base com Bootstrap
│   ├── home.html                # Página inicial (menu)
│   ├── importar.html            # Upload de CSV de alunos
│   ├── leitor.html               # Tela de leitura de ticket
│   └── relatorio.html            # Formulário de exportação por período
│
├── static/
│   └── ifam_humaita_logo_inicio.png
│
├── dados/
│   └── banco_ticket.db        # Banco SQLite (gerado automaticamente)
│
└── automacao_pdf/              # ⚙ Automação BotCity (PDF → CSV)
    ├── entrada_pdfs/            # você coloca os PDFs do SIGAA aqui
    ├── saida_csv/               # o CSV pronto para importar aparece aqui
    └── bot.py                   # o bot em si
```

---

## Banco de dados

O banco é criado automaticamente em `dados/banco_ticket.db` na primeira execução.

```
campus                          turmas                         alunos
┌───────────────┐               ┌───────────────┐              ┌───────────────┐
│ id_campus (PK)│◄──────┐       │ id_turma (PK) │◄──────┐      │ id_aluno (PK) │
│ nome          │       └───────│ campus_id (FK)│       └──────│ turma_id (FK) │
│ sigla         │               │ nome          │              │ matricula (UQ)│
└───────────────┘               │ curso         │              │ nome          │
                                 │ ano           │              │ ativo         │
                                 └───────────────┘              └───────────────┘
                                                                        ▲
                                                                        │
                                                                 refeicoes
                                                                 ┌───────────────┐
                                                                 │ id_refeicao(PK)│
                                                                 │ aluno_id (FK)  │
                                                                 │ data           │
                                                                 │ hora           │
                                                                 │ tipo (ALMOCO)  │
                                                                 └───────────────┘
```

---

## Rotas

| URL | View | Descrição |
|---|---|---|
| `/` | `home` | Menu principal |
| `/importar/` | `importar_csv` | Upload e importação de CSV |
| `/leitor/` | `leitor` | Leitura de matrícula e registro de refeição |
| `/relatorio/` | `relatorio` | Download de relatório CSV por período |

---

## Como executar o sistema web

### 1. Clonar o repositório e criar o ambiente virtual

```bash
git clone <url-do-repositorio>
cd TICKET_DIGITAL

python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Inicializar o banco de dados

```bash
python src/banco.py
```

### 4. Iniciar o servidor

```bash
python manage.py runserver
```

Acesse em: [http://localhost:8000](http://localhost:8000)

### Formato do CSV de importação

```csv
matricula,nome,turma
2024003321,João Lopes Silva,2024-INFO-1
2024002232,Maria Santos,2024-INFO-1
```

- Turmas inexistentes são criadas automaticamente vinculadas ao Campus Humaitá.
- Alunos já cadastrados (mesma matrícula) são ignorados — a importação pode ser rodada várias vezes
  sem duplicar ninguém.

### Fluxo de uso manual

1. **Importar alunos** — acesse `/importar/` e envie o CSV com matrícula, nome e turma.
2. **Registrar refeição** — acesse `/leitor/`, aproxime a carteirinha do leitor (ou digite a
   matrícula).
3. **Exportar relatório** — acesse `/relatorio/`, informe o período e baixe o CSV com todos os
   registros.

---

## Automação BotCity — PDF → CSV

O CSV de importação de alunos não precisa mais ser montado à mão. O SIGAA exporta uma **Lista de
Frequência em PDF** por turma — o bot lê esse(s) PDF(s) e já gera o CSV pronto para o passo
`/importar/`.

### Fluxo da automação

```
   SIGAA
     │  exporta "Lista de Frequência" em PDF (1 arquivo por turma)
     ▼
┌──────────────────────────┐
│ automacao_pdf/            │
│   entrada_pdfs/*.pdf       │  ← você salva os PDFs aqui (pode ser vários de uma vez)
└─────────────┬──────────────┘
              │  venv\Scripts\python.exe automacao_pdf\bot.py
              ▼
┌──────────────────────────────────────┐
│  bot.py  (BotCity)                    │
│  1. lê o texto do PDF (pdfplumber)    │
│  2. acha disciplina + turma + semestre│
│  3. acha matrícula + nome de cada linha│
│  4. monta o CSV consolidado            │
└─────────────┬──────────────────────────┘
              ▼
┌──────────────────────────┐
│ automacao_pdf/             │
│   saida_csv/*.csv           │  matricula,nome,turma
└─────────────┬────────────────┘
              │  upload manual (por enquanto)
              ▼
     http://localhost:8000/importar/
              │
              ▼
       dados/banco_ticket.db
```

### Como o bot identifica a turma

Cada PDF do SIGAA tem, no cabeçalho, algo como:

```
Disciplina: TIOPTPRODM00 - HM-PROGRAMAÇÃO PARA DISPOSITIVOS MÓVEIS   Ano/Semestre: 2026.0
Turma: 01 (25 alunos)
```

O bot combina esses três dados num identificador único por turma:

```
{código da disciplina} - T{número da turma} - {ano/semestre}
   TIOPTPRODM00        -      T01          -    2026.0
```

Isso evita que duas turmas diferentes (ou a mesma disciplina em semestres diferentes) sejam
confundidas como uma só ao importar.

### Passo a passo para rodar

```powershell
# 1. entre na pasta do projeto
cd C:\Users\pedro\OneDrive\Documentos\TICKET_DIGITAL

# 2. salve o(s) PDF(s) do SIGAA em automacao_pdf\entrada_pdfs\

# 3. rode o bot
venv\Scripts\python.exe automacao_pdf\bot.py

# 4. o CSV pronto aparece em automacao_pdf\saida_csv\
#    é só subir esse arquivo em http://localhost:8000/importar/
```

Se um PDF tiver um layout inesperado, o bot avisa no console (`[AVISO] ...`) e pula o arquivo, sem
inventar dado nenhum.

### Rodando desconectado x conectado ao BotCity Maestro

Por padrão o bot roda **100% local**, sem precisar de conta em nada. Ele já está preparado para,
no futuro, ser disparado pelo **BotCity Maestro** (o orquestrador na nuvem do BotCity) — nesse caso
ele reporta automaticamente a execução (turmas processadas, alunos, CSV gerado) no painel deles.
Para isso é necessário, do lado de fora do código:

1. Criar conta gratuita em [botcity.dev](https://botcity.dev)
2. Instalar o **BotCity Runner** na máquina que vai executar o bot
3. Cadastrar `automacao_pdf/` como uma *Automation* no Maestro
4. Criar um *Schedule* (ex: todo dia às 18:00)

---

## Observações

- O projeto está em modo de desenvolvimento (`DEBUG = True`). Antes de colocar em produção, altere
  a `SECRET_KEY` e configure `ALLOWED_HOSTS` em `teste/settings.py`.
- O campo `ativo` na tabela `alunos` existe para desativação futura, mas ainda não é utilizado nas
  consultas.
- A tela do leitor limpa o campo e recoloca o foco automaticamente após 2 segundos, otimizada para
  uso com leitor de código de barras físico.
- A automação BotCity (Cenário A) só gera o CSV — o upload em `/importar/` ainda é manual. Um
  Cenário B (o bot também subir o arquivo sozinho) pode ser adicionado depois.
