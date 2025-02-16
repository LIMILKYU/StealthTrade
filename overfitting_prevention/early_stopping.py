from tensorflow.keras.callbacks import EarlyStopping

def get_early_stopping(monitor="val_loss", patience=5):
    """
    조기 종료 콜백을 반환합니다.
    Args:
        monitor (str): 모니터링할 지표 (예: 'val_loss')
        patience (int): 개선되지 않은 epoch 수
    Returns:
        EarlyStopping: 조기 종료 콜백
    """
    return EarlyStopping(monitor=monitor, patience=patience, restore_best_weights=True)
