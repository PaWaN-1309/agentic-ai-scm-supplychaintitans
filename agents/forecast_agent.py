class MockForecastAgent:
    def kickoff(self):
        return {
            "predicted_demand": 120,
            "demand_level": "Medium"
        }

forecast_agent = MockForecastAgent()
