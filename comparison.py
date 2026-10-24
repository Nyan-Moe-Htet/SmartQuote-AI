"""Deterministic comparison rules for fictional supplier offers."""

from decimal import Decimal


def rm(value):
    return f"RM {value:,.2f}"


def compare_offers(offers, quantity):
    if type(quantity) is not int or not 1 <= quantity <= 1_000_000:
        raise ValueError("Enter a whole-number quantity between 1 and 1,000,000.")
    results = []
    for offer in offers:
        price = Decimal(str(offer["Unit price (RM)"]))
        fee = Decimal(str(offer["Delivery fee"]))
        results.append({
            **offer,
            "Total": price * quantity + fee,
            "Eligible": quantity >= offer["MOQ"],
        })
    return sorted(results, key=lambda row: (
        not row["Eligible"], row["Total"], row["Supplier"]
    ))
