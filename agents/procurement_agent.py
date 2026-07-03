class MockProcurementAgent:
    def kickoff(self):
        return {
            "supplier_name": "Titan Logistics & Supply",
            "supplier_rating": 4.8,
            "supplier_price": 75.0,
            "delivery_time": "4 days"
        }

procurement_agent = MockProcurementAgent()
