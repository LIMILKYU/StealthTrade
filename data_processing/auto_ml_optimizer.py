# ✅ 다양한 머신러닝 모델 자동 탐색 및 비교 (랜덤 포레스트, XGBoost, LSTM 등)
# ✅ 특징 선택 & 하이퍼파라미터 튜닝 최적화
# ✅ AutoML을 사용하여 최적의 모델을 자동 선택
# ✅ 모델 성능 비교 후, 가장 높은 성능의 모델을 저장

import numpy as np
import pandas as pd
import time
import joblib
from tpot import TPOTClassifier
from autosklearn.classification import AutoSklearnClassifier
import h2o
from h2o.automl import H2OAutoML
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_absolute_error

# 🔥 1. 데이터 로드 & 전처리
def load_data(csv_path):
    df = pd.read_csv(csv_path)
    
    # 📌 주요 특성 선택 (예: OHLCV + 기술적 지표)
    features = ["Open", "High", "Low", "Close", "Volume"]
    
    # 📌 종속 변수 설정 (목표: 상승(1) or 하락(0) 예측)
    df["Target"] = (df["Close"].shift(-1) > df["Close"]).astype(int)  

    # 데이터 정리
    df.dropna(inplace=True)
    
    X = df[features]
    y = df["Target"]
    
    return train_test_split(X, y, test_size=0.2, random_state=42)

# 🔥 2. TPOT AutoML 최적화
def train_tpot(X_train, X_test, y_train, y_test):
    print("🚀 TPOT AutoML 모델 학습 시작...")
    start_time = time.time()
    
    tpot = TPOTClassifier(generations=5, population_size=20, verbosity=2, n_jobs=-1)
    tpot.fit(X_train, y_train)
    
    y_pred = tpot.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"✅ TPOT 모델 학습 완료! 정확도: {accuracy:.4f}")
    print(f"⏳ 소요 시간: {time.time() - start_time:.2f}초")

    # 최적 모델 저장
    joblib.dump(tpot.fitted_pipeline_, "tpot_best_model.pkl")
    
    return accuracy

# 🔥 3. Auto-Sklearn AutoML 최적화
def train_autosklearn(X_train, X_test, y_train, y_test):
    print("🚀 Auto-Sklearn 모델 학습 시작...")
    start_time = time.time()
    
    automl = AutoSklearnClassifier(time_left_for_this_task=600, per_run_time_limit=30, n_jobs=-1)
    automl.fit(X_train, y_train)
    
    y_pred = automl.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"✅ Auto-Sklearn 모델 학습 완료! 정확도: {accuracy:.4f}")
    print(f"⏳ 소요 시간: {time.time() - start_time:.2f}초")

    # 최적 모델 저장
    joblib.dump(automl, "autosklearn_best_model.pkl")
    
    return accuracy

# 🔥 4. H2O AutoML 최적화
def train_h2o(X_train, X_test, y_train, y_test):
    print("🚀 H2O AutoML 모델 학습 시작...")
    start_time = time.time()
    
    # H2O 서버 시작
    h2o.init()
    
    train = h2o.H2OFrame(pd.concat([X_train, y_train], axis=1))
    test = h2o.H2OFrame(pd.concat([X_test, y_test], axis=1))

    # AutoML 실행
    aml = H2OAutoML(max_models=10, seed=42)
    aml.train(x=X_train.columns.tolist(), y="Target", training_frame=train)

    # 예측 및 평가
    preds = aml.leader.predict(test)
    accuracy = (preds.as_data_frame().values.flatten().round() == y_test.values).mean()

    print(f"✅ H2O AutoML 모델 학습 완료! 정확도: {accuracy:.4f}")
    print(f"⏳ 소요 시간: {time.time() - start_time:.2f}초")

    # 최적 모델 저장
    aml.leader.download_mojo(path="./h2o_best_model.mojo")
    
    return accuracy

# 🔥 5. 최적 모델 자동 선택
def select_best_model(csv_path):
    X_train, X_test, y_train, y_test = load_data(csv_path)

    # TPOT, Auto-Sklearn, H2O AutoML 실행
    tpot_acc = train_tpot(X_train, X_test, y_train, y_test)
    autosklearn_acc = train_autosklearn(X_train, X_test, y_train, y_test)
    h2o_acc = train_h2o(X_train, X_test, y_train, y_test)

    # 성능 비교 후 최적 모델 선택
    accuracies = {"TPOT": tpot_acc, "Auto-Sklearn": autosklearn_acc, "H2O": h2o_acc}
    best_model = max(accuracies, key=accuracies.get)

    print(f"🔥 최적 모델: {best_model} (정확도: {accuracies[best_model]:.4f})")

if __name__ == "__main__":
    select_best_model("price_data.csv")
