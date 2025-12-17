# EY_Pharma_Agent
```mermaid
graph LR
    %% Styling
    classDef ui fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000;
    classDef orch fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    classDef agent fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
    classDef data fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,stroke-dasharray: 5 5,color:#000;

    %% Layer 1: User Interface
    User([👤 User]) -->|Strategic Query| UI[💻 Streamlit UI]
    UI -->|API Key & Query| MA_Node

    %% Layer 2: Orchestration
    subgraph Orchestrator ["🧠 Master Orchestrator"]
        MA_Node[Master Agent]
        Planner[📝 Planner]
        Synthesizer[📄 Report Gen]
    end

    MA_Node --> Planner
    Planner --> Router{Task Router}

    %% Layer 3: Worker Agents
    subgraph Workers ["👷 Worker Agents"]
        direction TB
        CT_Agent[💊 ClinicalTrials]
        IQ_Agent[📊 IQVIA Market]
        PL_Agent[⚖️ Patent/IP]
        EX_Agent[🌍 EXIM Trade]
        WI_Agent[🌐 Web Intel]
        IK_Agent[📂 Internal RAG]
    end

    Router --> CT_Agent & IQ_Agent & PL_Agent & EX_Agent & WI_Agent & IK_Agent

    %% Layer 4: Data Sources
    subgraph Data ["💽 Data Sources"]
        CT_API[(ClinicalTrials.gov)]
        IQ_Mock[(IQVIA Sim)]
        Pat_Search[(Google Patents)]
        EX_Mock[(EXIM Sim)]
        DDG[(DuckDuckGo)]
        RAG[(Internal PDFs)]
    end

    CT_Agent <--> CT_API
    IQ_Agent <--> IQ_Mock
    PL_Agent <--> Pat_Search
    EX_Agent <--> EX_Mock
    WI_Agent <--> DDG
    IK_Agent <--> RAG

    %% Return Flow
    CT_Agent & IQ_Agent & PL_Agent & EX_Agent & WI_Agent & IK_Agent --> MA_Node
    MA_Node --> Synthesizer
    Synthesizer -->|Markdown Report| UI

    %% Apply Styles
    class UI ui;
    class MA_Node,Planner,Synthesizer,Router orch;
    class CT_Agent,IQ_Agent,PL_Agent,EX_Agent,WI_Agent,IK_Agent agent;
    class CT_API,IQ_Mock,Pat_Search,EX_Mock,DDG,RAG data;
```

flowchart TD
    %% --- STYLING ---
    classDef startend fill:#212121,stroke:#000,stroke-width:2px,color:#fff;
    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef decision fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#000;
    classDef agent fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
    classDef fallback fill:#ffcdd2,stroke:#c62828,stroke-width:2px,stroke-dasharray: 5 5,color:#000;
    classDef artifact fill:#f3e5f5,stroke:#7b1fa2,stroke-width:1px,stroke-dasharray: 2 2,color:#000;

    %% --- 1. SETUP & INPUT ---
    Start([🚀 Start App]) --> Secrets{Check Secrets}
    Secrets -- Missing --> Error([❌ Stop: Show Error])
    Secrets -- Found --> EnvVars[Set os.environ OPENAI_API_KEY]
    
    EnvVars --> CheckPDF{PDF in /data?}
    CheckPDF -- Yes --> RAGLoad[⚙️ RAG: Ingest & Embed to FAISS]
    CheckPDF -- No --> SkipRAG[Skip Internal Knowledge]
    
    RAGLoad & SkipRAG --> UserInput[/👤 User Query/]

    %% --- 2. PLANNER NODE ---
    UserInput --> Planner[🧠 Planner Node<br/>(gpt-4o-mini)]
    Planner -->|Generate| JSONPlan[📋 MasterPlan JSON]

    %% --- 3. EXECUTOR NODE (Parallel Execution) ---
    JSONPlan --> Router{Iterate 'required_agents'}
    
    subgraph Execution_Logic ["⚡ Worker Agent Execution"]
        direction TB
        
        %% CLINICAL TRIALS
        Router -->|'ClinicalTrialsAgent'| CT_Call[💊 ClinicalTrials Agent]
        CT_Call --> CT_API{ClinicalTrials.gov API}
        CT_API -- Success --> CT_Res[✅ Real Data]
        CT_API -- Fail/404 --> CT_Err[⚠️ Return Error String]

        %% IQVIA (Simulated)
        Router -->|'IQVIAInsightsAgent'| IQ_Call[📊 IQVIA Agent]
        IQ_Call --> IQ_Sim[🎲 Run Market Simulator<br/>(Mock Data)]
        IQ_Sim --> IQ_Res[✅ Market Sizing/CAGR]

        %% EXIM (Simulated)
        Router -->|'EXIMTrendsAgent'| EX_Call[🌍 EXIM Agent]
        EX_Call --> EX_Sim[🎲 Run Trade Simulator<br/>(Mock Data)]
        EX_Sim --> EX_Res[✅ Supply Chain Risk]

        %% PATENT (Hybrid)
        Router -->|'PatentLandscapeAgent'| PL_Call[⚖️ Patent Agent]
        PL_Call --> PL_Check{Search Tool?}
        PL_Check -- Yes --> PL_Search[🦆 DuckDuckGo Search]
        PL_Check -- No --> PL_Fall[🎲 Fallback Simulation]
        PL_Search & PL_Fall --> PL_Res[✅ IP/FTO Data]

        %% WEB INTEL (Hybrid)
        Router -->|'WebIntelligenceAgent'| WI_Call[🌐 Web Intel Agent]
        WI_Call --> WI_Try[🦆 DuckDuckGo Search]
        WI_Try -- Success --> WI_Real[✅ Live Results]
        WI_Try -- Fail/Block --> WI_Proxy[🔄 Simulated Proxy Response]
        WI_Proxy --> WI_Res[✅ Fallback News]

        %% RAG AGENT
        Router -->|'InternalKnowledgeAgent'| IK_Call[📂 Internal Knowledge]
        IK_Call --> IK_Query[🔍 Query Vector DB]
        IK_Query --> IK_Res[✅ Retrieved Context]
    end

    %% --- 4. SYNTHESIZER NODE ---
    CT_Res & CT_Err & IQ_Res & EX_Res & PL_Res & WI_Res & WI_Proxy & IK_Res --> Aggregator(📥 Collect Outputs)
    
    Aggregator --> Synthesizer[📝 Synthesizer Node<br/>(gpt-4o-mini)]
    Synthesizer -->|Format| Report[📄 Strategic Innovation Story<br/>(Markdown)]

    %% --- 5. OUTPUT ---
    Report --> UI_Display[💻 Streamlit Display]
    UI_Display --> Download[/📥 Download Report/]
    Download --> End([🏁 End])

    %% --- APPLY STYLES ---
    class Start,End,UserInput,Download,Error startend;
    class EnvVars,RAGLoad,SkipRAG,Planner,Synthesizer,Aggregator,UI_Display process;
    class Secrets,CheckPDF,Router,CT_API,PL_Check,WI_Try decision;
    class CT_Call,IQ_Call,EX_Call,PL_Call,WI_Call,IK_Call agent;
    class IQ_Sim,EX_Sim,PL_Fall,WI_Proxy,CT_Err fallback;
    class JSONPlan,Report artifact;
