import os
import cv2
import numpy as np
from ultralytics import YOLO
import logging

logger = logging.getLogger(__name__)

MODEL_GLOBAL = None
MODEL_PATH_GLOBAL = None

def load_model_once(model_path):
    global MODEL_PATH_GLOBAL, MODEL_GLOBAL
    if MODEL_GLOBAL is None or MODEL_PATH_GLOBAL != model_path:
        logger.info(f"Carregando modelo de {model_path}...")
        MODEL_GLOBAL = YOLO(model_path)
        MODEL_PATH_GLOBAL = model_path
        logger.info("Modelo carregado.")
    return MODEL_GLOBAL

def run_inference(image, model_path, timestamp_dir,
                  conf=0.05, iou=0.8, imgsz=640, confidence_threshold=0.7):
    try:
        model = load_model_once(model_path)

        # Salvar imagem bruta
        raw_path = os.path.join(timestamp_dir, "raw.png")
        cv2.imwrite(raw_path, image)
        logger.info(f"Imagem bruta salva em: {raw_path}")

        # Rodar predição em modo de CLASSIFICAÇÃO SEM salvar a imagem anotada
        results = model.predict(
            source=raw_path,
            task="classify",
            imgsz=imgsz,
            save=False,  # IMPORTANTE: Não salvar imagem com anotações
            conf=conf
        )

        if not results:
            raise RuntimeError("Nenhum resultado da classificação")

        r = results[0]
        probs = getattr(r, "probs", None)
        if probs is None:
            raise RuntimeError("Resultado inesperado: sem 'probs'")

        # Obter a classe com maior probabilidade
        top_idx = probs.top1  # Índice da classe com maior probabilidade
        top_conf = probs.top1conf.item()  # Confiança da classe com maior probabilidade
        class_name = model.names[top_idx] if hasattr(model, "names") else str(top_idx)

        logger.info(f"Classificação: {class_name} (confiança: {top_conf:.4f})")

        # Verificar se a confiança está acima do threshold
        if top_conf < confidence_threshold:
            logger.info(f"Confiança abaixo do threshold ({confidence_threshold}). Rejeitando análise.")
            # Para casos indeterminados, retornar apenas uma entrada INDETERMINADO
            defects_info = [{"class": "INDETERMINADO", "status": "rejected"}]
            defects_detected = None  # None indica análise rejeitada
        else:
            # Formatar resposta normal
            defects_info = [{"class": class_name, "confidence": round(top_conf, 4), "status": "accepted"}]
            defects_detected = class_name.upper() == "RUIM"  # Ajuste para "RUIM"

        # SEMPRE retornar a imagem original (sem anotações)
        result_path = raw_path

        return result_path, defects_detected, defects_info

    except Exception as e:
        logger.exception("Erro na inferência", exc_info=True)
        raise