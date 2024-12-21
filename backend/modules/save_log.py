from databases.models.log import LogData

def save_log(session, log_action, message, category="info"):
    """Saves a log entry to the database.

    Args:
        session: A SQLAlchemy session object.
        log_action: A string representing the action that triggered the log entry.
        message: A string containing the log message.
    """
    try:
        log = LogData(log_action=log_action, message=message, category=category)
        session.add(log)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()