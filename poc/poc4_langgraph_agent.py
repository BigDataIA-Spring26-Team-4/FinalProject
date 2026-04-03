"""
POC 4: Single-Agent LangGraph Demo
====================================
Minimal LangGraph graph with a News Analyst agent that analyzes
maritime risk using structured Pydantic output.

Prerequisites:
    1. Add to .env: OPENAI_API_KEY=your_key_here
    2. Run POC 3 first to have sanctions data available (optional)

Usage:
    poetry run python poc/poc4_langgraph_agent.py
"""

import os
import sys
from datetime import datetime, timezone
from typing import Annotated, TypedDict
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


def main():
    print(f"🚢 Maritime AI Sentinel — POC 4: LangGraph Agent Demo")
    print(f"{'=' * 60}")

    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY not set in .env")
        sys.exit(1)

    try:
        from langgraph.graph import StateGraph, END
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage, SystemMessage
        from pydantic import BaseModel, Field
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("   Run: poetry install")
        sys.exit(1)

    # ── Pydantic Output Schema ──
    class MaritimeRiskAssessment(BaseModel):
        """Structured output from the News Analyst agent."""
        region: str = Field(description="Geographic region assessed")
        risk_level: int = Field(ge=0, le=100, description="Risk score 0-100")
        summary: str = Field(description="Brief risk narrative")
        key_factors: list[str] = Field(description="Top risk factors identified")
        affected_chokepoints: list[str] = Field(description="Maritime chokepoints affected")
        recommended_actions: list[str] = Field(description="Recommended actions for shipping companies")
        requires_human_review: bool = Field(description="True if risk > 75")

    # ── Agent State ──
    class AgentState(TypedDict):
        query: str
        assessment: dict | None
        error: str | None

    # ── LLM Setup ──
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=OPENAI_API_KEY,
    )

    # Structured output LLM
    structured_llm = llm.with_structured_output(MaritimeRiskAssessment)

    # ── Agent Node ──
    SYSTEM_PROMPT = """You are the News Analyst agent in the Maritime AI Sentinel system.
Your role is to analyze geopolitical events and assess their impact on maritime shipping.

You have expertise in:
- Maritime chokepoint geography (Hormuz, Suez, Malacca, Bab el-Mandeb, Panama, Taiwan Strait, etc.)
- Geopolitical risk assessment for shipping routes
- Sanctions implications for maritime trade
- Weather and climate impacts on shipping

When assessing risk:
- Use a 0-100 scale (0=no risk, 100=complete disruption)
- Consider: military activity, sanctions, piracy, weather, port congestion
- Be specific about which chokepoints are affected
- Provide actionable recommendations
- Set requires_human_review=true if risk_level > 75

Base your analysis on current known geopolitical conditions. Be factual and cite
specific events or conditions that inform your assessment."""

    def news_analyst_node(state: AgentState) -> AgentState:
        """News Analyst agent — assesses maritime risk from geopolitical events."""
        try:
            messages = [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=state["query"]),
            ]
            result = structured_llm.invoke(messages)
            return {
                "query": state["query"],
                "assessment": result.model_dump(),
                "error": None,
            }
        except Exception as e:
            return {
                "query": state["query"],
                "assessment": None,
                "error": str(e),
            }

    # ── Build LangGraph ──
    print(f"\n📊 Building LangGraph agent...")

    graph = StateGraph(AgentState)
    graph.add_node("news_analyst", news_analyst_node)
    graph.set_entry_point("news_analyst")
    graph.add_edge("news_analyst", END)

    app = graph.compile()
    print(f"  ✅ Graph compiled: 1 node (news_analyst) → END")

    # ── Test Queries ──
    test_queries = [
        "What is the current risk level for container ships transiting the Strait of Hormuz?",
        "Assess the maritime risk in the Red Sea and Bab el-Mandeb strait for LNG tankers.",
        "What is the impact of current geopolitical tensions on the Taiwan Strait shipping route?",
    ]

    for i, query in enumerate(test_queries):
        print(f"\n{'─' * 60}")
        print(f"🔍 Query {i + 1}: {query}")
        print(f"{'─' * 60}")

        result = app.invoke({
            "query": query,
            "assessment": None,
            "error": None,
        })

        if result.get("error"):
            print(f"  ❌ Error: {result['error']}")
            continue

        assessment = result["assessment"]
        risk = assessment["risk_level"]

        # Color-code risk level
        if risk >= 75:
            risk_icon = "🔴"
            risk_label = "HIGH"
        elif risk >= 50:
            risk_icon = "🟡"
            risk_label = "MEDIUM"
        else:
            risk_icon = "🟢"
            risk_label = "LOW"

        print(f"\n  {risk_icon} Risk Level: {risk}/100 ({risk_label})")
        print(f"  📍 Region: {assessment['region']}")
        print(f"  🚨 HITL Required: {'YES' if assessment['requires_human_review'] else 'No'}")

        print(f"\n  📝 Summary:")
        print(f"     {assessment['summary']}")

        print(f"\n  ⚠️ Key Risk Factors:")
        for factor in assessment["key_factors"]:
            print(f"     • {factor}")

        print(f"\n  🗺️  Affected Chokepoints:")
        for cp in assessment["affected_chokepoints"]:
            print(f"     • {cp}")

        print(f"\n  ✅ Recommended Actions:")
        for action in assessment["recommended_actions"]:
            print(f"     • {action}")

    # ── Validate Pydantic Schema ──
    print(f"\n{'=' * 60}")
    print(f"📋 Schema Validation")
    print(f"{'=' * 60}")
    last_assessment = result["assessment"]
    try:
        validated = MaritimeRiskAssessment(**last_assessment)
        print(f"  ✅ Pydantic validation passed")
        print(f"  Fields: {list(validated.model_fields.keys())}")
        print(f"  risk_level type: {type(validated.risk_level).__name__} (constrained 0-100)")
    except Exception as e:
        print(f"  ❌ Validation failed: {e}")

    print(f"\n{'=' * 60}")
    print(f"✅ POC 4 complete — LangGraph agent with structured Pydantic output")
    print(f"   This proves: LangGraph orchestration, structured LLM output, risk assessment")
    print(f"   Next: Add MCP tools, RAG retrieval from ChromaDB, multi-agent supervisor")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
