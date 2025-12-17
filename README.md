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
