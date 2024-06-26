from abc import ABC
from typing import List
from fastagi.tools.base_tool import BaseTool, BaseToolkit, ToolConfiguration
from fastagi.tools.duck_duck_go.duck_duck_go_search import DuckDuckGoSearchTool
from fastagi.types.key_type import ToolConfigKeyType
from fastagi.models.tool_config import ToolConfig

class DuckDuckGoToolkit(BaseToolkit, ABC):
    name: str = "DuckDuckGo Search Toolkit"
    description: str = "Toolkit containing tools for performing DuckDuckGo search and extracting snippets and webpages"

    def get_tools(self) -> List[BaseTool]:
        return [DuckDuckGoSearchTool()]

    def get_env_keys(self) -> List[ToolConfiguration]:
        return [
            # Add more config keys specific to your project
        ]
