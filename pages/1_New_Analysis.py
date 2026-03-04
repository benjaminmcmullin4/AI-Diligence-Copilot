"""New Analysis -- Input form for submitting a diligence request."""

import uuid

import streamlit as st

st.set_page_config(
    page_title="New Analysis | Meridian",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
)

from components.styles import inject_custom_css
from core.config import get_settings
from core.database import init_db, save_analysis
from schemas.input import AnalysisRequest, BusinessModelType

inject_custom_css()
settings = get_settings()
init_db(settings.db_path)

from core.auth import require_auth
require_auth(settings)

# ── Header ──
st.markdown(
    """
    <div class="brand-header">
        <span class="brand-name">Meridian</span>
        <span class="tagline">New Analysis</span>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("---")

# ── Business Model Toggle ──
model_choice = st.radio(
    "Business Model",
    options=["SaaS", "Non-SaaS"],
    horizontal=True,
    help="Select the target company's business model type.",
)
business_model = BusinessModelType.SAAS if model_choice == "SaaS" else BusinessModelType.NON_SAAS

# ── Company Basics ──
st.subheader("Company Information")
col1, col2 = st.columns(2)
with col1:
    company_name = st.text_input("Company Name *", placeholder="e.g., Acme Corp")
with col2:
    website_url = st.text_input("Website URL", placeholder="https://www.example.com")
    fetch_website = st.checkbox("Fetch website content for analysis", value=True)

# ── Financial Inputs ──
st.subheader("Financial Data")

if business_model == BusinessModelType.SAAS:
    st.caption("SaaS-specific financial metrics. Leave blank if unknown.")
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        arr = st.number_input("ARR ($M)", min_value=0.0, value=None, step=0.1, format="%.1f")
        nrr = st.number_input("Net Revenue Retention (%)", min_value=0.0, max_value=300.0, value=None, step=0.1)
        grr = st.number_input("Gross Revenue Retention (%)", min_value=0.0, max_value=100.0, value=None, step=0.1)
    with fc2:
        customer_count = st.number_input("Total Customers", min_value=0, value=None, step=1)
        acv = st.number_input("Average Contract Value ($K)", min_value=0.0, value=None, step=0.1)
        yoy_growth = st.number_input("YoY Growth (%)", min_value=-100.0, value=None, step=0.1)
    with fc3:
        gross_margin = st.number_input("Gross Margin (%)", min_value=0.0, max_value=100.0, value=None, step=0.1)
        cac_payback = st.number_input("CAC Payback (months)", min_value=0.0, value=None, step=0.1)
        ltv_cac = st.number_input("LTV/CAC Ratio", min_value=0.0, value=None, step=0.1)

    # Non-SaaS fields set to None
    revenue = ebitda = ebitda_margin = fcf = same_store_growth = None
    unit_count = None
else:
    st.caption("Non-SaaS financial metrics. Leave blank if unknown.")
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        revenue = st.number_input("Revenue ($M)", min_value=0.0, value=None, step=0.1, format="%.1f")
        ebitda = st.number_input("EBITDA ($M)", min_value=-1000.0, value=None, step=0.1, format="%.1f")
    with fc2:
        ebitda_margin = st.number_input("EBITDA Margin (%)", min_value=-100.0, max_value=100.0, value=None, step=0.1)
        fcf = st.number_input("Free Cash Flow ($M)", min_value=-1000.0, value=None, step=0.1, format="%.1f")
    with fc3:
        unit_count = st.number_input("Number of Units/Locations", min_value=0, value=None, step=1)
        same_store_growth = st.number_input("Same-Store Growth (%)", min_value=-100.0, value=None, step=0.1)

    # SaaS fields set to None
    arr = nrr = grr = acv = yoy_growth = gross_margin = cac_payback = ltv_cac = None
    customer_count = None

# ── Qualitative Inputs ──
st.subheader("Qualitative Information")
st.caption("Provide as much context as possible for a richer analysis.")

company_description = st.text_area(
    "Company Description",
    placeholder="What does the company do? Who are its customers? Key products?",
    height=120,
)
internal_notes = st.text_area(
    "Internal Notes / IC Discussion Points",
    placeholder="Your team's preliminary thoughts, concerns, or areas of focus.",
    height=100,
)

col_q1, col_q2 = st.columns(2)
with col_q1:
    customer_reviews = st.text_area(
        "Customer Reviews / NPS Feedback",
        placeholder="Paste customer reviews, G2 feedback, NPS comments, etc.",
        height=120,
    )
    management_bios = st.text_area(
        "Management Bios",
        placeholder="Key team members, backgrounds, tenure, track record.",
        height=120,
    )
with col_q2:
    call_transcripts = st.text_area(
        "Call Transcripts / Expert Network Notes",
        placeholder="Paste relevant call notes, expert network transcripts, etc.",
        height=120,
    )
    known_competitors = st.text_area(
        "Known Competitors",
        placeholder="List competitors you're already aware of, separated by commas or newlines.",
        height=120,
    )

# ── File Upload ──
st.subheader("Document Upload")
uploaded_file = st.file_uploader(
    "Upload supplementary documents (.txt, .md)",
    type=["txt", "md"],
    help="Text files will be read and appended to the analysis context.",
)
uploaded_text = ""
if uploaded_file is not None:
    try:
        uploaded_text = uploaded_file.read().decode("utf-8")
        st.success(f"Loaded {len(uploaded_text):,} characters from {uploaded_file.name}")
    except Exception as e:
        st.error(f"Could not read file: {e}")

# ── Submit ──
st.markdown("---")

if st.button("Generate Diligence", type="primary", use_container_width=True):
    if not company_name.strip():
        st.error("Company name is required.")
        st.stop()

    if not settings.has_api_key:
        st.error("Anthropic API key is not configured. Add `ANTHROPIC_API_KEY` to your `.env` file.")
        st.stop()

    # Build the analysis request
    request = AnalysisRequest(
        company_name=company_name.strip(),
        business_model=business_model,
        website_url=website_url.strip(),
        fetch_website=fetch_website,
        arr=arr,
        nrr=nrr,
        grr=grr,
        customer_count=customer_count,
        acv=acv,
        yoy_growth=yoy_growth,
        gross_margin=gross_margin,
        cac_payback=cac_payback,
        ltv_cac=ltv_cac,
        revenue=revenue,
        ebitda=ebitda,
        ebitda_margin=ebitda_margin,
        fcf=fcf,
        unit_count=unit_count,
        same_store_growth=same_store_growth,
        company_description=company_description,
        internal_notes=internal_notes,
        customer_reviews=customer_reviews,
        call_transcripts=call_transcripts,
        management_bios=management_bios,
        known_competitors=known_competitors,
        uploaded_text=uploaded_text,
    )

    analysis_id = str(uuid.uuid4())

    # Save initial record to DB
    save_analysis(settings.db_path, analysis_id, {
        "company_name": request.company_name,
        "business_model": request.business_model.value,
        "status": "running",
        "request_json": request.model_dump_json(),
    })

    # Run pipeline with progress display
    with st.status("Running diligence pipeline...", expanded=True) as status_display:
        try:
            from pipeline.orchestrator import run_pipeline
        except ImportError:
            st.error("Pipeline module not found. Ensure `pipeline/orchestrator.py` exists.")
            save_analysis(settings.db_path, analysis_id, {
                "status": "failed", "error_message": "Pipeline module not found",
            })
            st.stop()

        stage_labels = {
            "website_fetch": "Fetching website content...",
            "stage_a": "Stage A: Condensing and classifying inputs...",
            "stage_b": "Stage B: Generating structured analysis...",
            "stage_c": "Stage C: Rendering IC memo...",
        }

        def _progress(stage: str, status: str) -> None:
            if status == "running" and stage in stage_labels:
                st.write(stage_labels[stage])

        try:
            result = run_pipeline(request, analysis_id, progress_callback=_progress)

            if result["status"] == "completed":
                status_display.update(label="Diligence complete!", state="complete", expanded=False)
                st.query_params["analysis_id"] = analysis_id
                st.switch_page("pages/2_Analysis_View.py")
            else:
                status_display.update(label="Pipeline failed", state="error")
                st.error(f"Pipeline error: {result.get('error', 'Unknown error')}")

        except Exception as e:
            status_display.update(label="Pipeline failed", state="error")
            save_analysis(settings.db_path, analysis_id, {
                "status": "failed", "error_message": str(e),
            })
            st.error(f"Pipeline error: {e}")
