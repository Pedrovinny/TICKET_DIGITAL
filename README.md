# Ticket Digital — Sistema de Controle de Refeições

Sistema web desenvolvido em Django para o **IFAM Campus Humaitá**, que controla a retirada de refeições pelos alunos por meio de leitura de carteirinha (QR Code / código de barras).

---

## Funcionalidades

| Módulo | Descrição |
|---|---|
| Importar CSV | Cadastra alunos em lote a partir de um arquivo `.csv` |
| Leitor de Ticket | Valida a matrícula do aluno e registra a refeição do dia |
| Relatórios | Exporta os registros de refeições em CSV por período |

**Regra de negócio principal:** cada aluno só pode retirar uma refeição por dia. Tentativas repetidas exibem aviso de alerta.

---

## Stack

- **Python 3** + **Django 6.0.6**
- **SQLite** — banco gerenciado diretamente via `src/banco.py` (sem ORM do Django)
- **Bootstrap 5.3.8** — interface responsiva

---

## Estrutura do Projeto

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
│   ├── base.html              # Layout base com Bootstrap
│   ├── home.html              # Página inicial (menu)
│   ├── importar.html          # Upload de CSV de alunos
│   ├── leitor.html            # Tela de leitura de ticket
│   └── relatorio.html         # Formulário de exportação por período
│
├── static/
│   └── ifam_humaita_logo_inicio.png
│
└── dados/
    └── banco_ticket.db        # Banco SQLite (gerado automaticamente)
```

---

## Banco de Dados

O banco é criado automaticamente em `dados/banco_ticket.db` na primeira execução.

```
campus
  id_campus  |  nome                  |  sigla
  ----------   ----------------------   ------
  1          |  IFAM Campus Humaitá   |  CHUM   ← criado automaticamente

turmas
  id_turma | nome | curso | ano | campus_id

alunos
  id_aluno | matricula (UNIQUE) | nome | turma_id | ativo

refeicoes
  id_refeicao | aluno_id | data | hora | tipo (padrão: ALMOCO)
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

## Formato do CSV de Importação

O arquivo deve ter as colunas abaixo (com cabeçalho):

```csv
matricula,nome,turma
2024001,João Silva,2024-INFO-1
2024002,Maria Santos,2024-INFO-1
```

- Turmas inexistentes são criadas automaticamente vinculadas ao Campus Humaitá.
- Alunos já cadastrados (mesma matrícula) são ignorados.

---

## Como Executar

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

---

## Fluxo de Uso

1. **Importar alunos** — acesse `/importar/` e envie o CSV com matrícula, nome e turma.
2. **Registrar refeição** — acesse `/leitor/`, aproxime a carteirinha do leitor (ou digite a matrícula). O sistema exibe:
   - **Verde** — refeição liberada e registrada.
   - **Amarelo** — aluno já retirou a refeição hoje.
   - **Vermelho** — matrícula não encontrada.
3. **Exportar relatório** — acesse `/relatorio/`, informe o período e baixe o CSV com todos os registros.

---

## Observações

- O projeto está em modo de desenvolvimento (`DEBUG = True`). Antes de colocar em produção, altere a `SECRET_KEY` e configure `ALLOWED_HOSTS` em `teste/settings.py`.
- O campo `ativo` na tabela `alunos` existe para desativação futura, mas ainda não é utilizado nas consultas.
- A tela do leitor limpa o campo e recoloca o foco automaticamente após 2 segundos, otimizada para uso com leitor de código de barras físico.
