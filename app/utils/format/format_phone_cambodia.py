def format_cambodia_phone(phone: str) -> str:
    """Convert a local Cambodian phone number to 855-prefixed format."""
    cleaned = phone.strip().replace(" ", "").replace("-", "")
    
    # Already has country code
    if cleaned.startswith("855"):
        return cleaned
    if cleaned.startswith("+855"):
        return cleaned[1:]  # drop the +
    
    # Strip leading 0 (local format), then prefix
    if cleaned.startswith("0"):
        cleaned = cleaned[1:]
    
    return "855" + cleaned