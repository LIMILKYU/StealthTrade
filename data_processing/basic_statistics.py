#단순 통계 분석이지만, 보다 깊이 있는 분석을 가능하게 하기 위해 기본적인 지표 + 고급 분석 기법을 포함했습니다.
#특히 시장 변동성, 이상 탐지, 이동 평균 비교, 상관관계 분석, 분포 분석까지 포함하여 다양한 시각에서 데이터를 분석할 수 있습니다.

import numpy as np
import pandas as pd
import scipy.stats as stats

class BasicStatistics:
    def __init__(self, data: pd.DataFrame):
        """
        기본적인 통계 분석을 수행하는 클래스.

        :param data: 분석할 시장 데이터 (OHLCV, 거래량, 호가 데이터 등)
        """
        self.data = data

    ## 🟢 기본 통계 분석 ##
    
    def calculate_mean(self, column: str):
        """ 평균 계산 """
        return self.data[column].mean()

    def calculate_median(self, column: str):
        """ 중앙값 계산 """
        return self.data[column].median()

    def calculate_variance(self, column: str):
        """ 분산 계산 """
        return self.data[column].var()

    def calculate_std_dev(self, column: str):
        """ 표준편차 계산 """
        return self.data[column].std()

    def calculate_quantiles(self, column: str, quantiles=[0.25, 0.5, 0.75]):
        """ 사분위수 계산 """
        return self.data[column].quantile(quantiles)

    def calculate_skewness(self, column: str):
        """ 왜도(Skewness) 계산 (데이터의 비대칭성) """
        return self.data[column].skew()

    def calculate_kurtosis(self, column: str):
        """ 첨도(Kurtosis) 계산 (데이터의 극단값 비율) """
        return self.data[column].kurt()

    def calculate_volatility(self, column: str):
        """ 변동성 계산 (표준편차 기반) """
        return self.calculate_std_dev(column)

    ## 🟠 고급 통계 분석 ##
    
    def calculate_z_score(self, column: str):
        """ Z-Score (표준화) 계산 """
        mean = self.calculate_mean(column)
        std_dev = self.calculate_std_dev(column)
        return (self.data[column] - mean) / std_dev

    def detect_outliers(self, column: str, threshold=3):
        """ 이상치 감지 (Z-Score 기반) """
        z_scores = self.calculate_z_score(column)
        return self.data[np.abs(z_scores) > threshold]

    def rolling_moving_average(self, column: str, window=5):
        """ 이동 평균 (Rolling Mean) 계산 """
        return self.data[column].rolling(window=window).mean()

    def bollinger_bands(self, column: str, window=20, num_std_dev=2):
        """ 볼린저 밴드 계산 """
        rolling_mean = self.rolling_moving_average(column, window)
        rolling_std = self.data[column].rolling(window=window).std()
        upper_band = rolling_mean + (rolling_std * num_std_dev)
        lower_band = rolling_mean - (rolling_std * num_std_dev)
        return rolling_mean, upper_band, lower_band

    def calculate_autocorrelation(self, column: str, lag=1):
        """ 자기상관(Autocorrelation) 계산 """
        return self.data[column].autocorr(lag=lag)

    def calculate_cross_correlation(self, column1: str, column2: str):
        """ 두 개의 변수 간 상관관계 계산 """
        return self.data[column1].corr(self.data[column2])

    def calculate_sharpe_ratio(self, column: str, risk_free_rate=0.01):
        """ 샤프 비율(Sharpe Ratio) 계산: 리스크 대비 수익률 평가 """
        mean_return = self.calculate_mean(column)
        volatility = self.calculate_volatility(column)
        return (mean_return - risk_free_rate) / volatility

    def fit_distribution(self, column: str):
        """ 데이터 분포에 적합한 확률분포 찾기 """
        data = self.data[column].dropna()
        distributions = ['norm', 't', 'gamma', 'beta', 'lognorm']
        best_fit = None
        best_ks = float('inf')

        for dist_name in distributions:
            dist = getattr(stats, dist_name)
            params = dist.fit(data)
            ks_statistic = stats.kstest(data, dist_name, args=params).statistic

            if ks_statistic < best_ks:
                best_ks = ks_statistic
                best_fit = dist_name

        return best_fit

    def describe(self):
        """ 전체 데이터에 대한 요약 통계 """
        return self.data.describe()

# 테스트 데이터 예제
if __name__ == "__main__":
    # 가상의 OHLCV 데이터 생성
    sample_data = {
        "timestamp": pd.date_range(start="2024-02-01", periods=100, freq="1T"),
        "open": np.random.uniform(30000, 31000, 100),
        "high": np.random.uniform(31000, 31500, 100),
        "low": np.random.uniform(29500, 30500, 100),
        "close": np.random.uniform(30000, 31000, 100),
        "volume": np.random.uniform(100, 500, 100)
    }

    df = pd.DataFrame(sample_data)

    # 통계 분석 객체 생성
    stats = BasicStatistics(df)

    print("📌 평균 가격:", stats.calculate_mean("close"))
    print("📌 중앙값:", stats.calculate_median("close"))
    print("📌 변동성 (표준편차):", stats.calculate_volatility("close"))
    print("📌 이상치 탐지:\n", stats.detect_outliers("close"))
    print("📌 볼린저 밴드:\n", stats.bollinger_bands("close"))
    print("📌 샤프 비율:", stats.calculate_sharpe_ratio("close"))
    print("📌 데이터 분포 적합성 검사:", stats.fit_distribution("close"))
    print("📌 데이터 요약:\n", stats.describe())

# 📌 포함된 기능
# ✅ 기본적인 통계 분석

# 평균 (mean)
# 중앙값 (median)
# 분산 (variance)
# 표준편차 (std_dev)
# 사분위수 (quantiles)
# 변동성 (volatility)
# ✅ 이상 탐지 (Anomaly Detection)

# Z-Score 기반 이상치 탐지 (detect_outliers)
# 볼린저 밴드 분석 (bollinger_bands)
# 자기상관 분석 (calculate_autocorrelation)
# ✅ 고급 통계 분석

# 왜도(Skewness), 첨도(Kurtosis) 분석
# 이동 평균(Rolling Mean) 계산
# 자산평가 지표: 샤프 비율(Sharpe Ratio)
# 데이터의 확률분포 적합성 분석 (fit_distribution)
# ✅ 상관관계 분석

# 자기상관(Autocorrelation) (calculate_autocorrelation)
# 다른 변수와의 상관관계 (Cross-Correlation) (calculate_cross_correlation)
# ✅ 기본 지표 + 시장 분석 활용 가능

# OHLCV 데이터를 활용하여 시장 변동성, 이상치 탐지, 샤프 비율 등 리스크 분석 가능