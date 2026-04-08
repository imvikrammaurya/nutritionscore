# NutritionScore AI 🍎
**A Multi-Agent AI system for real-time nutritional analysis and HSR validation.**

[![Live Demo](https://img.shields.io/badge/Demo-Live_on_Cloud_Run-blue)](https://nutritionscore-frontend-400760560700.asia-south1.run.app/)

### 🎯 The Mission
Nutrition labels are confusing. NutritionScore AI uses specialized AI agents to translate complex chemical names and percentages into a simple, government-standard **Health Star Rating (HSR)** and a school-ready **Traffic Light** score.

### ✨ Key Features
- **Dual Capture Hub:** Optimized for mobile with direct camera access or gallery uploads.
- **2026 HSR Algorithm:** Built-in logic for the latest Australian Health Star Rating standards.
- **Multi-Agent Orchestration:** Separate agents for Vision Extraction and Nutritional Scoring to ensure high accuracy.
- **Intelligent Benchmarking:** Uses AlloyDB vector search to compare products against a global health database.

### 🛠️ Technical Architecture


1. **Frontend:** Next.js (React) deployed on Cloud Run.
2. **Orchestration:** Python-based Multi-Agent framework using **Vertex AI (Gemini 3.1 Flash)**.
3. **Database:** **AlloyDB** for high-performance storage and **pg_vector** for similarity search.
4. **Networking:** Secured via **Private Service Connect (PSC)** and **VPC Connectors**.

### ⚙️ Environment Setup
To run the backend locally, ensure you have these variables in your `.env`:
`ALLOYDB_IP`, `ALLOYDB_PASSWORD`, `GCS_BUCKET_NAME`, `GCP_PROJECT_ID`

---
*Built for the 2026 Google Cloud AI Hackathon.*
