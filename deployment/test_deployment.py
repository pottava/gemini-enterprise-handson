import asyncio
import os
from absl import app, flags
import dotenv
import vertexai
from vertexai import agent_engines

FLAGS = flags.FLAGS

flags.DEFINE_string("project_id", None, "Google Cloud project ID.")
flags.DEFINE_string("location", None, "Google Cloud location.")
flags.DEFINE_string("bucket", None, "Google Cloud bucket.")

flags.DEFINE_string("resource_id", None, "ReasoningEngine resource ID.")
flags.DEFINE_string("user_id", None, "User ID (can be any string).")
flags.mark_flag_as_required("resource_id")
flags.mark_flag_as_required("user_id")


async def run(resource_id: str, user_id: str) -> None:
    agent = agent_engines.get(resource_id)
    print(f"Found agent with resource ID: {resource_id}")

    session = await agent.async_create_session(user_id=user_id)
    print(f"Created session for user ID: {user_id}")

    print("Type 'quit' to exit.")
    while True:
        user_input = input("Input: ")
        if user_input == "quit":
            break

        # print("[DEBUG] Sending query...")
        event_count = 0
        async for event in agent.async_stream_query(
            user_id=user_id, session_id=session["id"], message=user_input
        ):
            event_count += 1
            # print(f"[DEBUG] event #{event_count}: {event}")
            if "content" in event and "parts" in event["content"]:
                for part in event["content"]["parts"]:
                    if "text" in part:
                        print(f"Response: {part['text']}")
        # print(f"[DEBUG] Stream finished. Total events: {event_count}")

    await agent.async_delete_session(user_id=user_id, session_id=session["id"])
    print(f"Deleted session for user ID: {user_id}")


def main(argv: list[str]) -> None:  # pylint: disable=unused-argument

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

    vertexai.init(
        project=project_id,
        location=location,
        staging_bucket=f"gs://{bucket}",
    )

    asyncio.run(run(FLAGS.resource_id, FLAGS.user_id))


if __name__ == "__main__":
    app.run(main)
