from services.data_service import SmartPricingDataService


def get_data_service() -> SmartPricingDataService:
    return SmartPricingDataService()
