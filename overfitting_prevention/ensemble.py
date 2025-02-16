import numpy as np

def ensemble_predictions(models, X):
    """
    여러 모델의 예측을 평균 내어 앙상블 예측을 수행합니다.
    Args:
        models (list): 여러 개의 훈련된 모델 리스트
        X (numpy.ndarray): 입력 데이터
    Returns:
        numpy.ndarray: 앙상블된 예측 결과
    """
    predictions = np.array([model.predict(X) for model in models])
    return np.mean(predictions, axis=0)
