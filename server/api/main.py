import base64
import io

import numpy as np
import soundfile as sf
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from scipy.fft import fft, fftfreq

from backend.filters import apply_filter

app = FastAPI(title="Noise Cleaner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_CHART_POINTS = 1000


def downsample_series(x: np.ndarray, y: np.ndarray, max_points: int) -> tuple[list[float], list[float]]:
    """Bucket (x, y) into `max_points` and keep each bucket's min/max y value.

    A plain stride (y[::step]) can alias an oscillating signal into a
    near-flat line once the signal frequency approaches the new sample
    rate implied by the stride. Keeping the local min and max per bucket
    preserves the true amplitude envelope instead.
    """
    n = len(y)
    if n <= max_points:
        return x.tolist(), y.tolist()

    buckets = max(1, max_points // 2)
    edges = np.linspace(0, n, buckets + 1, dtype=int)

    x_out: list[float] = []
    y_out: list[float] = []
    for i in range(buckets):
        start, end = edges[i], edges[i + 1]
        if end <= start:
            continue
        chunk = y[start:end]
        chunk_x = x[start:end]
        min_idx, max_idx = sorted((int(chunk.argmin()), int(chunk.argmax())))
        x_out.append(float(chunk_x[min_idx]))
        y_out.append(float(chunk[min_idx]))
        x_out.append(float(chunk_x[max_idx]))
        y_out.append(float(chunk[max_idx]))

    return x_out, y_out


@app.post("/api/filter")
async def filter_audio(
    file: UploadFile = File(...),
    filter_type: str = Form(...),
    cutoff: float | None = Form(None),
    lowcut: float | None = Form(None),
    highcut: float | None = Form(None),
):
    if filter_type not in ("highpass", "lowpass", "bandpass"):
        raise HTTPException(400, "Geçersiz filtre tipi")

    raw = await file.read()
    try:
        data, sample_rate = sf.read(io.BytesIO(raw))
    except Exception:
        raise HTTPException(400, "Ses dosyası okunamadı")

    if data.ndim > 1:
        data = data.mean(axis=1)

    try:
        filtered = apply_filter(
            data,
            sample_rate,
            filter_type,
            cutoff=cutoff,
            lowcut=lowcut,
            highcut=highcut,
        )
    except ValueError as error:
        raise HTTPException(400, str(error))

    peak = np.max(np.abs(filtered))
    if peak > 0:
        filtered = filtered / peak

    n = len(data)
    t = np.linspace(0, n / sample_rate, num=n)

    xf = fftfreq(n, 1 / sample_rate)[: n // 2]
    yf = np.abs(fft(data))[: n // 2]
    yf_filtered = np.abs(fft(filtered))[: n // 2]

    out_buffer = io.BytesIO()
    sf.write(out_buffer, filtered, sample_rate, format="WAV")
    audio_base64 = base64.b64encode(out_buffer.getvalue()).decode("ascii")

    time_original, original_signal = downsample_series(t, data, MAX_CHART_POINTS)
    time_filtered, filtered_signal = downsample_series(t, filtered, MAX_CHART_POINTS)
    freq_original, original_spectrum = downsample_series(xf, yf, MAX_CHART_POINTS)
    freq_filtered, filtered_spectrum = downsample_series(xf, yf_filtered, MAX_CHART_POINTS)

    return {
        "sample_rate": sample_rate,
        "time_original": time_original,
        "original_signal": original_signal,
        "time_filtered": time_filtered,
        "filtered_signal": filtered_signal,
        "freq_original": freq_original,
        "original_spectrum": original_spectrum,
        "freq_filtered": freq_filtered,
        "filtered_spectrum": filtered_spectrum,
        "filtered_audio_base64": f"data:audio/wav;base64,{audio_base64}",
    }
