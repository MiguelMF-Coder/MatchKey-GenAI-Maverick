# backend/app/db/seed_fake_applications.py

import random
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.candidates import Candidate
from app.models.jobs import Job, Application


def seed_fake_applications(
    min_apps_per_job: int = 1,
    max_apps_per_job: int = 5,
) -> None:
    db: Session = SessionLocal()
    try:
        candidates = db.query(Candidate).all()
        jobs = db.query(Job).all()

        if not candidates or not jobs:
            print("[seed_fake_applications] No hay candidatos o jobs suficientes, saliendo.")
            return

        for job in jobs:
            # Miramos cuántas applications hay ya para no duplicar
            existing_apps = (
                db.query(Application)
                .filter(Application.job_id == job.id)
                .count()
            )

            # Si ya tiene aplicaciones, no tocamos nada
            if existing_apps > 0:
                continue

            n_apps = random.randint(min_apps_per_job, max_apps_per_job)
            sampled_candidates = random.sample(
                candidates,
                min(n_apps, len(candidates))
            )

            for cand in sampled_candidates:
                # Evitar duplicados super raros
                already = (
                    db.query(Application)
                    .filter(
                        Application.job_id == job.id,
                        Application.candidate_id == cand.id,
                    )
                    .first()
                )
                if already:
                    continue

                # Fecha de aplicación falsa (entre 1 y 15 días atrás)
                created_at = datetime.utcnow() - timedelta(days=random.randint(1, 15))

                app = Application(
                    job_id=job.id,
                    candidate_id=cand.id,
                    # Si Application tiene status → lo usamos, si no, quita este campo
                    status="applied",
                    created_at=created_at,
                )
                db.add(app)

        db.commit()
        print("[seed_fake_applications] Aplicaciones falsas generadas correctamente.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_fake_applications()
