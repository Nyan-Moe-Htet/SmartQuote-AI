"""SmartQuote AI — a lightweight quotation and purchasing prototype."""

from datetime import date

import streamlit as st
from comparison import compare_offers, rm


st.set_page_config(
    page_title="SmartQuote AI",
    layout="wide",
)

SAMPLE_QUOTATIONS = [
    {
        "Supplier": "Kencana Office Supplies",
        "Item": "A4 Copy Paper (80gsm)",
        "Quantity": "50 reams",
        "Unit price": "RM 14.80",
        "Status": "Received",
    },
    {
        "Supplier": "Metro Paper Trading",
        "Item": "A4 Copy Paper (80gsm)",
        "Quantity": "50 reams",
        "Unit price": "RM 13.90",
        "Status": "Received",
    },
    {
        "Supplier": "Prima Stationery",
        "Item": "A4 Copy Paper (80gsm)",
        "Quantity": "50 reams",
        "Unit price": "RM 15.20",
        "Status": "Awaiting reply",
    },
    {
        "Supplier": "Bina Jaya Hardware",
        "Item": "Nitrile Gloves (box of 100)",
        "Quantity": "20 boxes",
        "Unit price": "RM 18.50",
        "Status": "Received",
    },
]

PRICE_COMPARISON = {
    "A4 Copy Paper (80gsm)": [
        {"Supplier": "Metro Paper Trading", "Unit price (RM)": 13.90, "Delivery": "2–3 days", "MOQ": 20, "Delivery fee": 40, "Max days": 3},
        {"Supplier": "Kencana Office Supplies", "Unit price (RM)": 14.80, "Delivery": "1–2 days", "MOQ": 5, "Delivery fee": 10, "Max days": 2},
        {"Supplier": "Prima Stationery", "Unit price (RM)": 15.20, "Delivery": "3–5 days", "MOQ": 10, "Delivery fee": 0, "Max days": 5},
    ],
    "Nitrile Gloves (box of 100)": [
        {"Supplier": "Bina Jaya Hardware", "Unit price (RM)": 18.50, "Delivery": "2–3 days", "MOQ": 20, "Delivery fee": 35, "Max days": 3},
        {"Supplier": "SafePro Supplies", "Unit price (RM)": 19.20, "Delivery": "1–2 days", "MOQ": 5, "Delivery fee": 10, "Max days": 2},
        {"Supplier": "Meditek Trading", "Unit price (RM)": 20.00, "Delivery": "3–4 days", "MOQ": 10, "Delivery fee": 0, "Max days": 4},
    ],
    "Thermal Receipt Rolls (box of 50)": [
        {"Supplier": "Metro Paper Trading", "Unit price (RM)": 42.00, "Delivery": "2–3 days", "MOQ": 20, "Delivery fee": 80, "Max days": 3},
        {"Supplier": "Kencana Office Supplies", "Unit price (RM)": 44.50, "Delivery": "1–2 days", "MOQ": 5, "Delivery fee": 15, "Max days": 2},
        {"Supplier": "Prima Stationery", "Unit price (RM)": 46.00, "Delivery": "3–5 days", "MOQ": 10, "Delivery fee": 0, "Max days": 5},
    ],
}

NAVIGATION = [
    "Dashboard",
    "Quotations",
    "Price Comparison",
    "Purchase Orders",
    "Activity Log",
]


def render_dashboard() -> None:
    st.title("SmartQuote AI")
    st.subheader("Compare supplier quotations. Make better purchasing decisions.")
    st.write(
        "SmartQuote AI helps Malaysian SMEs organise supplier quotations, "
        "compare prices and prepare purchase-order drafts in one place."
    )
    st.caption(
        "Fictional sample data for demonstration only. All amounts are in Malaysian Ringgit (RM)."
    )

    st.header("Purchasing overview")
    metric_columns = st.columns(4)
    metrics = [
        ("Open quotations", "12", "Fictional sample"),
        ("Potential savings", "RM 4,280", "Fictional sample"),
        ("Purchase orders to review", "6", "Fictional sample"),
        ("Average supplier response", "2.4 days", "Fictional sample"),
    ]
    for column, (label, value, note) in zip(metric_columns, metrics):
        column.metric(label, value, help=note)

    st.header("Recent quotations")
    st.dataframe(SAMPLE_QUOTATIONS[:3], hide_index=True, width="stretch")


def render_quotations() -> None:
    st.title("Quotations")
    st.write("Review fictional supplier quotations and response status.")
    st.caption("Sample records only — no supplier messages are sent or received.")
    st.dataframe(SAMPLE_QUOTATIONS, hide_index=True, width="stretch")


def render_price_comparison() -> None:
    st.title("Price Comparison")
    st.info("All supplier names, prices, minimum orders, fees and delivery estimates are fictional demonstration data.")
    item = st.selectbox("Choose an item", list(PRICE_COMPARISON))
    st.caption("Quantity is in reams for paper, boxes of 100 for gloves, or boxes of 50 for receipt rolls.")
    quantity = st.number_input(
        "Required quantity", min_value=1, max_value=1_000_000,
        value=10, step=1, key="comparison_quantity",
    )
    try:
        offers = compare_offers(PRICE_COMPARISON[item], quantity)
    except ValueError as error:
        st.error(str(error))
        return
    st.caption("Total cost = unit price × requested quantity + delivery fee. No quantity adjustment, taxes or other charges are included.")
    eligible = [offer for offer in offers if offer["Eligible"]]
    rows = []
    for offer in offers:
        rank = 1 + sum(other["Total"] < offer["Total"] for other in eligible) if offer["Eligible"] else "—"
        rows.append({
            "Rank": str(rank), "Supplier": offer["Supplier"],
            "Unit price": rm(offer["Unit price (RM)"]),
            "Minimum order quantity": offer["MOQ"], "Order quantity": quantity,
            "Delivery fee": rm(offer["Delivery fee"]),
            "Estimated delivery": offer["Delivery"],
            "Total cost": rm(offer["Total"]),
            "Eligibility": "Eligible" if offer["Eligible"] else f"Ineligible: minimum {offer['MOQ']} required",
        })
    st.dataframe(rows, hide_index=True, width="stretch")
    st.caption("Eligible offers are ranked by total cost; equal totals share a rank. Ineligible totals are illustrative only, not orderable at this quantity.")
    if not eligible:
        st.warning("No supplier meets this quantity. Your requested quantity has not been changed. Enter a different quantity to compare again.")
        return
    best = eligible[0]
    tied = [offer["Supplier"] for offer in eligible if offer["Total"] == best["Total"]]
    st.success(
        f"Recommended: {', '.join(tied)} — lowest eligible total of {rm(best['Total'])} "
        f"for exactly {quantity} units. "
        f"{rm(best['Unit price (RM)'])} × {quantity} + {rm(best['Delivery fee'])} delivery = {rm(best['Total'])}."
    )
    st.write(f"{best['Supplier']} meets its minimum order of {best['MOQ']}; estimated delivery: {best['Delivery']}.")
    faster = [offer for offer in eligible if offer["Max days"] < best["Max days"]]
    if faster:
        alternative = min(faster, key=lambda offer: offer["Total"])
        st.write(
            f"Delivery trade-off: {alternative['Supplier']} estimates {alternative['Delivery']} "
            f"rather than {best['Delivery']}, for {rm(alternative['Total'] - best['Total'])} more "
            f"({rm(alternative['Total'])} total). Estimates are not guarantees."
        )
    else:
        st.write("No eligible alternative has a shorter estimated maximum delivery time.")


def render_purchase_orders() -> None:
    st.title("Purchase Orders")
    st.write("Create a local draft preview from a selected supplier quotation.")
    st.caption("This prototype does not send or save purchase orders.")

    suppliers = sorted({quote["Supplier"] for quote in SAMPLE_QUOTATIONS})
    items = list(PRICE_COMPARISON)

    with st.form("purchase_order_draft"):
        supplier = st.selectbox("Supplier", suppliers)
        item = st.selectbox("Item", items)
        quantity = st.number_input("Quantity", min_value=1, value=10, step=1)
        unit_price = st.number_input(
            "Unit price (RM)",
            min_value=0.01,
            value=13.90,
            step=0.10,
            format="%.2f",
        )
        submitted = st.form_submit_button("Preview purchase order")

    if submitted:
        total = quantity * unit_price
        st.subheader("Purchase order draft")
        st.write(f"**Supplier:** {supplier}")
        st.write(f"**Item:** {item}")
        st.write(f"**Quantity:** {quantity}")
        st.write(f"**Unit price:** RM {unit_price:,.2f}")
        st.metric("Draft total", f"RM {total:,.2f}")
        st.caption(f"Draft prepared on {date.today().strftime('%d %b %Y')}.")


def render_activity_log() -> None:
    st.title("Activity Log")
    st.write("A sample view of recent purchasing activity.")
    activity = [
        {"Date": "24 Oct 2026", "Activity": "Quotation received", "Details": "Metro Paper Trading · A4 Copy Paper"},
        {"Date": "23 Oct 2026", "Activity": "Price comparison viewed", "Details": "Nitrile Gloves · 3 sample offers"},
        {"Date": "22 Oct 2026", "Activity": "Purchase order draft prepared", "Details": "Kencana Office Supplies · Draft only"},
        {"Date": "21 Oct 2026", "Activity": "Quotation request created", "Details": "Thermal Receipt Rolls · Fictional sample"},
    ]
    st.dataframe(activity, hide_index=True, width="stretch")
    st.caption("Fictional activity for demonstration only.")


st.sidebar.title("SmartQuote AI")
st.sidebar.caption("Malaysian SME purchasing prototype")
selected_page = st.sidebar.radio("Navigation", NAVIGATION, label_visibility="collapsed")

if selected_page == "Dashboard":
    render_dashboard()
elif selected_page == "Quotations":
    render_quotations()
elif selected_page == "Price Comparison":
    render_price_comparison()
elif selected_page == "Purchase Orders":
    render_purchase_orders()
else:
    render_activity_log()
