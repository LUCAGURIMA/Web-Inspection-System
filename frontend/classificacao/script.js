document.addEventListener("DOMContentLoaded", () => {
    const captureBtn = document.getElementById("capture-btn");
    const resultImg = document.getElementById("result-img");
    const defectsList = document.getElementById("defects-list");
    const statusText = document.getElementById("status-text");

    const backendBaseUrl = window.location.origin;

    captureBtn.addEventListener("click", async () => {
        statusText.textContent = "Inspecionando...";
        statusText.style.color = ""; // Reset cor
        defectsList.innerHTML = "";
        resultImg.src = "";
        resultImg.alt = "Processando imagem...";

        try {
            // 1. Iniciar inspeção
            const response = await fetch(`${backendBaseUrl}/classification/inspect`, {
                method: "POST"
            });

            // 2. Verificar resposta
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Erro ${response.status}: ${errorText}`);
            }

            // 3. Processar dados JSON
            const data = await response.json();
            console.log("Dados recebidos:", data); // Para debug

            // 4. Exibir resultados
            if (data.status === "success") {
                // Exibir imagem
                const imgUrl = `${backendBaseUrl}${data.result_path}?t=${Date.now()}`;
                resultImg.src = imgUrl;
                resultImg.alt = "Resultado da inspeção";
                
                // Verificar o status da análise
                const firstDefect = data.defects_info[0];
                
                if (firstDefect.status === "rejected") {
                    // Caso INDETERMINADO - análise rejeitada
                    statusText.textContent = "Análise Indeterminada";
                    statusText.style.color = "#856404";
                    
                    const item = document.createElement("div");
                    item.className = "defect-item indeterminado";
                    item.textContent = "INDETERMINADO - Imagem não reconhecida pelo sistema";
                    defectsList.appendChild(item);
                } else {
                    // Caso normal - análise com confiança suficiente
                    if (data.defects_detected) {
                        statusText.textContent = "A fruta analisada é ruim para exportação:";
                        statusText.style.color = "#d32f2f";
                    } else {
                        statusText.textContent = "A fruta analisada é boa para exportação";
                        statusText.style.color = "#388e3c";
                    }
                    
                    // Exibir lista de defeitos com porcentagem apenas para casos aceitos
                    data.defects_info.forEach(defect => {
                        const item = document.createElement("div");
                        item.className = `defect-item ${defect.class.toLowerCase()}`;
                        if (defect.confidence) {
                            item.textContent = `${defect.class} (${(defect.confidence * 100).toFixed(1)}%)`;
                        } else {
                            item.textContent = defect.class;
                        }
                        defectsList.appendChild(item);
                    });
                }
            } else {
                throw new Error("Resposta inesperada do servidor");
            }
        } catch (err) {
            console.error("Erro na inspeção:", err);
            statusText.textContent = "Falha na inspeção";
            statusText.style.color = "#d32f2f";
            resultImg.alt = `Erro: ${err.message}`;
        }
    });
});