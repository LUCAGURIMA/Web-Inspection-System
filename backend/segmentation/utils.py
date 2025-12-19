import os
import cv2
from datetime import datetime
import logging
import shutil

logger = logging.getLogger(__name__)

def create_timestamp_dir(base_path: str) -> str:
    """
    Cria e retorna o diretório timestampado dentro de base_path.
    Ex: base_path/2025-08-11_14-55-07
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    full_path = os.path.join(base_path, timestamp)
    os.makedirs(full_path, exist_ok=True)
    logger.info(f"Diretório criado: {full_path}")
    return full_path

def save_image(image, base_path: str, category: str, filename: str = "result.png", png: bool = True) -> str:
    """
    Salva image (numpy BGR) em base_path/category/filename.
    Retorna o caminho completo do arquivo salvo.
    """
    dir_path = os.path.join(base_path, category)
    os.makedirs(dir_path, exist_ok=True)

    file_path = os.path.join(dir_path, filename)
    if png:
        cv2.imwrite(file_path, image, [cv2.IMWRITE_PNG_COMPRESSION, 0])
    else:
        cv2.imwrite(file_path, image)
    logger.info(f"Imagem salva em: {file_path}")
    return file_path

def safe_remove(path: str):
    """Remove arquivo se existir (silencioso)."""
    try:
        if os.path.exists(path):
            os.remove(path)
            logger.debug(f"Removido: {path}")
    except Exception as e:
        logger.warning(f"Falha ao remover {path}: {e}")

def copy_file(src: str, dst: str):
    """Copia arquivo, criando diretório destino se necessário."""
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(src, dst)
    logger.info(f"Copiado: {src} -> {dst}")