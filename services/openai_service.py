import asyncio
import logging

from openai import AsyncOpenAI

logger = logging.getLogger("ra_translate.openai")


class OpenAIService:
    def __init__(self, api_key: str, model: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def _ask(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
        try:
            response = await asyncio.wait_for(
                self.client.responses.create(
                    model=self.model,
                    input=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=temperature,
                ),
                timeout=30,
            )
            text = getattr(response, "output_text", "").strip()
            if not text:
                return "Não consegui gerar uma resposta agora. Tente novamente."
            return text
        except asyncio.TimeoutError:
            return "A IA demorou demais para responder. Tente novamente em instantes."
        except Exception as exc:
            logger.exception("Erro OpenAI: %s", exc)
            return "A IA está indisponível no momento. Tente novamente em instantes."

    async def translate_private(self, text: str) -> str:
        system = (
            "Você é um assistente de tradução para estudantes de inglês.\n"
            "Analise o texto enviado e responda no formato EXATO abaixo:\n\n"
            "Inglês: <frase original em inglês enviada pelo usuário>\n"
            "Português: <tradução natural em português do Brasil>\n"
            "Natural: <versão corrigida e mais natural em inglês, apenas se necessário; se já estiver boa, repita a frase original>\n\n"
            "Regras:\n"
            "- Se o usuário enviar uma frase em inglês, traduza para português.\n"
            "- Se a frase estiver com erros, mantenha em 'Inglês' exatamente como o usuário escreveu.\n"
            "- Em 'Português', mostre a tradução correta em português.\n"
            "- Em 'Natural', mostre a frase em inglês corrigida e natural.\n"
            "- Não use 'Original'.\n"
            "- Não use 'English'.\n"
            "- Não explique nada fora desse formato.\n"
        )
        return await self._ask(system, text)

    async def translate_public(self, text: str) -> str:
        system = (
            "Você é um tradutor para Discord.\n"
            "Se o texto estiver em português, traduza para inglês.\n"
            "Se o texto estiver em inglês, corrija e deixe natural em inglês.\n"
            "Responda apenas com a frase final, sem aspas e sem explicações."
        )
        return await self._ask(system, text)

    async def correct_english(self, text: str) -> str:
        system = (
            "Você é um professor de inglês. Corrija a frase do usuário e explique em português de forma breve. "
            "Formato:\n"
            "Sua frase: ...\n"
            "Forma corrigida: ...\n"
            "Explicação: ..."
        )
        return await self._ask(system, text)

    async def explain_text(self, text: str) -> str:
        system = (
            "Explique a frase enviada de forma didática e curta em português. "
            "Mostre:\n"
            "Inglês: ...\n"
            "Estrutura: ...\n"
            "Vocabulário: ...\n"
            "Resumo: ..."
        )
        return await self._ask(system, text)

    async def chat_en(self, text: str) -> str:
        system = (
            "Você conversa em inglês com um estudante. Responda em inglês, de forma clara, curta e natural. "
            "Se a frase dele tiver erro claro, corrija discretamente antes da resposta usando este formato:\n"
            "Correction: ...\n"
            "Reply: ..."
        )
        return await self._ask(system, text, temperature=0.6)

    async def chat_pt(self, text: str) -> str:
        system = (
            "Você é um professor de inglês que ensina em português do Brasil. "
            "Explique de forma simples, clara e objetiva, sem textos longos."
        )
        return await self._ask(system, text, temperature=0.4)

    async def training(self, mode: str) -> str:
        system = (
            "Crie um mini exercício de inglês curto e interativo em português. "
            "Tema enviado pelo usuário. Gere algo útil, amigável e direto. "
            "Inclua no máximo 1 exercício por resposta."
        )
        return await self._ask(system, mode, temperature=0.7)
