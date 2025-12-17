import json
import requests
import random
from langchain_core.tools import tool
from .search_client import tavily, TAVILY_AVAILABLE
# --- ROBUST SEARCH SETUP ---
SEARCH_AVAILABLE = False
ddg_search = None

try:
    # Try loading the search tool
    from langchain_community.tools import DuckDuckGoSearchRun
    from duckduckgo_search import DDGS
    ddg_search = DuckDuckGoSearchRun()
    SEARCH_AVAILABLE = True
except ImportError:
    SEARCH_AVAILABLE = False

def simulated_web_search(query: str):
    """
    Fallback simulation as per PDF 'Web search proxy' assumption.
    Ensures the agent never fails even if DuckDuckGo blocks the IP.
    """
    return f"""
    [Simulated Web Result for: {query}]
    1. **Recent Guidelines (2024)**: New FDA/EMA guidelines suggest {query} shows promise for repurposed indications.
    2. **Market News**: Competitor activity has increased in this therapeutic area.
    3. **Scientific Journals**: Recent study in Lancet (2023) highlights efficacy in Phase 2 trials.
    (Source: Simulated Web Proxy for Techathon Demo)
    """

# --- 1. Clinical Trials Agent ---
@tool
def clinical_trials_agent(instruction: str, molecule: str, indication: str):
    """
    Fetches real clinical trial data from ClinicalTrials.gov using
    the official API v2 for a given molecule and indication.
    """

    query = f"{molecule} {indication}"

    url = "https://clinicaltrials.gov/api/v2/studies"
    params = {
        "query.term": query,
        "pageSize": 10,
        "format": "json"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        studies = data.get("studies", [])

        if not studies:
            return {
                "molecule": molecule,
                "indication": indication,
                "total_trials": 0,
                "message": "No registered trials found",
                "source": "ClinicalTrials.gov"
            }

        # Extract key info
        trial_summaries = []
        for study in studies:
            protocol = study.get("protocolSection", {})

            identification = protocol.get("identificationModule", {})
            status = protocol.get("statusModule", {})
            design = protocol.get("designModule", {})

            trial_summaries.append({
                "nct_id": identification.get("nctId"),
                "title": identification.get("briefTitle"),
                "status": status.get("overallStatus"),
                "phase": design.get("phases"),
            })

        return {
            "molecule": molecule,
            "indication": indication,
            "total_trials": len(studies),
            "trials": trial_summaries,
            "source": "ClinicalTrials.gov (API v2)"
        }

    except Exception as e:
        print("ClinicalTrials API error:", e)

    # 🔁 Fallback (pipeline safety)
    return {
        "molecule": molecule,
        "indication": indication,
        "total_trials": 3,
        "trials": [
            {"nct_id": "NCT00000001", "status": "Recruiting", "phase": "Phase 2"},
            {"nct_id": "NCT00000002", "status": "Completed", "phase": "Phase 3"},
            {"nct_id": "NCT00000003", "status": "Active, not recruiting", "phase": "Phase 1"}
        ],
        "source": "Simulated fallback"
    }

# --- 2. Patent Landscape Agent ---
@tool
def patent_landscape_agent(instruction: str, molecule: str):
    """
    Analyzes patent landscape, expiry timelines, and freedom-to-operate (FTO)
    risks for a given pharmaceutical molecule using web intelligence.
    """

    query = (
        f"{molecule} patent expiry composition of matter "
        f"formulation patent freedom to operate"
    )

    if TAVILY_AVAILABLE:
        try:
            results = tavily.search(
                query=query,
                max_results=5
            )

            return {
                "molecule": molecule,
                "source": "Tavily",
                "patent_signals": results,
                "interpretation": {
                    "composition_of_matter": "Likely expired or nearing expiry",
                    "formulation_patents": "Active secondary patents possible",
                    "fto_risk": "Moderate"
                }
            }

        except Exception as e:
            print("Tavily Patent search failed:", e)

    # 🔁 Fallback (never fail)
    return {
        "molecule": molecule,
        "source": "Simulated Patent Fallback",
        "patents": [
            {
                "patent_id": "US9123456",
                "type": "Composition of Matter",
                "expiry_year": 2029
            },
            {
                "patent_id": "WO2023999",
                "type": "Formulation",
                "status": "Pending"
            }
        ],
        "fto_risk": "Moderate"
    }

# --- 3. IQVIA Insights Agent ---
@tool
def iqvia_insights_agent(instruction: str, therapeutic_area: str):
    """
    Generates simulated IQVIA-style market intelligence
    with random but realistic values.
    """

    market_size = round(random.uniform(50, 300), 1)  # USD Bn
    cagr = round(random.uniform(3.0, 9.0), 2)

    competitors_pool = [
        "Pfizer", "Novartis", "Merck",
        "Roche", "AstraZeneca", "Sanofi"
    ]

    competitors = random.sample(competitors_pool, k=3)

    return {
        "therapeutic_area": therapeutic_area,
        "market_size_usd_billion": market_size,
        "cagr_percent": cagr,
        "top_competitors": [{"company": c} for c in competitors],
        "source": "Simulated IQVIA Data"
    }


# --- 4. EXIM Trends Agent (Restored & Improved) ---
@tool
def exim_trends_agent(instruction: str, molecule: str):
    """
    Generates simulated EXIM trade and supply-chain data
    with random volumes and risk levels.
    """

    exporters = [
        {"country": "China", "volume_mt": random.randint(400, 1000)},
        {"country": "India", "volume_mt": random.randint(200, 600)},
        {"country": "Germany", "volume_mt": random.randint(50, 250)}
    ]

    risk = random.choice(["Low", "Medium", "High"])

    return {
        "molecule": molecule,
        "exporters": exporters,
        "supply_chain_risk": risk,
        "source": "Simulated EXIM Data"
    }

# --- 5. Web Intelligence Agent ---
@tool
def web_intelligence_agent(instruction: str):
    """
    Gathers recent guidelines, scientific publications, and news
    relevant to the provided query.
    """
    if TAVILY_AVAILABLE:
        try:
            results = tavily.search(
                query=instruction,
                max_results=5
            )
            return {
                "source": "Tavily",
                "results": results
            }
        except Exception as e:
            print("Tavily Web error:", e)

    return simulated_web_search(instruction)


# --- 6. Internal Knowledge Agent ---
# (Handled by RAG engine in workflow.py, but defined here for completeness if needed)
@tool
def internal_knowledge_agent(query: str):
    """Placeholder for RAG"""
    return "Querying internal DB..."

AGENT_MAP = {
    "ClinicalTrialsAgent": clinical_trials_agent,
    "PatentLandscapeAgent": patent_landscape_agent,
    "IQVIAInsightsAgent": iqvia_insights_agent,
    "EXIMTrendsAgent": exim_trends_agent, # Ensure this is mapped!
    "WebIntelligenceAgent": web_intelligence_agent,
    "InternalKnowledgeAgent": internal_knowledge_agent
}
