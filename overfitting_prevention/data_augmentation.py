import tensorflow as tf

def get_data_augmentation():
    """
    이미지 데이터 증강을 위한 레이어를 생성합니다.
    Returns:
        tf.keras.Sequential: 데이터 증강 레이어
    """
    return tf.keras.Sequential([
        tf.keras.layers.RandomFlip("horizontal"),
        tf.keras.layers.RandomRotation(0.1),
        tf.keras.layers.RandomZoom(0.1)
    ])
