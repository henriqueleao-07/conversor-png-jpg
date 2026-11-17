"""
Converte imagens PNG para JPG e compacta para menos de 85KB, já que o sistema pra subir as fotos 
dos produtos na empresa que trabalho, só consegue receber as fotos abaixo de 100KB.

Como usar:
  1) Arraste um ou mais arquivos PNG (ou uma pasta) em cima deste script; ou
  2) Crie uma pasta no explorador com o exato nome "fotos", no mesmo campo que está o script;
  3) Cole no terminal "python3 conversor.py fotos/fotos" e aperte enter;
  4) Será gerado uma pasta dentro de "fotos" com o nome "convertidos";
  5) A partir disso, é so baixar a pasta "convertidos".

Requer instalar a biblioteca: pip install pillow
"""

import io
import sys
from pathlib import Path
from PIL import Image

LIMITE_KB = 85
LIMITE_BYTES = LIMITE_KB * 1024
QUALIDADE_MIN = 20
QUALIDADE_MAX = 95

def para_rgb(img):
    """Converte para RGB; transparência vira fundo branco."""
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        img = img.convert("RGBA")
        fundo = Image.new("RGB", img.size, (255, 255, 255))
        fundo.paste(img, mask=img.split()[-1])
        return fundo
    return img.convert("RGB")


def jpeg_em_memoria(img, qualidade):
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=qualidade, optimize=True)
    return buf.getvalue()


def comprimir(img):
    """Acha a maior qualidade que fica <= 100KB. Reduz o tamanho se precisar."""
    while True:
        baixo, alto = QUALIDADE_MIN, QUALIDADE_MAX
        melhor = None
        while baixo <= alto:
            meio = (baixo + alto) // 2
            dados = jpeg_em_memoria(img, meio)
            if len(dados) <= LIMITE_BYTES:
                melhor = (dados, meio)
                baixo = meio + 1
            else:
                alto = meio - 1
        if melhor:
            return melhor[0], melhor[1], img.size
        largura, altura = img.size
        img = img.resize((int(largura * 0.9), int(altura * 0.9)), Image.LANCZOS)


def processar(caminho):
    pasta_saida = caminho.parent / "convertidos"
    pasta_saida.mkdir(exist_ok=True)
    destino = pasta_saida / (caminho.stem + ".jpg")
    with Image.open(caminho) as original:
        img = para_rgb(original)
        tamanho_original = img.size
    dados, qualidade, tamanho_final = comprimir(img)
    destino.write_bytes(dados)

    msg = f"OK  {caminho.name} -> convertidos/{destino.name} | {len(dados) / 1024:.1f} KB | qualidade {qualidade}"
    if tamanho_final != tamanho_original:
        msg += f" | redimensionada {tamanho_original} -> {tamanho_final}"
    print(msg)


def coletar_arquivos(entradas):
    arquivos = []
    for entrada in entradas:
        p = Path(entrada.strip().strip('"').strip("'"))
        if p.is_dir():
            arquivos.extend(sorted(f for f in p.iterdir() if f.suffix.lower() == ".png"))
        elif p.is_file():
            arquivos.append(p)
        else:
            print(f"Não encontrado: {p}")
    return arquivos


def main():
    entradas = sys.argv[1:]
    if not entradas:
        entrada = input("Caminho do arquivo PNG (ou pasta): ")
        entradas = [entrada]

    arquivos = coletar_arquivos(entradas)
    if not arquivos:
        print("Nenhum arquivo para processar.")
        return

    for arq in arquivos:
        try:
            processar(arq)
        except Exception as erro:
            print(f"ERRO em {arq.name}: {erro}")

    input("\nConcluído! Pressione Enter para fechar...")


if __name__ == "__main__":
    main()