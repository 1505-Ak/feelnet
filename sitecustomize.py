# Auto-executed by Python at startup if present on PYTHONPATH
# Forces the Transformers library to ignore TensorFlow/Flax backends
# so that missing libtensorflow dylibs don't crash the app.
import os
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("TRANSFORMERS_NO_FLAX", "1") 