import asyncio
import os
import logging
from dotenv import load_dotenv
from src.agents.inspector import InspectorLaboral

# Load environment variables
load_dotenv()

# Setup minimal logging to see what's happening
logging.basicConfig(level=logging.INFO)

async def test_agent_loop():
    print("🚀 Initializing Inspector Laboral Agent...")
    agent = InspectorLaboral()
    
    context = "Denuncia por falta de protectores auditivos en la zona de prensas de la fábrica de componentes automotrices."
    print(f"\n📝 Contexto: {context}")
    
    try:
        print("\n⏳ Ejecutando flujo completo (Draft -> Perplexity -> Refinement)...")
        result = await agent.generate_structured_draft_verified(context)
        
        print("\n✅ Flujo completado con éxito.")
        print(f"📌 Resumen: {result.get('summary')}")
        print(f"⚖️ Estado Verificación: {result.get('verification_status')}")
        print("-" * 50)
        print("📄 Contenido Refinado (Primeras 300 caracteres):")
        print(result.get('content', '')[:300] + "...")
        print("-" * 50)
        
    except Exception as e:
        print(f"\n❌ Error en el flujo del agente: {e}")

if __name__ == "__main__":
    asyncio.run(test_agent_loop())
