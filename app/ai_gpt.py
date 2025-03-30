from openai import AzureOpenAI
import os
from dotenv import load_dotenv
import json
from app.query_loki import query_logs, build_grafana_link

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

with open("data.json") as f:
    apps_data = json.load(f)

def ask_gpt(pergunta: str) -> dict:
    prompt = f"""
Você é uma IA interna. Responda com base neste JSON:
{json.dumps(apps_data, indent=2)}

Pergunta: {pergunta}

Regras:
- Responda de forma direta e objetiva.
- Só retorne os campos estritamente necessários.
- Se a pergunta for sobre logs ou últimos registros, use o campo "application_name" da aplicação correspondente para buscar os logs.
- Nunca diga "com base nos dados fornecidos".
- Se não souber, responda com "Informação não encontrada".
"""

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Você é uma IA interna que responde somente com base nos dados fornecidos."},
                {"role": "user", "content": prompt}
            ],
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            max_tokens=500,
            temperature=0.5
        )

        content = response.choices[0].message.content.strip()

        resposta_formatada = {}

        # primeiro tenta formatar como chave: valor
        linhas = content.splitlines()
        for linha in linhas:
            if ":" in linha:
                chave, valor = linha.split(":", 1)
                resposta_formatada[chave.strip()] = valor.strip()

        # se não encontrou nenhum campo estruturado, assume conteúdo como resposta direta
        if not resposta_formatada:
            resposta_formatada["resposta"] = content

        # verifica se algum application_name conhecido foi citado
        for app in apps_data:
            app_name = app["application_name"]
            if app_name in content:
                logs = query_logs(app_name, limit=5)
                grafana_link = build_grafana_link(app_name)

                resposta_formatada["logs"] = logs or ["Sem logs encontrados."]
                resposta_formatada["grafana_link"] = grafana_link
                break

        return resposta_formatada

    except Exception as e:
        return {"erro": f"Erro na IA (Azure): {str(e)}"}
