"""Cliente Neo4j para integração com memórias via MCP."""

from datetime import datetime
from typing import Any


class Neo4jClient:
    """Cliente para interagir com Neo4j via MCP tools.

    Este cliente usa as ferramentas MCP do neo4j-memory server para
    armazenar e recuperar conhecimento sobre ideias de vídeo.

    IMPORTANTE: Este cliente retorna estruturas de dados que devem ser
    usadas com as ferramentas MCP do Claude (mcp__neo4j-memory__*).
    Não interage diretamente com Neo4j - delega para o Claude SDK.
    """

    def criar_requisicao_contexto(self, task_description: str) -> dict[str, Any]:
        """Cria requisição para buscar contexto antes de gerar títulos.

        Args:
            task_description: Descrição da tarefa (ex: "Gerar títulos sobre streaming")

        Returns:
            Dict com parâmetros para mcp__neo4j-memory__get_context_for_task
        """
        return {
            "tool": "mcp__neo4j-memory__get_context_for_task",
            "params": {"task_description": task_description},
        }

    def criar_requisicao_busca(
        self,
        query: str,
        label: str = "Learning",
        limit: int = 5,
        depth: int = 1,
    ) -> dict[str, Any]:
        """Cria requisição para buscar memórias similares.

        Args:
            query: Texto para buscar
            label: Label das memórias (padrão: "Learning")
            limit: Máximo de resultados
            depth: Profundidade de relacionamentos

        Returns:
            Dict com parâmetros para mcp__neo4j-memory__search_memories
        """
        return {
            "tool": "mcp__neo4j-memory__search_memories",
            "params": {
                "query": query,
                "label": label,
                "limit": limit,
                "depth": depth,
            },
        }

    def criar_requisicao_sugestao(self, current_task: str) -> dict[str, Any]:
        """Cria requisição para obter sugestões baseadas no histórico.

        Args:
            current_task: Descrição da tarefa atual

        Returns:
            Dict com parâmetros para mcp__neo4j-memory__suggest_best_approach
        """
        return {
            "tool": "mcp__neo4j-memory__suggest_best_approach",
            "params": {"current_task": current_task},
        }

    def criar_memoria_ideia(
        self,
        ideia_original: str,
        validation_score: float,
        angle: str,
        estimated_views: str,
    ) -> dict[str, Any]:
        """Cria requisição para salvar memória da ideia de vídeo.

        Args:
            ideia_original: Texto da ideia bruta
            validation_score: Score de validação (0-10)
            angle: Ângulo identificado (ex: "comparação técnica")
            estimated_views: Estimativa de views (ex: "20K-50K")

        Returns:
            Dict com parâmetros para mcp__neo4j-memory__create_memory
        """
        return {
            "tool": "mcp__neo4j-memory__create_memory",
            "params": {
                "label": "Learning",
                "properties": {
                    "name": ideia_original,
                    "raw_idea": ideia_original,
                    "validation_score": validation_score,
                    "angle": angle,
                    "estimated_views": estimated_views,
                    "created_at": datetime.now().strftime("%Y-%m-%d"),
                },
            },
        }

    def criar_memoria_titulo(
        self,
        titulo: str,
        ctr_score: float,
        formula: str,
        triggers: str,
    ) -> dict[str, Any]:
        """Cria requisição para salvar memória de título gerado.

        Args:
            titulo: Título recomendado
            ctr_score: Score de CTR estimado (0-10)
            formula: Fórmula usada (ex: "Fórmula 1: Choque + Número")
            triggers: Gatilhos psicológicos (ex: "FOMO, Curiosidade")

        Returns:
            Dict com parâmetros para mcp__neo4j-memory__create_memory
        """
        return {
            "tool": "mcp__neo4j-memory__create_memory",
            "params": {
                "label": "Learning",
                "properties": {
                    "name": titulo,
                    "ctr_score": ctr_score,
                    "formula": formula,
                    "triggers": triggers,
                    "created_at": datetime.now().strftime("%Y-%m-%d"),
                },
            },
        }

    def criar_conexao(
        self,
        from_memory_id: str,
        to_memory_id: str,
        connection_type: str,
        properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Cria requisição para conectar duas memórias.

        Args:
            from_memory_id: ID da memória origem
            to_memory_id: ID da memória destino
            connection_type: Tipo de conexão (ex: "GENERATED", "ABOUT", "SIMILAR_TO")
            properties: Propriedades opcionais da conexão

        Returns:
            Dict com parâmetros para mcp__neo4j-memory__create_connection
        """
        params: dict[str, Any] = {
            "from_memory_id": from_memory_id,
            "to_memory_id": to_memory_id,
            "connection_type": connection_type,
        }
        if properties:
            params["properties"] = properties

        return {"tool": "mcp__neo4j-memory__create_connection", "params": params}

    def criar_aprendizado(
        self,
        task: str,
        result: str,
        success: bool = True,
        category: str | None = None,
    ) -> dict[str, Any]:
        """Cria requisição para registrar aprendizado.

        Args:
            task: Tarefa executada
            result: Resultado obtido
            success: Se foi bem-sucedido
            category: Categoria do aprendizado

        Returns:
            Dict com parâmetros para mcp__neo4j-memory__learn_from_result
        """
        params: dict[str, Any] = {
            "task": task,
            "result": result,
            "success": success,
        }
        if category:
            params["category"] = category

        return {"tool": "mcp__neo4j-memory__learn_from_result", "params": params}

    def criar_memoria_topico(self, topico: str) -> dict[str, Any]:
        """Cria requisição para salvar tópico.

        Args:
            topico: Nome do tópico (ex: "streaming", "multi-agents")

        Returns:
            Dict com parâmetros para mcp__neo4j-memory__create_memory
        """
        return {
            "tool": "mcp__neo4j-memory__create_memory",
            "params": {
                "label": "Learning",
                "properties": {
                    "name": topico,
                    "category": "topic",
                },
            },
        }

    # ========== PADRÕES: Claude SDK ==========

    def criar_memoria_pattern(
        self,
        pattern_name: str,
        description: str,
        code_snippet: str | None = None,
        success_rate: float | None = None,
    ) -> dict[str, Any]:
        """Cria memória de padrão de uso do Claude SDK.

        Args:
            pattern_name: Nome do padrão (ex: "ClaudeSDKClient with async context")
            description: Descrição do padrão
            code_snippet: Snippet de código (opcional)
            success_rate: Taxa de sucesso (0-1)

        Returns:
            Dict com parâmetros para criar memória de padrão
        """
        return {
            "tool": "mcp__neo4j-memory__create_memory",
            "params": {
                "label": "Learning",
                "properties": {
                    "name": pattern_name,
                    "category": "sdk_pattern",
                    "description": description,
                    "code_snippet": code_snippet or "",
                    "success_rate": success_rate or 0.0,
                    "created_at": datetime.now().strftime("%Y-%m-%d"),
                },
            },
        }

    def criar_memoria_conceito(
        self,
        concept_name: str,
        explanation: str,
        use_cases: list[str] | None = None,
    ) -> dict[str, Any]:
        """Cria memória de conceito do Claude SDK.

        Args:
            concept_name: Nome do conceito (ex: "Streaming", "Multi-turn conversation")
            explanation: Explicação do conceito
            use_cases: Casos de uso onde aplicar

        Returns:
            Dict com parâmetros para criar memória de conceito
        """
        return {
            "tool": "mcp__neo4j-memory__create_memory",
            "params": {
                "label": "Learning",
                "properties": {
                    "name": concept_name,
                    "category": "sdk_concept",
                    "explanation": explanation,
                    "use_cases": ",".join(use_cases or []),
                    "created_at": datetime.now().strftime("%Y-%m-%d"),
                },
            },
        }

    def criar_memoria_exemplo(
        self,
        example_name: str,
        code: str,
        demonstrates_what: str,
        complexity: str = "medium",
    ) -> dict[str, Any]:
        """Cria memória de exemplo de código.

        Args:
            example_name: Nome do exemplo (ex: "Streaming chat with MCP")
            code: Código completo do exemplo
            demonstrates_what: O que demonstra
            complexity: Complexidade (easy, medium, hard)

        Returns:
            Dict com parâmetros para criar memória de exemplo
        """
        return {
            "tool": "mcp__neo4j-memory__create_memory",
            "params": {
                "label": "Learning",
                "properties": {
                    "name": example_name,
                    "category": "code_example",
                    "code": code,
                    "demonstrates": demonstrates_what,
                    "complexity": complexity,
                    "created_at": datetime.now().strftime("%Y-%m-%d"),
                },
            },
        }

    def criar_memoria_validacao(
        self,
        validation_name: str,
        validates_what: str,
        test_code: str | None = None,
        passes: bool = True,
    ) -> dict[str, Any]:
        """Cria memória de validação/teste.

        Args:
            validation_name: Nome da validação (ex: "Test streaming response")
            validates_what: O que está validando
            test_code: Código do teste (opcional)
            passes: Se passou no teste

        Returns:
            Dict com parâmetros para criar memória de validação
        """
        return {
            "tool": "mcp__neo4j-memory__create_memory",
            "params": {
                "label": "Learning",
                "properties": {
                    "name": validation_name,
                    "category": "validation",
                    "validates": validates_what,
                    "test_code": test_code or "",
                    "passes": passes,
                    "created_at": datetime.now().strftime("%Y-%m-%d"),
                },
            },
        }

    def criar_memoria_gatilho(
        self,
        trigger_name: str,
        description: str,
        effectiveness_score: float | None = None,
    ) -> dict[str, Any]:
        """Cria memória de gatilho psicológico.

        Args:
            trigger_name: Nome do gatilho (ex: "FOMO", "Curiosidade")
            description: Descrição de como usar
            effectiveness_score: Score de eficácia (0-10)

        Returns:
            Dict com parâmetros para criar memória de gatilho
        """
        return {
            "tool": "mcp__neo4j-memory__create_memory",
            "params": {
                "label": "Learning",
                "properties": {
                    "name": trigger_name,
                    "category": "psychological_trigger",
                    "description": description,
                    "effectiveness_score": effectiveness_score or 0.0,
                    "created_at": datetime.now().strftime("%Y-%m-%d"),
                },
            },
        }

    # ========== PADRÕES: Ângulos e Formatos ==========

    def criar_memoria_angulo(
        self,
        angle_name: str,
        best_for_topics: list[str] | None = None,
        avg_score: float | None = None,
    ) -> dict[str, Any]:
        """Cria memória de ângulo de abordagem.

        Args:
            angle_name: Nome do ângulo (ex: "comparação técnica", "tutorial prático")
            best_for_topics: Tópicos onde funciona melhor
            avg_score: Score médio de validação

        Returns:
            Dict com parâmetros para criar memória de ângulo
        """
        return {
            "tool": "mcp__neo4j-memory__create_memory",
            "params": {
                "label": "Learning",
                "properties": {
                    "name": angle_name,
                    "category": "angle_pattern",
                    "best_for_topics": ",".join(best_for_topics or []),
                    "avg_score": avg_score or 0.0,
                    "created_at": datetime.now().strftime("%Y-%m-%d"),
                },
            },
        }

    def criar_memoria_formato(
        self,
        format_name: str,
        retention_rate: str | None = None,
        ideal_duration: str | None = None,
    ) -> dict[str, Any]:
        """Cria memória de formato de vídeo.

        Args:
            format_name: Nome do formato (ex: "tutorial", "comparison", "speedrun")
            retention_rate: Taxa de retenção média
            ideal_duration: Duração ideal (ex: "10-15min")

        Returns:
            Dict com parâmetros para criar memória de formato
        """
        return {
            "tool": "mcp__neo4j-memory__create_memory",
            "params": {
                "label": "Learning",
                "properties": {
                    "name": format_name,
                    "category": "format_pattern",
                    "retention_rate": retention_rate or "N/A",
                    "ideal_duration": ideal_duration or "N/A",
                    "created_at": datetime.now().strftime("%Y-%m-%d"),
                },
            },
        }

    # ========== RELACIONAMENTOS: Claude SDK Knowledge Graph ==========

    def conectar_exemplo_implementa_pattern(
        self,
        exemplo_id: str,
        pattern_id: str,
        implementation_quality: str = "good",
    ) -> dict[str, Any]:
        """Conecta exemplo de código ao padrão que ele implementa.

        Args:
            exemplo_id: ID da memória do exemplo de código
            pattern_id: ID da memória do padrão
            implementation_quality: Qualidade da implementação (good, excellent, needs_improvement)

        Returns:
            Dict com parâmetros para criar conexão IMPLEMENTS
        """
        return self.criar_conexao(
            from_memory_id=exemplo_id,
            to_memory_id=pattern_id,
            connection_type="IMPLEMENTS",
            properties={"quality": implementation_quality},
        )

    def conectar_exemplo_demonstra_conceito(
        self,
        exemplo_id: str,
        conceito_id: str,
        clarity_score: float | None = None,
    ) -> dict[str, Any]:
        """Conecta exemplo ao conceito que ele demonstra.

        Args:
            exemplo_id: ID da memória do exemplo
            conceito_id: ID da memória do conceito
            clarity_score: Score de clareza da demonstração (0-10)

        Returns:
            Dict com parâmetros para criar conexão DEMONSTRATES
        """
        return self.criar_conexao(
            from_memory_id=exemplo_id,
            to_memory_id=conceito_id,
            connection_type="DEMONSTRATES",
            properties={"clarity_score": clarity_score or 0.0},
        )

    def conectar_validacao_valida_pattern(
        self,
        validacao_id: str,
        pattern_id: str,
        test_passed: bool = True,
        edge_cases_covered: int = 0,
    ) -> dict[str, Any]:
        """Conecta validação/teste ao padrão que ela valida.

        Args:
            validacao_id: ID da memória da validação
            pattern_id: ID da memória do padrão
            test_passed: Se o teste passou
            edge_cases_covered: Quantos edge cases foram cobertos

        Returns:
            Dict com parâmetros para criar conexão VALIDATES
        """
        return self.criar_conexao(
            from_memory_id=validacao_id,
            to_memory_id=pattern_id,
            connection_type="VALIDATES",
            properties={
                "passed": test_passed,
                "edge_cases_covered": edge_cases_covered,
            },
        )

    def conectar_pattern_requires_conceito(
        self,
        pattern_id: str,
        conceito_id: str,
        importance: str = "required",
    ) -> dict[str, Any]:
        """Conecta padrão ao conceito que é pré-requisito.

        Args:
            pattern_id: ID da memória do padrão
            conceito_id: ID da memória do conceito
            importance: Importância (required, recommended, optional)

        Returns:
            Dict com parâmetros para criar conexão REQUIRES
        """
        return self.criar_conexao(
            from_memory_id=pattern_id,
            to_memory_id=conceito_id,
            connection_type="REQUIRES",
            properties={"importance": importance},
        )

    def conectar_conceito_extends_conceito(
        self,
        conceito_base_id: str,
        conceito_avancado_id: str,
    ) -> dict[str, Any]:
        """Conecta conceito base ao conceito avançado que o estende.

        Args:
            conceito_base_id: ID do conceito base
            conceito_avancado_id: ID do conceito avançado

        Returns:
            Dict com parâmetros para criar conexão EXTENDS
        """
        return self.criar_conexao(
            from_memory_id=conceito_avancado_id,
            to_memory_id=conceito_base_id,
            connection_type="EXTENDS",
        )

    def conectar_pattern_supersedes_pattern(
        self,
        pattern_novo_id: str,
        pattern_antigo_id: str,
        reason: str | None = None,
    ) -> dict[str, Any]:
        """Conecta padrão novo ao padrão antigo que ele substitui.

        Args:
            pattern_novo_id: ID do padrão mais recente
            pattern_antigo_id: ID do padrão obsoleto
            reason: Razão da substituição

        Returns:
            Dict com parâmetros para criar conexão SUPERSEDES
        """
        return self.criar_conexao(
            from_memory_id=pattern_novo_id,
            to_memory_id=pattern_antigo_id,
            connection_type="SUPERSEDES",
            properties={"reason": reason or "Improved approach"},
        )

    # ========== RELACIONAMENTOS: Similaridade e Co-ocorrência ==========

    def conectar_formulas_combinadas(
        self,
        formula1_id: str,
        formula2_id: str,
        combined_ctr: float,
    ) -> dict[str, Any]:
        """Conecta fórmulas que funcionam bem juntas.

        Args:
            formula1_id: ID da primeira fórmula
            formula2_id: ID da segunda fórmula
            combined_ctr: CTR quando combinadas

        Returns:
            Dict com parâmetros para criar conexão WORKS_WELL_WITH
        """
        return self.criar_conexao(
            from_memory_id=formula1_id,
            to_memory_id=formula2_id,
            connection_type="WORKS_WELL_WITH",
            properties={"combined_ctr": combined_ctr},
        )

    def conectar_topicos_similares(
        self,
        topico1_id: str,
        topico2_id: str,
        similarity_score: float,
    ) -> dict[str, Any]:
        """Conecta tópicos similares.

        Args:
            topico1_id: ID do primeiro tópico
            topico2_id: ID do segundo tópico
            similarity_score: Score de similaridade (0-1)

        Returns:
            Dict com parâmetros para criar conexão SIMILAR_TO
        """
        return self.criar_conexao(
            from_memory_id=topico1_id,
            to_memory_id=topico2_id,
            connection_type="SIMILAR_TO",
            properties={"similarity_score": similarity_score},
        )

    # ========== ANÁLISE: Buscar Padrões ==========

    def buscar_melhores_formulas(
        self, min_ctr: float = 8.0, limit: int = 10
    ) -> dict[str, Any]:
        """Busca fórmulas com melhor performance.

        Args:
            min_ctr: CTR mínimo para filtrar
            limit: Máximo de resultados

        Returns:
            Dict com parâmetros para buscar fórmulas de alto CTR
        """
        return {
            "tool": "mcp__neo4j-memory__search_memories",
            "params": {
                "query": f"formula_pattern CTR >= {min_ctr}",
                "label": "Learning",
                "limit": limit,
                "depth": 2,
            },
        }

    def buscar_angulos_por_topico(self, topico: str, limit: int = 5) -> dict[str, Any]:
        """Busca ângulos que funcionam bem para um tópico.

        Args:
            topico: Nome do tópico
            limit: Máximo de resultados

        Returns:
            Dict com parâmetros para buscar ângulos relacionados
        """
        return {
            "tool": "mcp__neo4j-memory__search_memories",
            "params": {
                "query": f"angle_pattern {topico}",
                "label": "Learning",
                "limit": limit,
                "depth": 2,
            },
        }
