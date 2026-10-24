"""Run with: .pythonlibs/bin/python -m unittest discover -s tests -v"""
import unittest
from decimal import Decimal

from streamlit.testing.v1 import AppTest
import quotations
import purchase_workflow as workflow


class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.app = AppTest.from_file("../app.py").run()

    def page(self, name):
        self.app.sidebar.radio[0].set_value(name).run()
        self.assertFalse(self.app.exception)

    def button(self, label):
        next(b for b in self.app.button if b.label == label).click().run()
        self.assertFalse(self.app.exception)

    def text(self, label, value):
        next(w for w in self.app.text_input if w.label == label).set_value(value)

    def number(self, label, value):
        next(w for w in self.app.number_input if w.label == label).set_value(value)

    def test_intake_comparison_approval_and_rejection(self):
        self.page("Quotations")
        self.button("Add Quotation")
        self.assertIn("Supplier name is required", self.app.error[0].value)
        self.assertEqual(self.app.session_state["quotations"], [])
        self.text("Supplier name", "Demo Supply")
        self.text("Product name/specification", "A4 Copy Paper (80gsm)")
        self.text("Pack content unit", "ream")
        self.number("Unit price per order unit (RM)", -1.0)
        self.button("Add Quotation")
        self.assertIn("Unit price", self.app.error[0].value)
        self.assertEqual(self.app.session_state["quotations"], [])
        self.number("Unit price per order unit (RM)", 12.0)
        self.number("Delivery fee (RM)", 5.0)
        self.button("Add Quotation")
        self.assertEqual(len(self.app.session_state["quotations"]), 1)
        self.assertEqual(self.app.session_state["purchases"], {})
        self.page("Dashboard")
        self.page("Quotations")
        self.assertEqual(len(self.app.session_state["quotations"]), 1)
        self.page("Price Comparison")
        rows = self.app.dataframe[0].value
        row = rows[rows.Supplier == "Demo Supply"].iloc[0]
        self.assertEqual(row["Total cost"], "RM 125.00")
        self.assertEqual(row["Data source"], "User-entered demonstration data")
        self.app.selectbox[1].select("Demo Supply").run()
        self.button("Submit for Approval")
        self.assertEqual(next(iter(self.app.session_state["purchases"].values()))["Status"], "Pending approval")
        self.assertFalse(self.app.session_state["drafts"])
        self.page("Purchase Orders")
        self.button("Approve Purchase")
        self.button("Generate purchase-order draft")
        draft = next(iter(self.app.session_state["drafts"].values()))
        self.assertEqual(draft["Offer"]["Total"], Decimal("125.00"))
        self.assertEqual(draft["Status"], "Draft — Not Sent")
        self.page("Price Comparison")
        self.app.selectbox[1].select("Prima Stationery").run()
        self.button("Submit for Approval")
        self.button("Reject Purchase")
        reference = next(k for k, p in self.app.session_state["purchases"].items() if p["Status"] == "Rejected")
        with self.assertRaises(ValueError):
            workflow.generate_draft(self.app.session_state, reference, {})
        self.page("Activity Log")
        actions = [e["Activity"] for e in self.app.session_state["events"]]
        for action in ["Quotation created", "Comparison", "Submitted for approval", "Approved", "Rejected", "Draft generated"]:
            self.assertIn(action, actions)
        self.assertEqual(len(self.app.session_state["drafts"]), 1)

    def test_validation_grouping_status_and_duplicates(self):
        state = {"quotations": [], "events": []}
        base = {"A4 Copy Paper (80gsm)": [{"Supplier": "Sample Supplier"}]}
        args = dict(state=state, base=base, supplier="Test Demo", product="A4 Copy Paper (80gsm)", unit="ream",
                    pack_size=1, price=12, moq=1, fee=0, days_min=1, days_max=3, status="Received")
        for invalid in [
            {"product": " "}, {"unit": ""}, {"supplier": ""}, {"price": -1}, {"price": 0},
            {"fee": -1}, {"price": float("nan")}, {"fee": float("inf")},
            {"pack_size": 0}, {"pack_size": 1.5}, {"moq": -1}, {"moq": True},
            {"days_min": 0}, {"days_max": 0}, {"days_min": 4}, {"status": "Approved"},
        ]:
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                quotations.create_quotation(**(args | invalid))
        self.assertFalse(state["quotations"])
        first = quotations.create_quotation(**args)
        self.assertEqual(first["group"], "A4 Copy Paper (80gsm)")
        with self.assertRaises(ValueError):
            quotations.create_quotation(**(args | {"supplier": " test DEMO "}))
        pack = quotations.create_quotation(**(args | {"pack_size": 2}))
        spec = quotations.create_quotation(**(args | {"product": "A4 Copy Paper (70gsm)"}))
        unit = quotations.create_quotation(**(args | {"unit": "sheet"}))
        pending = quotations.create_quotation(**(args | {"product": "Pending demo", "status": "Awaiting reply"}))
        expired = quotations.create_quotation(**(args | {"product": "Expired demo", "status": "Expired"}))
        catalog = quotations.catalog(base, state["quotations"])
        self.assertEqual(len({first["group"], pack["group"], spec["group"], unit["group"]}), 4)
        self.assertNotIn(pending["group"], catalog)
        self.assertNotIn(expired["group"], catalog)
        self.assertEqual(len(catalog[first["group"]]), 2)
        self.assertEqual(len(state["events"]), 6)


if __name__ == "__main__":
    unittest.main()
