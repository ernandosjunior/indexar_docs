import os
import re
from multiprocessing import Pool, cpu_count
from pypdf import PdfReader
from tqdm import tqdm
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID, NUMERIC
from whoosh.analysis import StandardAnalyzer

INDEX_DIR = "indice_boletins"

schema = Schema(
    arquivo=ID(stored=True),
    caminho=ID(stored=True),
    numero=NUMERIC(stored=True),
    ano=NUMERIC(stored=True),
    pagina=NUMERIC(stored=True),
    conteudo=TEXT(
    stored=True,
    analyzer=StandardAnalyzer(),
    phrase=True
)
)


def extrair_info_nome(nome):
    match = re.search(r'bgpm(\d+)-(\d+)', nome.lower())
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None


def listar_pdfs_recursivo(pasta_raiz, pastas_excluir=None):

    if pastas_excluir is None:
        pastas_excluir = []

    # normaliza nomes para comparação
    pastas_excluir = set(p.lower() for p in pastas_excluir)

    arquivos = []

    for root, dirs, files in os.walk(pasta_raiz):

        # remove diretórios que devem ser ignorados
        dirs[:] = [d for d in dirs if d.lower() not in pastas_excluir]

        for file in files:
            if file.lower().endswith(".pdf"):
                arquivos.append(os.path.join(root, file))

    return arquivos


def extrair_paginas_pdf(arquivo):

    resultados = []

    try:

        reader = PdfReader(arquivo)

        numero, ano = extrair_info_nome(os.path.basename(arquivo))

        for i, pagina in enumerate(reader.pages):

            texto = pagina.extract_text()

            if not texto:
                continue

            resultados.append({
                "arquivo": os.path.basename(arquivo),
                "caminho": arquivo,
                "numero": numero,
                "ano": ano,
                "pagina": i + 1,
                "conteudo": texto
            })

    except Exception as e:
        print("Erro:", arquivo, e)

    return resultados


def indexar(pasta_raiz, pastas_excluir=None):

    arquivos = listar_pdfs_recursivo(pasta_raiz, pastas_excluir)

    print("Total PDFs:", len(arquivos))

    if not os.path.exists(INDEX_DIR):
        os.mkdir(INDEX_DIR)

    ix = create_in(INDEX_DIR, schema)

    writer = ix.writer()

    with Pool(cpu_count()-5) as pool:

        for paginas in tqdm(pool.imap_unordered(extrair_paginas_pdf, arquivos),
                           total=len(arquivos)):

            for doc in paginas:
                writer.add_document(**doc)

    writer.commit()

    print("Indexação finalizada")


if __name__ == "__main__":

    pasta_raiz = r"\\pm.es.gov.br.local\fs\DTIC\PUBLICO (TEMPORARIO)\BOLETIM"

    indexar(pasta_raiz)