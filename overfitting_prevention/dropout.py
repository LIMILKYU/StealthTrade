import tensorflow as tf

def apply_dropout(model, rate=0.5):
    """
    드롭아웃 레이어를 모델에 추가합니다.
    Args:
        model (tf.keras.Model): 드롭아웃을 적용할 모델
        rate (float): 드롭아웃 비율 (0~1)
    Returns:
        tf.keras.Model: 드롭아웃이 추가된 모델
    """
    new_model = tf.keras.Sequential()
    for layer in model.layers:
        new_model.add(layer)
        if hasattr(layer, "activation"):
            new_model.add(tf.keras.layers.Dropout(rate))
    return new_model
