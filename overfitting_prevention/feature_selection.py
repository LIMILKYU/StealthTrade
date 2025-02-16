from sklearn.feature_selection import SelectKBest, f_classif

def select_best_features(X, y, k=10):
    """
    K개의 최적 특징을 선택합니다.
    Args:
        X (numpy.ndarray): 입력 데이터
        y (numpy.ndarray): 타겟 데이터
        k (int): 선택할 특징 개수
    Returns:
        tuple: (변환된 X 데이터, 선택된 특징)
    """
    selector = SelectKBest(score_func=f_classif, k=k)
    X_new = selector.fit_transform(X, y)
    return X_new, selector
