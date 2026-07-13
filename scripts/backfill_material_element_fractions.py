from __future__ import annotations

import argparse

from app.core.database import SessionLocal
from app.services.material.composition_backfill_service import (
    MaterialCompositionBackfillService,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Backfill normalized MaterialElement fractions from structured "
            "Materials Project composition data."
        )
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help=(
            "Commit corrected fractions. Without this option, the script "
            "runs in dry-run mode and rolls back all changes."
        ),
    )

    parser.add_argument(
        "--mp-id",
        type=str,
        default=None,
        help=(
            "Process one Materials Project material only, "
            "for example 'mp-19017'."
        ),
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    db = SessionLocal()

    try:
        service = MaterialCompositionBackfillService(db)

        summary = service.run(
            apply_changes=args.apply,
            mp_id=args.mp_id,
        )

        service.print_summary(
            summary,
            applied=args.apply,
        )
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()