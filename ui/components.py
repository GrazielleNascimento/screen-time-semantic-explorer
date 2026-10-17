"""
components.py - Componentes visuais pequenos e reutilizáveis (HTML via st.markdown).

Todo texto que pode vir dos PDFs passa por html.escape. Nenhuma regra de negócio aqui.
"""

import base64
import html
from pathlib import Path
from typing import Callable

import streamlit as st

def _html(markup: str) -> None:
    st.markdown(markup, unsafe_allow_html=True)


def chips(terms: list[str]) -> str:
    """HTML de uma lista de termos como 'chips'."""
    return "".join(f'<span class="chip">{html.escape(term)}</span>' for term in terms)


def page_header(title: str, description: str) -> None:
    """Título da página (st.title) + descrição curta."""
    st.title(title)
    _html(f'<div class="page-header"><p>{html.escape(description)}</p></div>')


def section_title(text: str) -> None:
    _html(f'<div class="section-title">{html.escape(text)}</div>')


def kpi_card(label: str, value: str, icon: str, tone: str = "primary") -> None:
    """Card de métrica: ícone em círculo colorido, número grande e rótulo cinza."""
    _html(
        f'<div class="card kpi"><div class="kpi-icon tone-{tone}">{icon}</div><div>'
        f'<div class="metric-value">{html.escape(value)}</div>'
        f'<div class="metric-label">{html.escape(label)}</div></div></div>'
    )


def action_card(icon: str, title: str, description: str, button_label: str,
                on_click: Callable, args: tuple) -> None:
    """Card de ação: ícone, título, descrição e botão (o clique chama `on_click(*args)`)."""
    with st.container(key=f"action_{title}"):
        _html(
            f'<div class="action-icon">{icon}</div>'
            f'<div class="action-title">{html.escape(title)}</div>'
            f'<div class="action-desc">{html.escape(description)}</div>'
        )
        st.button(button_label, key=f"open_{title}", on_click=on_click, args=args, width="stretch")


@st.cache_data
def _svg_data_uri(path: str) -> str | None:
    """Data URI base64 do SVG, ou None se o arquivo não existir."""
    file = Path(path)
    if not file.exists():
        return None
    return "data:image/svg+xml;base64," + base64.b64encode(file.read_bytes()).decode()


def topic_card(index: int, title: str, text: str, svg_path: Path, emoji: str, color: str,
               tint: str, border: str, on_click: Callable, args: tuple) -> None:
    """Card de tema: ilustração (ou emoji), título, frase e botão. `tint` e `border` pintam o card (junto com `color`)."""
    uri = _svg_data_uri(str(svg_path))
    picture = f'<img src="{uri}" alt="">' if uri else f'<span class="topic-emoji">{emoji}</span>'
    with st.container(key=f"topic_{index}"):
        _html(f"<style>.st-key-topic_{index} {{ background: {tint}; border-color: {border}; }}</style>")
        _html(
            f'<div class="topic-img" style="background:{color}">{picture}</div>'
            f'<div class="action-title">{html.escape(title)}</div>'
            f'<div class="action-desc">{html.escape(text)}</div>'
        )
        st.button("Ask about this topic", key=f"ask_{index}", on_click=on_click, args=args, width="stretch")


def result_card(rank: int, source_file: str, chunk_idx: int, distance: float, text: str) -> None:
    """Card de resultado da busca: número, PDF, chunk, distância, barra de similaridade e texto."""
    similarity = max(0.0, min(1.0, 1 - distance))  # distância de cosseno -> similaridade 0..1
    _html(
        f'<div class="card"><div class="result-head">'
        f'<span class="result-rank">#{rank}</span>'
        f'<span class="result-meta">{html.escape(source_file)} · chunk {chunk_idx} · '
        f'distance {distance:.4f}</span></div>'
        f'<div class="result-text">{html.escape(text)}</div>'
        f'<div class="sim-track"><div class="sim-fill" style="width:{similarity * 100:.0f}%"></div></div>'
        f'<div class="sim-label">similarity {similarity:.0%}</div></div>'
    )


def empty_state(emoji: str, title: str, text: str) -> None:
    """Estado vazio amigável."""
    _html(
        f'<div class="card empty"><div class="emoji">{emoji}</div>'
        f'<div class="action-title">{html.escape(title)}</div><div>{html.escape(text)}</div></div>'
    )


def sidebar_brand() -> None:
    """Bloco de marca no topo da sidebar."""
    _html(
        '<div class="brand"><div class="brand-icon">🔎</div><div>'
        '<div class="brand-name">Semantic Explorer</div>'
        '<div class="brand-sub">Screen time &amp; children research</div></div></div>'
    )


def sidebar_footer() -> None:
    """Rodapé da sidebar."""
    _html('<div class="sidebar-footer">v1.0 · Powered by ChromaDB · MiniLM</div>')


def footer() -> None:
    """Rodapé único e fino em todas as páginas."""
    _html(
        '<div class="page-footer">'
        '© 2026 Grazielle Nascimento Ferreira'
        '</div>'
    )
