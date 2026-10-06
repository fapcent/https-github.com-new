import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import AzureOpenAI
from dotenv import load_dotenv

# 1. Charge les clés secrètes depuis le fichier .env
load_dotenv()

# 2. Initialise l'API FastAPI
app = FastAPI(title="Generix Multi-Tenant AI Agent")

# 3. Configure la connexion à ton Azure Foundry (Suède)
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

# 4. Définit le format de la requête attendue
class ChatRequest(BaseModel):
    query: str
    tenant_id: str

# 5. La logique "Multi-Tenant" (3 publics = 3 comportements)
def get_system_prompt_for_tenant(tenant_id: str) -> str:
    prompts = {
        "tenant-a": "Tu es un expert Supply Chain. Parle en termes de ROI, d'optimisation des flux et de rentabilité.",
        "tenant-b": "Tu es un assistant pour les opérateurs d'entrepôt. Fais des réponses courtes, directes, axées sur la sécurité et la logistique terrain.",
        "admin": "Tu es un ingénieur DevOps/Cyber. Fournis des réponses très techniques sur l'infrastructure Cloud et Kubernetes."
    }
    return prompts.get(tenant_id, "Tu es un assistant IA standard.")

# 6. La route de l'API pour discuter avec l'agent
@app.post("/chat")
async def chat_with_agent(request: ChatRequest):
    try:
        # Récupère le prompt adapté au client
        system_prompt = get_system_prompt_for_tenant(request.tenant_id)

        # Envoie la question à GPT-4o sur Azure
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.query}
            ],
            temperature=0.7
        )
        
        return {
            "tenant": request.tenant_id,
            "reply": response.choices[0].message.content
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))