import json
from query_loki import query_logs, build_grafana_link

# Carrega os dados das aplicações
with open("data.json") as f:
    apps = json.load(f)

# Mapeia palavras-chave comuns da pergunta para campos do JSON
intent_map = {
    "dns": "dns",
    "porta": "porta",
    "responsável": "responsavel",
    "responsavel": "responsavel",
    "application name": "application_name",
    "nome da aplicação": "application_name",
    "healthcheck": "url_healthcheck",
    "endpoint de status": "url_healthcheck"
}

def process_question(pergunta: str):
    pergunta = pergunta.lower()

    for app in apps:
        # Verifica se todos os termos do nome_fantasia estão na pergunta
        if all(p in pergunta for p in app["nome_fantasia"].lower().split()):
            # Procura por intenção (ex: dns, porta, etc.)
            for palavra, campo in intent_map.items():
                if palavra in pergunta:
                    valor = app.get(campo)
                    return {campo: valor}

            # Se nenhuma intenção for reconhecida, retorna logs e link
            application = app.get("application_name")
            logs = query_logs(application)
            link = build_grafana_link(application)
            return {
                "application_name": application,
                "logs": logs,
                "grafana_link": link
            }

    return {"erro": "Aplicação não encontrada"}
