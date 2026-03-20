import os
from whoosh.index import open_dir
from whoosh.qparser import QueryParser

from excel_writer import ExcelOutputWriter


INDEX_DIR = "indices//indice_boletins_proximidade"

ix = open_dir(INDEX_DIR)

def montar_consulta(nome, termos):
    partes = [f'"{nome} {t}"~200' for t in termos]
    return " OR ".join(partes)

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
        
        return dados_ordenados
        
        lista = []

        for i, r in enumerate(dados_ordenados):
        #     print(f"\n[{i}]")
        #     print("Arquivo:", r["arquivo"])
        #     print("Boletim:", r["numero"], "Ano:", r["ano"])
        #     print("Página:", r["pagina"])
        #     print("Contexto:", r["snippet"])

            lista.append(r["caminho"])

        return lista


def abrir_pdf(caminho):

    os.startfile(caminho)


if __name__ == "__main__":

    # while True:

    #     nome = input("\nDigite termo de busca: ")


    #     termos = [
    #         "exame toxicologico",
    #         "lei complementar 864 2017",
    #         "lei complementar 848 2017",
    #         "848",
    #         "864",
    #         "conselho de justificação",
    #         "artigo 15 inciso V",
    #         "lc 962 2020"
    #     ]

    #     consulta = montar_consulta(nome, termos)

    #     caminhos = buscar(consulta)

    #     rotina_abrir_pdf = True

    #     while rotina_abrir_pdf and caminhos:    
    #         escolha = input("\nDigite número para abrir PDF ou 'q' para sair: ")

    #         if escolha.strip() == 'q':
    #             rotina_abrir_pdf = False
    #         elif escolha.strip():
    #             abrir_pdf(caminhos[int(escolha)])

        nomes = input("\nDigite termo de busca: ")

        ano_inicio = int(input("Ano início: ") or 0)
        ano_fim = int(input("Ano fim: ") or 9999)


        termos = [
            "exame toxicologico",
            "lei complementar 864 2017",
            "lei complementar 848 2017",
            "848",
            "864",
            "conselho de justificação",
            "artigo 15 inciso V",
            "lc 962 2020"
        ]
        
        excel_writer = ExcelOutputWriter("resultados_busca.xlsx")

        lista_nomes = [n.strip() for n in nomes.split(",") if n.strip()]
        lista_consultas = {}
        for nome in lista_nomes:
            consulta = montar_consulta(nome, termos)
            dados = buscar(consulta)
            lista_consultas[nome] = dados

        # Salvar resultados em Excel
        sheets = {nome: dados for nome, dados in lista_consultas.items()}
        excel_writer.write(sheets)
        
            