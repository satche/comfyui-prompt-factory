from typing import Any, Dict, Tuple


class MergeStrings:
    """
    A class to represent a dynamic node in ComfyUI.
    """
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("string",)
    FUNCTION = "merge_strings"
    CATEGORY = "⚙️ Prompt Factory/🛠️ Utils"

    @classmethod
    def INPUT_TYPES(s) -> Dict[str, dict]:
        return {
            "required": {
                "separator": ("STRING", {"default": ", "})},
            "optional": {}
        }

    def merge_strings(self, separator, **kwargs) -> Tuple[Any | None]:
        value = separator.join(
            v for v in kwargs.values()
            if isinstance(v, str)
        )
        return (value,)
