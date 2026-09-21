import sys
import tempfile
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.pipeline import DocumentIntelligencePipeline


st.set_page_config(
    page_title="Multimodal Document Intelligence",
    page_icon="📄",
    layout="wide",
)


@st.cache_resource
def load_pipeline():
    return DocumentIntelligencePipeline()


pipeline = load_pipeline()


st.title("📄 Multimodal Document Intelligence")

st.write(
    "Upload business documents to automatically classify, extract, "
    "validate and cross-check them for financial and operational risks."
)


with st.sidebar:
    st.header("System")

    st.markdown(
        """
        **Pipeline**
        - Document classification
        - Multimodal extraction
        - Internal validation
        - Cross-document matching
        - Duplicate detection
        - Risk scoring
        - Human-review decision
        """
    )

    st.header("Supported documents")

    st.markdown(
        """
        - Invoice
        - Purchase Order
        - Delivery Receipt
        """
    )

    st.caption(
        "Portfolio demonstration using synthetic business documents."
    )


uploaded_files = st.file_uploader(
    "Upload documents",
    type=[
        "pdf",
        "png",
        "jpg",
        "jpeg",
    ],
    accept_multiple_files=True,
)


if st.button(
    "Analyze documents",
    type="primary",
    use_container_width=True,
):
    if not uploaded_files:
        st.warning(
            "Upload at least one document first."
        )
        st.stop()

    temporary_paths = []

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            for uploaded_file in uploaded_files:
                suffix = Path(
                    uploaded_file.name
                ).suffix

                destination = (
                    Path(temp_dir)
                    / uploaded_file.name
                )

                destination.write_bytes(
                    uploaded_file.getvalue()
                )

                temporary_paths.append(
                    destination
                )

            with st.spinner(
                "Analyzing documents..."
            ):
                result = pipeline.process_documents(
                    temporary_paths
                )

    except Exception as error:
        st.error(
            f"Document analysis failed: {error}"
        )
        st.stop()

    risk = result["risk"]

    st.divider()
    st.subheader("Risk Assessment")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Risk Score",
            f'{risk["risk_score"]}/100',
        )

    with col2:
        st.metric(
            "Risk Level",
            risk["risk_level"].title(),
        )

    with col3:
        st.metric(
            "Human Review",
            "Required"
            if risk["review_required"]
            else "Not Required",
        )

    if risk["risk_level"] == "high":
        st.error(
            "High-risk transaction — human review required."
        )

    elif risk["risk_level"] == "medium":
        st.warning(
            "Potential issue detected — human review recommended."
        )

    else:
        st.success(
            "No significant risk detected."
        )

    if risk["findings"]:
        st.subheader("Risk Findings")

        for finding in risk["findings"]:
            st.write(
                f'**{finding["type"].replace("_", " ").title()}**'
            )
            st.write(finding["message"])
            st.caption(
                f'Risk contribution: +{finding["points"]} points'
            )

    st.divider()
    st.subheader("Documents")

    for item in result["documents"]:
        extracted = item["extracted"]
        validation = item["validation"]

        with st.expander(
            f'{item["filename"]} — '
            f'{extracted.document_type.replace("_", " ").title()}'
        ):
            st.write(
                "**Classification method:**",
                item["classification"]["method"],
            )

            st.write(
                "**Internal validation:**",
                "Passed"
                if validation["valid"]
                else "Failed",
            )

            if validation["issues"]:
                for issue in validation["issues"]:
                    st.warning(
                        issue["message"]
                    )

            st.subheader(
                "Extracted Data"
            )

            st.json(
                extracted.model_dump(
                    exclude_none=True
                )
            )

    transaction = result[
        "transaction_result"
    ]

    if transaction is not None:
        st.divider()
        st.subheader(
            "Cross-Document Matching"
        )

        if transaction["match"]:
            st.success(
                "The transaction documents are consistent."
            )

        else:
            st.error(
                f'{len(transaction["mismatches"])} '
                "cross-document discrepancies detected."
            )

            for mismatch in transaction["mismatches"]:
                st.write(
                    f'**{mismatch["field"].replace("_", " ").title()}**'
                )

                st.write(
                    f'{mismatch["source_a"]}: '
                    f'{mismatch["value_a"]}'
                )

                st.write(
                    f'{mismatch["source_b"]}: '
                    f'{mismatch["value_b"]}'
                )

    if result["duplicate_results"]:
        st.divider()
        st.subheader(
            "Duplicate Invoice Analysis"
        )

        for duplicate in result[
            "duplicate_results"
        ]:
            if duplicate["is_duplicate"]:
                st.warning(
                    f'Potential duplicate: '
                    f'{duplicate["invoice_a"]} ↔ '
                    f'{duplicate["invoice_b"]}'
                )
            else:
                st.success(
                    f'No duplicate detected: '
                    f'{duplicate["invoice_a"]} ↔ '
                    f'{duplicate["invoice_b"]}'
                )

            st.write(
                f'Similarity: '
                f'{duplicate["similarity"]:.1%}'
            )

    st.divider()
    st.subheader("Pipeline")

    st.code(
        "Document Upload\n"
        "      ↓\n"
        "Classification\n"
        "      ↓\n"
        "Structured Extraction\n"
        "      ↓\n"
        "Internal Validation\n"
        "      ↓\n"
        "Cross-Document Matching\n"
        "      ↓\n"
        "Duplicate Detection\n"
        "      ↓\n"
        "Risk Assessment\n"
        "      ↓\n"
        "Human Review Decision",
        language=None,
    )
