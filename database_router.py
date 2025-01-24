class DatabaseRouter:
    """
    Управление запросами между базами данных PostgreSQL и SQLite.
    """
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'postgres_app':
            return 'default'
        elif model._meta.app_label == 'sqlite_app':
            return 'sqlite'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'postgres_app':
            return 'default'
        elif model._meta.app_label == 'sqlite_app':
            return 'sqlite'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        db_set = ('default', 'sqlite')
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'postgres_app':
            return db == 'default'
        elif app_label == 'sqlite_app':
            return db == 'sqlite'
        return None
