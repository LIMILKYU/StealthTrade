import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.regularizers import l1_l2
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# ✅ 1. 데이터 생성 (더 복잡한 패턴 추가)
np.random.seed(42)
X = np.random.rand(10000, 10)
noise = np.random.randn(10000) * 0.05
y = ((X[:, 0] * 0.8 + X[:, 1] * 0.5 + X[:, 2] * 0.3 + noise) > 0.7).astype(int)

# ✅ 2. 데이터 정규화 (특징 스케일링)
scaler = StandardScaler()
X = scaler.fit_transform(X)

# ✅ 3. 데이터 분할 (Train/Test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ✅ 4. AI 모델 구축 (과적합 방지 적용)
model = Sequential([
    Dense(64, activation='relu', kernel_regularizer=l1_l2(l1=0.01, l2=0.01), input_shape=(10,)),
    BatchNormalization(),  # ✅ 배치 정규화 추가
    Dropout(0.2),  # ✅ Dropout 값 조정
    Dense(32, activation='relu', kernel_regularizer=l1_l2(l1=0.01, l2=0.01)),
    BatchNormalization(),  # ✅ 배치 정규화 추가
    Dropout(0.2),
    Dense(1, activation='sigmoid')  # ✅ 확률 예측
])

# ✅ 5. 모델 컴파일 (학습률 조정)
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
              loss='binary_crossentropy', metrics=['accuracy'])

# ✅ 6. 조기 종료(Early Stopping) 적용 (min_delta 추가)
early_stopping = tf.keras.callbacks.EarlyStopping(
    monitor='val_loss', patience=5, min_delta=0.001, restore_best_weights=True
)

# ✅ 7. 모델 학습 실행
history = model.fit(X_train, y_train, validation_data=(X_test, y_test),
                    epochs=100, batch_size=32, callbacks=[early_stopping])

# ✅ 8. 모델 평가
test_loss, test_acc = model.evaluate(X_test, y_test)
print(f"✅ 테스트 정확도: {test_acc:.4f}")
