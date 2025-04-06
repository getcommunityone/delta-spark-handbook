""" Module for python logging for cdc_tech_environment_service with minimal dependencies. """

import sys  # don't remove required for error handling
import os
import logging
import logging.config
import logging.handlers
from logging.handlers import TimedRotatingFileHandler

# from opentelemetry.instrumentation.flask import FlaskInstrumentor
from datetime import datetime
import traceback
import inspect
import platform
from pathlib import Path


from opentelemetry.sdk._logs import LoggingHandler, LoggerProvider

from opentelemetry._logs import (
    set_logger_provider,
)

from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter
from c1_core.c1_log_service.environment_tracing import TracerSingleton
 

# Import from sibling directory ..\cdc_tech_environment_service
OS_NAME = os.name

# Define ANSI escape codes for red
RED = "\033[91m"
RESET = "\033[0m"

# Create a custom formatter that colors error messages in red
class ColoredFormatter(logging.Formatter):
    def format(self, record):
        if record.levelno == logging.ERROR:
            record.msg = f"{RED}{record.msg}{RESET}"
        return super().format(record)


if OS_NAME.lower() == "nt":  # Windows environment
    print("environment_logging: windows")
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

    env_path = os.path.dirname(os.path.abspath(sys.executable))
    sys.path.append(os.path.join(env_path, "share"))

    try:
        ENV_SHARE_PATH = Path.home()
    except RuntimeError as e:
        print(f"Warning: Error occurred while determining home directory: {e}")
        # Provide a fallback path or handle the error as required
        # Replace 'fallback_directory_path' with an appropriate path or another way to handle the error
        ENV_SHARE_PATH = Path(os.environ.get("HOME"))
        print(f"Using Fallback Environment Variable path: {ENV_SHARE_PATH}")

    LOG_FILENAME = ENV_SHARE_PATH / "c1_core_logging.txt"

else:  # Non-Windows environment
    print("environment_logging: non-windows")

    ENV_SHARE_FALLBACK_PATH = "/usr/local/share"

    env_path = os.path.dirname(os.path.abspath(sys.executable))
    share_path_option1 = os.path.join(env_path, "share")

    try:
        # Check if the first path exists
        if os.path.exists(share_path_option1):
            # If the first path exists, use it
            ENV_SHARE_PATH = share_path_option1
        else:
            # If the first path does not exist, try the second path
            ENV_SHARE_PATH = os.path.join(os.path.expanduser("~"), "share")

        # Append the chosen path to sys.path
        sys.path.append(ENV_SHARE_PATH)
        LOG_FILENAME = os.path.join(ENV_SHARE_PATH, "c1_core_logging.txt")

    except RuntimeError as e:
        # Handle the error if home directory can't be determined
        print(f"Error occurred: {e}")
        # Set a fallback path or handle the error appropriately
        # Example: using a predefined directory or terminating the program
        # Replace 'fallback_directory_path' with an actual path or another error handling strategy
        ENV_SHARE_PATH = ENV_SHARE_FALLBACK_PATH
        LOG_FILENAME = os.path.join(ENV_SHARE_PATH, "c1_core_logging.txt")
        sys.path.append(ENV_SHARE_PATH)

# Default Application Insights connection string - Dev
APPLICATIONINSIGHTS_CONNECTION_STRING_DEV = (
    "InstrumentationKey=8f02ef9a-cd94-48cf-895a-367f102e8a24;"
    "IngestionEndpoint=https://eastus-8.in.applicationinsights.azure.com/;"
    "LiveEndpoint=https://eastus.livediagnostics.monitor.azure.com/"
)

# Construct the full path for the log file
log_file_path = LOG_FILENAME

try:
    FOLDER_EXISTS = os.path.exists(ENV_SHARE_PATH)
    if not FOLDER_EXISTS:
        # Create a new directory because it does not exist
        os.makedirs(ENV_SHARE_PATH)
except Exception as e:
    FOLDER_EXISTS = os.path.exists(ENV_SHARE_FALLBACK_PATH)
    if not FOLDER_EXISTS:
        if platform.system() != "Windows":
            # Create a new directory because it does not exist
            os.makedirs(ENV_SHARE_FALLBACK_PATH)

print(f"Log files stored at LOG_FILENAME:{LOG_FILENAME}")

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(module)s - %(lineno)d - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        'colored': {  # Use the colored formatter for the console output
            '()': ColoredFormatter,  # Apply custom colored formatter for terminal
            'format': '%(asctime)s - %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        "file_formatter": {
            "format": "%(asctime)s - %(name)s - %(module)s - %(lineno)d - %(levelname)s - %(message)s",  # Plain format for file
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "logfile": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "filename": LOG_FILENAME,
            "formatter": "file_formatter",  # Use the plain text formatter for the log file
            "backupCount": 2,
        },
        "verbose_output": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "colored",  # Use colored formatter for the console
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "tryceratops": {
            "level": "INFO",
            "handlers": [
                "verbose_output",
            ],
        },
    },
    "root": {"level": "DEBUG", "handlers": ["logfile", "verbose_output"]},  # Add both handlers to root logger
    "LAVA_CORE_DEV": {"level": "DEBUG", "handlers": ["logfile"]},
}

# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)


class LoggerSingleton:
    """
    A Python wrapper class around OpenTelemetry Logger using a
    singleton design pattern, so that the logger instance is created
    only once and the same instance is used throughout the application.

    Raises:
        Exception: If an attempt is made to create another instance
                   of this singleton class.

    Returns:
        LoggerSingleton: An instance of the LoggerSingleton class.
    """

    _instance = None

    @staticmethod
    def instance(
        calling_namespace_name: str,
        calling_service_name: str,
        data_product_id: str = "wonder_metadata",
        environment: str = "dev",
    ):
        """
        Returns the singleton instance of the LoggerSingleton class.

        Args:
            calling_namespace_name (str): The name of the calling namespace.
            calling_service_name (str): The name of the calling service.
            data_product_id (str, optional): The ID of the data product. Defaults to "wonder_metadata".
            environment (str, optional): The environment name. Defaults to "dev".

        Returns:
            LoggerSingleton: The singleton instance of the LoggerSingleton class.
        """

        if LoggerSingleton._instance is None:
            LoggerSingleton(
                calling_namespace_name,
                calling_service_name,
                data_product_id,
                environment,
            )
        return LoggerSingleton._instance

    def __init__(
        self,
        calling_namespace_name,
        calling_service_name,
        data_product_id,
        environment,
        default_connection_string=None,
    ):
        """
        Initializes the LoggerSingleton class.

        Args:
            calling_namespace_name (str): The namespace name of the calling service.
            calling_service_name (str): The name of the calling service.
            data_product_id (str, optional): The ID of the data product. Defaults to "wonder_metadata".
            environment (str, optional): The environment name. Defaults to "dev".
            default_connection_string (str, optional): The default connection string. Defaults to None.
        """

        if LoggerSingleton._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            LoggerSingleton._instance = self

        self.calling_namespace_name = calling_namespace_name
        self.calling_service_name = calling_service_name
        self.data_product_id = data_product_id
        self.environment = environment
        cloud_role_name = calling_namespace_name + "." + calling_service_name + "." + data_product_id
        logger_provider = LoggerProvider()
        set_logger_provider(logger_provider)

        
        if environment == "prod":
            # PROD
            default_connection_string = (
                "InstrumentationKey=e7808e07-4242-4ed3-908e-c0a4c3b719b1;"
                "IngestionEndpoint=https://eastus-8.in.applicationinsights.azure.com/;"
                "LiveEndpoint=https://eastus.livediagnostics.monitor.azure.com/"
            )
        else:
            # DEV
            default_connection_string = APPLICATIONINSIGHTS_CONNECTION_STRING_DEV

        connection_string = default_connection_string
        # Set your connection string and role name explicitly
 

        # Set the environment variable if it is not already set
        if "APPLICATIONINSIGHTS_CONNECTION_STRING" not in os.environ:
            os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"] = connection_string

        try:
            if connection_string:
                log_exporter = AzureMonitorLogExporter(
                    connection_string=connection_string
                )
                
                if cloud_role_name:
                    log_exporter._cloud_role_name = cloud_role_name  # Set cloud role name for AI
                    log_exporter._cloud_role_instance = self._generate_role_instance()

                logger_provider.add_log_record_processor(
                    BatchLogRecordProcessor(log_exporter)
                )
            else:
                raise ValueError("default_connection_string is not set.")

        except Exception as ex_app_insights:
            # Add the connection_string to the error message
            print(
                f"Failed to connect with connection_string: {connection_string}, Error: {ex_app_insights}"
            )

        # Attach LoggingHandler to root logger
        self.file_path = LOG_FILENAME
        os.makedirs(os.path.dirname(ENV_SHARE_PATH), exist_ok=True)
        # Create a console handler and set its log level to INFO
        log_format = LOGGING_CONFIG["formatters"]["colored"]["format"]
        datefmt = LOGGING_CONFIG["formatters"]["colored"]["datefmt"]

        self.azure_handler = LoggingHandler()

        formatter = ColoredFormatter(log_format, datefmt)
        self.console_handler = logging.StreamHandler(sys.stdout)
        self.console_handler.setFormatter(formatter)
        self.console_handler.setLevel(
            logging.getLevelName(LOGGING_CONFIG["handlers"]["verbose_output"]["level"])
        )

        self.file_handler = TimedRotatingFileHandler(
            self.file_path, when="midnight", interval=1, backupCount=7
        )

       

        # Set formatter for file handler
        self.file_handler.setFormatter(formatter)
        logger_name = f"{calling_namespace_name}:{calling_service_name}"
        self.logger = logging.getLogger(logger_name)
        self.logger.addHandler(self.file_handler)
        self.logger.addHandler(self.console_handler)
        self.logger.addHandler(self.azure_handler)

        # Set the threshold of logger to INFO
        self.logger.setLevel(logging.INFO)

    def _generate_role_instance(self):
        """
        Generates a unique role instance identifier.

        Returns:
            str: A unique role instance identifier.
        """
        return f"{platform.node()}-{os.getpid()}"

    def get_log_file_path(self):
        """
        Returns the path to the log file.

        Returns:
            str: The path to the log file.
        """
        return self.file_path

    def validate_application_insights_connection_string(
        self, environment="dev", default_connection_string=None
    ):
        """
        Validates the Application Insights connection string and sends test logs.

        This function checks if the environment variable 'APPLICATIONINSIGHTS_CONNECTION_STRING'
        is set. If not, it uses a default connection string for testing purposes. The function
        then initializes a logger and creates an instance of the AzureMonitorLogExporter using
        the connection string. Test log messages are sent to Application Insights using the logger
        and exporter to validate the connection.

        Note: The default_connection_string used for testing in this function should be replaced
        with the actual instrumentation key and endpoint URLs from your Application Insights
        resource in a production environment.

        Raises:
            ValueError: If the provided connection string is invalid or missing.

        Returns:
            None: This function does not return anything but prints messages to the console
            indicating the success or failure of the test log messages.
        """

        if default_connection_string is None or default_connection_string == "":
            if environment == "prod":
                # PROD
                default_connection_string = (
                    "InstrumentationKey=d091b27b-14e0-437f-ae3c-90f3f04ef3dc;"
                    "IngestionEndpoint=https://eastus-8.in.applicationinsights.azure.com/;"
                    "LiveEndpoint=https://eastus.livediagnostics.monitor.azure.com/"
                )
            else:
                # DEV
                default_connection_string = (
                    "InstrumentationKey=8f02ef9a-cd94-48cf-895a-367f102e8a24;"
                    "IngestionEndpoint=https://eastus-8.in.applicationinsights.azure.com/;"
                    "LiveEndpoint=https://eastus.livediagnostics.monitor.azure.com/"
                )
        connection_string = default_connection_string

        # Log some test messages
        self.logger.info("This is a test log message.")
        self.logger.warning("This is a warning log message.")
        self.logger.error("This is an error log message.")

        return (
            f"Successfully sent test logs to Application Insights: {connection_string}."
        )

    def get_exception_info(self, message, exc_info):
        """
        Retrieves detailed information about the most recently handled exception.

        This function should be called inside an 'except' block only.
        It extracts and formats various details about the exception and its context,
        such as the type and message of the exception, the filename and line number
        where the exception occurred, the function name where the exception was raised,
        the current date and time, and the full stack trace.

        Args:
            message (str): Additional message to be included in the exception information.
            exc_info (tuple): The exception information as returned by sys.exc_info().
                The tuple should contain (type, value, traceback).

        Returns:
            dict: A dictionary containing detailed information about the exception.
            The dictionary includes the following keys: '
            filename','lineno','name' ,'type','message','date_time','full_traceback'
        Raises:
            TypeError: If exc_info is not a tuple or does not have three elements.
        """
        exc_type, exc_value, exc_traceback = exc_info
        message = message or str(exc_value) if message or exc_value else ""

        traceback_details = {
            "namespace": self.calling_namespace_name,
            "service": self.calling_service_name,
            "filename_cdh": exc_traceback.tb_frame.f_code.co_filename,
            "lineno_cdh": exc_traceback.tb_lineno,
            "name_cdh": exc_traceback.tb_frame.f_code.co_name,
            "type_cdh": exc_type.__name__,
            # or just str(exc_value) for the message alone
            "message_cdh": str(message),
            "date_time_cdh": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "full_traceback_cdh": traceback.format_exception(
                exc_type, exc_value, exc_traceback
            ),
        }

        return traceback_details

    def error_with_exception(self, message, exc_info):
        """
        Logs an error message with exception details (if available).

        Args:
            message (str): The error message to be logged.
            exc_info (tuple): The exception information as returned by sys.exc_info().
                The tuple should contain (type, value, traceback).

        Raises:
            TypeError: If exc_info is not a tuple or does not have three elements.
        """

        try:
            if not isinstance(exc_info, tuple) or len(exc_info) != 3:
                raise TypeError(
                    "exc_info should be a tuple containing (type, value, traceback)."
                )

            exc_type, exc_instance, exc_traceback = exc_info

            # Convert traceback object to a string
            exc_traceback_str = "".join(traceback.format_tb(exc_traceback))

            # Get the calling frame
            frame = inspect.currentframe().f_back

            # Get the parameter values from the calling frame
            args, _, _, values = inspect.getargvalues(frame)

            # Log the exception information
            exception_info = f"{exc_type.__name__}: {exc_instance}: {exc_traceback_str}"
            message = f"{message}: {exception_info}"
            self.logger.error(message)
            properties = self.get_exception_info(message, exc_info)
            # Add each parameter to the properties object
            for arg in args:
                property_name = f"parameter_{str(arg)}"
                properties[property_name] = values[arg]

            message = str(message)
            self.logger.exception(message, extra=properties)
        except Exception as e_with_exception:
            print(
                f"Unable to log: An error occurred while handling an exception: {str(e_with_exception)}"
            )
            # raise ValueError("An error occurred while handling an exception")

    def get_env_share_path(self):
        """
        Returns the environment share path.

        :return: The environment share path.
        """
        return ENV_SHARE_PATH

    def initialize_logging_and_tracing(self):
        """
        Initializes logging and tracing for the CDC admin service.

        Args:
            namespace_name (str): The namespace name.
            service_name (str): The service name.

        Returns:
            tuple: A tuple containing the tracer and logger objects.
        """

        namespace_name = self.calling_namespace_name
        service_name = self.calling_service_name
        data_product_id = self.data_product_id
        environment = self.environment

        tracer = TracerSingleton.instance(
            namespace_name, service_name, data_product_id, environment
        ).get_tracer()
        logger = LoggerSingleton.instance(
            namespace_name, service_name, data_product_id, environment
        ).get_logger()

        return tracer, logger

    def truncate_log_file(self):
        """
        Truncate a log file.

        Returns:
        bool: True if the file was successfully truncated, False otherwise.
        """
        try:
            # 'w' mode will truncate the file.
            with open(LOG_FILENAME, "w", encoding="utf-8"):
                pass
            return 200
        except Exception as e_truncate_file:
            print(
                f"Unable to truncate file {LOG_FILENAME}. Error: {str(e_truncate_file)}"
            )
            return 500

    def get_logger(self):
        """
        Get the logger instance.

        Returns:
            logging.Logger: The logger instance.
        """
        return self.logger

    def force_flush(self):
        """This method forces an immediate write of all log
        messages currently in the buffer.

        In normal operation, log messages may be buffered for
        efficiency. This method ensures that all buffered messages
        are immediately written to their destination. It can be
        useful in scenarios where you want to ensure that all
        log messages have been written out, such as before ending
        a program.
        """
        for h in self.logger.handlers:
            h.flush()

    def get_datetime(self, entry):
        """
        Convert the first field of an entry to a datetime object.

        The log_entries will be sorted based on the datetime values returned by get_datetime.
        If parsing fails for an entry, the first field of that entry will be set to datetime.min.

        Args:
            entry (list): The entry containing datetime information.

        Returns:
            datetime: The datetime object converted from the first field of the entry,
            or datetime.min if parsing fails.
        """

        try:
            if isinstance(entry, str):
                entry = entry.split("\u001F")
            if len(entry) >= 2:
                date_time_str = entry[0]
                datetime_obj = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
                return datetime_obj
            else:
                error_msg = "Could not parse datetime from entry " + str(entry)
                raise ValueError(error_msg)
        except (TypeError, ValueError) as ex:
            print(
                f"Could not parse datetime from entry: { str(entry)}. Error: {str(ex)}"
            )
            return datetime.min

    def get_log_file_tail(self, number_of_lines=100):
        """
        Read the last number_of_lines from the log file, sorted by date in descending order.

        Args:
        file_path (str): The path to the log file.
        number_of_lines (int, optional): The number of lines to read from the end of the file. Defaults to 100.

        Returns:
        tuple: A tuple containing the actual number of lines read and the last number_of_lines of the log file.
        """

        try:
            self.force_flush()
            tracer_singleton = TracerSingleton.instance(
                self.calling_namespace_name,
                self.calling_service_name,
                self.data_product_id,
                self.environment,
            )
            tracer_singleton.force_flush()
            with open(LOG_FILENAME, "r", encoding="utf-8") as file:
                lines = file.readlines()

                if lines is not None:
                    # Sort the lines by date in descending order
                    lines.sort(
                        key=self.get_datetime,
                        reverse=True,
                    )

                    # Get the actual number of lines to read
                    actual_number_of_lines = min(number_of_lines, len(lines))

                    # Get the last number_of_lines
                    last_lines = lines[:actual_number_of_lines]

                    # Combine the lines into a single string
                    log_content = "".join(last_lines)
                    return 200, actual_number_of_lines, str(log_content)

                # Handle the case when lines is None
                actual_number_of_lines = 0
                log_content = ""
                return 500, actual_number_of_lines, str(log_content)

        except FileNotFoundError:
            error_msg = f"File {LOG_FILENAME} not found."
            return 500, 0, str(error_msg)
