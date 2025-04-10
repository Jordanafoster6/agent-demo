from typing import TypedDict

class DesignContext(TypedDict):
    design_image_url: str
    status: str
    original_prompt: str
    current_prompt: str

def create_design_context(url: str, prompt: str) -> DesignContext:
    """Create a standardized design context object."""
    return {
        "design_image_url": url,
        "status": "refining",
        "original_prompt": prompt,
        "current_prompt": prompt,
    }