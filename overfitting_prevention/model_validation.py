import numpy as np
from sklearn.model_selection import KFold

def k_fold_validation(model, X, y, k=5):
    """
    K-폴드 교차 검증을 수행합니다.
    Args:
        model: 훈련할 모델
        X (numpy.ndarray): 입력 데이터
        y (numpy.ndarray): 타겟 데이터
        k (int): K-폴드 개수
    Returns:
        float: 평균 검증 점수
    """
    kf = KFold(n_splits=k, shuffle=True, random_state=42)
    scores = []
    
    for train_idx, val_idx in kf.split(X):
        X_train, X_val = X[train_idx], X[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]

        model.fit(X_train, y_train)
        scores.append(model.score(X_val, y_val))

    return np.mean(scores)
