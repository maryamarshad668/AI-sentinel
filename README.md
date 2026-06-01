AI-Sentinel 
Intelligent Technical Debt & Code Quality Analyzer
 This project is actively under development. Core functionality is complete and has been evaluated in an academic setting. Further improvements to accuracy, UI, and pipeline robustness are in progress.

Overview
AI-Sentinel is an AI-powered system designed to identify and quantify technical debt in software codebases — one of the most costly and underdiagnosed problems in the software industry. Research estimates that developers lose approximately 23% of their productive time navigating poorly structured or suboptimal code.
AI-Sentinel addresses this by combining classical machine learning with large language model reasoning to deliver both risk scores and actionable refactoring suggestions — automatically.

Pipeline
Codebase Input
      ↓
Static Code Analysis
(complexity, duplication, coupling, code smells)
      ↓
XGBoost Risk Predictor
(outputs debt risk score per module/file)
      ↓
Refactoring Engine
(generates human-readable improvement suggestions)
      ↓
Structured Report Output
(flagged files, risk scores, recommendations)



Tech Stack:
Backend: Python, FastAPI
Static Analysis: radon, Python ast
ML Model: XGBoost 
LLM: Ollama + CodeLlama 13B (primary) / DeepSeek-Coder 6.7B (lightweight alternative)
Frontend: Gradio (demo), D3.js (heatmap)
Database: SQLite (dev) / PostgreSQL (production)
CI/CD: GitHub Actions 
Security Data: NIST NVD REST API 

Features
Automated code scanning — analyzes entire codebases for quality issues
Risk scoring — quantifies technical debt per file and module using ML
LLM-powered suggestions — generates specific, actionable refactoring guidance
Structured reporting — outputs findings in a clean, readable format for engineering teams
Industry-oriented — designed for real codebases, not toy examples

Use Cases
Engineering teams managing large or legacy codebases
Code review automation and pre-merge quality checks
Academic and research evaluation of software quality metrics
Developer productivity tooling


