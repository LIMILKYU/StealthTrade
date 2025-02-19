function backtest_result = matlab_backtest(price_data)
    % MATLAB 기반 백테스팅
    returns = diff(log(price_data)); % 로그 수익률 계산
    sharpe_ratio = mean(returns) / std(returns); % 샤프 비율 계산
    fprintf("📊 Sharpe Ratio: %.2f\n", sharpe_ratio);
    backtest_result = sharpe_ratio;
end
