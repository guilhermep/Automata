import uuid
from unittest.mock import PropertyMock, patch

import pytest

from automata.config.base import AgentConfigName
from automata.core.agent.task.task import AutomataTask
from automata.core.base.task import TaskStatus

from ..conftest import MockRepositoryManager


@patch("logging.config.dictConfig", return_value=None)
def test_task_inital_state(_, task):
    assert task.status == TaskStatus.CREATED


@patch("logging.config.dictConfig", return_value=None)
def test_register_task(_, task, registry):
    registry.register(task)
    assert task.status == TaskStatus.REGISTERED


@patch("logging.config.dictConfig", return_value=None)
def test_setup_environment(_, task, environment, registry):
    registry.register(task)
    environment.setup(task)
    assert task.observer is not None
    assert task.status == TaskStatus.PENDING


@patch("logging.config.dictConfig", return_value=None)
def test_setup_task_no_setup(_, task, registry):
    with pytest.raises(Exception):
        registry.setup(task)


@patch.object(AutomataTask, "status", new_callable=PropertyMock)
def test_status_setter(mock_status, task):
    task.status = TaskStatus.RETRYING
    mock_status.assert_called_once_with(TaskStatus.RETRYING)


@patch.object(AutomataTask, "notify_observer")
def test_callback(mock_notify_observer, task, environment, registry):
    registry.register(task)
    environment.setup(task)
    # Notify observer should be called twice, once at register and once at setup
    assert mock_notify_observer.call_count == 2


def test_deterministic_task_id(automata_agent_config_builder):
    task_1 = AutomataTask(
        test1="arg1",
        test2="arg2",
        priority=5,
        generate_deterministic_id=True,
        config=automata_agent_config_builder,
        helper_agent_names="test",
        instructions="test1",
    )

    task_2 = AutomataTask(
        test1="arg1",
        test2="arg2",
        priority=5,
        generate_deterministic_id=True,
        config=automata_agent_config_builder,
        helper_agent_names="test",
        instructions="test1",
    )

    task_3 = AutomataTask(
        test1="arg1",
        test2="arg3",
        priority=5,
        generate_deterministic_id=True,
        config=automata_agent_config_builder,
        helper_agent_names="test",
        instructions="test1",
    )

    task_4 = AutomataTask(
        test1="arg1",
        test2="arg2",
        priority=5,
        generate_deterministic_id=False,
        config=automata_agent_config_builder,
        helper_agent_names="test",
        instructions="test1",
    )

    assert task_1.task_id == task_2.task_id
    assert task_1.task_id != task_3.task_id
    assert task_1.task_id != task_4.task_id
    assert isinstance(task_4.task_id, uuid.UUID)


def test_deterministic_vs_non_deterministic_task_id():
    task_1 = AutomataTask(
        MockRepositoryManager(),
        test1="arg1",
        test2="arg2",
        priority=5,
        generate_deterministic_id=True,
        config_to_load=AgentConfigName.TEST.value,
        instructions="test1",
    )

    task_2 = AutomataTask(
        MockRepositoryManager(),
        test1="arg1",
        test2="arg2",
        priority=5,
        generate_deterministic_id=False,
        config_to_load=AgentConfigName.TEST.value,
        instructions="test1",
    )
    assert task_1.task_id != task_2.task_id
