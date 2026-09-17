import numpy as np
from scipy.signal import butter, lfilter


def butter_highpass(cutoff: float, fs: float, order: int = 4):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    return butter(order, normal_cutoff, btype="high")


def butter_lowpass(cutoff: float, fs: float, order: int = 4):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    return butter(order, normal_cutoff, btype="low")


def butter_bandpass(lowcut: float, highcut: float, fs: float, order: int = 4):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    return butter(order, [low, high], btype="band")


def apply_filter(
    data: np.ndarray,
    fs: float,
    filter_type: str,
    cutoff: float | None = None,
    lowcut: float | None = None,
    highcut: float | None = None,
    order: int = 4,
) -> np.ndarray:
    if filter_type == "highpass":
        b, a = butter_highpass(cutoff, fs, order)
    elif filter_type == "lowpass":
        b, a = butter_lowpass(cutoff, fs, order)
    elif filter_type == "bandpass":
        b, a = butter_bandpass(lowcut, highcut, fs, order)
    else:
        raise ValueError(f"Bilinmeyen filtre tipi: {filter_type}")

    return lfilter(b, a, data)
