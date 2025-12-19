document.addEventListener('DOMContentLoaded', () => {
    const segmentationButton = document.getElementById('segmentation-btn');
    const classificationButton = document.getElementById('classification-btn');
    
    segmentationButton.addEventListener('click', () => {
        window.location.href = '/segmentation';
    });

    classificationButton.addEventListener('click', () => {
        window.location.href = '/classification';
    });
});