document.addEventListener("DOMContentLoaded", () => {
    const captureBtn = document.getElementById("capture-btn");
    const resultImg = document.getElementById("result-img");
    const defectsList = document.getElementById("defects-list");
    const statusText = document.getElementById("status-text");

    const backendBaseUrl = window.location.origin; // Alterado para usar o origin

    captureBtn.addEventListener("click", async () => {
        statusText.textContent = "Inspecionando...";
        defectsList.innerHTML = "";
        resultImg.src = "";
        resultImg.alt = "Processando imagem...";

        try {
            // 1. Iniciar inspeção
            const response = await fetch(`${backendBaseUrl}/segmentation/inspect`, {
                method: "POST"
            });

            // 2. Verificar resposta
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Erro ${response.status}: ${errorText}`);
            }

            // 3. Processar dados JSON
            const data = await response.json();

            // 4. Exibir resultados
            if (data.status === "success") {
                // Exibir imagem
                const imgUrl = `${backendBaseUrl}${data.result_path}?t=${Date.now()}`;
                resultImg.src = imgUrl;
                resultImg.alt = "Resultado da inspeção";
                
                // Exibir status
                statusText.textContent = data.defects_detected
                    ? "Defeitos encontrados:"
                    : "Nenhum defeito detectado.";
                
                // Exibir lista de defeitos
                data.defects_info.forEach(defect => {
                    const item = document.createElement("div");
                    item.className = `defect-item ${defect.class.toLowerCase()}`;
                    item.textContent = `${defect.class} (${(defect.confidence * 100).toFixed(1)}%)`;
                    defectsList.appendChild(item);
                });
            } else {
                throw new Error("Resposta inesperada do servidor");
            }
        } catch (err) {
            console.error("Erro na inspeção:", err);
            statusText.textContent = "Falha na inspeção";
            resultImg.alt = `Erro: ${err.message}`;
        }
    });
});