# main.py
# ──────────────────────────────────────────────
# 🚀 Entry point: CrewAI 파이프라인 실행
# ──────────────────────────────────────────────

import dotenv
import yaml
from crewai import Agent, Task, Crew
from crewai.project import CrewBase, agent, task, crew
from tools.tools import fetch_and_store_news, generate_embeddings_for_articles
from services import db_services
from models import Article, Event, Report

# ────────────────────────────────
# 1️⃣ 환경변수 로드
# ────────────────────────────────
dotenv.load_dotenv()

# ────────────────────────────────
# 2️⃣ YAML 설정 파일 로드
# ────────────────────────────────
with open("config/agents.yaml", "r", encoding="utf-8") as f:
    AGENTS_CONFIG = yaml.safe_load(f)

with open("config/tasks.yaml", "r", encoding="utf-8") as f:
    TASKS_CONFIG = yaml.safe_load(f)


# ────────────────────────────────
# 3️⃣ Crew 정의
# ────────────────────────────────
@CrewBase
class NewsReaderCrew:
    """전체 뉴스 수집 → 임베딩 → 클러스터링 → 리포트 작성 파이프라인"""

    agents_config = AGENTS_CONFIG
    tasks_config = TASKS_CONFIG

    # ========== AGENTS ========== #
    @agent
    def collector(self):
        return Agent(config=self.agents_config["rss_collector_agent"], tools=[fetch_and_store_news])

    @agent
    def embedder(self):
        return Agent(config=self.agents_config["embedder"], tools=[generate_embeddings_for_articles])

    @agent
    def clusterer(self):
        return Agent(config=self.agents_config["clusterer"])

    @agent
    def reporter(self):
        return Agent(config=self.agents_config["reporter"])

    # ========== TASKS ========== #
    @task
    def collect_news_task(self):
        return Task(config=self.tasks_config["collect_news_task"])

    @task
    def embed_articles_task(self):
        return Task(config=self.tasks_config["embed_articles_task"])

    @task
    def cluster_events_task(self):
        return Task(config=self.tasks_config["cluster_events_task"])

    @task
    def generate_report_task(self):
        return Task(config=self.tasks_config["generate_report_task"])

    # ========== CREW ========== #
    @crew
    def assemble(self):
        """Crew 구성: 4개 에이전트와 4개 태스크"""
        return Crew(
            agents=[
                self.collector(),
                self.embedder(),
                self.clusterer(),
                self.reporter(),
            ],
            tasks=[
                self.collect_news_task(),
                self.embed_articles_task(),
                self.cluster_events_task(),
                self.generate_report_task(),
            ],
            verbose=True,
        )


# ────────────────────────────────
# 4️⃣ 실행 Entry
# ────────────────────────────────
if __name__ == "__main__":
    print("🚀 Starting NewsReaderCrew...\n")

    # Crew 인스턴스 생성
    crew_instance = NewsReaderCrew().assemble()

    # 입력값 전달 (예: topic)
    inputs = {"topic": "global energy crisis"}

    # 전체 워크플로우 실행
    result = crew_instance.kickoff(inputs=inputs)

    print("\n✅ Pipeline finished!")
    print(result)
