"""
DEPRECATED: multi-agent loop removed by single-shot refactor.

This module previously coordinated planner/executor/critic-based
task execution. The new workflow generates a single coordinated
script via `primr.agents.coder.generate` and validates/repairs with
`primr.agents.validator` and `primr.agents.critic` from the operator.

If you are still importing functions from here, update to use the
new single-shot APIs. Calls to the previous `run_agent` or
`execute_ready_tasks` will raise a RuntimeError to make the
deprecation explicit.
"""


def execute_ready_tasks(*args, **kwargs):
    raise RuntimeError(
        "execute_ready_tasks() is deprecated. Use the single-shot coder flow in operators."
    )


def run_agent(*args, **kwargs):
    raise RuntimeError(
        "run_agent() is deprecated. Use primr.agents.coder.generate from operators."
    )

