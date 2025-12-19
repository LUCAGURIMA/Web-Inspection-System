import os
import cv2
import torch
import gc
import numpy as np
import logging
import traceback
from ultralytics import YOLO
from .utils import safe_remove

logger = logging.getLogger(__name__)

MODEL_PATH_GLOBAL = None
MODEL_GLOBAL = None

def load_model_once(model_path):
    global MODEL_PATH_GLOBAL, MODEL_GLOBAL
    if MODEL_GLOBAL is None or MODEL_PATH_GLOBAL != model_path:
        logger.info(f"Carregando modelo de {model_path}...")
        MODEL_GLOBAL = YOLO(model_path)
        MODEL_PATH_GLOBAL = model_path
        logger.info("Modelo carregado.")
    return MODEL_GLOBAL

def run_inference(image, model_path, timestamp_dir,
                  conf=0.05, iou=0.8, imgsz=1280):
    try:
        model = load_model_once(model_path)
        
        # Salvar imagem bruta
        raw_path = os.path.join(timestamp_dir, "raw.png")
        cv2.imwrite(raw_path, image)
        logger.info(f"Imagem bruta salva em: {raw_path}")

        # Criar diretório para resultados
        result_dir = os.path.join(timestamp_dir, "result")
        os.makedirs(result_dir, exist_ok=True)
        
        # Executar inferência
        results = model.predict(
            source=raw_path,
            conf=conf,
            iou=iou,
            imgsz=imgsz,
            save=True,
            project=timestamp_dir,
            name="result",
            exist_ok=True
        )

        # Processar defeitos
        defects_info = []
        for r in results:
            if r.boxes:
                for cls_t, conf_t in zip(r.boxes.cls, r.boxes.conf):
                    cls_idx = int(cls_t.item())
                    conf_score = float(conf_t.item())
                    class_name = model.names[cls_idx]
                    defects_info.append({
                        "class": class_name, 
                        "confidence": conf_score
                    })
        
        # Encontrar arquivo resultante
        result_files = [f for f in os.listdir(result_dir) 
                      if f.lower().endswith((".png", ".jpg", ".jpeg"))]
        
        if not result_files:
            raise RuntimeError("Nenhum arquivo de resultado encontrado")
        
        result_file = result_files[0]
        result_path = os.path.join(result_dir, result_file)
        logger.info(f"Arquivo de resultado: {result_path}")
        
        return result_path, bool(defects_info), defects_info

    except Exception as e:
        logger.error(f"Erro na inferência: {e}")
        logger.error(traceback.format_exc())
        raise
    finally:
        # Limpeza
        if 'raw_path' in locals() and os.path.exists(raw_path):
            safe_remove(raw_path)
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()