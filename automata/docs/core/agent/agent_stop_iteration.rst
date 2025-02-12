AgentStopIteration
==================

``AgentStopIteration`` is an exception raised when the agent stops
iterating. This can occur during the execution of tasks in the
``AutomataAgent``. The agent may stop iterating due to having reached a
stopping criteria or completing the assigned tasks.

Related Symbols
---------------

-  ``automata.tests.unit.test_automata_agent.test_run_with_no_completion``
-  ``automata.tests.unit.test_automata_agent.test_iter_step_without_api_call``
-  ``automata.core.agent.error.AgentMaxIterError``
-  ``automata.core.base.agent.Agent.__iter__``
-  ``automata.core.agent.agents.AutomataOpenAIAgent.__iter__``
-  ``automata.core.agent.agents.AutomataOpenAIAgent.run``

Example
-------

The following example demonstrates how to catch an
``AgentStopIteration`` exception while using an ``AutomataOpenAIAgent``.

.. code:: python

   from automata.core.agent.agents import AutomataOpenAIAgent
   from automata.core.agent.error import AgentStopIteration

   agent = AutomataOpenAIAgent()

   try:
       while True:
           agent.iter_step()
   except AgentStopIteration:
       print("Agent has stopped iterating.")

Limitations
-----------

``AgentStopIteration`` is an exception specific to the
``AutomataAgent``. It is not applicable in other agent contexts.

Follow-up Questions:
--------------------

-  Are there any alternative ways of implementing a stop iteration for
   agents other than raising an exception?
