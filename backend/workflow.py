from langgraph.graph import StateGraph, END
from typing import TypedDict
from .master_agent import generate_master_plan
from .worker_agents import AGENT_MAP
from .rag_engine import rag_system
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import json

class GraphState(TypedDict):
    user_query: str
    master_plan: dict
    agent_outputs: dict
    final_report: str
    api_key: str

def plan_step(state: GraphState):
    print("--- ORCHESTRATOR: Generating Plan ---")
    plan = generate_master_plan(state["user_query"], state["api_key"])
    return {"master_plan": plan.dict()}

def execute_step(state: GraphState):
    print("\n--- ORCHESTRATOR: Executing Agents ---")
    plan = state["master_plan"]
    results = {}
    
    for task in plan["required_agents"]:
        agent_name = task["agent_name"]
        instruction = task["specific_instruction"]
        
        print(f"\n>>> Running {agent_name}")
        print(f"Instruction: {instruction}")

        if agent_name == "InternalKnowledgeAgent":
            output = rag_system.query(instruction)

        elif agent_name in AGENT_MAP:
            try:
                output = AGENT_MAP[agent_name].invoke({
                    "instruction": instruction,
                    "molecule": plan["molecule"],
                    "indication": plan["indication"],
                    "therapeutic_area": plan["therapeutic_area"]
                })
            except Exception as e:
                output = f"Error executing {agent_name}: {e}"

        else:
            output = "Error: Agent not found."

        # 🔥 PRINT AGENT OUTPUT HERE
        print(f"\n--- OUTPUT FROM {agent_name} ---")
        print(output)
        print("-" * 80)

        results[agent_name] = output
        
    return {"agent_outputs": results}


def synthesize_step(state: GraphState):
    print("--- ORCHESTRATOR: Synthesizing Report ---")
    
    llm = ChatOpenAI(
        model="gpt-4o-mini", 
        api_key=state["api_key"],
        temperature=0.3
    )
    
    summary_prompt = f"""
    You are a Pharmaceutical Strategy Consultant.
    User Query: "{state['user_query']}"
    
    Data Gathered from Agents:
    {json.dumps(state['agent_outputs'], indent=2)}
    
    Task:
    Write a "Strategic Innovation Story" report (Markdown).
    
    Structure:
    1. **Executive Summary**: Feasibility snapshot.
    2. **Clinical Landscape**: Competitors and trial status.
    3. **IP & Legal**: Patent expiry and FTO risks.
    4. **Commercial Viability**: Market size and trends.
    5. **Supply Chain**: API sourcing risks.
    6. **Recommendation**: Clear Go/No-Go decision.
    """
    
    response = llm.invoke([HumanMessage(content=summary_prompt)])
    return {"final_report": response.content}

def build_pharma_graph():
    workflow = StateGraph(GraphState)
    workflow.add_node("Planner", plan_step)
    workflow.add_node("Executor", execute_step)
    workflow.add_node("Synthesizer", synthesize_step)
    workflow.set_entry_point("Planner")
    workflow.add_edge("Planner", "Executor")
    workflow.add_edge("Executor", "Synthesizer")
    workflow.add_edge("Synthesizer", END)
    return workflow.compile()
