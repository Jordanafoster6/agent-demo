from typing import TypedDict, Optional, List

class ProductContext(TypedDict, total=False):
    blueprint_id: int
    blueprint_name: str
    print_provider_id: int
    variant_ids: List[int]
    image_url: str
    title: str
    description: str
    sizes: List[str]
    color: str
    material: str
    price_tier: str  # "cheap" | "midrange" | "premium"
    quantity: int
    user_notes: str