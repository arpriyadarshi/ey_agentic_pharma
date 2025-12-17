# EY_Pharma_Agent

graph TD
    %% Styling
    classDef ui fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef orch fill:#fff9c4,stroke:#fbc02d,stroke-width:2px;
    classDef agent fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;
    classDef data fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,stroke-dasharray: 5 5;

    %% Layer 1: User Interface
    User([👤 User / Pharma Planner]) -->|Enters Strategic Query| UI[💻 Streamlit Interface]
    UI -->|API Key & Query| MA_Node

    %% Layer 2: Orchestration Layer (LangGraph)
    subgraph Orchestrator ["🧠 Master Orchestrator (LangGraph)"]
        MA_Node[Master Agent Controller]
        Planner[📝 Planner LLM<br/>(Generates JSON Plan)]
        Synthesizer[📄 Report Synthesizer<br/>(Markdown Report)]
    end

    MA_Node -->|1. Generate Plan| Planner
    Planner -->|2. Delegate Tasks| Router{Task Router}

    %% Layer 3: Worker Agents
    subgraph Worker_Layer ["👷 Specialized Worker Agents"]
        CT_Agent[💊 ClinicalTrials Agent]
        IQ_Agent[📊 IQVIA Insights Agent]
        PL_Agent[⚖️ Patent Landscape Agent]
        EX_Agent[🌍 EXIM Trends Agent]
        WI_Agent[🌐 Web Intelligence Agent]
        IK_Agent[📂 Internal Knowledge Agent]
    end

    Router -->|Fetch Trials| CT_Agent
    Router -->|Market Data| IQ_Agent
    Router -->|Check IP| PL_Agent
    Router -->|Trade Data| EX_Agent
    Router -->|News/Guidelines| WI_Agent
    Router -->|Strategy Docs| IK_Agent

    %% Layer 4: Data & External APIs
    subgraph Data_Layer ["💽 Data Sources & APIs"]
        CT_API[(ClinicalTrials.gov API)]
        IQ_Mock[(IQVIA Simulator)]
        Pat_Search[(Google Patents / Mock)]
        EX_Mock[(EXIM Simulator)]
        DDG[(DuckDuckGo Search)]
        RAG[(FAISS Vector DB<br/>Internal PDFs)]
    end

    CT_Agent <--> CT_API
    IQ_Agent <--> IQ_Mock
    PL_Agent <--> Pat_Search
    EX_Agent <--> EX_Mock
    WI_Agent <--> DDG
    IK_Agent <--> RAG

    %% Return Flow
    CT_Agent & IQ_Agent & PL_Agent & EX_Agent & WI_Agent & IK_Agent -->|3. Return Data| MA_Node
    MA_Node -->|4. Synthesize Findings| Synthesizer
    Synthesizer -->|5. Final Strategy Report| UI

    %% Apply Styles
    class UI ui;
    class MA_Node,Planner,Synthesizer,Router orch;
    class CT_Agent,IQ_Agent,PL_Agent,EX_Agent,WI_Agent,IK_Agent agent;
    class CT_API,IQ_Mock,Pat_Search,EX_Mock,DDG,RAG data;
