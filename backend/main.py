import logging
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import datetime

from backend.segmentation.camera_handler import CameraHandler as SegCameraHandler
from backend.segmentation.inference import run_inference as seg_run_inference
from backend.segmentation.utils import create_timestamp_dir as seg_create_timestamp_dir

from backend.classification.camera_handler import CameraHandler as ClassCameraHandler
from backend.classification.inference import run_inference as class_run_inference
from backend.classification.utils import create_timestamp_dir as class_create_timestamp_dir

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

BASE_DIR = Path(__file__).parent
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")

app = FastAPI()

# ===== CORS =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir frontend
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

class SegmentationSystem:
    def __init__(self):
        self.base_image_dir = os.path.join(BASE_DIR, "segmentation", "images")
        os.makedirs(self.base_image_dir, exist_ok=True)
        self.model_path = os.path.join(BASE_DIR, "segmentation", "models", "best.pt")
        self.conf = 0.45
        self.iou = 0.8
        self.imgsz = 1280

    def perform_inspection(self):
        try:
            logger.info("Iniciando inspeção de segmentação...")

            # 1. Criar diretório com timestamp
            timestamp_dir = seg_create_timestamp_dir(self.base_image_dir)
            logger.info(f"Diretório criado: {timestamp_dir}")

            # 2. Capturar imagem
            logger.info("Conectando à câmera...")
            cam = SegCameraHandler()
            cam.open_camera()
            raw_img = cam.capture_image()
            cam.close_camera()
            logger.info(f"Imagem capturada. Shape: {raw_img.shape}")

            # 3. Processar imagem
            logger.info("Executando inferência...")
            result_path, defects_detected, defects_info = seg_run_inference(
                raw_img,
                self.model_path,
                timestamp_dir,
                conf=self.conf,
                iou=self.iou,
                imgsz=self.imgsz
            )
            logger.info(f"Resultado da inferência: {result_path}")

            # 4. Verificar resultado
            if not os.path.exists(result_path):
                logger.error("Arquivo de resultado não encontrado!")
                raise HTTPException(status_code=500, detail="Result image not found")

            # 5. Gerar URL de acesso
            rel_path = os.path.relpath(result_path, self.base_image_dir)
            image_url = f"/segmentation/images/{rel_path.replace(os.path.sep, '/')}"
            logger.info(f"URL da imagem: {image_url}")

            return {
                "status": "success",
                "defects_detected": defects_detected,
                "defects_info": defects_info,
                "result_path": image_url
            }

        except Exception as e:
            logger.exception("ERRO NO PROCESSO DE INSPEÇÃO DE SEGMENTAÇÃO", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

class ClassificationSystem:
    def __init__(self):
        self.base_image_dir = os.path.join(BASE_DIR, "classification", "images")
        os.makedirs(self.base_image_dir, exist_ok=True)
        self.model_path = os.path.join(BASE_DIR, "classification", "models", "best.pt")
        self.conf = 0.5
        self.iou = 0.5
        self.imgsz = 640
        self.confidence_threshold = 0.7

    def perform_inspection(self):
        try:
            logger.info("Iniciando inspeção de classificação...")

            # 1. Criar diretório com timestamp
            timestamp_dir = class_create_timestamp_dir(self.base_image_dir)
            logger.info(f"Diretório criado: {timestamp_dir}")

            # 2. Capturar imagem
            logger.info("Conectando à câmera...")
            cam = ClassCameraHandler()
            cam.open_camera()
            raw_img = cam.capture_image()
            cam.close_camera()
            logger.info(f"Imagem capturada. Shape: {raw_img.shape}")

            # 3. Processar imagem
            logger.info("Executando inferência...")
            result_path, defects_detected, defects_info = class_run_inference(
                raw_img,
                self.model_path,
                timestamp_dir,
                conf=self.conf,
                iou=self.iou,
                imgsz=self.imgsz,
                confidence_threshold=self.confidence_threshold
            )
            logger.info(f"Resultado da inferência: {result_path}")

            # 4. Verificar resultado
            if not os.path.exists(result_path):
                logger.error("Arquivo de resultado não encontrado!")
                raise HTTPException(status_code=500, detail="Result image not found")

            # 5. Gerar URL de acesso
            rel_path = os.path.relpath(result_path, self.base_image_dir)
            image_url = f"/classification/images/{rel_path.replace(os.path.sep, '/')}"
            logger.info(f"URL da imagem: {image_url}")

            return {
                "status": "success",
                "defects_detected": defects_detected,
                "defects_info": defects_info,
                "result_path": image_url
            }

        except Exception as e:
            logger.exception("ERRO NO PROCESSO DE INSPEÇÃO DE CLASSIFICAÇÃO", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

# Instâncias dos sistemas
seg_system = SegmentationSystem()
class_system = ClassificationSystem()

# Montar diretórios de imagens
app.mount("/segmentation/images", StaticFiles(directory=seg_system.base_image_dir), name="seg_images")
app.mount("/classification/images", StaticFiles(directory=class_system.base_image_dir), name="class_images")

@app.get("/")
def home_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/segmentation")
def segmentation_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "segmentacao", "index.html"))

@app.get("/classification")
def classification_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "classificacao", "index.html"))

@app.post("/segmentation/inspect")
async def segmentation_inspect():
    return seg_system.perform_inspection()

@app.post("/classification/inspect")
async def classification_inspect():
    return class_system.perform_inspection()

@app.get("/test")
async def test_endpoint():
    return {
        "message": "Teste bem-sucedido",
        "timestamp": datetime.datetime.now().isoformat()
    }

if __name__ == "__main__":
    # Verificar permissões
    logger.info(f"Diretório base de imagens segmentação: {seg_system.base_image_dir}")
    logger.info(f"Diretório base de imagens classificação: {class_system.base_image_dir}")
    
    # Testar criação de arquivo
    for base_dir in [seg_system.base_image_dir, class_system.base_image_dir]:
        test_file = os.path.join(base_dir, "test_permission.txt")
        try:
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            logger.info(f"Permissões de escrita OK para {base_dir}")
        except Exception as e:
            logger.error(f"Problema de permissões em {base_dir}: {str(e)}")
    
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)