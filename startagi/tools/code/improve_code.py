import re
from typing import Type, Optional, List

from pydantic import BaseModel, Field

from fastagi.agent.agent_prompt_builder import AgentPromptBuilder
from fastagi.helper.error_handler import ErrorHandler
from fastagi.helper.prompt_reader import PromptReader
from fastagi.helper.token_counter import TokenCounter
from fastagi.lib.logger import logger
from fastagi.llms.base_llm import BaseLlm
from fastagi.models.agent_execution import AgentExecution
from fastagi.models.agent_execution_feed import AgentExecutionFeed
from fastagi.resource_manager.file_manager import FileManager
from fastagi.tools.base_tool import BaseTool
from fastagi.tools.tool_response_query_manager import ToolResponseQueryManager


class ImproveCodeSchema(BaseModel):
    pass


class ImproveCodeTool(BaseTool):
    """
    Used to improve the already generated code by reading the code from the files

    Attributes:
        llm: LLM used for code generation.
        name : The name of the tool.
        description : The description of the tool.
        resource_manager: Manages the file resources.
    """
    llm: Optional[BaseLlm] = None
    agent_id: int = None
    agent_execution_id: int = None
    name = "ImproveCodeTool"
    description = (
        "This tool improves the generated code."
    )
    args_schema: Type[ImproveCodeSchema] = ImproveCodeSchema
    resource_manager: Optional[FileManager] = None
    tool_response_manager: Optional[ToolResponseQueryManager] = None
    goals: List[str] = []

    class Config:
        arbitrary_types_allowed = True

    def _execute(self) -> str:
        """
        Execute the improve code tool.

        Returns:
            Improved code or error message.
        """
        # Get all file names that the CodingTool has written
        file_names = self.resource_manager.get_files()
        logger.info(file_names)
        # Loop through each file
        for file_name in file_names:
            if '.txt' not in file_name and '.sh' not in file_name and '.json' not in file_name:
                # Read the file content
                content = self.resource_manager.read_file(file_name)

                # Generate a prompt from improve_code.txt
                prompt = PromptReader.read_tools_prompt(__file__, "improve_code.txt")

                # Combine the hint from the file, goals, and content
                prompt = prompt.replace("{goals}", AgentPromptBuilder.add_list_items_to_string(self.goals))
                prompt = prompt.replace("{content}", content)

                # Add the file content to the chat completion prompt
                prompt = prompt + "\nOriginal Code:\n```\n" + content + "\n```"



                # Use LLM to generate improved code
                result = self.llm.chat_completion([{'role': 'system', 'content': prompt}])
                
                if result is not None and 'error' in result and result['message'] is not None:
                   ErrorHandler.handle_openai_errors(self.toolkit_config.session, self.agent_id, self.agent_execution_id, result['message'])

                # Extract the response first
                response = result.get('response')
                if not response: 
                    logger.info("RESPONSE NOT AVAILABLE")

                # Now extract the choices from response
                choices = response.get('choices')
                if not choices: 
                    logger.info("CHOICES NOT AVAILABLE")

                # Now you can safely extract the message content
                improved_content = choices[0]["message"]["content"]
                # improved_content = result["messages"][0]["content"]
                parsed_content = re.findall("```(?:\w*\n)?(.*?)```", improved_content, re.DOTALL)
                parsed_content_code = "\n".join(parsed_content)

                # Rewrite the file with the improved content
                save_result = self.resource_manager.write_file(file_name, parsed_content_code)

                if save_result.startswith("Error"):
                    return save_result
            else:
                continue

        return f"All codes improved and saved successfully in: " + " ".join(file_names)