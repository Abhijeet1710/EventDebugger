How to Run Agent
uv run python -m ai_app.main 2>/dev/null
PYTHONPATH=src uv run python -m ai_app.main

CLI -  PYTHONPATH=src uv run ai-debug

How to run ingestion-service
cd /Users/abhijeetkhamkar/Desktop/Projects/AI/EventDebugger/ingestion-service
./mvnw spring-boot:run

# ###################

1. [Minor] Validate if the basic filter functionality is working
2. [Major] RCA - Github Integration, RCA, Fix