import logging
import textwrap
from typing import List

from automata.config.base import LLMProvider
from automata.core.agent.tool.registry import AutomataOpenAIAgentToolBuilderRegistry
from automata.core.base.agent import AgentToolBuilder, AgentToolProviders
from automata.core.base.tool import Tool
from automata.core.embedding.symbol_similarity import SymbolSimilarityCalculator
from automata.core.llm.providers.openai import OpenAIAgentToolBuilder, OpenAITool
from automata.core.symbol.search.symbol_search import SymbolSearch

logger = logging.getLogger(__name__)


class ContextOracleToolBuilder(AgentToolBuilder):
    """The ContextOracleTools provides a tool that combines SymbolSearch and SymbolSimilarity to create contexts."""

    def __init__(
        self,
        symbol_search: SymbolSearch,
        symbol_doc_similarity: SymbolSimilarityCalculator,
        **kwargs,
    ) -> None:
        self.symbol_search = symbol_search
        self.symbol_doc_similarity = symbol_doc_similarity

    def build(self) -> List[Tool]:
        """Builds the tools associated with the context oracle."""
        return [
            Tool(
                name="context-oracle",
                function=self._get_context,
                description=textwrap.dedent(
                    """
                This tool combines SymbolSearch and SymbolSimilarity to create contexts. Given a query, it uses SymbolSimilarity calculate the similarity between each symbol's documentation and the query returns the most similar document. Then, it leverages SymbolSearch to combine Semantic Search with PageRank to find the most relevant symbols to the query. The overview documentation of these symbols is then concated to the result of the SymbolSimilarity query to create a context.

                For instance, if a query reads 'Tell me about SymbolRank', it will find the most similar document to this query from the embeddings, which in this case would be the documentation for the SymbolRank class. Then, it will use SymbolSearch to fetch some of the most relevant symbols which would be 'Symbol', 'SymbolSearch', 'SymbolGraph', etc. This results in a comprehensive context for the query.
                """
                ),
            )
        ]

    def _get_context(self, query: str, max_related_symbols=5) -> str:
        """
        Retrieves the context corresponding to a given query.

        The function constructs the context by concatenating the source code and documentation of the most semantically
        similar symbol to the query with the documentation summary of the most highly
        ranked symbols. The ranking of symbols is based on their semantic similarity to the query.
        """
        doc_output = self.symbol_doc_similarity.calculate_query_similarity_dict(query)
        most_similar_doc_embedding = self.symbol_doc_similarity.embedding_handler.get_embedding(
            sorted(doc_output.items(), key=lambda x: -x[1])[0][0]
        )
        print("The most similar doc embedding = ", most_similar_doc_embedding)
        rank_output = self.symbol_search.symbol_rank_search(query)

        result = most_similar_doc_embedding.source_code

        result += most_similar_doc_embedding.embedding_source

        counter = 0
        for symbol, _ in rank_output:
            if counter >= max_related_symbols:
                break
            try:
                result += "%s\n" % symbol.dotpath
                result += self.symbol_doc_similarity.embedding_handler.get_embedding(
                    symbol
                ).summary
                counter += 1
            except Exception as e:
                logger.error(
                    "Failed to get embedding for symbol %s with error: %s",
                    symbol,
                    e,
                )
                continue
        return result


@AutomataOpenAIAgentToolBuilderRegistry.register_tool_manager
class ContextOracleOpenAIToolBuilder(ContextOracleToolBuilder, OpenAIAgentToolBuilder):
    TOOL_TYPE = AgentToolProviders.CONTEXT_ORACLE
    PLATFORM = LLMProvider.OPENAI

    def build_for_open_ai(self) -> List[OpenAITool]:
        tools = super().build()

        # Predefined properties and required parameters
        properties = {
            "query": {"type": "string", "description": "The query string to search for."},
            "max_related_symbols": {
                "type": "integer",
                "description": "The maximum number of related symbols to return.",
            },
        }
        required = ["query"]

        openai_tools = []
        for tool in tools:
            openai_tool = OpenAITool(
                function=tool.function,
                name=tool.name,
                description=tool.description,
                properties=properties,
                required=required,
            )
            openai_tools.append(openai_tool)

        return openai_tools
