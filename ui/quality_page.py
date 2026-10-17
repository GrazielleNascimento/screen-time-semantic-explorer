"""
quality_page.py - Mostra o relatório de qualidade gerado por src/run_quality.py.
"""

import streamlit as st

from ui.components import empty_state, kpi_card, page_header

SIDE_BY_SIDE = ("Before cleaning", "After cleaning")


def split_sections(report_text: str) -> tuple[str, dict[str, str]]:
    """Separa o cabeçalho do relatório e cada seção '## Título' (só apresentação)."""
    head, *parts = report_text.split("\n## ")
    sections = {}
    for part in parts:
        title, _, body = part.partition("\n")
        sections[title.strip()] = body.strip()
    return head, sections


def render(total_chunks: int, n_removed: int, report_text: str | None) -> None:
    """Desenha KPIs e o relatório; `report_text` é None se o relatório não existe."""
    page_header("Quality report", "What the Isolation Forest flagged, and how the database looked before and after cleaning.")

    if report_text is None:
        empty_state("🛡️", "No report yet", "Generate it with: python src/run_quality.py")
        return

    original_total = total_chunks + n_removed
    removed_pct = 100 * n_removed / original_total if original_total else 0.0
    cols = st.columns(4)
    with cols[0]:
        kpi_card("Chunks before cleaning", f"{original_total:,}", "📄", "primary")
    with cols[1]:
        kpi_card("Chunks removed", f"{n_removed:,}", "🧹", "warning")
    with cols[2]:
        kpi_card("Chunks after cleaning", f"{total_chunks:,}", "✅", "success")
    with cols[3]:
        kpi_card("Share removed", f"{removed_pct:.2f}%", "📉", "danger")

    head, sections = split_sections(report_text)
    head = head.split("\n", 1)[1] if head.startswith("# ") else head  # o título já está no cabeçalho da página
    with st.container(key="card_report_head"):
        st.markdown(head)

    left, right = st.columns(2)
    for col, title in zip((left, right), SIDE_BY_SIDE):
        with col.container(key=f"card_{title.split()[0].lower()}"):
            st.markdown(f"#### {title}")
            st.markdown(sections.get(title, ""))

    for title, body in sections.items():
        if title not in SIDE_BY_SIDE:
            with st.container(key=f"card_{title.split()[0].lower()}_{len(title)}"):
                st.markdown(f"#### {title}")
                st.markdown(body)
