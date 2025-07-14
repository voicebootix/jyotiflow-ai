"""
Configuration file for Prokerala Smart Pricing System costs
"""

import os

# API and service costs (in USD)
OTHER_COSTS = {
    "openai_gpt4": float(os.getenv("OPENAI_GPT4_COST", "0.09")),  # ~2000 tokens
    "rag_processing": float(os.getenv("RAG_PROCESSING_COST", "0.02")),  # RAG knowledge retrieval
    "server_compute": float(os.getenv("SERVER_COMPUTE_COST", "0.01"))   # Server processing
}

# Voice/Video processing costs
VOICE_VIDEO_COSTS = {
    "voice_processing": float(os.getenv("VOICE_PROCESSING_COST", "0.05")),
    "video_processing": float(os.getenv("VIDEO_PROCESSING_COST", "0.08")),
    "live_chat_processing": float(os.getenv("LIVE_CHAT_PROCESSING_COST", "0.15"))
}

# Default Prokerala API configuration
DEFAULT_PROKERALA_CONFIG = {
    "max_cost_per_call": float(os.getenv("PROKERALA_MAX_COST_PER_CALL", "0.036")),
    "default_margin": float(os.getenv("PROKERALA_DEFAULT_MARGIN", "5.0"))  # 500%
}

def get_other_costs():
    """Get other service costs dictionary"""
    return OTHER_COSTS.copy()

def get_voice_video_costs():
    """Get voice/video processing costs"""
    return VOICE_VIDEO_COSTS.copy()

def get_prokerala_config():
    """Get Prokerala configuration"""
    return DEFAULT_PROKERALA_CONFIG.copy()