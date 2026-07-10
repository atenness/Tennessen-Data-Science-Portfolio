from __future__ import annotations

import base64
import html
import json
import re
import uuid
from datetime import date, datetime
from pathlib import Path
import time
from urllib.parse import urlparse

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from io import BytesIO


APP_DIR = Path(__file__).resolve().parent
SETTINGS_DIR = Path.home() / ".leo_linkedin_download_dashboard"
PROJECTS_PATH = SETTINGS_DIR / "download_projects.json"
DEFAULT_LOG_NAME = "download_review_log.csv"
LOGO_PATH = APP_DIR / "assets" / "LEO_Primary_Logo_Dot_2C_PMS_Partner_Lockup.png"
PARTNER_LOGO_DIR = APP_DIR / "assets" / "Partner Logos"

NAVY = "#0b2240"
GOLD = "#cb9700"
GREEN = "#16a34a"
GRAY = "#6b7280"
USER_FIRST_NAME = "Intern"


def cell_text(value: object) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    return str(value).strip()


def clean_path(raw_path: str) -> Path:
    return Path(raw_path.strip().strip('"').strip("'")).expanduser()


def is_inside_app_dir(path: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(APP_DIR)
        return True
    except ValueError:
        return False


def compact_normalized(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", "", cell_text(value).lower())


def matching_column(columns: list[str], candidates: list[str]) -> str | None:
    normalized_columns = {compact_normalized(column): column for column in columns}
    for candidate in candidates:
        column = normalized_columns.get(compact_normalized(candidate))
        if column is not None:
            return column
    return None


def row_value(row: pd.Series, candidates: list[str]) -> str:
    column = matching_column(row.index.tolist(), candidates)
    if column is None:
        return ""
    return cell_text(row.get(column, ""))


def filename_part(value: object) -> str:
    text = re.sub(r"[^\w.-]+", "_", cell_text(value))
    text = text.strip("._")
    return text or "missing_id"


def default_study_id_column(columns: list[str]) -> str:
    for candidate in ["exp_leoid", "study_id", "studyid", "leo_id", "participant_id", "id"]:
        column = matching_column(columns, [candidate])
        if column is not None:
            return column
    for column in columns:
        lowered = column.lower()
        if ("study" in lowered and "id" in lowered) or ("leo" in lowered and "id" in lowered):
            return column
    return columns[0] if columns else ""


def detected_link_columns(columns: list[str]) -> list[str]:
    preferred = [
        "link1",
        "link2",
        "link3",
        "url1",
        "url2",
        "url3",
        "profile1",
        "profile2",
        "profile3",
        "linkedin_url1",
        "linkedin_url2",
        "linkedin_url3",
    ]
    detected: list[str] = []
    for candidate in preferred:
        column = matching_column(columns, [candidate])
        if column is not None and column not in detected:
            detected.append(column)
    for column in columns:
        normalized = compact_normalized(column)
        if column in detected:
            continue
        if "link" in normalized or "url" in normalized:
            detected.append(column)
    return detected


def rank_for_link_column(column: str, fallback_position: int) -> int:
    patterns = [
        r"(?:link|url|profile|candidate|result)[_\-\s#]*([0-9]+)\b",
        r"\b([0-9]+)\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, cell_text(column), flags=re.IGNORECASE)
        if match:
            try:
                rank = int(match.group(1))
                if rank > 0:
                    return rank
            except ValueError:
                pass
    return fallback_position + 1


def build_filename(study_id: object, link_rank: int, download_date: date | None = None) -> str:
    download_date = download_date or date.today()
    return f"{filename_part(study_id)}-url{link_rank}-{download_date:%Y%m%d}"


def normalize_url(value: object) -> str:
    text = cell_text(value)
    if not text:
        return ""
    if re.match(r"^https?://", text, flags=re.IGNORECASE):
        return text
    if text.lower().startswith("www."):
        return f"https://{text}"
    if "." in text and " " not in text:
        return f"https://{text}"
    return text


def is_openable_url(value: object) -> bool:
    parsed = urlparse(normalize_url(value))
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def project_name_from_path(path_text: str) -> str:
    path = clean_path(path_text) if path_text.strip() else Path("")
    text = compact_normalized(path_text)
    if "npower" in text:
        return "NPower"
    if path.stem:
        clean_name = re.sub(r"[_-]+", " ", path.stem).strip()
        return clean_name[:1].upper() + clean_name[1:] if clean_name else "Project"
    return "Project"


def image_data_uri(path: Path) -> str:
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def partner_logo_path(project_name: str) -> Path | None:
    if not PARTNER_LOGO_DIR.exists():
        return None
    normalized_project = compact_normalized(project_name)
    candidates = [
        PARTNER_LOGO_DIR / f"{project_name}_logo.png",
        PARTNER_LOGO_DIR / f"{project_name}.png",
        PARTNER_LOGO_DIR / f"{project_name}_logo.jpg",
        PARTNER_LOGO_DIR / f"{project_name}.jpg",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    for candidate in PARTNER_LOGO_DIR.iterdir():
        if not candidate.is_file():
            continue
        normalized_name = compact_normalized(candidate.stem)
        if normalized_name in {normalized_project, f"{normalized_project}logo"}:
            return candidate
    return None


def render_logo_pair(project_name: str) -> str:
    pieces = []
    if LOGO_PATH.exists():
        try:
            pieces.append(
                f'<img class="leo-logo" src="{image_data_uri(LOGO_PATH)}" alt="LEO logo">'
            )
        except Exception:
            pass
    partner_path = partner_logo_path(project_name)
    if partner_path is not None:
        try:
            pieces.append(
                f'<img class="partner-logo" src="{image_data_uri(partner_path)}" '
                f'alt="{html.escape(project_name)} logo">'
            )
        except Exception:
            pass
    return "".join(pieces)


def render_project_badge(project_name: str) -> str:
    logo_path = partner_logo_path(project_name)
    if logo_path is not None:
        try:
            return f'<img class="project-badge-logo" src="{image_data_uri(logo_path)}" alt="{html.escape(project_name)}">'
        except Exception:
            pass
    label = html.escape(project_name[:12] if project_name else "Project")
    return f'<span class="project-badge-text">{label}</span>'


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def display_datetime(value: object) -> str:
    text = cell_text(value)
    if not text:
        return ""
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return text
    return parsed.strftime("%m/%d/%Y %I:%M %p")


def load_projects() -> dict[str, dict[str, object]]:
    if not PROJECTS_PATH.exists():
        return {}
    try:
        raw = json.loads(PROJECTS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}
    if isinstance(raw, dict):
        projects = raw.get("projects", raw)
    else:
        projects = {}
    if not isinstance(projects, dict):
        return {}
    cleaned: dict[str, dict[str, object]] = {}
    for project_id, project in projects.items():
        if isinstance(project, dict):
            cleaned[str(project_id)] = project
    return cleaned


def save_projects(projects: dict[str, dict[str, object]]) -> None:
    SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "projects": projects,
        "saved_at": now_iso(),
    }
    PROJECTS_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def project_progress(project: dict[str, object]) -> tuple[int, int, float]:
    log_path_text = cell_text(project.get("review_log_path", ""))
    if log_path_text:
        log_path = clean_path(log_path_text)
        if log_path.exists():
            try:
                log_df = pd.read_csv(log_path, dtype=str, keep_default_na=False)
                if {"Study ID", "Downloaded"}.issubset(log_df.columns):
                    total_from_log = len(log_df)
                    downloaded_from_log = int((log_df["Downloaded"].apply(yes_no) == "Yes").sum())
                    percent_from_log = (downloaded_from_log / total_from_log * 100) if total_from_log else 0.0
                    return downloaded_from_log, total_from_log, percent_from_log
            except Exception:
                pass
    downloaded = int(project.get("downloaded_participants", 0) or 0)
    total = int(project.get("total_participants", 0) or 0)
    downloaded = min(downloaded, total) if total else downloaded
    percent = (downloaded / total * 100) if total else 0.0
    return downloaded, total, percent


def project_sort_key(project: dict[str, object]) -> str:
    return cell_text(project.get("last_opened", project.get("created_at", "")))


@st.cache_data(show_spinner=False)
def load_first_workbook_sheet(
    file_bytes: bytes,
    file_name: str,
) -> tuple[str, pd.DataFrame]:
    workbook = BytesIO(file_bytes)

    excel = pd.ExcelFile(workbook)
    sheet_name = excel.sheet_names[0]

    workbook.seek(0)

    df = pd.read_excel(
        workbook,
        sheet_name=sheet_name,
        dtype=str,
        keep_default_na=False,
    )

    df.columns = df.columns.astype(str)

    return sheet_name, df


def default_review_log_path(workbook_path_text: str) -> Path:
    workbook_stem = filename_part(clean_path(workbook_path_text).stem).lower()
    if workbook_stem and workbook_stem != "missing_id":
        return APP_DIR / f"{workbook_stem}_{DEFAULT_LOG_NAME}"
    return APP_DIR / DEFAULT_LOG_NAME


def seconds_number(value: object) -> float:
    try:
        return max(0.0, float(cell_text(value) or 0))
    except ValueError:
        return 0.0


def yes_no(value: object) -> str:
    text = compact_normalized(value)
    return "Yes" if text in {"yes", "y", "true", "1"} else "No"


def study_ids_from_df(df: pd.DataFrame, study_id_column: str) -> list[str]:
    values = [cell_text(value) for value in df[study_id_column].tolist()]
    return [value if value else f"row_{idx + 1}" for idx, value in enumerate(values)]


def read_review_log(log_path: Path, study_ids: list[str]) -> pd.DataFrame:
    base = pd.DataFrame(
        {
            "Study ID": study_ids,
            "Time": [0.0] * len(study_ids),
            "Downloaded": ["No"] * len(study_ids),
        }
    )
    if not log_path.exists():
        return base
    try:
        existing = pd.read_csv(log_path, dtype=str, keep_default_na=False)
    except Exception:
        return base
    if "Study ID" not in existing.columns:
        return base

    existing = existing.copy()
    if "Time" not in existing.columns:
        existing["Time"] = "0"
    if "Downloaded" not in existing.columns:
        existing["Downloaded"] = "No"

    existing_map = {
        cell_text(row["Study ID"]): {
            "Time": seconds_number(row.get("Time", 0)),
            "Downloaded": yes_no(row.get("Downloaded", "No")),
        }
        for _, row in existing.iterrows()
    }
    for idx, study_id in enumerate(study_ids):
        prior = existing_map.get(study_id)
        if prior is None:
            continue
        base.at[idx, "Time"] = prior["Time"]
        base.at[idx, "Downloaded"] = prior["Downloaded"]
    return base


def write_review_log(log_path: Path, review_log: pd.DataFrame) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    output = review_log.loc[:, ["Study ID", "Time", "Downloaded"]].copy()
    output["Time"] = output["Time"].apply(lambda value: f"{seconds_number(value):.1f}")
    output["Downloaded"] = output["Downloaded"].apply(yes_no)
    output.to_csv(log_path, index=False)


def mark_participant_downloaded(
    review_log: pd.DataFrame,
    row_index: int,
    elapsed_seconds: float,
) -> pd.DataFrame:
    updated = review_log.copy()
    current_time = seconds_number(updated.at[row_index, "Time"])
    updated.at[row_index, "Time"] = current_time + max(0.0, elapsed_seconds)
    updated.at[row_index, "Downloaded"] = "Yes"
    return updated


def participant_progress(review_log: pd.DataFrame) -> tuple[int, int, float]:
    total = len(review_log)
    downloaded = int((review_log["Downloaded"].apply(yes_no) == "Yes").sum()) if total else 0
    percent = (downloaded / total * 100) if total else 0.0
    return downloaded, total, percent


def first_pending_index(review_log: pd.DataFrame) -> int:
    pending = review_log.index[review_log["Downloaded"].apply(yes_no) != "Yes"].tolist()
    if pending:
        return int(pending[0])
    return max(0, len(review_log) - 1)


def ensure_project(
    projects: dict[str, dict[str, object]],
    workbook_path: str,
    review_log_path: str,
    study_id_column: str,
    downloaded_participants: int,
    total_participants: int,
    row_index: int,
) -> dict[str, object]:
    active_id = st.session_state.get("active_download_project_id")
    existing = projects.get(active_id) if active_id else None
    if existing is not None:
        project = existing
    else:
        active_id = str(uuid.uuid4())
        project = {
            "id": active_id,
            "name": project_name_from_path(workbook_path),
            "workbook_path": workbook_path,
            "review_log_path": review_log_path,
            "study_id_column": study_id_column,
            "created_at": now_iso(),
        }
        projects[active_id] = project
        st.session_state["active_download_project_id"] = active_id

    project["id"] = active_id
    project["name"] = cell_text(project.get("name", "")) or project_name_from_path(workbook_path)
    project["workbook_path"] = workbook_path
    project["review_log_path"] = review_log_path
    project["study_id_column"] = study_id_column
    project["row_index"] = int(row_index)
    project["downloaded_participants"] = int(downloaded_participants)
    project["total_participants"] = int(total_participants)
    project["last_opened"] = now_iso()
    save_projects(projects)
    return project


def save_project_state(
    projects: dict[str, dict[str, object]],
    project: dict[str, object],
    row_index: int,
    downloaded_participants: int | None = None,
    total_participants: int | None = None,
) -> None:
    project_id = cell_text(project.get("id", ""))
    if not project_id:
        return
    project["row_index"] = int(row_index)
    project["last_opened"] = now_iso()
    if downloaded_participants is not None:
        project["downloaded_participants"] = int(downloaded_participants)
    if total_participants is not None:
        project["total_participants"] = int(total_participants)
    projects[project_id] = project
    save_projects(projects)


def render_copy_button(text: str, label: str, key: str) -> None:
    safe_text = json.dumps(text)
    safe_id = re.sub(r"[^a-zA-Z0-9_-]+", "-", key)
    components.html(
        f"""
        <button id="copy-{safe_id}" type="button">{html.escape(label)}</button>
        <span id="status-{safe_id}" aria-live="polite"></span>
        <style>
            body {{
                margin: 0;
                font-family: Arial, sans-serif;
            }}
            button {{
                background: {NAVY};
                border: 1px solid {NAVY};
                border-radius: 6px;
                color: white;
                cursor: pointer;
                font-size: 0.88rem;
                font-weight: 700;
                min-height: 46px;
                padding: 0.35rem 0.7rem;
                width: 100%;
            }}
            button:active {{
                transform: translateY(1px);
            }}
            span {{
                color: {GREEN};
                display: block;
                font-size: 0.78rem;
                font-weight: 700;
                min-height: 1rem;
                padding-top: 0.15rem;
                text-align: center;
            }}
        </style>
        <script>
            const button = document.getElementById("copy-{safe_id}");
            const status = document.getElementById("status-{safe_id}");
            async function copyText() {{
                try {{
                    await navigator.clipboard.writeText({safe_text});
                    status.textContent = "Copied";
                }} catch (error) {{
                    const box = document.createElement("textarea");
                    box.value = {safe_text};
                    box.style.position = "fixed";
                    box.style.opacity = "0";
                    document.body.appendChild(box);
                    box.focus();
                    box.select();
                    try {{
                        document.execCommand("copy");
                        status.textContent = "Copied";
                    }} catch (fallbackError) {{
                        status.textContent = "Select the filename above";
                    }}
                    document.body.removeChild(box);
                }}
                window.setTimeout(() => {{
                    status.textContent = "";
                }}, 1600);
            }}
            button.addEventListener("click", copyText);
        </script>
        """,
        height=58,
    )


def apply_css() -> None:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: #fbfbfc;
            color: #111827;
        }}
        div[data-testid="stSidebar"] {{
            background: #ffffff;
            border-right: 1px solid #e5e7eb;
        }}
        h1, h2, h3 {{
            color: {NAVY};
            letter-spacing: 0;
        }}
        button[kind="primary"],
        button[data-testid="stBaseButton-primary"],
        a[data-testid="stLinkButton"] {{
            background: {NAVY} !important;
            border-color: {NAVY} !important;
            color: white !important;
        }}
        a[data-testid="stLinkButton"] p {{
            color: white !important;
        }}
        div[data-testid="stSelectbox"],
        div[data-testid="stSelectbox"] *,
        div[data-baseweb="select"],
        div[data-baseweb="select"] * {{
            cursor: pointer !important;
        }}
        div[data-testid="stSelectbox"] input {{
            caret-color: transparent !important;
        }}
        .main-wrap {{
            margin: 0 auto;
            max-width: 1380px;
        }}
        .dashboard-wrap {{
            margin: 0 auto;
            max-width: 1380px;
        }}
        .launch-wrap {{
            margin: 5.5rem auto 0 auto;
            max-width: 1100px;
        }}
        .launch-title {{
            color: {NAVY};
            font-size: 1.75rem;
            font-weight: 850;
            padding-bottom: 0.7rem;
            border-bottom: 3px solid {GOLD};
        }}
        .launch-copy {{
            color: #374151;
            font-size: 1rem;
            margin: 1.05rem 0 1.9rem 0;
        }}
        .project-row {{
            align-items: center;
            background: white;
            border: 1px solid #d6dde7;
            border-radius: 6px;
            display: grid;
            gap: 0.75rem;
            grid-template-columns: 130px 1.7fr 0.8fr 1.1fr 120px 120px;
            margin-bottom: 0.45rem;
            padding: 0.7rem 0.85rem;
        }}
        .project-badge {{
            align-items: center;
            border: 1px solid #e5e7eb;
            border-radius: 6px;
            display: flex;
            height: 52px;
            justify-content: center;
            overflow: hidden;
        }}
        .project-badge-logo {{
            max-height: 34px;
            max-width: 98px;
            object-fit: contain;
        }}
        .project-badge-text {{
            border: 1px solid #dbe4f0;
            border-radius: 6px;
            color: {NAVY};
            font-size: 0.85rem;
            font-weight: 800;
            padding: 0.28rem 0.55rem;
        }}
        .project-name {{
            color: {NAVY};
            font-size: 1rem;
            font-weight: 850;
        }}
        .project-file {{
            color: #4b5563;
            font-size: 0.82rem;
            overflow-wrap: anywhere;
        }}
        .project-metric {{
            color: {NAVY};
            font-size: 1rem;
            font-weight: 850;
        }}
        .project-sub {{
            color: #4b5563;
            font-size: 0.82rem;
        }}
        .launch-logo {{
            bottom: 1.4rem;
            left: 1.4rem;
            position: fixed;
        }}
        .launch-logo .leo-logo {{
            max-height: 44px;
            max-width: 170px;
        }}
        .header-bar {{
            align-items: center;
            border-bottom: 3px solid {GOLD};
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.75rem;
            padding: 0 0 0.55rem 0;
        }}
        .header-title {{
            color: {NAVY};
            font-size: 1.48rem;
            font-weight: 850;
        }}
        .logo-strip {{
            align-items: center;
            display: flex;
            gap: 0.55rem;
            justify-content: flex-end;
        }}
        .leo-logo {{
            max-height: 42px;
            max-width: 165px;
            object-fit: contain;
        }}
        .partner-logo {{
            max-height: 38px;
            max-width: 120px;
            object-fit: contain;
        }}
        .participant-title {{
            color: {NAVY};
            font-size: 1.2rem;
            font-weight: 850;
            margin: 0.25rem 0 0.1rem 0;
        }}
        .participant-count {{
            color: {GRAY};
            font-size: 0.88rem;
            font-weight: 650;
            margin-bottom: 0.35rem;
        }}
        .empty-link {{
            background: #fff7ed;
            border: 1px solid #fed7aa;
            border-radius: 6px;
            color: #9a3412;
            font-size: 0.85rem;
            font-weight: 700;
            padding: 0.65rem;
            text-align: center;
        }}
        .action-grid {{
            margin-top: 1rem;
        }}
        .open-disabled {{
            align-items: center;
            background: #fee2e2;
            border: 1px solid #fca5a5;
            border-radius: 6px;
            color: #991b1b;
            display: flex;
            font-size: 0.9rem;
            font-weight: 800;
            justify-content: center;
            min-height: 46px;
        }}
        .progress-row {{
            align-items: center;
            display: grid;
            gap: 0.8rem;
            grid-template-columns: minmax(0, 1fr) 118px;
            margin-top: 2.2rem;
        }}
        .progress-shell {{
            background: #e5e7eb;
            border-radius: 6px;
            height: 20px;
            overflow: hidden;
        }}
        .progress-fill {{
            background: {GREEN};
            height: 100%;
        }}
        .progress-label {{
            color: #374151;
            font-size: 0.85rem;
            font-weight: 750;
            margin-bottom: 0.35rem;
        }}
        .percent-box {{
            align-items: center;
            background: white;
            border: 1px solid #d6dde7;
            border-radius: 6px;
            color: {NAVY};
            display: flex;
            font-size: 1rem;
            font-weight: 850;
            justify-content: center;
            min-height: 46px;
        }}
        @media (max-width: 900px) {{
            .project-row {{
                grid-template-columns: 1fr;
            }}
            .progress-row {{
                grid-template-columns: 1fr;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def apply_dashboard_no_scroll_css() -> None:
    st.markdown(
        """
        <style>
        html,
        body,
        div[data-testid="stAppViewContainer"],
        div[data-testid="stAppViewContainer"] > .main {
            overflow: hidden !important;
        }
        div[data-testid="stAppViewContainer"] .main .block-container {
            max-height: 100vh;
            overflow: hidden !important;
            padding-bottom: 0 !important;
            padding-top: 1.75rem !important;
        }
        section[data-testid="stSidebar"] > div {
            overflow: hidden !important;
        }
        div[data-testid="stVerticalBlock"] {
            gap: 0.55rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(project_name: str) -> None:
    st.markdown(
        f"""
        <div class="main-wrap">
            <div class="header-bar">
                <div class="header-title">LinkedIn Profile Download Dashboard</div>
                <div class="logo-strip">{render_logo_pair(project_name)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_launch_page(projects: dict[str, dict[str, object]]) -> None:
    st.markdown('<div class="launch-wrap">', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="launch-title">Welcome, {html.escape(USER_FIRST_NAME)}!</div>
        <div class="launch-copy">Continue working on an existing project below or start a new one.</div>
        """,
        unsafe_allow_html=True,
    )
    st.subheader("Projects")

    ordered_projects = sorted(
        projects.values(),
        key=project_sort_key,
        reverse=True,
    )
    if not ordered_projects:
        st.info("No download projects yet.")

    for project in ordered_projects:
        project_id = cell_text(project.get("id", ""))
        project_name = cell_text(project.get("name", "")) or "Project"
        workbook_path = cell_text(project.get("workbook_path", ""))
        downloaded, total, percent = project_progress(project)
        last_opened = display_datetime(project.get("last_opened", ""))
        file_label = Path(workbook_path).name if workbook_path else "No workbook selected"

        with st.container(border=True):
            row_cols = st.columns([1.1, 3.0, 1.3, 2.2, 1.1, 1.1], gap="small")
            with row_cols[0]:
                st.markdown(
                    f'<div class="project-badge">{render_project_badge(project_name)}</div>',
                    unsafe_allow_html=True,
                )
            with row_cols[1]:
                st.markdown(
                    f"""
                    <div class="project-name">{html.escape(project_name)}</div>
                    <div class="project-file">{html.escape(file_label)}</div>
                    """,
                    unsafe_allow_html=True,
                )
            with row_cols[2]:
                st.markdown(
                    f"""
                    <div class="project-metric">{downloaded}/{total}</div>
                    <div class="project-sub">{percent:.1f}%</div>
                    """,
                    unsafe_allow_html=True,
                )
            with row_cols[3]:
                st.markdown(
                    f"""
                    <div class="project-sub">Last opened</div>
                    <div class="project-metric">{html.escape(last_opened or 'Never')}</div>
                    """,
                    unsafe_allow_html=True,
                )
            with row_cols[4]:
                if st.button("Resume", key=f"resume_{project_id}", type="primary", use_container_width=True):
                    st.session_state["active_download_project_id"] = project_id
                    st.session_state["download_view"] = "dashboard"
                    st.session_state["loaded_download_project_id"] = ""
                    st.rerun()
            with row_cols[5]:
                if st.button("Delete", key=f"delete_{project_id}", use_container_width=True):
                    projects.pop(project_id, None)
                    save_projects(projects)
                    st.rerun()

    if st.button("New Project", use_container_width=True):
        st.session_state["active_download_project_id"] = ""
        st.session_state["download_view"] = "dashboard"
        st.session_state["loaded_download_project_id"] = ""
        st.session_state["download_row_index"] = 0
        st.session_state["download_links_path_input"] = ""
        st.session_state["download_review_log_path_input"] = ""
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    if LOGO_PATH.exists():
        st.markdown(
            f'<div class="launch-logo">{render_logo_pair("")}</div>',
            unsafe_allow_html=True,
        )


def render_action_pair(
    row: pd.Series,
    study_id: str,
    column: str,
    column_position: int,
    row_index: int,
) -> None:
    raw_url = cell_text(row.get(column, ""))
    open_url = normalize_url(raw_url)
    link_rank = rank_for_link_column(column, column_position)
    filename = build_filename(study_id, link_rank)

    if raw_url and is_openable_url(raw_url):
        st.link_button(f"Open URL #{link_rank}", open_url, use_container_width=True)
    else:
        st.markdown(
            f'<div class="open-disabled">URL #{link_rank} Not Found</div>',
            unsafe_allow_html=True,
        )
    render_copy_button(filename, f"Copy File Name #{link_rank}", f"{row_index}-{column}-{filename}")


def go_to_previous_participant(
    projects: dict[str, dict[str, object]],
    project: dict[str, object],
    row_index: int,
    completed_count: int,
    participant_total: int,
) -> None:
    previous_index = max(0, row_index - 1)
    st.session_state["download_row_index"] = previous_index
    st.session_state.pop("participant_timer_key", None)
    save_project_state(projects, project, previous_index, completed_count, participant_total)

def go_to_previous_participant(row_index: int) -> None: 
    st.session_state["download_row_index"] = max(0, row_index - 1) 
    st.session_state.pop("participant_timer_key", None)

def go_to_next_participant(
    row_index: int,
    review_log: pd.DataFrame,
) -> None:
    started_at = float(
        st.session_state.get("participant_started_at", time.time())
    )

    elapsed_seconds = time.time() - started_at

    updated_log = mark_participant_downloaded(
        review_log,
        row_index,
        elapsed_seconds,
    )

    st.session_state["review_log"] = updated_log

    _, participant_total, _ = participant_progress(updated_log)

    next_index = min(
        row_index + 1,
        max(0, participant_total - 1),
    )

    st.session_state["download_row_index"] = next_index
    st.session_state.pop("participant_timer_key", None)


def render_bottom_progress(completed: int, total: int) -> None:
    percent = (completed / total * 100) if total else 0.0
    st.markdown(
        f"""
        <div class="progress-row">
            <div>
                <div class="progress-label">Participants complete: {completed} of {total}</div>
                <div class="progress-shell">
                    <div class="progress-fill" style="width:{percent:.2f}%;"></div>
                </div>
            </div>
            <div class="percent-box">{percent:.1f}%</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(
    page_title="LinkedIn Profile Download Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_css()

projects = load_projects()
st.session_state.setdefault("download_view", "launch")
st.session_state.setdefault("download_row_index", 0)
st.session_state.setdefault("active_download_project_id", "")

if st.session_state.get("download_view") == "launch":
    render_launch_page(projects)
    st.stop()

active_project_id = cell_text(st.session_state.get("active_download_project_id", ""))
active_project = projects.get(active_project_id, {}) if active_project_id else {}

if st.session_state.get("loaded_download_project_id") != active_project_id:
    st.session_state["download_links_path_input"] = cell_text(active_project.get("workbook_path", ""))
    st.session_state["download_review_log_path_input"] = cell_text(active_project.get("review_log_path", ""))
    st.session_state["download_row_index"] = int(active_project.get("row_index", 0) or 0)
    st.session_state["loaded_download_project_id"] = active_project_id

apply_dashboard_no_scroll_css()

with st.sidebar:
    if st.button("Projects", use_container_width=True):
        st.session_state["download_view"] = "launch"
        st.rerun()

    st.divider()

    uploaded_workbook = st.file_uploader(
        "Upload Excel workbook",
        type=["xlsx", "xls"],
        accept_multiple_files=False,
        help="Drag and drop an Excel workbook here.",
    )

workbook_df: pd.DataFrame | None = None
workbook_error = ""
selected_sheet = ""
workbook_source = ""

if uploaded_workbook is not None:
    try:
        file_bytes = uploaded_workbook.getvalue()

        selected_sheet, workbook_df = load_first_workbook_sheet(
            file_bytes,
            uploaded_workbook.name,
        )

        workbook_source = uploaded_workbook.name

    except Exception as exc:
        workbook_error = f"Could not load workbook: {exc}"

project_name = (
    project_name_from_path(uploaded_workbook.name)
    if uploaded_workbook is not None
    else "Project"
)

render_header(project_name)

if workbook_error:
    st.error(workbook_error)
    st.stop()

if workbook_df is None:
    st.info("Upload an Excel workbook in the sidebar.")
    st.stop()

if workbook_df.empty:
    st.warning("The workbook's first sheet has no participant rows.")
    st.stop()

columns = workbook_df.columns.astype(str).tolist()
with st.sidebar:
    st.header("Columns")
    default_id = cell_text(active_project.get("study_id_column", ""))
    if default_id not in columns:
        default_id = default_study_id_column(columns)
    study_id_column = st.selectbox(
        "Study ID column",
        columns,
        index=columns.index(default_id) if default_id in columns else 0,
    )

link_columns = detected_link_columns(columns)[:3]
study_ids = study_ids_from_df(workbook_df, study_id_column)

log_signature = (
    f"{workbook_source}|{study_id_column}|"
    f"{len(workbook_df)}|{'|'.join(study_ids)}"
)

if st.session_state.get("download_log_signature") != log_signature:
    st.session_state["download_log_signature"] = log_signature

    st.session_state["review_log"] = pd.DataFrame(
        {
            "Study ID": study_ids,
            "Time": [0.0] * len(study_ids),
            "Downloaded": ["No"] * len(study_ids),
        }
    )

    st.session_state["download_row_index"] = 0
    st.session_state.pop("participant_timer_key", None)

review_log = st.session_state["review_log"]
review_log_name = (
    f"{Path(uploaded_workbook.name).stem}_download_review_log.csv"
)

row_index = max(0, min(int(st.session_state.get("download_row_index", 0)), len(workbook_df) - 1))
st.session_state["download_row_index"] = row_index
completed_count, participant_total, _ = participant_progress(review_log)

#project = ensure_project(
#    projects=projects,
#    workbook_path=workbook_source,
#    review_log_path="",
#    study_id_column=study_id_column,
#    downloaded_participants=completed_count,
#    total_participants=participant_total,
#    row_index=row_index,
#)

row = workbook_df.iloc[row_index]
study_id = cell_text(row.get(study_id_column, "")) or study_ids[row_index]
timer_key = f"{workbook_source}|{study_id}|{row_index}"
if st.session_state.get("participant_timer_key") != timer_key:
    st.session_state["participant_timer_key"] = timer_key
    st.session_state["participant_started_at"] = time.time()

nav_prev, nav_next, nav_count = st.columns([0.75, 0.75, 2.2], gap="small")
with nav_prev:
    st.button(
        "Previous",
        disabled=row_index <= 0,
        use_container_width=True,
        on_click=go_to_previous_participant,
        args=(row_index,),
    )

with nav_next:
    next_label = (
        "Finish"
        if row_index >= len(workbook_df) - 1
        else "Next"
    )

    st.button(
        next_label,
        type="primary",
        use_container_width=True,
        on_click=go_to_next_participant,
        args=(row_index, review_log),
    )

with nav_count:
    st.markdown(
        f"""
        <div class="participant-title">{html.escape(study_id or "Missing study ID")}</div>
        <div class="participant-count">
            Participant {row_index + 1} of {len(workbook_df)}
        </div>
        """,
        unsafe_allow_html=True,
    )

# Refresh the local variables after button callbacks
review_log = st.session_state["review_log"]
completed_count, participant_total, _ = participant_progress(review_log)

if not link_columns:
    st.warning("No link fields were detected in the workbook's first sheet.")
    render_bottom_progress(completed_count, participant_total)
    st.stop()

st.markdown('<div class="action-grid"></div>', unsafe_allow_html=True)
panel_columns = st.columns(3, gap="small")
for offset in range(3):
    with panel_columns[offset]:
        if offset < len(link_columns):
            render_action_pair(
                row=row,
                study_id=study_id,
                column=link_columns[offset],
                column_position=offset,
                row_index=row_index,
            )
        else:
            st.markdown(
                f'<div class="open-disabled">URL #{offset + 1} Not Found</div>',
                unsafe_allow_html=True,
            )
            render_copy_button(
                build_filename(study_id, offset + 1),
                f"Copy File Name #{offset + 1}",
                f"{row_index}-missing-link-{offset + 1}",
            )

review_log = st.session_state["review_log"]
completed_count, participant_total, _ = participant_progress(review_log)

review_log_csv = review_log.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Review Log",
    data=review_log_csv,
    file_name=review_log_name,
    mime="text/csv",
    use_container_width=True,
)

render_bottom_progress(completed_count, participant_total)