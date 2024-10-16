import boto3
import json
import os
import boto3.exceptions
class AnswersFacade():
    """
    Uma classe para gerenciar respostas usando diversos métodos de processamento de linguagem natural via AWS Bedrock.

    Atributos:
    -----------
    answers : str
        Resposta padrão para perguntas não respondidas.
    pergunta : str
        Texto da pergunta a ser processada.

    Métodos:
    --------
    get_answer_by_flow()
        Obtém a resposta utilizando um fluxo predefinido na AWS Bedrock.

    get_answer_llm()
        Obtém a resposta utilizando um modelo de linguagem de grande escala na AWS Bedrock.

    get_answers_base_conhecimento()
        Obtém a resposta consultando uma base de conhecimento configurada na AWS Bedrock.
    """

    def __init__(self, texto):
        """
        Inicializa a classe AnswersFacade com o texto da pergunta.

        Parâmetros:
        -----------
        texto : str
            O texto da pergunta a ser processada.
        """
        self.answers = "Não consigo responder a essa questão."
        self.pergunta = texto

    def get_answer_by_flow(self):
        """
        Obtém a resposta utilizando um fluxo predefinido na AWS Bedrock.

        Retorna:
        --------
        str
            A resposta obtida do fluxo configurado na AWS Bedrock.
        """
        bedrock = boto3.client(service_name="bedrock-agent-runtime")
        res = bedrock.invoke_flow(
            flowAliasIdentifier=os.environ.get("FLOW_ALIAS_ID"),
            flowIdentifier=os.environ.get("FLOW_ID"),
            inputs=[
                {
                    "content": {"document": str(self.pergunta)},
                    "nodeName": "FlowInputNode",
                    "nodeOutputName": "document"
                }
            ]
        )
        try:
            result = {}
            for event in res.get("responseStream"):
                result.update(event)
        except:
            pass
        self.answers = result['flowOutputEvent']['content']['document']
        bedrock.close()
        return self.answers

    def get_answer_llm(self):
        """
        Obtém a resposta utilizando um modelo de linguagem de grande escala na AWS Bedrock.

        Retorna:
        --------
        str
            A resposta obtida do modelo de linguagem configurado na AWS Bedrock.
        """
        bedrock = boto3.client(service_name="bedrock-runtime")
        body = json.dumps({
            "max_tokens": 256,
            "messages": [{"role": "user", "content": str(self.pergunta)}],
            "anthropic_version": "bedrock-2023-05-31"
        })
        response = bedrock.invoke_model(body=body, modelId=os.environ.get("MODEL_ID"))
        response_body = json.loads(response.get("body").read())
        resposta = response_body.get("content")[0]['text']
        self.answers = str(resposta)
        return self.answers

    def get_answers_base_conhecimento(self):
        """
        Obtém a resposta consultando uma base de conhecimento configurada na AWS Bedrock.

        Retorna:
        --------
        str
            A resposta gerada a partir da base de conhecimento configurada na AWS Bedrock.
        """
        bedrock = boto3.client(service_name="bedrock-agent-runtime")
        res = bedrock.retrieve_and_generate(
            input={"text": str(self.pergunta)},
            retrieveAndGenerateConfiguration={
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": os.environ.get("KNOWLEDGE_BASE_ID"),
                    "modelArn": os.environ.get("MODEL_ID"),
                    "retrievalConfiguration": {
                        "vectorSearchConfiguration": {
                            "overrideSearchType": "SEMANTIC"
                        }
                    },
                    "generationConfiguration": {
                        "guardrailConfiguration": {
                            'guardrailId': os.environ.get("GUARD_RAIL_ID"),
                            'guardrailVersion': os.environ.get("GUARD_RAIL_VERSION")
                        },
                        "inferenceConfig": {
                            "textInferenceConfig": {
                                "temperature": float(os.environ.get("TEMPERATURE")),
                                "topP": float(os.environ.get("TOP_P"))
                            }
                        },
                        "additionalModelRequestFields": {
                            "top_k": int(os.environ.get("TOP_K"))
                        },
                        "promptTemplate": {
                            "textPromptTemplate": "Você é um atendente da CCEE e deve apresentar respostas que estejam na base de conhecimento; sem juízo, sem abordagem de outro tema diferente de comercialização de energia. A resposta gerada a partir da base de conhecimento é: $search_results$."
                        }
                    }
                },
                "type": "KNOWLEDGE_BASE"
            }
        )
        self.answers = str(res['output']['text'])
        bedrock.close()
        return self.answers
 