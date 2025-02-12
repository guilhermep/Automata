import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from automata.config.base import AgentConfigName, LLMProvider
from automata.core.base.tool import Tool
from automata.core.llm.completion import (
    LLMConversationDatabaseProvider,
    LLMIterationResult,
)

logger = logging.getLogger(__name__)


class Agent(ABC):
    """
    An abstract class for implementing a agent.
    An agent is an autonomous entity that can perform actions and communicate with other agents.
    """

    def __init__(self, instructions: str) -> None:
        self.instructions = instructions
        self.completed = False
        self.database_provider: Optional[LLMConversationDatabaseProvider] = None

    @abstractmethod
    def __iter__(self):
        pass

    @abstractmethod
    def __next__(self) -> LLMIterationResult:
        """
        Iterates the agent by performing a single step of its task.
        A single step is a new conversation turn, which consists of generating
        a new 'asisstant' message, and parsing the reply from the 'user'.

        Returns:
            LLMIterationResult:
            The latest assistant and user messages, or None if the task is completed.
        """
        pass

    @abstractmethod
    def run(self) -> str:
        """
        Runs the agent until it completes its task.
        The task is complete when next returns None.

        Raises:
            AgentError: If the agent has already completed its task or exceeds the maximum number of iterations.
        """
        pass

    @abstractmethod
    def set_database_provider(self, provider: LLMConversationDatabaseProvider) -> None:
        pass

    @abstractmethod
    def _setup(self) -> None:
        pass


class AgentToolProviders(Enum):
    """
    An enum for the different types of agent tools.

    Each tool type corresponds to a different type of agent tool.
    The associated builders are located in automata/core/agent/builder/*
    """

    PY_READER = "py_reader"
    PY_WRITER = "py_writer"
    SYMBOL_SEARCH = "symbol_search"
    CONTEXT_ORACLE = "context_oracle"


class AgentToolBuilder(ABC):
    """

    AgentToolBuilder is an abstract class for building tools for agents.

    Each builder builds the tools associated with a specific AgentToolProviders.
    """

    TOOL_TYPE: Optional[AgentToolProviders] = None
    PLATFORM: Optional[LLMProvider] = None

    @abstractmethod
    def build(self) -> List[Tool]:
        pass


class AgentInstance(BaseModel):
    """An abstract class for implementing an agent instance."""

    config_name: AgentConfigName = AgentConfigName.DEFAULT
    description: str = ""
    kwargs: Dict[str, Any] = {}

    class Config:
        arbitrary_types_allowed = True

    @abstractmethod
    def run(self, instructions: str) -> str:
        pass

    @classmethod
    def create(
        cls, config_name: AgentConfigName, description: str = "", **kwargs
    ) -> "AgentInstance":
        return cls(config_name=config_name, description=description, kwargs=kwargs)
