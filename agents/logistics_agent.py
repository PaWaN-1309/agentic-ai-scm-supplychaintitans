class MockLogisticsAgent:
    def kickoff(self):
        return {
            "courier": "FedEx",
            "eta": "3 days",
            "tracking_id": "FTX-998811"
        }

logistics_agent = MockLogisticsAgent()
