import os
import cv2
import numpy as np
import logging
from pypylon import pylon

logger = logging.getLogger(__name__)

class CameraHandler:
    def __init__(self):
        self.camera = None

    def open_camera(self):
        logger.info("Conectando à câmera...")
        tl_factory = pylon.TlFactory.GetInstance()
        devices = tl_factory.EnumerateDevices()

        # Log para depuração: listar devices encontrados (modelo, IP se disponível)
        device_infos = []
        for d in devices:
            model = d.GetModelName() if hasattr(d, "GetModelName") else "<unknown>"
            ip = d.GetIpAddress() if hasattr(d, "GetIpAddress") else None
            device_infos.append({"model": model, "ip": ip})
        logger.info(f"Devices encontrados: {device_infos}")

        if not devices:
            raise RuntimeError("Nenhuma câmera encontrada.")

        # Selecionar por IP se variável de ambiente CAMERA_IP estiver definida
        preferred_ip = os.getenv("CAMERA_IP")
        selected_device = None
        if preferred_ip:
            for d in devices:
                if hasattr(d, "GetIpAddress") and d.GetIpAddress() == preferred_ip:
                    selected_device = d
                    break

        if selected_device is None:
            selected_device = devices[0]

        self.camera = pylon.InstantCamera(tl_factory.CreateDevice(selected_device))
        self.camera.Open()

        # Configurar para resolução máxima
        self.camera.Width.SetValue(self.camera.Width.Max)
        self.camera.Height.SetValue(self.camera.Height.Max)

        logger.info(f"Câmera conectada: {selected_device.GetModelName()}")

    def capture_image(self):
        if not self.camera:
            raise RuntimeError("Câmera não está aberta.")

        self.camera.StartGrabbingMax(1)
        grab_result = self.camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

        if grab_result.GrabSucceeded():
            image = grab_result.Array  # Bayer ou BGR
            if len(image.shape) == 2:  # Bayer -> converter para BGR
                image = cv2.cvtColor(image, cv2.COLOR_BAYER_BG2BGR)
            grab_result.Release()
            logger.info(f"Imagem capturada com shape: {image.shape}")
            return image
        else:
            grab_result.Release()
            raise RuntimeError("Falha na captura de imagem.")

    def close_camera(self):
        if self.camera and self.camera.IsOpen():
            self.camera.Close()
            logger.info("Câmera fechada.")