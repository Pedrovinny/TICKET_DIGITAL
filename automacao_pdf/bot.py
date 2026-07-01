"""
Bot BotCity - conversao de lista de turma (PDF do SIGAA) em CSV de importacao.

Le todos os PDFs de entrada_pdfs/, extrai matricula/nome/turma e gera um CSV
consolidado em saida_csv/, no formato esperado por /importar/ (teste/views.py).

Cenario A: so gera o CSV. O upload em /importar/ continua manual.

Roda desconectado do BotCity Maestro por padrao. Se disparado com
--server/--login/--key (BotMaestroSDK.from_sys_args), passa a reportar a
execucao tambem no painel do Maestro.
"""

import csv
import re
from datetime import datetime
from pathlib import Path

import pdfplumber
from botcity.maestro import BotMaestroSDK

BASE_DIR = Path(__file__).resolve().parent
ENTRADA_DIR = BASE_DIR / "entrada_pdfs"
SAIDA_DIR = BASE_DIR / "saida_csv"

# Ex: "TIOPTPRODM00 - HM-PROGRAMAÇÃO PARA DISPOSITIVOS MÓVEIS 2026.0"
RE_DISCIPLINA = re.compile(r"([A-Z]{2,}\d{2,})\s*-\s*(.+?)\s+(\d{4}\.\d)")
# Ex: "01 (25 alunos)"
RE_TURMA_NUM = re.compile(r"\b(\d{1,2})\s*\(\d+\s*alunos?\)", re.IGNORECASE)
# Ex: "1 2024333105 AMANDA BARROS CHAVES"
RE_ALUNO = re.compile(r"^\s*\d+\s+(\d{6,12})\s+(.+?)\s*$")

BotMaestroSDK.RAISE_NOT_CONNECTED = False
maestro = BotMaestroSDK.from_sys_args()


def extrair_turma(texto):
    match_disciplina = RE_DISCIPLINA.search(texto)
    match_turma_num = RE_TURMA_NUM.search(texto)

    if not match_disciplina or not match_turma_num:
        return None

    codigo, _nome_disciplina, semestre = match_disciplina.groups()
    turma_num = match_turma_num.group(1)

    return f"{codigo}-T{turma_num}-{semestre}"


def extrair_alunos(texto):
    alunos = []

    for linha in texto.splitlines():
        match = RE_ALUNO.match(linha)
        if match:
            matricula, nome = match.groups()
            alunos.append((matricula, nome.strip()))

    return alunos


def processar_pdf(caminho_pdf):
    with pdfplumber.open(caminho_pdf) as pdf:
        texto = "\n".join(pagina.extract_text() or "" for pagina in pdf.pages)

    turma = extrair_turma(texto)
    alunos = extrair_alunos(texto)

    if turma is None or not alunos:
        return None

    return turma, alunos


def main():
    pdfs = sorted(ENTRADA_DIR.glob("*.pdf"))

    if not pdfs:
        print(f"Nenhum PDF encontrado em {ENTRADA_DIR}")
        return

    linhas_csv = []
    turmas_ok = 0
    turmas_ignoradas = []

    for caminho_pdf in pdfs:
        resultado = processar_pdf(caminho_pdf)

        if resultado is None:
            turmas_ignoradas.append(caminho_pdf.name)
            print(f"[AVISO] Nao foi possivel ler '{caminho_pdf.name}' (layout inesperado) - pulando.")
            continue

        turma, alunos = resultado
        turmas_ok += 1

        for matricula, nome in alunos:
            linhas_csv.append((matricula, nome, turma))

        print(f"[OK] {caminho_pdf.name} -> turma '{turma}' ({len(alunos)} alunos)")

    if not linhas_csv:
        print("Nenhum aluno extraido. Nenhum CSV foi gerado.")
        return

    SAIDA_DIR.mkdir(exist_ok=True)
    nome_saida = f"turmas_importar_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    caminho_saida = SAIDA_DIR / nome_saida

    # utf-8-sig: mesma codificacao que teste/views.py espera ao ler o CSV importado
    with open(caminho_saida, "w", newline="", encoding="utf-8-sig") as arquivo:
        writer = csv.writer(arquivo)
        writer.writerow(["matricula", "nome", "turma"])
        writer.writerows(linhas_csv)

    print("=" * 50)
    print(f"Turmas processadas: {turmas_ok}")
    if turmas_ignoradas:
        print(f"Turmas ignoradas (layout inesperado): {len(turmas_ignoradas)} -> {', '.join(turmas_ignoradas)}")
    print(f"Total de alunos: {len(linhas_csv)}")
    print(f"CSV gerado em: {caminho_saida}")
    print("=" * 50)

    maestro.new_log_entry(
        "conversao_pdf_turma",
        {
            "turmas_processadas": turmas_ok,
            "turmas_ignoradas": len(turmas_ignoradas),
            "total_alunos": len(linhas_csv),
            "csv_gerado": str(caminho_saida),
        },
    )


if __name__ == "__main__":
    main()
