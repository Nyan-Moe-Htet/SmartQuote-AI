"""Session-only demonstration quotation intake and like-for-like grouping."""
from decimal import Decimal, InvalidOperation
from uuid import uuid4

import streamlit as st

from comparison import rm
from purchase_workflow import log

SAMPLE_UNITS = {
    "A4 Copy Paper (80gsm)": ("ream", 1),
    "Nitrile Gloves (box of 100)": ("glove", 100),
    "Thermal Receipt Rolls (box of 50)": ("roll", 50),
}
STATUSES = ["Received", "Awaiting reply", "Expired"]


def normalized(text):
    return " ".join(text.split()).casefold()


def money(value, label, positive=False):
    try:
        amount = Decimal(str(value))
    except InvalidOperation:
        raise ValueError(f"{label} must be a valid RM amount.")
    if not amount.is_finite() or amount < 0 or (positive and amount == 0) or amount > 1_000_000_000:
        raise ValueError(f"{label} must be {'greater than zero' if positive else 'zero or more'} and at most RM 1,000,000,000.")
    if amount != amount.quantize(Decimal("0.01")):
        raise ValueError(f"{label} must have at most two decimal places.")
    return amount


def create_quotation(state, base, supplier, product, unit, pack_size, price, moq, fee, days_min, days_max, status):
    supplier, product, unit = (" ".join(value.split()) for value in (supplier, product, unit))
    for label, value in [("Supplier name", supplier), ("Product name/specification", product), ("Pack content unit", unit)]:
        if not value:
            raise ValueError(f"{label} is required.")
        if len(value) > 150:
            raise ValueError(f"{label} must be 150 characters or fewer.")
    for label, value in [("Pack size", pack_size), ("Minimum order quantity", moq), ("Minimum delivery days", days_min), ("Maximum delivery days", days_max)]:
        limit = 365 if "days" in label else 1_000_000
        if type(value) is not int or not 1 <= value <= limit:
            raise ValueError(f"{label} must be a whole number between 1 and {limit:,}.")
    if days_max < days_min:
        raise ValueError("Maximum delivery days cannot be less than minimum delivery days.")
    if status not in STATUSES:
        raise ValueError("Choose a valid quotation status.")
    price, fee = money(price, "Unit price", positive=True), money(fee, "Delivery fee")
    identity = (normalized(product), normalized(unit), pack_size)
    group = None
    for name, (sample_unit, size) in SAMPLE_UNITS.items():
        if identity == (normalized(name), normalized(sample_unit), size):
            group = name
            break
    for quotation in state["quotations"]:
        if quotation["identity"] == identity:
            group = quotation["group"]
    if group is None:
        group = f"{product} | per pack of {pack_size} {unit}"
        if group in base or any(q["group"] == group and q["identity"] != identity for q in state["quotations"]):
            raise ValueError("This product label conflicts with another specification. Use a more specific product name.")
    suppliers = [o["Supplier"] for o in base.get(group, [])]
    suppliers += [q["offer"]["Supplier"] for q in state["quotations"] if q["group"] == group]
    if normalized(supplier) in {normalized(name) for name in suppliers}:
        raise ValueError("This supplier already has an offer for this exact specification and pack size. Duplicate offers are not supported.")
    quotation = {
        "reference": "QUOTE-" + uuid4().hex,
        "group": group, "identity": identity, "product": product, "status": status,
        "offer": {
            "Supplier": supplier, "Unit price (RM)": price,
            "MOQ": moq, "Delivery fee": fee,
            "Delivery": f"{days_min}–{days_max} days", "Max days": days_max,
            "Pack": f"{pack_size} {unit} per order unit",
            "Source": "User-entered demonstration data",
        },
    }
    state["quotations"].append(quotation)
    log(state, "Quotation created", f"{quotation['reference']} | {supplier} | {group} | {quotation['offer']['Pack']} | {rm(price)} | {status}")
    return quotation


def catalog(base, quotations):
    result = {name: list(offers) for name, offers in base.items()}
    for quotation in quotations:
        if quotation["status"] == "Received":
            result.setdefault(quotation["group"], []).append(quotation["offer"])
    return result


def pack_label(item, offer=None):
    if offer and "Pack" in offer:
        return offer["Pack"]
    unit, size = SAMPLE_UNITS[item]
    return f"{size} {unit} per order unit"


def render_intake(base):
    st.subheader("Add Quotation")
    st.info("Demonstration entries only. Do not enter real customer, supplier or personal data. Nothing is sent; entries last only for this session.")
    st.caption("Enter the full product name AND specification. Offers match only when product/specification, pack size and content unit all match (ignoring case and extra spaces). No unit conversion is performed.")
    st.table([{"Product/specification": item, "Pack size": size, "Content unit": unit}
              for item, (unit, size) in SAMPLE_UNITS.items()])
    with st.form("add_quotation"):
        supplier = st.text_input("Supplier name")
        product = st.text_input("Product name/specification")
        unit = st.text_input("Pack content unit", help="Use the reference units above to match a sample offer; otherwise enter a unit such as piece or kg.")
        pack_size = st.number_input("Pack size (content units per order unit)", value=1, step=1)
        price = st.number_input("Unit price per order unit (RM)", value=1.00, step=0.01, format="%.2f")
        moq = st.number_input("Minimum order quantity (order units)", value=1, step=1)
        fee = st.number_input("Delivery fee (RM)", value=0.00, step=0.01, format="%.2f")
        days_min = st.number_input("Minimum estimated delivery days", value=1, step=1)
        days_max = st.number_input("Maximum estimated delivery days", value=3, step=1)
        status = st.selectbox("Quotation status", STATUSES)
        st.caption("Only Received offers enter comparison. Received does not mean purchase approval.")
        save = st.form_submit_button("Add Quotation")
    if save:
        try:
            create_quotation(st.session_state, base, supplier, product, unit, pack_size, price, moq, fee, days_min, days_max, status)
        except ValueError as error:
            st.error(str(error))
        else:
            st.success("Demonstration quotation added. It is available during this session; no purchase was approved.")
    st.subheader("User-entered demonstration quotations")
    if not st.session_state["quotations"]:
        st.caption("No user-entered quotations in this session yet.")
    else:
        st.dataframe([{
            "Supplier": q["offer"]["Supplier"], "Product/specification": q["product"],
            "Pack": q["offer"]["Pack"], "Unit price": rm(q["offer"]["Unit price (RM)"]),
            "MOQ (order units)": q["offer"]["MOQ"], "Delivery fee": rm(q["offer"]["Delivery fee"]),
            "Delivery estimate": q["offer"]["Delivery"], "Status": q["status"],
            "Source": q["offer"]["Source"],
        } for q in st.session_state["quotations"]], hide_index=True, width="stretch")
