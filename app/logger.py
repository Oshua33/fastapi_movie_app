import logging
import logging.handlers


PAPERTRAIL_HOST = "logs3.papertrailapp.com"
PAPERTRAIL_PORT = 29749

# Configure the SysLogHandler for Papertrail
syslog_handler = logging.handlers.SysLogHandler(address=(PAPERTRAIL_HOST, PAPERTRAIL_PORT))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
syslog_handler.setFormatter(formatter)

# Configure the console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Setup the logging configuration
logging.basicConfig(
    level=logging.INFO,
    handlers=[syslog_handler, console_handler]
)

def get_logger(name):
    logger = logging.getLogger(name)
    return logger
