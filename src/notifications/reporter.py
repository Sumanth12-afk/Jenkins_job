from __future__ import annotations

from html import escape

from src.core.models import BuildRecord


def build_rebuild_report(records: list[BuildRecord]) -> tuple[str, str]:
    subject = f"Image rebuild report: {len(records)} build(s) completed"
    rows = "\n".join(
        "<tr>"
        f"<td>{escape(record.service_name)}</td>"
        f"<td>{escape(record.status)}</td>"
        f"<td><code>{escape(record.new_tag)}</code></td>"
        f"<td>{escape(record.jenkins_build_url or '')}</td>"
        "</tr>"
        for record in records
    )
    body = f"""
    <h2>CI/CD Image Rebuild Report</h2>
    <p>The following image rebuilds have completed. QA can deploy these exact tags.</p>
    <table border="1" cellspacing="0" cellpadding="6">
      <thead>
        <tr><th>Service</th><th>Status</th><th>New image tag</th><th>Jenkins build</th></tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
    """
    return subject, body
