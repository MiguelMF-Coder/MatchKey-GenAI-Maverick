# backend/app/services/notifications/email_service.py

import os
import smtplib
from email.mime.text import MIMEText


def send_selection_email(
    candidate_email: str,
    candidate_name: str,
    job_title: str,
    company_name: str,
) -> None:
    """
    Envía un email al candidato indicando que ha sido preseleccionado.
    Si las variables de entorno de SMTP no están configuradas, hace un simple print (modo dev).
    """

    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    from_email = os.getenv("FROM_EMAIL", smtp_user or "no-reply@matchkey.ai")

    subject = f"Has sido preseleccionado para una vacante en {company_name}"
    body = f"""
Hola {candidate_name or ''},

Tu perfil ha llamado la atención de {company_name} para la posición:

    {job_title}

Un miembro del equipo de RRHH se pondrá en contacto contigo en los próximos días
para agendar una entrevista (telefónica o presencial).

¡Mucha suerte!

El equipo de MatchKey
"""

    # Si no hay configuración SMTP, no rompemos nada: solo logueamos
    if not (smtp_host and smtp_port and from_email):
        print("[send_selection_email] SMTP no configurado. Email simulado:")
        print("---------------------------------------------------")
        print(f"To: {candidate_email}")
        print(f"Subject: {subject}")
        print(body)
        print("---------------------------------------------------")
        return

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = candidate_email

    try:
        with smtplib.SMTP(smtp_host, int(smtp_port)) as server:
            server.starttls()
            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)
            server.sendmail(from_email, [candidate_email], msg.as_string())
        print(f"[send_selection_email] Email enviado a {candidate_email}")
    except Exception as e:
        # No queremos que una caída de SMTP rompa el flujo principal
        print(f"[send_selection_email] Error enviando email: {e}")
