def calculate_risk(
    validation_results=None,
    transaction_result=None,
    duplicate_result=None,
):
    score = 0
    findings = []

    if validation_results:
        for result in validation_results:
            for issue in result.get(
                "issues",
                [],
            ):
                severity = issue.get(
                    "severity",
                    "medium",
                )

                points = {
                    "low": 5,
                    "medium": 15,
                    "high": 30,
                }.get(
                    severity,
                    15,
                )

                score += points

                findings.append(
                    {
                        "source": "document_validation",
                        "type": issue["type"],
                        "message": issue["message"],
                        "points": points,
                    }
                )

    if transaction_result:
        for mismatch in transaction_result.get(
            "mismatches",
            [],
        ):
            field = mismatch["field"]

            field_points = {
                "unit_price": 25,
                "delivery_quantity": 25,
                "subtotal": 15,
                "vat": 10,
                "total": 15,
                "supplier": 20,
                "customer": 15,
                "item": 20,
                "po_number": 25,
            }

            points = field_points.get(
                field,
                10,
            )

            score += points

            findings.append(
                {
                    "source": "cross_document",
                    "type": f"{field}_mismatch",
                    "message": (
                        f"{field} differs between "
                        f"{mismatch['source_a']} and "
                        f"{mismatch['source_b']}: "
                        f"{mismatch['value_a']} vs "
                        f"{mismatch['value_b']}."
                    ),
                    "points": points,
                }
            )

    if (
        duplicate_result
        and duplicate_result.get(
            "is_duplicate"
        )
    ):
        points = 40
        score += points

        findings.append(
            {
                "source": "duplicate_detection",
                "type": "potential_duplicate",
                "message": (
                    "Potential duplicate invoice detected "
                    f"with similarity "
                    f"{duplicate_result['similarity']:.1%}."
                ),
                "points": points,
            }
        )

    score = min(
        score,
        100,
    )

    if score >= 60:
        level = "high"
        review_required = True
    elif score >= 25:
        level = "medium"
        review_required = True
    else:
        level = "low"
        review_required = False

    return {
        "risk_score": score,
        "risk_level": level,
        "review_required": review_required,
        "findings": findings,
    }
