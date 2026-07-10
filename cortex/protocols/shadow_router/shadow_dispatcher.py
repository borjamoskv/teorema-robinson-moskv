from typing import Protocol, List
from cortex.protocols.shadow_router.decision_receipt import DecisionReceipt

class ShadowJob:
    def __init__(self, model_alias: str, payload: dict, decision_receipt_id: str):
        self.model_alias = model_alias
        self.payload = payload
        self.decision_receipt_id = decision_receipt_id


class ShadowDispatcher(Protocol):
    """
    Protocol for a durable queue to execute shadow jobs.
    Must NOT use asyncio.create_task in production.
    Implementations could use Celery, SQS, RabbitMQ, etc.
    """
    async def enqueue(self, job: ShadowJob) -> None:
        ...


class InMemoryMockDispatcher:
    """Development mock. Do NOT use in production to avoid missing shadow jobs on restart."""
    def __init__(self):
        self.queue: List[ShadowJob] = []
        self.failed_enqueues = 0

    async def enqueue(self, job: ShadowJob) -> None:
        self.queue.append(job)
