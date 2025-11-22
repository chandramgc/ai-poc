"""
LangChain integration for LLM pipeline.

Wraps Hugging Face pipeline with LangChain interfaces.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline

from app.core.config import get_settings
from app.core.logging import get_logger
from app.llm.loader import get_pipeline

logger = get_logger(__name__)


# Global chain instance
_chain: Optional[LLMChain] = None


def load_system_prompt() -> str:
    """
    Load system prompt from file.
    
    Returns:
        str: System prompt text
    """
    prompt_file = Path(__file__).parent / "prompts" / "base_system.txt"
    
    if not prompt_file.exists():
        logger.warning(f"System prompt file not found: {prompt_file}")
        return "You are a helpful AI assistant."
    
    with open(prompt_file, "r") as f:
        return f.read().strip()


def get_langchain_llm() -> HuggingFacePipeline:
    """
    Get LangChain-wrapped Hugging Face pipeline.
    
    Returns:
        HuggingFacePipeline: LangChain LLM wrapper
    """
    settings = get_settings()
    pipe = get_pipeline()
    
    # Wrap pipeline with LangChain
    llm = HuggingFacePipeline(
        pipeline=pipe,
        model_kwargs={
            "temperature": settings.model.temperature,
            "max_new_tokens": settings.model.max_tokens,
            "top_p": settings.model.top_p,
            "top_k": settings.model.top_k,
        },
    )
    
    return llm


def get_chain(system_prompt: Optional[str] = None) -> LLMChain:
    """
    Get or create LangChain LLMChain.
    
    Parameters:
        system_prompt (Optional[str]): Custom system prompt
        
    Returns:
        LLMChain: Configured LangChain chain
    """
    global _chain
    
    if _chain is not None:
        logger.debug("Returning existing chain instance")
        return _chain
    
    logger.info("Creating new LangChain chain")
    
    # Load system prompt
    sys_prompt = system_prompt or load_system_prompt()
    
    # Create prompt template - using double braces for literal braces in f-string
    prompt_template = PromptTemplate(
        input_variables=["prompt"],
        template=f"{sys_prompt}\n\nUser: {{prompt}}\n\nAssistant:",
    )
    
    # Get LLM
    llm = get_langchain_llm()
    
    # Create chain
    _chain = LLMChain(llm=llm, prompt=prompt_template)
    
    logger.info("LangChain chain created successfully")
    return _chain


def run_chain(prompt: str, **kwargs: Any) -> str:
    """
    Run the LangChain chain with given prompt.
    
    Parameters:
        prompt (str): User prompt
        **kwargs: Additional parameters for the chain
        
    Returns:
        str: Generated response
    """
    chain = get_chain()
    
    try:
        response = chain.run(prompt=prompt, **kwargs)
        return response.strip()
    except Exception as e:
        logger.error(f"Chain execution failed: {str(e)}")
        raise