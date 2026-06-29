from django.shortcuts import render
from src.banco import *

import csv
import io


def home(request):
    return render(request, "home.html")


def importar_csv(request):

    mensagem = ""

    if request.method == "POST":

        arquivo = request.FILES.get("arquivo")

        if arquivo:

            # Lê o arquivo CSV
            texto = io.StringIO(
                arquivo.read().decode("utf-8-sig")
            )

            leitor = csv.DictReader(texto)

            # Debug
            print("=" * 50)
            print("Colunas encontradas:", leitor.fieldnames)
            print("=" * 50)

            total = 0

            for linha in leitor:

                print(linha)

                matricula = linha["matricula"].strip()
                nome = linha["nome"].strip()
                turma = linha["turma"].strip()

                # Procurar turma
                turma_id = buscar_turma_nome(turma)

                # Se não existir, cria
                if turma_id is None:

                    inserir_turma(
                        nome=turma,
                        curso="",
                        ano=2026,
                        campus_id=1
                    )

                    turma_id = buscar_turma_nome(turma)

                # Verifica se o aluno já existe
                aluno = buscar_aluno_matricula(matricula)

                if aluno is None:

                    inserir_aluno(
                        nome,
                        matricula,
                        turma_id
                    )

                    total += 1

            mensagem = f"{total} alunos importados com sucesso."

    return render(
        request,
        "importar.html",
        {
            "mensagem": mensagem
        }
    )


def leitor(request):
    return render(request, "leitor.html")


def relatorio(request):
    return render(request, "relatorio.html")