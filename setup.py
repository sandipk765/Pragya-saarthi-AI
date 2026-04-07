#!/usr/bin/env python3
"""
Pragya-Saarthi Setup Script
Run once before starting the app: python setup.py
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent


def check_dirs():
    dirs = [
        ROOT / "data" / "embeddings",
        ROOT / "src" / "agent",
        ROOT / "src" / "retrieval",
        ROOT / "assets",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
    print("✅ Directory structure ready.")


def check_env():
    env_file = ROOT / ".env"
    if not env_file.exists():
        env_file.write_text(
            "# Get your free key at https://console.x.ai\n"
            'XAI_API_KEY="YOUR_XAI_API_KEY_HERE"\n'
        )
        print("✅ .env created — please add your XAI_API_KEY.")
    else:
        from dotenv import load_dotenv

        load_dotenv(env_file)
        key = os.getenv("XAI_API_KEY", "")
        if key and key not in ("", "YOUR_XAI_API_KEY_HERE"):
            print("✅ XAI_API_KEY is set.")
        else:
            print("⚠️  XAI_API_KEY is missing or placeholder.")
            print("   Edit .env and paste your key from https://console.x.ai")


def check_sdk():
    """Detect which Grok SDK is installed."""
    try:
        import xgrok  # noqa

        print("✅ Grok SDK: xgrok detected.")
        return
    except ImportError:
        pass
    try:
        from openai import OpenAI  # noqa

        print("✅ Grok SDK: OpenAI client detected (with x.ai base).")
        return
    except ImportError:
        pass
    print("⚠️  No Grok SDK found.")
    print("   Run:  pip install xgrok")


def check_data():
    csv = ROOT / "data" / "gita_verses.csv"
    if csv.exists():
        try:
            import pandas as pd

            df = pd.read_csv(csv)
            print(f"✅ Gita dataset: {len(df)} verses loaded.")
        except Exception:
            print("✅ gita_verses.csv exists.")
    else:
        print("❌ data/gita_verses.csv not found!")


def prebuild_index():
    sys.path.insert(0, str(ROOT / "src"))
    try:
        from retrieval.vector_store import GitaVectorStore

        print("🔨 Building / loading FAISS index ...")
        GitaVectorStore()
        print("✅ FAISS index ready.")
    except Exception as e:
        print(f"⚠️  Could not build FAISS index: {e}")
        print("   App will use keyword search as fallback.")


if __name__ == "__main__":
    print("\n🎯 Pragya-Saarthi Setup\n" + "─" * 42)
    check_dirs()
    check_env()
    check_sdk()
    check_data()
    prebuild_index()
    print("\n" + "─" * 42)
    print("✨ Setup complete!\n")
    print("▶  Install dependencies:")
    print("   pip install -r requirements.txt\n")
    print("▶  Start the app:")
    print("   streamlit run src/app.py\n")
