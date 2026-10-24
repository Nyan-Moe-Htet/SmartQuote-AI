"""Session-only purchase approval state transitions; no external side effects."""
from copy import deepcopy
from datetime import datetime
from uuid import uuid4
from zoneinfo import ZoneInfo

from comparison import compare_offers, rm


def now():
    return datetime.now(ZoneInfo("Asia/Kuala_Lumpur")).isoformat(timespec="seconds")


def initialize(state):
    for key, value in [("purchases", {}), ("events", []), ("drafts", {})]:
        if key not in state:
            state[key] = value


def log(state, action, details):
    state["events"].append({"Date/time (Malaysia)": now(), "Activity": action, "Details": details})


def validate(purchase, catalog):
    offers = compare_offers(catalog[purchase["Item"]], purchase["Quantity"])
    match = next((o for o in offers if o["Supplier"] == purchase["Offer"]["Supplier"]), None)
    if not match or not match["Eligible"] or match != purchase["Offer"]:
        raise ValueError("Offer is ineligible or has changed. Compare and submit a new request.")
    return match


def submit(state, item, quantity, supplier, catalog):
    offer = next((o for o in compare_offers(catalog[item], quantity) if o["Supplier"] == supplier), None)
    purchase = {"Item": item, "Quantity": quantity, "Offer": deepcopy(offer), "Status": "Pending approval"}
    if not offer:
        raise ValueError("Select a valid supplier.")
    validate(purchase, catalog)
    reference = "REQ-" + uuid4().hex
    state["purchases"][reference] = purchase
    log(state, "Submitted for approval", f"{reference} | {supplier} | {item} | {quantity} units | {rm(offer['Total'])}")
    return reference


def decide(state, reference, approved, catalog):
    purchase = state["purchases"][reference]
    if purchase["Status"] != "Pending approval":
        raise ValueError("This request already has a decision.")
    validate(purchase, catalog)
    purchase["Status"] = "Approved" if approved else "Rejected"
    log(state, purchase["Status"], f"{reference} | {purchase['Offer']['Supplier']} | {purchase['Item']} | {purchase['Quantity']} units")


def generate_draft(state, reference, catalog):
    purchase = state["purchases"][reference]
    if purchase["Status"] != "Approved":
        raise ValueError("Only an explicitly approved purchase can generate a draft.")
    validate(purchase, catalog)
    if reference not in state["drafts"]:
        state["drafts"][reference] = {
            **deepcopy(purchase), "Reference": "DRAFT-" + uuid4().hex,
            "Date": now(), "Status": "Draft — Not Sent",
        }
        log(state, "Draft generated", f"{state['drafts'][reference]['Reference']} | {reference} | {purchase['Offer']['Supplier']} | {purchase['Item']} | {rm(purchase['Offer']['Total'])}")
    return state["drafts"][reference]
