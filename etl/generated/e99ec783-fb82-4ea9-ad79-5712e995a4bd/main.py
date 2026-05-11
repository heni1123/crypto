import argparse
import asyncio
import logging
import signal
import time
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ETLPipeline:
    def __init__(self, config: str, dry_run: bool, phase: str) -> None:
        self.config = config
        self.dry_run = dry_run
        self.phase = phase

    async def extract(self) -> int:
        # Extraction logic here
        return 50  # Example row count

    async def transform(self, row_count: int) -> int:
        # Transformation logic here
        return row_count  # Example row count

    async def load(self, row_count: int) -> None:
        # Loading logic here
        pass

    async def run(self) -> int:
        start_time = time.time()
        try:
            extracted_rows = await self.extract()
            transformed_rows = await self.transform(extracted_rows)
            await self.load(transformed_rows)
            return 0  # Success
        except Exception as e:
            logger.error(f"ETL process failed: {e}")
            return 2  # Failed
        finally:
            duration = time.time() - start_time
            logger.info(f"ETL completed in {duration:.2f} seconds with {extracted_rows} rows extracted and {transformed_rows} rows loaded.")

async def main() -> None:
    parser = argparse.ArgumentParser(description="ETL Pipeline for Crypto Market Data")
    parser.add_argument("--config", required=True, help="Path to the configuration file")
    parser.add_argument("--dry-run", action="store_true", help="Run the pipeline in dry run mode")
    parser.add_argument("--phase", choices=["extract", "transform", "load"], help="Specify the phase to run")
    args = parser.parse_args()

    pipeline = ETLPipeline(config=args.config, dry_run=args.dry_run, phase=args.phase)

    exit_code = await pipeline.run()
    exit(exit_code)

def signal_handler(sig: int, frame: Any) -> None:
    logger.info("Graceful shutdown initiated.")
    exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    asyncio.run(main())