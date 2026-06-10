import os
from absl import app, flags
import dotenv
import vertexai
from vertexai import agent_engines

from store.agent import root_agent

FLAGS = flags.FLAGS
flags.DEFINE_string("project_id", None, "Google Cloud project ID.")
flags.DEFINE_string("location", None, "Google Cloud location.")
flags.DEFINE_string("bucket", None, "Google Cloud bucket.")
flags.DEFINE_string("resource_id", None, "ReasoningEngine resource ID.")

flags.DEFINE_bool("list", False, "List all agents.")
flags.DEFINE_bool("create", False, "Creates a new agent.")
flags.DEFINE_bool("delete", False, "Deletes an existing agent.")
flags.mark_bool_flags_as_mutual_exclusive(["create", "delete"])


REQUIREMENTS = [
    "google-adk[a2a]>=2.2.0",
    "google-cloud-aiplatform[adk,agent-engines]>=1.157.0",
    "requests>=2.34.2",
]
EXTRA_PACKAGES = ["./store"]


def create_or_update() -> None:
    """Creates a new agent engine, or updates it if one with the same display name already exists."""
    adk_app = agent_engines.AdkApp(agent=root_agent, enable_tracing=True)

    agent_config = {
        "agent_engine": adk_app,
        "display_name": root_agent.name,
        "requirements": REQUIREMENTS,
        "extra_packages": EXTRA_PACKAGES,
    }

    existing = list(agent_engines.list(filter=f"display_name={root_agent.name}"))
    if existing:
        remote_agent = existing[0]
        print(f"Found existing agent: {remote_agent.resource_name} — updating...")
        remote_agent.update(**agent_config)
        print(f"Updated remote agent: {remote_agent.resource_name}")
    else:
        remote_agent = agent_engines.create(**agent_config)
        print(f"Created remote agent: {remote_agent.resource_name}")


def delete(resource_id: str) -> None:
    remote_agent = agent_engines.get(resource_id)
    remote_agent.delete(force=True)
    print(f"Deleted remote agent: {resource_id}")


def list_agents() -> None:
    remote_agents = agent_engines.list()
    template = """
{agent.name} ("{agent.display_name}")
- Create time: {agent.create_time}
- Update time: {agent.update_time}
"""
    remote_agents_string = "\n".join(
        template.format(agent=agent) for agent in remote_agents
    )
    print(f"All remote agents:\n{remote_agents_string}")


def main(argv: list[str]) -> None:
    del argv  # unused
    dotenv.load_dotenv()

    project_id = (
        FLAGS.project_id if FLAGS.project_id else os.getenv("GOOGLE_CLOUD_PROJECT")
    )
    location = FLAGS.location if FLAGS.location else os.getenv("GOOGLE_CLOUD_LOCATION")
    bucket = FLAGS.bucket if FLAGS.bucket else os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")

    if not project_id:
        print("Missing required environment variable: GOOGLE_CLOUD_PROJECT")
        return
    elif not location:
        print("Missing required environment variable: GOOGLE_CLOUD_LOCATION")
        return
    elif not bucket:
        print("Missing required environment variable: GOOGLE_CLOUD_STORAGE_BUCKET")
        return

    print(f"PROJECT: {project_id}")
    print(f"LOCATION: {location}")
    print(f"BUCKET: {bucket}")

    vertexai.init(
        project=project_id,
        location=location,
        staging_bucket=f"gs://{bucket}",
    )

    if FLAGS.list:
        list_agents()
    elif FLAGS.create:
        create_or_update()
    elif FLAGS.delete:
        if not FLAGS.resource_id:
            print("resource_id is required for delete")
            return
        delete(FLAGS.resource_id)
    else:
        print("Unknown command")


if __name__ == "__main__":
    app.run(main)
