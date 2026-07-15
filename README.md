# **AI-Sentinel**

## **Intelligent Technical Debt & Code Quality Analyzer**

> **🚧 This project is actively under development.**
>
> Core functionality is complete and has been evaluated in an academic setting. Further improvements to accuracy, UI, and pipeline robustness are currently in progress.

---

# **Overview**

**AI-Sentinel** is an AI-powered system designed to identify and quantify **technical debt** in software codebases—one of the most costly and underdiagnosed problems in the software industry.

Research estimates that developers lose approximately **23% of their productive time** navigating poorly structured or suboptimal code.

AI-Sentinel addresses this challenge by combining **classical machine learning** with **large language model (LLM) reasoning** to deliver accurate **risk scores** and **actionable refactoring suggestions** automatically.

---

# **Pipeline**

```text
Codebase Input
      │
      ▼
Static Code Analysis
(complexity, duplication, coupling, code smells)
      │
      ▼
XGBoost Risk Predictor
(outputs debt risk score per module/file)
      │
      ▼
Refactoring Engine
(generates human-readable improvement suggestions)
      │
      ▼
Structured Report Output
(flagged files, risk scores, recommendations)
```

---

# **Tech Stack**

### **Backend**
- Python
- FastAPI

### **Static Analysis**
- Radon
- Python AST

### **Machine Learning**
- XGBoost

### **Large Language Models**
- Ollama
- CodeLlama 13B *(Primary)*
- DeepSeek-Coder 6.7B *(Lightweight Alternative)*

### **Frontend**
- Gradio *(Demo Interface)*
- D3.js *(Risk Heatmap Visualization)*

### **Database**
- SQLite *(Development)*
- PostgreSQL *(Production)*

### **CI/CD**
- GitHub Actions

### **Security Intelligence**
- NIST NVD REST API

---

# **Features**

-  **Automated Code Scanning** — Analyzes entire codebases for quality issues.
-  **Risk Scoring** — Quantifies technical debt for each file and module using machine learning.
-  **LLM-Powered Refactoring Suggestions** — Generates clear, actionable code improvement recommendations.
-  **Structured Reporting** — Produces clean and readable reports for engineering teams.
-  **Industry-Oriented Design** — Built for real-world software projects, not toy examples.

---

# **Use Cases**

- Engineering teams managing large or legacy codebases
- Code review automation and pre-merge quality checks
- Academic research on software quality metrics
- Developer productivity and technical debt management
