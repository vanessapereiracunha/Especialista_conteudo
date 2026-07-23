from __future__ import annotations

from application.validators import extract_json_payload
from domain.configurations import AppConfig
from domain.models import DistributionOutput, EditorialKnowledgeMap, EditorialOutput, ReviewReport, VideoScript
from infrastructure.llm_client import LLMClient
from prompts.prompts import DISTRIBUTION_SYSTEM_PROMPT, build_distribution_prompt
from pydantic import ValidationError


class DistributionAgent:
    def __init__(self, llm_client: LLMClient, config: AppConfig) -> None:
        self.llm_client = llm_client
        self.config = config

    def _quality_issues(self, distribution: DistributionOutput) -> list[str]:
        issues: list[str] = []
        if len(distribution.scripts) != 3:
            issues.append("Retorne exatamente 3 roteiros.")
            return issues

        edu, prov, ugc = distribution.scripts
        hook_edu = (edu.hook or "").lower()
        hook_prov = (prov.hook or "").lower()
        hook_ugc = (ugc.hook or "").lower()
        dev_edu = (edu.development or "").lower()
        dev_prov = (prov.development or "").lower()
        dev_ugc = (ugc.development or "").lower()

        if "pergunta" not in hook_edu or ("três" not in hook_edu and "3" not in hook_edu):
            issues.append("No educacional, use gancho com 3 perguntas.")
        if not all(term in dev_edu for term in ["objetivo", "recurso", "obstá"]):
            issues.append("No educacional, o desenvolvimento deve conter objetivo, recursos e obstáculo.")
        if "precisa" not in hook_prov and "e se" not in hook_prov:
            issues.append("No provocativo, use gancho do tipo 'E se...' ou 'precisa mesmo...'.")
        if not any(term in dev_prov for term in ["desgaste", "recurso", "energia"]):
            issues.append("No provocativo, traga explicitamente desgaste/recursos/energia.")
        if not (hook_ugc.startswith("eu") or "eu " in hook_ugc or "uma coisa" in hook_ugc):
            issues.append("No UGC, use gancho em primeira pessoa com tom de relato real.")
        if "movimento" not in dev_ugc or "progresso" not in dev_ugc:
            issues.append("No UGC, inclua o insight 'movimento não é progresso' (ou equivalente).")
        if not any(term in dev_ugc for term in ["doutrina", "tempo", "terreno", "mando", "disciplina"]):
            issues.append("No UGC, conecte o relato a um princípio concreto (ex.: os cinco fatores).")

        if "salv" not in (edu.platform_rationale or "").lower():
            issues.append("No educacional, a justificativa deve citar salvamento/checklist.")
        if "coment" not in (prov.platform_rationale or "").lower():
            issues.append("No provocativo, a justificativa deve citar comentários/discussão.")
        if "ident" not in (ugc.platform_rationale or "").lower() and "narrat" not in (ugc.platform_rationale or "").lower():
            issues.append("No UGC, a justificativa deve citar identificação/narrativa pessoal.")

        return issues

    def _fallback_distribution(self) -> DistributionOutput:
        return DistributionOutput(
            scripts=[
                VideoScript(
                    approach="educacional",
                    hook="Antes de começar seu próximo projeto, faça estas três perguntas.",
                    development=(
                        "No início da obra, Sun Tzu enfatiza a importância de avaliar as condições antes de agir. Inspirado "
                        "nessa lógica de avaliação, antes de agir, pergunte: qual é o objetivo real, quais recursos você tem "
                        "e qual é o principal obstáculo do contexto. Essa pausa reduz retrabalho e movimento inútil, e te "
                        "ajuda a escolher onde vale gastar energia."
                    ),
                    visual_suggestion=(
                        "Criador falando para a câmera com as três perguntas aparecendo uma a uma na tela. "
                        "Fechar com a frase: 'movimento não é progresso'."
                    ),
                    call_to_action="Salva este vídeo para revisar antes da próxima entrega importante.",
                    priority_platform="Instagram Reels",
                    platform_rationale="O Reels favorece checklist visual e salvamentos para consulta rápida depois.",
                ),
                VideoScript(
                    approach="contrario_ou_provocativo",
                    hook="E se o seu maior erro estratégico for insistir numa batalha que você nem precisava enfrentar?",
                    development=(
                        "Nem toda disputa merece sua energia. Em Sun Tzu, campanhas longas desgastam recursos e enfraquecem a operação. "
                        "No trabalho real, insistir por orgulho pode custar tempo, foco e qualidade. Às vezes, reposicionar e reduzir desgaste "
                        "te aproxima mais do objetivo do que entrar de frente."
                    ),
                    visual_suggestion=(
                        "Texto grande na tela: 'precisa mesmo entrar nessa?'. Depois, palavras-chave: 'desgaste', 'recurso', 'objetivo'."
                    ),
                    call_to_action="Comenta 'contexto' se você já insistiu numa disputa que só drenou energia.",
                    priority_platform="Instagram Reels",
                    platform_rationale="O Reels favorece ganchos de contraste e incentiva comentários e discussão.",
                ),
                VideoScript(
                    approach="ugc",
                    hook="Uma coisa que aprendi com A Arte da Guerra mudou a forma como eu começo projetos.",
                    development=(
                        "Eu costumava começar pela primeira tarefa que aparecia. Depois, eu passei a parar antes de agir e avaliar: "
                        "objetivo, recursos e obstáculo. Depois eu percebi que essa lógica podia ser ampliada com os cinco fatores que Sun Tzu usa "
                        "para avaliar uma guerra: doutrina, tempo, terreno, mando e disciplina. Movimento não é progresso. Essa mudança simples me "
                        "ajudou a ser menos reativo e a escolher melhor onde investir esforço."
                    ),
                    visual_suggestion="Vídeo selfie em ambiente cotidiano, fala espontânea, legendas curtas: 'objetivo', 'recurso', 'obstáculo'.",
                    call_to_action="Se esse tipo de aprendizado aplicado faz sentido pra você, me segue para mais ideias que mudam a prática.",
                    priority_platform="Instagram Reels",
                    platform_rationale="O formato vertical e conversacional favorece narrativa pessoal e identificação.",
                ),
            ]
        )

    def run(
        self,
        idea_map: EditorialKnowledgeMap,
        editorial: EditorialOutput,
        review: ReviewReport,
    ) -> DistributionOutput:
        guidance = ""

        for attempt in range(3):
            response = self.llm_client.generate(
                system_prompt=DISTRIBUTION_SYSTEM_PROMPT,
                user_prompt=build_distribution_prompt(
                    self.config,
                    idea_map,
                    editorial,
                    review,
                    extra_guidance=guidance,
                ),
                temperature=self.config.llm.temperature,
            )
            payload = extract_json_payload(response)

            try:
                distribution = DistributionOutput.model_validate(payload)
            except ValidationError:
                if attempt == 2:
                    raise
                guidance = (
                    "A resposta anterior veio com estrutura incompleta. Retorne novamente um JSON válido com 3 roteiros, "
                    "cada um com hook, development, visual_suggestion, call_to_action, priority_platform e platform_rationale."
                )
                continue

            issues = self._quality_issues(distribution)
            if issues and attempt < 2:
                guidance = (
                    "Ajuste os roteiros para ficar mais forte e menos genérico:\n"
                    "- Educacional: gancho com 3 perguntas e CTA de salvar.\n"
                    "- Provocativo: gancho 'precisa mesmo entrar nessa?' e CTA de comentar.\n"
                    "- UGC: relato pessoal em primeira pessoa com insight 'movimento não é progresso'.\n"
                    "- Justificativas de plataforma devem ser diferentes (salvar vs comentar vs identificação).\n"
                    f"Problemas detectados: {', '.join(issues)}"
                )
                continue

            if issues:
                return self._fallback_distribution()

            return distribution

        raise ValueError("Falha inesperada ao gerar roteiros de distribuição válidos.")
