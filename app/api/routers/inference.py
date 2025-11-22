"""
Text generation inference router.

Provides endpoints for LLM text generation.
"""

from fastapi import APIRouter, Depends

from app.api.dependencies import APIKeyDep, RateLimitDep
from app.api.schemas import GenerateRequest, GenerateResponse
from app.core.cache import get_cache
from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.security import filter_content, sanitize_output, validate_prompt_length
from app.llm.loader import generate_text
from app.utils.errors import GenerationError
from app.utils.timing import measure_latency

logger = get_logger(__name__)
router = APIRouter(prefix="/v1", tags=["generation"])


@router.post("/generate", response_model=GenerateResponse)
async def generate(
    request: GenerateRequest,
    api_key: APIKeyDep,
    rate_limit: RateLimitDep,
):
    """
    Generate text from a prompt.
    
    Performs text generation using the loaded LLM with optional caching.
    
    Parameters:
        request (GenerateRequest): Generation request with prompt and parameters
        api_key (APIKeyDep): Validated API key
        rate_limit (RateLimitDep): Rate limit check
        
    Returns:
        GenerateResponse: Generated text response
        
    Raises:
        GenerationError: If text generation fails
    """
    settings = get_settings()
    cache = get_cache()
    
    # Validate and filter prompt
    validate_prompt_length(request.prompt)
    filter_content(request.prompt)
    
    # Prepare generation parameters
    gen_params = {
        "max_tokens": request.max_tokens,
        "temperature": request.temperature,
        "top_p": request.top_p,
        "top_k": request.top_k,
    }
    
    # Remove None values
    gen_params = {k: v for k, v in gen_params.items() if v is not None}
    
    # Check cache
    cached_response = cache.get(
        model_name=settings.model.name,
        prompt=request.prompt,
        params=gen_params,
    )
    
    if cached_response:
        logger.info("Serving response from cache")
        return GenerateResponse(
            generated_text=cached_response,
            prompt=request.prompt,
            model=settings.model.name,
            tokens_generated=len(cached_response.split()),
            cached=True,
        )
    
    # Generate text
    try:
        logger.info(f"Generating text for prompt: {request.prompt[:50]}...")
        
        generated_text = generate_text(
            prompt=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            top_k=request.top_k,
        )
        
        # Sanitize output
        generated_text = sanitize_output(generated_text)
        
        # Cache response
        cache.set(
            model_name=settings.model.name,
            prompt=request.prompt,
            params=gen_params,
            response=generated_text,
        )
        
        logger.info(f"Successfully generated {len(generated_text)} characters")
        
        return GenerateResponse(
            generated_text=generated_text,
            prompt=request.prompt,
            model=settings.model.name,
            tokens_generated=len(generated_text.split()),
            cached=False,
        )
        
    except Exception as e:
        logger.error(f"Generation failed: {str(e)}")
        raise GenerationError(
            message="Failed to generate text",
            details={"error": str(e)}
        ) from e
