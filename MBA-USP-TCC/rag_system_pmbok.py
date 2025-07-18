import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

class PMBOKRAGSystem:
    """
    Sistema RAG (Retrieval Augmented Generation) baseado no PMBOK.
    
    Este sistema utiliza embeddings para recuperar conhecimento relevante do PMBOK
    para enriquecer as análises e recomendações dos agentes.
    """
    
    def __init__(self, domain="cronograma", model_name="all-MiniLM-L6-v2", knowledge_dir=None):
        """
        Inicializa o sistema RAG.
        
        Args:
            domain: Domínio do conhecimento (cronograma, custos, escopo, riscos)
            model_name: Nome do modelo de embeddings
            knowledge_dir: Diretório com a base de conhecimento (opcional)
        """
        self.domain = domain
        self.model_name = model_name
        
        # Definir diretório da base de conhecimento
        if knowledge_dir is None:
            # Usar diretório padrão relativo ao arquivo atual
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.knowledge_dir = os.path.join(current_dir, "..", "knowledge_base")
        else:
            self.knowledge_dir = knowledge_dir
        
        # Criar diretório se não existir
        os.makedirs(self.knowledge_dir, exist_ok=True)
        
        # Carregar modelo de embeddings
        try:
            self.model = SentenceTransformer(model_name)
            self.embedding_size = self.model.get_sentence_embedding_dimension()
        except:
            print(f"Erro ao carregar modelo {model_name}. Usando fallback.")
            self.model = None
            self.embedding_size = 384  # Tamanho padrão para fallback
        
        # Carregar ou criar base de conhecimento
        self.documents = self._load_knowledge()
        
        # Criar índice de embeddings
        self.index = self._create_index()
    
    def _load_knowledge(self):
        """
        Carrega a base de conhecimento do PMBOK.
        
        Returns:
            Lista de documentos
        """
        # Verificar se existe arquivo de conhecimento para o domínio
        knowledge_file = os.path.join(self.knowledge_dir, f"pmbok_{self.domain}.json")
        
        if os.path.exists(knowledge_file):
            # Carregar conhecimento existente
            with open(knowledge_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Criar base de conhecimento padrão
            documents = self._create_default_knowledge()
            
            # Salvar base de conhecimento
            with open(knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(documents, f, ensure_ascii=False, indent=2)
            
            return documents
    
    def _create_default_knowledge(self):
        """
        Cria uma base de conhecimento padrão para o domínio.
        
        Returns:
            Lista de documentos
        """
        if self.domain == "cronograma":
            return [
                {
                    "id": "cronograma_001",
                    "title": "Gerenciamento do Cronograma - Visão Geral",
                    "content": "O gerenciamento do cronograma do projeto inclui os processos necessários para gerenciar o término pontual do projeto. Os processos de gerenciamento do cronograma são: Planejar o gerenciamento do cronograma, Definir as atividades, Sequenciar as atividades, Estimar as durações das atividades, Desenvolver o cronograma e Controlar o cronograma."
                },
                {
                    "id": "cronograma_002",
                    "title": "Método do Caminho Crítico (CPM)",
                    "content": "O método do caminho crítico (CPM) é usado para estimar a duração mínima do projeto e determinar o grau de flexibilidade nos caminhos lógicos da rede dentro do modelo do cronograma. Esta técnica de análise de rede do cronograma calcula as datas de início e término mais cedo e mais tarde, teóricas, para todas as atividades, sem considerar quaisquer limitações de recursos."
                },
                {
                    "id": "cronograma_003",
                    "title": "Técnica de Otimização de Recursos",
                    "content": "As técnicas de otimização de recursos incluem, mas não estão limitadas a: Nivelamento de recursos - técnica na qual as datas de início e término são ajustadas com base nas restrições de recursos, com o objetivo de equilibrar a demanda por recursos com a oferta disponível. Estabilização de recursos - técnica que ajusta as atividades de um modelo de cronograma, de modo que as necessidades de recursos do projeto não excedam certos limites predefinidos."
                },
                {
                    "id": "cronograma_004",
                    "title": "Compressão do Cronograma",
                    "content": "As técnicas de compressão do cronograma são usadas para encurtar a duração do cronograma sem reduzir o escopo do projeto. Incluem: Fast tracking - técnica de compressão do cronograma em que atividades ou fases normalmente executadas em sequência são realizadas em paralelo. Crashing - técnica de compressão do cronograma na qual os custos e recursos são aumentados para reduzir a duração."
                },
                {
                    "id": "cronograma_005",
                    "title": "Análise de Valor Agregado (EVA) para Cronograma",
                    "content": "A análise de valor agregado (EVA) compara a linha de base do cronograma com o progresso real para determinar se há variações. Métricas importantes incluem: Valor Planejado (PV) - orçamento autorizado para o trabalho planejado. Valor Agregado (EV) - medida do trabalho realizado expressa em termos do orçamento autorizado. Índice de Desempenho de Cronograma (SPI) - medida de eficiência do cronograma expressa como a razão entre o valor agregado e o valor planejado. SPI = EV/PV."
                },
                {
                    "id": "cronograma_006",
                    "title": "Interpretação do SPI",
                    "content": "O Índice de Desempenho de Cronograma (SPI) é interpretado da seguinte forma: SPI > 1,0: Mais trabalho foi concluído do que o planejado (adiantado). SPI = 1,0: O trabalho concluído é exatamente igual ao planejado (no prazo). SPI < 1,0: Menos trabalho foi concluído do que o planejado (atrasado). Um SPI < 0,8 é geralmente considerado crítico e requer ações corretivas imediatas."
                },
                {
                    "id": "cronograma_007",
                    "title": "Ações Corretivas para Atrasos no Cronograma",
                    "content": "Quando o projeto está atrasado (SPI < 1,0), as seguintes ações corretivas podem ser consideradas: Revisar o caminho crítico e identificar oportunidades de fast-tracking. Alocar recursos adicionais para atividades críticas. Reduzir o escopo, se aprovado pelos stakeholders. Revisar as dependências entre atividades para identificar oportunidades de otimização. Implementar horas extras para recuperar o atraso. Considerar a revisão da linha de base do cronograma se os atrasos forem significativos e não recuperáveis."
                },
                {
                    "id": "cronograma_008",
                    "title": "Monitoramento e Controle do Cronograma",
                    "content": "O processo de controle do cronograma envolve: Determinar o status atual do cronograma do projeto. Influenciar os fatores que criam mudanças no cronograma. Determinar se o cronograma do projeto mudou. Gerenciar as mudanças reais conforme ocorrem. Um sistema eficaz de controle de cronograma deve incluir procedimentos para registrar, analisar e relatar desvios do cronograma, bem como para implementar ações corretivas."
                },
                {
                    "id": "cronograma_009",
                    "title": "Ferramentas de Gerenciamento de Cronograma",
                    "content": "Ferramentas comuns para gerenciamento de cronograma incluem: Software de gerenciamento de projetos para criar e manter o modelo do cronograma. Sistemas de coleta de dados para registrar o progresso real. Reuniões de revisão de status para avaliar o progresso. Técnicas de previsão para estimar o término. Sistemas de gerenciamento de mudanças para controlar alterações no cronograma."
                },
                {
                    "id": "cronograma_010",
                    "title": "Melhores Práticas para Gerenciamento de Cronograma",
                    "content": "Melhores práticas para gerenciamento eficaz do cronograma incluem: Desenvolver um cronograma realista com a participação da equipe. Incluir reservas de contingência para riscos conhecidos. Manter o cronograma atualizado com o progresso real. Comunicar regularmente o status do cronograma aos stakeholders. Analisar tendências de desempenho para identificar problemas potenciais antecipadamente. Implementar ações corretivas rapidamente quando desvios são identificados. Documentar lições aprendidas para projetos futuros."
                }
            ]
        elif self.domain == "custos":
            return [
                {
                    "id": "custos_001",
                    "title": "Gerenciamento dos Custos - Visão Geral",
                    "content": "O gerenciamento dos custos do projeto inclui os processos envolvidos em planejamento, estimativas, orçamentos, financiamentos, gerenciamento e controle dos custos, de modo que o projeto possa ser terminado dentro do orçamento aprovado. Os processos de gerenciamento dos custos são: Planejar o gerenciamento dos custos, Estimar os custos, Determinar o orçamento e Controlar os custos."
                },
                {
                    "id": "custos_002",
                    "title": "Tipos de Custos",
                    "content": "Os custos do projeto podem ser classificados como: Custos diretos - diretamente atribuíveis às atividades do projeto (mão de obra, materiais, equipamentos). Custos indiretos - não diretamente atribuíveis, mas necessários para o projeto (overhead, administração). Custos fixos - permanecem constantes independentemente do volume de trabalho. Custos variáveis - variam de acordo com o volume de trabalho. Custos de qualidade - custos relacionados à prevenção, avaliação e falhas."
                },
                {
                    "id": "custos_003",
                    "title": "Técnicas de Estimativa de Custos",
                    "content": "As técnicas de estimativa de custos incluem: Estimativa análoga - usa custos de projetos anteriores similares. Estimativa paramétrica - usa relações estatísticas entre dados históricos e variáveis. Estimativa bottom-up - estima custos de componentes individuais e os agrega. Estimativa de três pontos - usa estimativas otimista, mais provável e pessimista. Análise de reservas - adiciona reservas para contingências e gerenciamento."
                },
                {
                    "id": "custos_004",
                    "title": "Determinação do Orçamento",
                    "content": "O processo de determinação do orçamento envolve: Agregar os custos estimados das atividades individuais ou pacotes de trabalho. Adicionar reservas para contingências para riscos conhecidos. Adicionar reservas de gerenciamento para mudanças não planejadas. Estabelecer a linha de base dos custos - versão aprovada do orçamento do projeto no tempo. Determinar requisitos de financiamento - total e periódicos."
                },
                {
                    "id": "custos_005",
                    "title": "Análise de Valor Agregado (EVA) para Custos",
                    "content": "A análise de valor agregado (EVA) integra escopo, cronograma e custos. Métricas importantes incluem: Valor Planejado (PV) - orçamento autorizado para o trabalho planejado. Valor Agregado (EV) - medida do trabalho realizado expressa em termos do orçamento. Custo Real (AC) - custo real incorrido para o trabalho realizado. Índice de Desempenho de Custo (CPI) - medida de eficiência de custos expressa como a razão entre o valor agregado e o custo real. CPI = EV/AC."
                },
                {
                    "id": "custos_006",
                    "title": "Interpretação do CPI",
                    "content": "O Índice de Desempenho de Custo (CPI) é interpretado da seguinte forma: CPI > 1,0: O trabalho está sendo realizado a um custo menor que o planejado (abaixo do orçamento). CPI = 1,0: O trabalho está sendo realizado exatamente ao custo planejado (dentro do orçamento). CPI < 1,0: O trabalho está sendo realizado a um custo maior que o planejado (acima do orçamento). Um CPI < 0,8 é geralmente considerado crítico e requer ações corretivas imediatas."
                },
                {
                    "id": "custos_007",
                    "title": "Previsões de Custos",
                    "content": "As previsões de custos incluem: Estimativa para Terminar (ETC) - custo esperado para terminar todo o trabalho restante. Estimativa no Término (EAC) - custo total esperado para concluir todo o trabalho. Variação no Término (VAC) - diferença entre o orçamento no término e a estimativa no término. Fórmulas comuns: EAC = AC + ETC (para variações atípicas) ou EAC = BAC/CPI (para variações típicas). VAC = BAC - EAC."
                },
                {
                    "id": "custos_008",
                    "title": "Ações Corretivas para Desvios de Custos",
                    "content": "Quando o projeto está acima do orçamento (CPI < 1,0), as seguintes ações corretivas podem ser consideradas: Revisar as categorias de custo com maior desvio. Implementar medidas de economia sem impactar a qualidade. Renegociar contratos com fornecedores. Revisar o escopo para identificar possíveis reduções. Otimizar a alocação de recursos. Revisar processos para identificar ineficiências. Implementar controles mais rigorosos para aprovação de despesas futuras."
                },
                {
                    "id": "custos_009",
                    "title": "Controle de Custos",
                    "content": "O processo de controle de custos envolve: Monitorar o status do projeto para atualizar os custos. Gerenciar mudanças na linha de base de custos. Assegurar que os gastos não excedam os recursos autorizados. Monitorar o desempenho de custos para detectar variações. Registrar mudanças apropriadas na linha de base de custos. Informar as partes interessadas sobre mudanças aprovadas. Agir para manter os excessos de custos dentro de limites aceitáveis."
                },
                {
                    "id": "custos_010",
                    "title": "Melhores Práticas para Gerenciamento de Custos",
                    "content": "Melhores práticas para gerenciamento eficaz de custos incluem: Desenvolver estimativas realistas com a participação da equipe. Incluir reservas adequadas para riscos conhecidos. Manter o orçamento atualizado com os custos reais. Comunicar regularmente o status dos custos aos stakeholders. Analisar tendências de desempenho para identificar problemas potenciais antecipadamente. Implementar ações corretivas rapidamente quando desvios são identificados. Documentar lições aprendidas para projetos futuros."
                }
            ]
        elif self.domain == "escopo":
            return [
                {
                    "id": "escopo_001",
                    "title": "Gerenciamento do Escopo - Visão Geral",
                    "content": "O gerenciamento do escopo do projeto inclui os processos necessários para assegurar que o projeto inclua todo o trabalho necessário, e apenas o necessário, para terminar o projeto com sucesso. Os processos de gerenciamento do escopo são: Planejar o gerenciamento do escopo, Coletar os requisitos, Definir o escopo, Criar a EAP, Validar o escopo e Controlar o escopo."
                },
                {
                    "id": "escopo_002",
                    "title": "Definição do Escopo",
                    "content": "A definição do escopo envolve desenvolver uma descrição detalhada do projeto e do produto. Ela prepara a declaração detalhada do escopo do projeto, que serve como base para futuras decisões do projeto. A declaração do escopo do projeto documenta: Descrição do escopo do produto, Entregas do projeto, Critérios de aceitação, Exclusões do projeto, Restrições e Premissas."
                },
                {
                    "id": "escopo_003",
                    "title": "Estrutura Analítica do Projeto (EAP)",
                    "content": "A Estrutura Analítica do Projeto (EAP) é uma decomposição hierárquica do escopo total do trabalho a ser executado pela equipe do projeto a fim de atingir os objetivos do projeto e criar as entregas exigidas. A EAP organiza e define o escopo total do projeto e representa o trabalho especificado na declaração do escopo do projeto aprovada."
                },
                {
                    "id": "escopo_004",
                    "title": "Validação do Escopo",
                    "content": "A validação do escopo é o processo de formalização da aceitação das entregas concluídas do projeto. Ela proporciona objetividade ao processo de aceitação e aumenta a probabilidade da aceitação final do produto, serviço ou resultado, através da validação de cada entrega. Este processo é realizado periodicamente durante o projeto."
                },
                {
                    "id": "escopo_005",
                    "title": "Controle do Escopo",
                    "content": "O controle do escopo é o processo de monitoramento do status do escopo do projeto e do produto e gerenciamento das mudanças feitas na linha de base do escopo. O principal benefício deste processo é permitir que a linha de base do escopo seja mantida ao longo de todo o projeto. O controle do escopo assegura que todas as mudanças solicitadas e ações corretivas ou preventivas recomendadas sejam processadas através do processo Realizar o controle integrado de mudanças."
                },
                {
                    "id": "escopo_006",
                    "title": "Gerenciamento de Requisitos",
                    "content": "O gerenciamento de requisitos inclui as atividades para determinar, documentar e gerenciar as necessidades e requisitos das partes interessadas para atender aos objetivos do projeto. Os requisitos são a base para definir o escopo do projeto e do produto. Eles devem ser documentados, analisados, priorizados, e aprovados antes de serem incluídos na linha de base do escopo."
                },
                {
                    "id": "escopo_007",
                    "title": "Mudanças de Escopo",
                    "content": "As mudanças de escopo são alterações na linha de base do escopo aprovada. Elas podem ocorrer devido a: Requisitos não identificados inicialmente, Mudanças nas necessidades dos stakeholders, Restrições ou premissas que se provaram inválidas, Oportunidades de melhoria identificadas durante o projeto. Todas as mudanças de escopo devem ser formalmente documentadas, avaliadas quanto ao impacto, e aprovadas antes da implementação."
                },
                {
                    "id": "escopo_008",
                    "title": "Impacto das Mudanças de Escopo",
                    "content": "As mudanças de escopo podem ter impacto significativo no projeto, afetando: Cronograma - adição de trabalho geralmente aumenta a duração do projeto. Custos - trabalho adicional geralmente aumenta os custos do projeto. Recursos - pode ser necessário alocar recursos adicionais. Qualidade - mudanças apressadas podem comprometer a qualidade. Riscos - novas atividades podem introduzir novos riscos. É essencial avaliar completamente esses impactos antes de aprovar mudanças de escopo."
                },
                {
                    "id": "escopo_009",
                    "title": "Processo de Controle de Mudanças",
                    "content": "O processo de controle de mudanças para o escopo inclui: Identificar e documentar a mudança solicitada. Avaliar o impacto da mudança no cronograma, custo, recursos, qualidade e riscos. Justificar a necessidade da mudança. Obter aprovação dos stakeholders apropriados. Atualizar a linha de base do escopo e outros documentos do projeto. Comunicar a mudança aprovada a todas as partes interessadas. Implementar a mudança de forma controlada."
                },
                {
                    "id": "escopo_010",
                    "title": "Melhores Práticas para Gerenciamento de Escopo",
                    "content": "Melhores práticas para gerenciamento eficaz do escopo incluem: Envolver os stakeholders na definição do escopo. Documentar claramente o escopo, incluindo o que está dentro e fora do escopo. Obter aprovação formal da declaração do escopo. Criar uma EAP detalhada e completa. Implementar um processo rigoroso de controle de mudanças. Comunicar regularmente o status do escopo aos stakeholders. Validar formalmente as entregas com os stakeholders. Documentar lições aprendidas relacionadas ao escopo para projetos futuros."
                }
            ]
        elif self.domain == "riscos":
            return [
                {
                    "id": "riscos_001",
                    "title": "Gerenciamento dos Riscos - Visão Geral",
                    "content": "O gerenciamento dos riscos do projeto inclui os processos de condução de planejamento, identificação, análise, planejamento de respostas, implementação de respostas e monitoramento de riscos em um projeto. Os processos são: Planejar o gerenciamento dos riscos, Identificar os riscos, Realizar a análise qualitativa dos riscos, Realizar a análise quantitativa dos riscos, Planejar as respostas aos riscos, Implementar respostas aos riscos e Monitorar os riscos."
                },
                {
                    "id": "riscos_002",
                    "title": "Identificação de Riscos",
                    "content": "A identificação dos riscos é o processo de determinação dos riscos que podem afetar o projeto e de documentação das suas características. O principal benefício deste processo é a documentação dos riscos existentes e o conhecimento e a capacidade que ele fornece à equipe do projeto de antecipar eventos. Técnicas incluem: Brainstorming, Técnica Delphi, Entrevistas, Análise de causa-raiz, Análise SWOT, Análise de premissas e restrições."
                },
                {
                    "id": "riscos_003",
                    "title": "Análise Qualitativa de Riscos",
                    "content": "A análise qualitativa dos riscos é o processo de priorização de riscos para análise ou ação adicional através da avaliação e combinação de sua probabilidade de ocorrência e impacto. O principal benefício deste processo é permitir que os gerentes de projetos reduzam o nível de incerteza e foquem nos riscos de alta prioridade. A matriz de probabilidade e impacto é uma ferramenta comum para classificar riscos."
                },
                {
                    "id": "riscos_004",
                    "title": "Análise Quantitativa de Riscos",
                    "content": "A análise quantitativa dos riscos é o processo de analisar numericamente o efeito combinado dos riscos identificados e outras fontes de incerteza nos objetivos gerais do projeto. O principal benefício deste processo é que ele produz informações quantitativas dos riscos para apoiar a tomada de decisões a fim de reduzir a incerteza do projeto. Técnicas incluem: Simulação de Monte Carlo, Análise de sensibilidade, Análise de valor monetário esperado, Árvore de decisão."
                },
                {
                    "id": "riscos_005",
                    "title": "Planejamento de Respostas aos Riscos",
                    "content": "O planejamento das respostas aos riscos é o processo de desenvolvimento de opções, seleção de estratégias e acordos sobre ações para abordar a exposição geral de riscos do projeto, e também para tratar os riscos individuais do projeto. Estratégias para riscos negativos (ameaças) incluem: Evitar, Transferir, Mitigar e Aceitar. Estratégias para riscos positivos (oportunidades) incluem: Explorar, Melhorar, Compartilhar e Aceitar."
                },
                {
                    "id": "riscos_006",
                    "title": "Implementação de Respostas aos Riscos",
                    "content": "A implementação das respostas aos riscos é o processo de implementar planos acordados de resposta aos riscos. O principal benefício deste processo é a garantia de que as respostas aos riscos acordadas sejam executadas conforme planejado, a fim de abordar a exposição ao risco do projeto geral, minimizar ameaças individuais do projeto e maximizar oportunidades individuais do projeto."
                },
                {
                    "id": "riscos_007",
                    "title": "Monitoramento dos Riscos",
                    "content": "O monitoramento dos riscos é o processo de monitorar a implementação de planos acordados de resposta aos riscos, acompanhar riscos identificados, identificar e analisar novos riscos, e avaliar a eficácia do processo de risco ao longo do projeto. O principal benefício deste processo é permitir que as decisões do projeto sejam baseadas em informações atuais sobre a exposição ao risco do projeto geral e riscos individuais do projeto."
                },
                {
                    "id": "riscos_008",
                    "title": "Registro de Riscos",
                    "content": "O registro de riscos é um documento em que os resultados da análise de riscos e o planejamento das respostas aos riscos são registrados. Ele contém: Lista de riscos identificados, Proprietários dos riscos, Resultados da análise qualitativa e quantitativa, Estratégias de resposta acordadas, Ações específicas para implementar a estratégia de resposta escolhida, Sintomas e sinais de alerta, Orçamento e cronograma para respostas, Planos de contingência e reservas."
                },
                {
                    "id": "riscos_009",
                    "title": "Categorias de Riscos",
                    "content": "As categorias de riscos fornecem uma estrutura para identificar riscos de forma sistemática. Categorias comuns incluem: Riscos técnicos - relacionados à tecnologia, requisitos, complexidade, interfaces, desempenho e confiabilidade. Riscos de gestão - relacionados a estimativas, planejamento, controle e comunicação. Riscos organizacionais - relacionados a recursos, financiamento e priorização. Riscos externos - relacionados a legislação, mercado, cliente, concorrência, fornecedores, clima e desastres naturais."
                },
                {
                    "id": "riscos_010",
                    "title": "Melhores Práticas para Gerenciamento de Riscos",
                    "content": "Melhores práticas para gerenciamento eficaz de riscos incluem: Envolver os stakeholders na identificação e análise de riscos. Manter o registro de riscos atualizado ao longo do projeto. Revisar regularmente os riscos em reuniões de status. Designar proprietários para cada risco. Desenvolver planos de resposta específicos e acionáveis. Alocar reservas adequadas para contingências. Monitorar gatilhos de risco e implementar respostas rapidamente quando necessário. Comunicar regularmente o status dos riscos aos stakeholders. Documentar lições aprendidas relacionadas a riscos para projetos futuros."
                }
            ]
        else:
            # Domínio genérico
            return [
                {
                    "id": "geral_001",
                    "title": "Gerenciamento de Projetos - Visão Geral",
                    "content": "O gerenciamento de projetos é a aplicação de conhecimentos, habilidades, ferramentas e técnicas às atividades do projeto a fim de cumprir os seus requisitos. O gerenciamento de projetos é realizado através da aplicação e integração apropriadas dos processos de gerenciamento de projetos identificados para o projeto."
                },
                {
                    "id": "geral_002",
                    "title": "Áreas de Conhecimento do PMBOK",
                    "content": "O Guia PMBOK identifica 10 áreas de conhecimento: Gerenciamento da integração, Gerenciamento do escopo, Gerenciamento do cronograma, Gerenciamento dos custos, Gerenciamento da qualidade, Gerenciamento dos recursos, Gerenciamento das comunicações, Gerenciamento dos riscos, Gerenciamento das aquisições e Gerenciamento das partes interessadas."
                },
                {
                    "id": "geral_003",
                    "title": "Grupos de Processos de Gerenciamento de Projetos",
                    "content": "Os processos de gerenciamento de projetos são agrupados em cinco categorias: Processos de iniciação, Processos de planejamento, Processos de execução, Processos de monitoramento e controle, e Processos de encerramento."
                }
            ]
    
    def _create_index(self):
        """
        Cria um índice de embeddings para a base de conhecimento.
        
        Returns:
            Índice FAISS
        """
        # Verificar se há documentos
        if not self.documents:
            return None
        
        # Extrair conteúdo dos documentos
        texts = [doc["content"] for doc in self.documents]
        
        # Criar embeddings
        if self.model:
            embeddings = self.model.encode(texts)
        else:
            # Fallback para quando o modelo não está disponível
            embeddings = np.random.rand(len(texts), self.embedding_size).astype('float32')
        
        # Criar índice
        index = faiss.IndexFlatL2(self.embedding_size)
        index.add(embeddings.astype('float32'))
        
        return index
    
    def query(self, query_text, top_k=3):
        """
        Busca documentos relevantes para a consulta.
        
        Args:
            query_text: Texto da consulta
            top_k: Número de documentos a retornar
            
        Returns:
            Lista de documentos relevantes
        """
        # Verificar se há índice
        if self.index is None or not self.documents:
            return []
        
        # Criar embedding da consulta
        if self.model:
            query_embedding = self.model.encode([query_text])
        else:
            # Fallback para quando o modelo não está disponível
            query_embedding = np.random.rand(1, self.embedding_size).astype('float32')
        
        # Buscar documentos similares
        top_k = min(top_k, len(self.documents))
        distances, indices = self.index.search(query_embedding.astype('float32'), top_k)
        
        # Retornar documentos relevantes
        relevant_docs = [self.documents[idx] for idx in indices[0]]
        
        return relevant_docs
    
    def augment_prompt(self, query, template=None):
        """
        Aumenta o prompt com conhecimento relevante do PMBOK.
        
        Args:
            query: Consulta para buscar conhecimento relevante
            template: Template para o prompt aumentado (opcional)
            
        Returns:
            Prompt aumentado
        """
        # Buscar documentos relevantes
        relevant_docs = self.query(query)
        
        # Extrair conhecimento relevante
        knowledge = ""
        for doc in relevant_docs:
            knowledge += f"- {doc['title']}: {doc['content']}\n\n"
        
        # Usar template padrão se não for fornecido
        if template is None:
            template = """
            Com base nas melhores práticas do PMBOK para gerenciamento de {domain}, analise a seguinte situação:
            
            {query}
            
            Conhecimento relevante do PMBOK:
            {knowledge}
            
            Considerando as melhores práticas acima, forneça uma análise detalhada e recomendações:
            """
        
        # Substituir placeholders no template
        augmented_prompt = template.format(
            domain=self.domain,
            query=query,
            knowledge=knowledge
        )
        
        return augmented_prompt

# Exemplo de uso
if __name__ == "__main__":
    # Criar sistema RAG para o domínio de cronograma
    rag_system = PMBOKRAGSystem(domain="cronograma")
    
    # Consulta de exemplo
    query = "O projeto está com SPI de 0.85, indicando atraso no cronograma. Quais ações devem ser tomadas?"
    
    # Buscar documentos relevantes
    relevant_docs = rag_system.query(query)
    
    print("Documentos relevantes:")
    for doc in relevant_docs:
        print(f"- {doc['title']}")
    
    # Gerar prompt aumentado
    augmented_prompt = rag_system.augment_prompt(query)
    
    print("\nPrompt aumentado:")
    print(augmented_prompt)
