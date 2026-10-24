"""SmartQuote AI — a lightweight quotation and purchasing prototype."""

from datetime import date

import streamlit as st


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
        {"Supplier": "Metro Paper Trading", "Unit price (RM)": 13.90, "Delivery": "2–3 days"},
        {"Supplier": "Kencana Office Supplies", "Unit price (RM)": 14.80, "Delivery": "1–2 days"},
        {"Supplier": "Prima Stationery", "Unit price (RM)": 15.20, "Delivery": "3–5 days"},
    ],
    "Nitrile Gloves (box of 100)": [
        {"Supplier": "Bina Jaya Hardware", "Unit price (RM)": 18.50, "Delivery": "2–3 days"},
        {"Supplier": "SafePro Supplies", "Unit price (RM)": 19.20, "Delivery": "1–2 days"},
        {"Supplier": "Meditek Trading", "Unit price (RM)": 20.00, "Delivery": "3–4 days"},
    ],
    "Thermal Receipt Rolls (box of 50)": [
        {"Supplier": "Metro Paper Trading", "Unit price (RM)": 42.00, "Delivery": "2–3 days"},
        {"Supplier": "Kencana Office Supplies", "Unit price (RM)": 44.50, "Delivery": "1–2 days"},
        {"Supplier": "Prima Stationery", "Unit price (RM)": 46.00, "Delivery": "3–5 days"},
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
    st.write("Compare sample supplier pricing and delivery estimates by item.")

    item = st.selectbox("Choose an item", list(PRICE_COMPARISON))
    offers = PRICE_COMPARISON[item]
    lowest_offer = min(offers, key=lambda offer: offer["Unit price (RM)"])

    st.dataframe(offers, hide_index=True, width="stretch")
    st.success(
        f"Lowest sample offer: {lowest_offer['Supplier']} at "
        f"RM {lowest_offer['Unit price (RM)']:.2f} per unit."
    )


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
