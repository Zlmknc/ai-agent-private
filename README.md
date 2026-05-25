# ai-agent-private
First aiAgent project
We gonna try to build our first ai agent project

1. Download and install docker first
2. Start to buil docker for ai agent container system
in powershell  
  2.1
   docker --version
   docker compose version     both give you version then
   mkdir C:\ai-agent
   mkdir C:\ai-agent\models
   mkdir C:\ai-agent\chroma-data
   mkdir C:\ai-agent\agent-data
   mkdir C:\ai-agent\logs
   mkdir C:\ai-agent\agent

   2.2 create your .yml file but for now it will be empty
   docker-compose.yml

   2.3
   cd C:\ai-agent
   docker compose up -d
   after these steps in your docker desktop, three container will be green

   2.4
   upload first model - upload with internet and later you can use them offline
   Llama 3.2 (3B, ~2GB — hızlı başlangıç için iyi)
   docker exec ollama ollama pull llama3.2
    
   Embedding modeli (RAG için gerekecek)
   docker exec ollama ollama pull nomic-embed-text
    
   
   
