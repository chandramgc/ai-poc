"""
Model loader module for Hugging Face models.

Handles loading and initialization of Hugging Face models with transformers pipeline.
"""

import os
from pathlib import Path
from typing import Optional

import torch
from transformers import pipeline, Pipeline

from app.core.config import get_settings
from app.core.logging import get_logger
from app.utils.errors import ModelLoadError

logger = get_logger(__name__)


# Global pipeline instance
_pipeline: Optional[Pipeline] = None


def load_pipeline() -> Pipeline:
    """
    Load and initialize the Hugging Face pipeline.
    
    Returns:
        Pipeline: Initialized transformers pipeline
        
    Raises:
        ModelLoadError: If model loading fails
    """
    global _pipeline
    
    if _pipeline is not None:
        logger.info("Returning existing pipeline instance")
        return _pipeline
    
    settings = get_settings()
    
    try:
        logger.info(f"Loading model: {settings.model.name}")
        logger.info(f"Model source: {settings.model.source}")
        logger.info(f"Device: {settings.model.device}")
        
        # Set Hugging Face token if provided
        token = settings.huggingface_token
        if not token:
            logger.warning(
                "HUGGINGFACE_TOKEN not set. Public models will work, "
                "but gated models will fail."
            )
        
        # Determine device
        device = -1  # CPU
        if settings.model.device == "cuda" and torch.cuda.is_available():
            device = 0
            logger.info("Using CUDA device")
        else:
            logger.info("Using CPU device")
        
        # Model path or identifier
        model_path = settings.model.name
        if settings.model.source == "local":
            model_path = Path(model_path).resolve()
            logger.info(f"Loading from local path: {model_path}")
        
        # Load pipeline
        _pipeline = pipeline(
            "text-generation",
            model=model_path,
            device=device,
            token=token,
            dtype=torch.float16 if device >= 0 else torch.float32,
            trust_remote_code=True,
        )
        
        logger.info(f"Successfully loaded model: {settings.model.name}")
        return _pipeline
        
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        raise ModelLoadError(
            message=f"Failed to load model {settings.model.name}",
            details={"error": str(e), "model": settings.model.name}
        ) from e


def get_pipeline() -> Pipeline:
    """
    Get the cached pipeline instance.
    
    Returns:
        Pipeline: Transformers pipeline
        
    Raises:
        ModelLoadError: If pipeline is not initialized
    """
    if _pipeline is None:
        raise ModelLoadError(
            message="Pipeline not initialized. Call load_pipeline() first.",
            details={"hint": "Ensure startup event has completed"}
        )
    
    return _pipeline


def unload_pipeline():
    """Unload pipeline and free memory."""
    global _pipeline
    
    if _pipeline is not None:
        logger.info("Unloading pipeline")
        _pipeline = None
        
        # Force garbage collection
        import gc
        gc.collect()
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        logger.info("Pipeline unloaded successfully")


def generate_text(
    prompt: str,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    top_k: Optional[int] = None,
) -> str:
    """
    Generate text using the loaded pipeline.
    
    Parameters:
        prompt (str): Input prompt
        max_tokens (Optional[int]): Maximum tokens to generate
        temperature (Optional[float]): Sampling temperature
        top_p (Optional[float]): Nucleus sampling parameter
        top_k (Optional[int]): Top-k sampling parameter
        
    Returns:
        str: Generated text
    """
    settings = get_settings()
    pipe = get_pipeline()
    
    # Use config defaults if not provided
    max_tokens = max_tokens or settings.model.max_tokens
    temperature = temperature if temperature is not None else settings.model.temperature
    top_p = top_p if top_p is not None else settings.model.top_p
    top_k = top_k if top_k is not None else settings.model.top_k
    
    logger.info(f"Generating text with max_tokens={max_tokens}, temp={temperature}")
    
    try:
        # Generate
        outputs = pipe(
            prompt,
            max_new_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            do_sample=temperature > 0,
            return_full_text=False,
        )
        
        # Extract generated text
        generated_text = outputs[0]["generated_text"]
        logger.info(f"Generated {len(generated_text)} characters")
        
        return generated_text
        
    except Exception as e:
        logger.error(f"Generation failed: {str(e)}")
        raise
