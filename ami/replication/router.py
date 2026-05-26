class DataWarehouseRouter:
    app_label = "replication"
    db_alias = "data_ware_house"

    def db_for_read(self, model, **hints):
        if model._meta.app_label == self.app_label:
            return self.db_alias
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == self.app_label:
            return self.db_alias
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == self.app_label:
            return db == self.db_alias
        if db == self.db_alias:
            return False
        return None
