# FR-PT Translator 🎙️➡️📖
Tradutor simultâneo **Francês → Português** feito em Python, utilizando:
- [Vosk](https://alphacephei.com/vosk/) para reconhecimento de voz **offline**
- [DeepL API](https://www.deepl.com/pro-api) para tradução **online**
- [SoundDevice](https://python-sounddevice.readthedocs.io/) para captura do microfone

Projeto criado para uso em aulas, permitindo transcrever a fala do professor em francês e exibir/salvar a tradução em português.

---

## 🚀 Funcionalidades
- Captura voz em francês pelo microfone
- Transcreve localmente (offline) usando Vosk
- Traduz em tempo real para português via DeepL
- Mostra francês e português no terminal
- Salva tudo em um arquivo `transcricao_fr_pt.txt`

---

## 🛠️ Requisitos
- **Python 3.9+**
- Sistema operacional Windows/Linux/Mac
- Microfone configurado no sistema
- Conta gratuita na **DeepL API** (500.000 caracteres/mês grátis)

---

## 📦 Instalação

1. Clone este repositório:
   ```bash
   git clone https://github.com/specht1000/FR-PT-Translator.git
   cd FR-PT-Translator

2. Crie um ambiente virtual e ative:
   ```bash 
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate

3. Instale as dependências:
   ```bash
     pip install -r requirements.txt

4. Baixe o modelo de voz em francês do site do Vosk
  - Recomendado: vosk-model-fr-0.22
  - Extraia a pasta dentro do projeto, ficando assim:
    FR-PT-Translator/
      ├── fr_pt_live_translator.py
      ├── requirements.txt
      ├── vosk-model-fr-0.22/


   
