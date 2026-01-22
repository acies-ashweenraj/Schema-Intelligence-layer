import os
from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph
from langchain_groq import ChatGroq


class GraphRAG:
    """
    Graph-RAG over Neo4j using Groq LLM.
    """

    def __init__(
        self,
        neo4j_url: str,
        neo4j_user: str,
        neo4j_password: str,
        api_key: str,
        model: str = "llama-3.3-70b-versatile",
        neo4j_database: str | None = None
    ):
        """
        neo4j_database:
            - Optional
            - If not provided, will read from NEO4J_DATABASE env
            - Defaults to 'neo4j'
        """

        if neo4j_database is None:
            neo4j_database = os.getenv("NEO4J_DATABASE", "neo4j")

        # -------------------------------
        # Connect to Neo4j (IMPORTANT FIX)
        # -------------------------------
        self.graph = Neo4jGraph(
            url=neo4j_url,
            username=neo4j_user,
            password=neo4j_password,
            database=neo4j_database   # ✅ THIS WAS MISSING
        )

        # Load graph schema (metadata only)
        self.graph.refresh_schema()

        # -------------------------------
        # Groq LLM
        # -------------------------------
        self.llm = ChatGroq(
            model=model,
            temperature=0,
            api_key=api_key
        )

        # -------------------------------
        # Graph-RAG chain
        # -------------------------------
        self.chain = GraphCypherQAChain.from_llm(
            llm=self.llm,
            graph=self.graph,
            verbose=True,
            validate_cypher=True,
            return_intermediate_steps=True,
            allow_dangerous_requests=True  # ⚠️ keep only for trusted users
        )

    def ask(self, question: str) -> str:
        response = self.chain.invoke({"query": question})

        if not response.get("result"):
            return (
                "I don't have enough information in the knowledge graph "
                "to answer this question."
            )

        return response["result"]
