# Sistema de Visão Combinado

Este projeto combina dois sistemas de visão computacional: segmentação de imagens e classificação de imagens.

## Estrutura do Projeto

### Backend
- `backend/main.py`: Ponto de entrada principal da aplicação FastAPI. Contém classes OOP para cada sistema.
- `backend/segmentation/`: Módulo para o sistema de segmentação.
  - `camera_handler.py`: Gerenciamento da câmera.
  - `inference.py`: Lógica de inferência com YOLO para segmentação.
  - `utils.py`: Utilitários para criação de diretórios e manipulação de imagens.
  - `models/`: Modelos treinados para segmentação.
  - `images/`: Diretório para armazenar imagens capturadas e resultados.
- `backend/classification/`: Módulo para o sistema de classificação.
  - Estrutura similar ao de segmentação, mas adaptada para classificação de imagens.

### Frontend
- `frontend/index.html`: Página inicial com botões para acessar os sistemas.
### Frontend
- `frontend/index.html`: Página inicial com botões para acessar os sistemas.
- `frontend/segmentacao/index.html`: Interface para o sistema de segmentação.
- `frontend/segmentacao/script.js`: JavaScript para interação com o sistema de segmentação.
- `frontend/classificacao/index.html`: Interface para o sistema de classificação.
- `frontend/classificacao/script.js`: JavaScript para interação com o sistema de classificação.
- `frontend/home.css`: Estilos para a página inicial.
- `frontend/inspection.css`: Estilos para as páginas de inspeção.
- `frontend/home.js`: JavaScript para navegação na página inicial.
- `frontend/logos/`: Pasta com imagens dos logos.

## Como Executar

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

2. Execute o servidor:
   ```bash
   python backend/main.py
   ```

3. Acesse `http://localhost:8000` no navegador.

## Funcionalidades

- **Página Inicial**: Dois botões para escolher entre segmentação e classificação.
- **Sistema de Segmentação**: Captura imagem, processa com modelo YOLO para detectar defeitos em objetos.
- **Sistema de Classificação**: Captura imagem, classifica com modelo YOLO.

## Adicionando Novos Sistemas

Para adicionar um novo sistema de visão:

1. Crie um novo módulo em `backend/` (ex: `backend/novo_sistema/`).
2. Implemente uma classe similar a `SegmentationSystem` ou `ClassificationSystem` em `main.py`.
3. Adicione uma rota em `main.py` (ex: `/novo_sistema/inspect`).
4. Crie uma nova pasta em `frontend/` (ex: `frontend/novo_sistema/`) com `index.html` e `script.js`.
5. Adicione um botão na `index.html` para acessar o novo sistema.
6. Implemente o JavaScript correspondente para interagir com o backend.

## Arquitetura OOP

O backend utiliza programação orientada a objetos com classes dedicadas para cada sistema, facilitando a manutenção e extensão do código.
