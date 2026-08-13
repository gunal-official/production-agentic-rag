import re
from time import perf_counter

from langgraph.graph import END, START, StateGraph
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.state import AgentState
from app.agents.tools.calculator import calculate
from app.llm.groq_provider import GroqProvider
from app.services.evidence import EvidenceService
from app.services.search import SearchService


class AgenticRAG:
    def __init__(self, session: AsyncSession):
        self.search_service = SearchService(session)
        self.evidence_service = EvidenceService()
        self.llm = GroqProvider()
        self.graph = self._build_graph()

    def _build_graph(self):
        builder = StateGraph(AgentState)

        builder.add_node(
            "classify_tool",
            self.classify_tool,
        )

        builder.add_node(
            "retrieve",
            self.retrieve_documents,
        )

        builder.add_node(
            "verify",
            self.verify_evidence,
        )

        builder.add_node(
            "rewrite",
            self.rewrite_query,
        )

        builder.add_node(
            "generate",
            self.generate_answer,
        )

        builder.add_node(
            "calculate",
            self.run_calculator,
        )

        builder.add_node(
            "refuse",
            self.refuse_answer,
        )

        builder.add_edge(
            START,
            "classify_tool",
        )

        builder.add_conditional_edges(
            "classify_tool",
            self.route_after_tool_classification,
            {
                "rag": "retrieve",
                "calculator": "calculate",
                "refuse": "refuse",
            },
        )

        builder.add_edge(
            "retrieve",
            "verify",
        )

        builder.add_conditional_edges(
            "verify",
            self.route_after_verification,
            {
                "generate": "generate",
                "rewrite": "rewrite",
                "refuse": "refuse",
            },
        )

        builder.add_edge(
            "rewrite",
            "retrieve",
        )

        builder.add_edge(
            "generate",
            END,
        )

        builder.add_edge(
            "calculate",
            END,
        )

        builder.add_edge(
            "refuse",
            END,
        )

        return builder.compile()

    def _add_trace(
        self,
        state: AgentState,
        node: str,
        started_at: float,
        **metadata,
    ) -> list[dict]:
        trace = list(
            state.get(
                "trace",
                [],
            )
        )

        duration_ms = (
            perf_counter() - started_at
        ) * 1000

        trace.append(
            {
                "node": node,
                "duration_ms": round(
                    duration_ms,
                    2,
                ),
                **metadata,
            }
        )

        return trace

    async def classify_tool(
        self,
        state: AgentState,
    ) -> AgentState:
        started_at = perf_counter()

        question = state["question"].strip()

        if not question:
            return {
                "tool_name": "refuse",
                "trace": self._add_trace(
                    state,
                    "classify_tool",
                    started_at,
                    tool="refuse",
                ),
            }

        calculator_pattern = (
            r"^[\d\s\+\-\*\/\(\)\.\^]+$"
        )

        normalized_question = (
            question
            .lower()
            .replace("calculate", "")
            .replace("what is", "")
            .replace("=", "")
            .strip()
        )

        if re.fullmatch(
            calculator_pattern,
            normalized_question,
        ):
            return {
                "tool_name": "calculator",
                "tool_result": normalized_question,
                "trace": self._add_trace(
                    state,
                    "classify_tool",
                    started_at,
                    tool="calculator",
                ),
            }

        return {
            "tool_name": "rag",
            "retrieval_query": question,
            "trace": self._add_trace(
                state,
                "classify_tool",
                started_at,
                tool="rag",
            ),
        }

    def route_after_tool_classification(
        self,
        state: AgentState,
    ) -> str:
        tool_name = state.get(
            "tool_name",
            "refuse",
        )

        if tool_name == "calculator":
            return "calculator"

        if tool_name == "rag":
            return "rag"

        return "refuse"

    async def retrieve_documents(
        self,
        state: AgentState,
    ) -> AgentState:
        started_at = perf_counter()

        query = state.get(
            "retrieval_query",
            state["question"],
        )

        results = await self.search_service.search(
            query=query,
            top_k=state.get("top_k", 5),
        )

        return {
            "search_results": results,
            "trace": self._add_trace(
                state,
                "retrieve",
                started_at,
                result_count=len(results),
            ),
        }

    async def verify_evidence(
        self,
        state: AgentState,
    ) -> AgentState:
        started_at = perf_counter()

        results = state.get(
            "search_results",
            [],
        )

        evidence_valid = (
            self.evidence_service.is_sufficient(
                results
            )
        )

        return {
            "evidence_valid": evidence_valid,
            "trace": self._add_trace(
                state,
                "verify",
                started_at,
                evidence_valid=evidence_valid,
            ),
        }

    def route_after_verification(
        self,
        state: AgentState,
    ) -> str:
        if state.get("evidence_valid"):
            return "generate"

        retry_count = state.get(
            "retry_count",
            0,
        )

        if retry_count < 1:
            return "rewrite"

        return "refuse"

    async def rewrite_query(
        self,
        state: AgentState,
    ) -> AgentState:
        started_at = perf_counter()

        prompt = f"""
Rewrite the following user question into a concise search query.

Rules:
- Do not answer the question.
- Return only the rewritten search query.
- Preserve the original meaning.
- Do not invent new facts.

Original question:
{state["question"]}

Search query:
""".strip()

        rewritten = await self.llm.generate(
            prompt
        )

        rewritten_query = rewritten.strip()

        return {
            "retrieval_query": rewritten_query,
            "retry_count": state.get(
                "retry_count",
                0,
            )
            + 1,
            "trace": self._add_trace(
                state,
                "rewrite",
                started_at,
                rewritten_query=rewritten_query,
            ),
        }

    async def generate_answer(
        self,
        state: AgentState,
    ) -> AgentState:
        started_at = perf_counter()

        results = state.get(
            "search_results",
            [],
        )

        context_parts: list[str] = []

        for index, result in enumerate(
            results,
            start=1,
        ):
            page_label = (
                f"page {result.page_number}"
                if result.page_number is not None
                else "page unavailable"
            )

            context_parts.append(
                "\n".join(
                    [
                        f"[Source {index}]",
                        f"File: {result.filename}",
                        f"Location: {page_label}",
                        f"Content: {result.content}",
                    ]
                )
            )

        context = "\n\n".join(
            context_parts
        )

        prompt = f"""
You are a grounded enterprise knowledge assistant.

Answer the user's question using ONLY the evidence below.

Rules:
1. Do not use outside knowledge.
2. Do not invent facts.
3. Every factual claim must be supported by the evidence.
4. Cite factual claims using [Source N].
5. Use only source numbers that appear below.
6. Never invent citations.
7. If multiple sources support a claim, cite them together.
8. If the evidence is insufficient, answer exactly:
   "I don't have enough information in the available documents."
9. Keep the answer concise and factual.

Evidence:

{context}

Question:
{state["question"]}

Answer:
""".strip()

        answer = await self.llm.generate(
            prompt
        )

        return {
            "answer": answer,
            "trace": self._add_trace(
                state,
                "generate",
                started_at,
                source_count=len(results),
            ),
        }

    async def run_calculator(
        self,
        state: AgentState,
    ) -> AgentState:
        started_at = perf_counter()

        expression = state.get(
            "tool_result",
            "",
        )

        expression = expression.replace(
            "^",
            "**",
        )

        try:
            result = calculate(
                expression
            )

            return {
                "answer": str(result),
                "tool_result": str(result),
                "trace": self._add_trace(
                    state,
                    "calculate",
                    started_at,
                    success=True,
                ),
            }

        except (
            ValueError,
            SyntaxError,
            ZeroDivisionError,
            OverflowError,
        ):
            return {
                "answer": (
                    "I could not evaluate "
                    "that calculation safely."
                ),
                "trace": self._add_trace(
                    state,
                    "calculate",
                    started_at,
                    success=False,
                ),
            }

    async def refuse_answer(
        self,
        state: AgentState,
    ) -> AgentState:
        started_at = perf_counter()

        return {
            "answer": (
                "I don't have enough information "
                "in the available documents."
            ),
            "trace": self._add_trace(
                state,
                "refuse",
                started_at,
            ),
        }

    async def run(
        self,
        question: str,
        top_k: int = 5,
    ) -> AgentState:
        result = await self.graph.ainvoke(
            {
                "question": question,
                "retrieval_query": question,
                "top_k": top_k,
                "retry_count": 0,
                "trace": [],
            }
        )

        return result