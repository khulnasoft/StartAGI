from __future__ import absolute_import
import sys

from sqlalchemy.orm import sessionmaker

from fastagi.helper.tool_helper import handle_tools_import
from fastagi.lib.logger import logger

from datetime import timedelta
from celery import Celery

from fastagi.config.config import get_config
from fastagi.helper.agent_schedule_helper import AgentScheduleHelper
from fastagi.models.configuration import Configuration
from fastagi.models.agent import Agent
from fastagi.models.db import connect_db
from fastagi.types.model_source_types import ModelSourceType

from sqlalchemy import event
from fastagi.models.agent_execution import AgentExecution
from fastagi.helper.webhook_manager import WebHookManager

redis_url = get_config('REDIS_URL', 'fast__redis:6379')

app = Celery("fastagi", include=["fastagi.worker"], imports=["fastagi.worker"])
app.conf.broker_url = "redis://" + redis_url + "/0"
app.conf.result_backend = "redis://" + redis_url + "/0"
app.conf.worker_concurrency = 10
app.conf.accept_content = ['application/x-python-serialize', 'application/json']


beat_schedule = {
    'initialize-schedule-agent': {
        'task': 'initialize-schedule-agent',
        'schedule': timedelta(minutes=5),
    },
    'execute_waiting_workflows': {
        'task': 'execute_waiting_workflows',
        'schedule': timedelta(minutes=2),
    },
}
app.conf.beat_schedule = beat_schedule

@event.listens_for(AgentExecution.status, "set")
def agent_status_change(target, val,old_val,initiator):
    if not hasattr(sys, '_called_from_test'):
        webhook_callback.delay(target.id,val,old_val)

@app.task(name="execute_waiting_workflows", autoretry_for=(Exception,), retry_backoff=2, max_retries=5)
def execute_waiting_workflows():
    """Check if wait time of wait workflow step is over and can be resumed."""

    from fastagi.jobs.agent_executor import AgentExecutor
    logger.info("Executing waiting workflows job")
    AgentExecutor().execute_waiting_workflows()

@app.task(name="initialize-schedule-agent", autoretry_for=(Exception,), retry_backoff=2, max_retries=5)
def initialize_schedule_agent_task():
    """Executing agent scheduling in the background."""

    schedule_helper = AgentScheduleHelper()
    schedule_helper.update_next_scheduled_time()
    schedule_helper.run_scheduled_agents()


@app.task(name="execute_agent", autoretry_for=(Exception,), retry_backoff=2, max_retries=5)
def execute_agent(agent_execution_id: int, time):
    """Execute an agent step in background."""
    from fastagi.jobs.agent_executor import AgentExecutor
    handle_tools_import()
    logger.info("Execute agent:" + str(time) + "," + str(agent_execution_id))
    AgentExecutor().execute_next_step(agent_execution_id=agent_execution_id)


@app.task(name="summarize_resource", autoretry_for=(Exception,), retry_backoff=2, max_retries=5,serializer='pickle')
def summarize_resource(agent_id: int, resource_id: int):
    """Summarize a resource in background."""
    from fastagi.resource_manager.resource_summary import ResourceSummarizer
    from fastagi.types.storage_types import StorageType
    from fastagi.models.resource import Resource
    from fastagi.resource_manager.resource_manager import ResourceManager

    engine = connect_db()
    Session = sessionmaker(bind=engine)
    session = Session()
    agent_config = Agent.fetch_configuration(session, agent_id)
    organisation = Agent.find_org_by_agent_id(session, agent_id)
    model_source = Configuration.fetch_configurations(session, organisation.id, "model_source", agent_config["model"]) or "OpenAi"
    if ModelSourceType.GooglePalm.value in model_source or ModelSourceType.Replicate.value in model_source:
        return

    resource = session.query(Resource).filter(Resource.id == resource_id).first()
    file_path = resource.path

    if resource.storage_type == StorageType.S3.value:
        documents = ResourceManager(str(agent_id)).create_llama_document_s3(file_path)
    else:
        documents = ResourceManager(str(agent_id)).create_llama_document(file_path)

    logger.info("Summarize resource:" + str(agent_id) + "," + str(resource_id))
    resource_summarizer = ResourceSummarizer(session=session, agent_id=agent_id, model=agent_config["model"])
    resource_summarizer.add_to_vector_store_and_create_summary(resource_id=resource_id,
                                                               documents=documents)
    session.close()

@app.task(name="webhook_callback", autoretry_for=(Exception,), retry_backoff=2, max_retries=5,serializer='pickle')
def webhook_callback(agent_execution_id,val,old_val):
    engine = connect_db()
    Session = sessionmaker(bind=engine)
    with Session() as session:
        WebHookManager(session).agent_status_change_callback(agent_execution_id, val, old_val)
    
