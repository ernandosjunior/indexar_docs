import os
from whoosh.index import open_dir
from whoosh.qparser import QueryParser


INDEX_DIR = "indice_boletins"

ix = open_dir(INDEX_DIR)


def buscar(consulta):

    with ix.searcher() as searcher:

        query = QueryParser("conteudo", ix.schema).parse(consulta)

        resultados = searcher.search(query, limit=None)
        resultados.fragmenter.charlimit = None

        dados = []

        for r in resultados:
            dados.append({
                "arquivo": r["arquivo"],
                "numero": int(r.get("numero", 0)) if r.get("numero") else 0,
                "ano": int(r.get("ano", 0)) if r.get("ano") else 0,
                "pagina": r["pagina"],
                "snippet": r.highlights("conteudo"),
                "caminho": r["caminho"]
            })

        # Ordena por ano e depois por número
        dados_ordenados = sorted(dados, key=lambda x: (x["ano"], x["numero"]))

        lista = []

        for i, r in enumerate(dados_ordenados):
            print(f"\n[{i}]")
            print("Arquivo:", r["arquivo"])
            print("Boletim:", r["numero"], "Ano:", r["ano"])
            print("Página:", r["pagina"])
            print("Contexto:", r["snippet"])

            lista.append(r["caminho"])

        return lista


def abrir_pdf(caminho):

    os.startfile(caminho)


if __name__ == "__main__":

    while True:

        consulta = input("\nDigite termo de busca: ")

        caminhos = buscar(consulta)

        escolha = input("\nDigite número para abrir PDF (ENTER para ignorar): ")

        if escolha.strip():

            abrir_pdf(caminhos[int(escolha)])