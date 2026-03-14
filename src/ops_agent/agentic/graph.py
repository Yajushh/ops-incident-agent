"""LangGraph workflow definition.

Chapter 1: Minimal linear graph
  collect_metrics -> generate_action_plan -> END

Future chapters will add:
  - Routing/branching nodes
  - Human-in-the-loop nodes
  - Retry logic
  - Error handling
"""

from langgraph.graph import END, StateGraph

from ops_agent.agentic.nodes import collect_metrics_node, generate_action_plan_node
from ops_agent.agentic.state import RunState
from ops_agent.agentic.tools.contracts import MetricsClient


def create_workflow_graph(metrics_client: MetricsClient) -> StateGraph:
    """Create the LangGraph workflow.

    Args:
        metrics_client: Metrics client implementation (real or fake)

    Returns:
        Compiled StateGraph ready for execution
    """
    # Create graph
    workflow = StateGraph(RunState)

    # Add nodes
    workflow.add_node(
        "collect_metrics",
        lambda state: collect_metrics_node(state, metrics_client),
    )
    workflow.add_node("generate_action_plan", generate_action_plan_node)

    # Define edges (linear flow for Chapter 1)
    workflow.set_entry_point("collect_metrics")
    workflow.add_edge("collect_metrics", "generate_action_plan")
    workflow.add_edge("generate_action_plan", END)

    # Compile graph
    return workflow.compile()

