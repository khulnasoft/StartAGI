from abc import ABC
from typing import List
from startagi.tools.base_tool import BaseTool, BaseToolkit, ToolConfiguration
from startagi.tools.jira.create_issue import CreateIssueTool
from startagi.tools.jira.edit_issue import EditIssueTool
from startagi.tools.jira.get_projects import GetProjectsTool
from startagi.tools.jira.search_issues import SearchJiraTool
from startagi.types.key_type import ToolConfigKeyType
from startagi.models.tool_config import ToolConfig


class JiraToolkit(BaseToolkit, ABC):
    name: str = "Jira Toolkit"
    description: str = "Toolkit containing tools for Jira integration"

    def get_tools(self) -> List[BaseTool]:
        return [
            CreateIssueTool(),
            EditIssueTool(),
            GetProjectsTool(),
            SearchJiraTool(),
        ]

    def get_env_keys(self) -> List[ToolConfiguration]:
        return [
            ToolConfiguration(key="JIRA_INSTANCE_URL", key_type=ToolConfigKeyType.STRING, is_required= True, is_secret = False),
            ToolConfiguration(key="JIRA_USERNAME", key_type=ToolConfigKeyType.STRING, is_required=True, is_secret=False),
            ToolConfiguration(key="JIRA_API_TOKEN", key_type=ToolConfigKeyType.STRING, is_required=True, is_secret=True)
        ]