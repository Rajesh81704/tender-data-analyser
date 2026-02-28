from app.api.dao.health_dao import HealthDAO

class HealthService:
    def __init__(self):
        self.health_dao = HealthDAO()
    
    def get_health_info(self):
        return self.health_dao.fetch_health_data()
