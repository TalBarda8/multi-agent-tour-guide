"""
Module 1: Request Validator
Validates user input and initializes request context
"""

from datetime import datetime
from typing import Dict, Any

from src.models import TransactionContext, create_transaction_id
from src.logging_config import get_logger


class ValidationError(Exception):
    """Raised when request validation fails"""
    pass


def validate_request(
    origin: str,
    destination: str,
    preferences: Dict[str, Any] = None
) -> TransactionContext:
    """
    Validate user input and create transaction context

    Input Contract:
        - origin: str (address or place name)
        - destination: str (address or place name)
        - preferences: dict (optional user preferences)

    Output Contract:
        - TransactionContext object with transaction_id and validated data

    Raises:
        - ValidationError if validation fails

    Args:
        origin: Starting location
        destination: Ending location
        preferences: Optional user preferences

    Returns:
        TransactionContext with generated transaction ID
    """
    logger = get_logger()

    # Generate transaction ID
    transaction_id = create_transaction_id()

    # Initialize preferences
    if preferences is None:
        preferences = {}

    try:
        # Validate origin
        if not origin or not isinstance(origin, str) or not origin.strip():
            raise ValidationError("Origin must be a non-empty string")

        # Validate destination
        if not destination or not isinstance(destination, str) or not destination.strip():
            raise ValidationError("Destination must be a non-empty string")

        # Normalize inputs
        origin = origin.strip()
        destination = destination.strip()

        # Normalize preferences
        normalized_preferences = _normalize_preferences(preferences)

        # Create transaction context
        context = TransactionContext(
            transaction_id=transaction_id,
            origin=origin,
            destination=destination,
            user_preferences=normalized_preferences,
            current_stage="validation"
        )

        # Log successful validation
        logger.info(
            "Request validated",
            transaction_id=transaction_id,
            origin=origin,
            destination=destination
        )

        return context

    except ValidationError as e:
        # Log validation failure
        logger.error(
            "Request validation failed",
            transaction_id=transaction_id,
            error=str(e)
        )
        raise


def _normalize_preferences(preferences: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize and validate user preferences

    Args:
        preferences: Raw preferences from user

    Returns:
        Normalized preferences dictionary
    """
    normalized = {}

    # Normalize content type preference
    if "content_type" in preferences:
        content_type = preferences["content_type"].lower()
        valid_types = ["auto", "video", "music", "history"]
        if content_type in valid_types:
            normalized["content_type"] = content_type
        else:
            # Default to auto if invalid
            normalized["content_type"] = "auto"
    else:
        normalized["content_type"] = "auto"

    # Normalize avoid list
    if "avoid" in preferences and isinstance(preferences["avoid"], list):
        normalized["avoid"] = [str(item).lower() for item in preferences["avoid"]]
    else:
        normalized["avoid"] = []

    return normalized
