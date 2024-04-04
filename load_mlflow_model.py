import mlflow
from dotenv import load_dotenv
from app.configs.config import Settings


def main() -> None:
    load_dotenv()

    settings = Settings()

    mlflow.set_tracking_uri('https://mlflow-test.pepemoss.com')
    mlflow.artifacts.download_artifacts(
        artifact_uri=settings.model_id, dst_path=f'{settings.app_path}/model'
    )


if __name__ == "__main__":
    main()
