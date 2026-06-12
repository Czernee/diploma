from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from configurator.catalog import ProductCatalogProvider
from configurator.ml import MLConfigurationRanker


def main() -> None:
    provider = ProductCatalogProvider()
    catalog = provider.load_catalog()

    ranker = MLConfigurationRanker()
    ranker.ensure_trained(catalog)
    if ranker.metrics is None:
        raise RuntimeError("Model training did not produce metrics")

    artifact_dir = Path("ml_artifacts")
    artifact_dir.mkdir(exist_ok=True)
    ranker.save_artifact(artifact_dir / "configuration_ranker.joblib")
    (artifact_dir / "configuration_ranker_metrics.json").write_text(
        json.dumps(asdict(ranker.metrics), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(asdict(ranker.metrics), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
