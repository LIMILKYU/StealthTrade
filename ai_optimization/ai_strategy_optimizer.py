import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import MinMaxScaler

# ✅ 1. 데이터 생성 (랜덤 값이 아닌 실제 패턴 반영)
np.random.seed(42)
X = np.random.rand(5000, 15)
y = ((X[:, 0] * 0.7 + X[:, 1] * 0.5 + X[:, 2] * 0.3 + np.random.randn(5000) * 0.05) > 0.65).astype(int)

# ✅ 2. 데이터 정규화 (MinMaxScaler 적용)
scaler = MinMaxScaler()
X = scaler.fit_transform(X)

# ✅ 3. 데이터 분할 (Train/Test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ✅ 4. 랜덤 포레스트 모델 최적화 (과적합 방지 적용)
rf_model = RandomForestClassifier(
    n_estimators=200,  # ✅ 트리 개수 증가 → 일반화 성능 향상
    max_depth=None,  # ✅ 트리가 자동으로 적절한 깊이까지 성장하도록 설정
    min_samples_split=5,  # ✅ 분할을 더 자주 허용하여 유연성 증가
    min_samples_leaf=2,  # ✅ 트리 잎 노드 최소 샘플 개수 조정
    max_features="sqrt",  # ✅ 특징 선택 시 sqrt(전체 특징)만 고려 → 일반화 성능 개선
    bootstrap=True,  # ✅ 부트스트랩 샘플링 활성화 → 데이터 다양성 확보
    random_state=42
)

# ✅ 5. 교차 검증 적용 (cv=3로 조정하여 속도 향상)
cv_scores = cross_val_score(rf_model, X_train, y_train, cv=3)
print(f"📊 교차 검증 평균 정확도: {cv_scores.mean():.4f}")

# ✅ 6. 모델 학습
rf_model.fit(X_train, y_train)

# ✅ 7. 테스트 평가
test_acc = rf_model.score(X_test, y_test)
print(f"✅ 테스트 데이터 정확도: {test_acc:.4f}")
