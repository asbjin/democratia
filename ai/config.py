# DemocratIA - AI module configuration

import os


GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

if not GROQ_API_KEY:
    import warnings
    warnings.warn("GROQ_API_KEY not set. AI features will not work.")
