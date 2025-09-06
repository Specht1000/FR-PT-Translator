import json
import os
import queue
import sys
import time
from datetime import datetime

import numpy as np
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from dotenv import load_dotenv

# Tradução DeepL
import deepl


# =============== CONFIGURAÇÕES ===============

# Caminho do modelo Vosk FR (pasta descompactada do modelo)
VOSK_MODEL_PATH = r"vosk-model-fr-0.22/vosk-model-fr-0.22"  # altere se necessário

# Sample rate usado pelo Vosk (16000 é padrão)
SAMPLE_RATE = 16000

# Tamanho do bloco (quanto menor, mais responsivo; não exagere para não sobrecarregar)
BLOCK_SIZE = 4000

# Arquivo de log onde salvaremos [FR] e [PT]
LOG_FILE = "transcricao_fr_pt.txt"

# Idiomas para DeepL
DEEPL_SOURCE = "FR"     # francês
DEEPL_TARGET = "PT-BR"  # português (Brasil). Pode usar "PT-PT" para português europeu.

# Mostrar também parciais enquanto a pessoa fala? (True/False)
SHOW_PARTIAL = False


# =============== UTILITÁRIOS ===============

def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def append_log(line: str):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def list_input_devices():
    print("\n=== Dispositivos de entrada disponíveis ===")
    print(sd.query_devices())


# =============== TRADUTOR ===============

class DeepLTranslator:
    def __init__(self, api_key: str):
        self.translator = deepl.Translator(api_key)

    def translate(self, text: str, source_lang: str = DEEPL_SOURCE, target_lang: str = DEEPL_TARGET) -> str:
        if not text.strip():
            return ""
        # DeepL retorna objeto; pegamos o .text
        result = self.translator.translate_text(text, source_lang=source_lang, target_lang=target_lang)
        return result.text


# =============== CAPTURA + RECONHECIMENTO ===============

def run_live_translator(device_index=None):
    # Carrega .env e DeepL
    load_dotenv()
    deepl_key = os.getenv("DEEPL_API_KEY", "").strip()
    if not deepl_key:
        print("ERRO: defina DEEPL_API_KEY no .env")
        sys.exit(1)

    translator = DeepLTranslator(deepl_key)

    # Checagem do modelo Vosk
    if not os.path.isdir(VOSK_MODEL_PATH):
        print(f"ERRO: pasta do modelo Vosk não encontrada: {VOSK_MODEL_PATH}")
        sys.exit(1)

    print(f"Iniciando Vosk (modelo: {VOSK_MODEL_PATH})...")
    model = Model(VOSK_MODEL_PATH)
    rec = KaldiRecognizer(model, SAMPLE_RATE)
    rec.SetWords(True)

    # Fila de áudio
    q = queue.Queue()

    def audio_callback(indata, frames, time_info, status):
        if status:
            print(f"[sounddevice] {status}", file=sys.stderr)
        # Converte para bytes (mono, 16 kHz esperado)
        q.put(bytes(indata))

    # Abre stream do microfone
    print("Abrindo microfone...")
    stream = sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=BLOCK_SIZE,
        device=device_index,      # None = padrão do sistema
        dtype="int16",
        channels=1,
        callback=audio_callback,
    )

    print("\n=== TRADUTOR SIMULTÂNEO FR->PT ===")
    print("Fale/aponte o microfone para o professor. Pressione Ctrl+C para encerrar.")
    print(f"Salvando transcrição em: {LOG_FILE}\n")
    append_log(f"\n===== Sessão iniciada {timestamp()} =====")

    try:
        with stream:
            last_partial = ""
            while True:
                data = q.get()
                if rec.AcceptWaveform(data):
                    # Frase finalizada
                    res = json.loads(rec.Result())
                    fr_text = (res.get("text") or "").strip()
                    if fr_text:
                        # Tradução DeepL
                        pt_text = translator.translate(fr_text)

                        # Saída no console
                        print(f"[FR] {fr_text}")
                        print(f"[PT] {pt_text}\n")

                        # Log
                        append_log(f"[{timestamp()}] [FR] {fr_text}")
                        append_log(f"[{timestamp()}] [PT] {pt_text}")
                else:
                    # Parcial (enquanto a pessoa fala)
                    if SHOW_PARTIAL:
                        pres = json.loads(rec.PartialResult())
                        partial = (pres.get("partial") or "").strip()
                        # Evita flood
                        if partial and partial != last_partial:
                            last_partial = partial
                            print(f"(parcial) {partial}", end="\r", flush=True)
    except KeyboardInterrupt:
        print("\nEncerrando...")
    finally:
        append_log(f"===== Sessão encerrada {timestamp()} =====\n")


if __name__ == "__main__":
    # Dica: rode uma vez list_input_devices() para ver o índice do seu microfone
    # list_input_devices()

    # Se quiser forçar um dispositivo específico, passe o índice (ex.: 1, 2, 3...)
    # Ex.: run_live_translator(device_index=1)
    run_live_translator(device_index=None)