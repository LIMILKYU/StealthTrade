import tensorflow as tf

def apply_l1_l2_regularization(model, l1=0.01, l2=0.01):
    """
    모델의 모든 가중치에 L1 및 L2 정규화를 적용합니다.
    Args:
        model (tf.keras.Model): 정규화를 적용할 모델
        l1 (float): L1 정규화 강도
        l2 (float): L2 정규화 강도
    Returns:
        tf.keras.Model: 정규화가 적용된 모델
    """
    for layer in model.layers:
        if hasattr(layer, "kernel_regularizer"):
            layer.kernel_regularizer = tf.keras.regularizers.l1_l2(l1=l1, l2=l2)
    return model
