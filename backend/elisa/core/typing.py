# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from typeguard import check_type as _check_type
from typing    import get_type_hints
from typing    import Any

def check_type(value: object, typed_dict_type: Any) -> None:
    """
    Wrapper around `typeguard.check_type` to allow extra keys, if the checked value
    is a dictionary. We need this due to the layered architecture, where each layer
    passes a received message to the next layer and each layer expects a different
    set of keys in the dictionary.
    """
    if not isinstance(value, dict):
        raise TypeError(f"Not a dict")

    annotations   = get_type_hints(typed_dict_type)
    required_keys = getattr(typed_dict_type, "__required_keys__", set())

    for key, expected_type in annotations.items():
        if key not in value:
            if key in required_keys:
                raise TypeError(f"Missing required key '{key}'")
            continue

        _check_type(value[key], expected_type)