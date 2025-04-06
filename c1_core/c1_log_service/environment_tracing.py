import os
import sys
import platform
import time
import socket
import logging
from datetime import datetime
from pathlib import Path

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter, SimpleSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
from logging.handlers import TimedRotatingFileHandler
from opentelemetry.sdk.trace.export import SpanExportResult


dbutils_exists = "dbutils" in locals() or "dbutils" in globals()
if dbutils_exists is False:  # Use '==' for comparison instead of 'is'
    # pylint: disable=invalid-name
    dbutils = None


# Import from sibling directory ..\cdc_tech_environment_service
OS_NAME = os.name
sys.path.append("..")

TRACE_FILE_NAME_PREFIX = "c1_core_tracing"

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

    TRACE_FILENAME = ENV_SHARE_PATH / f"{TRACE_FILE_NAME_PREFIX}.txt"

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
        SUB_PATH = f"{TRACE_FILE_NAME_PREFIX}.txt"
        SUB_PATH = SUB_PATH.lstrip("/\\")
        TRACE_FILENAME = os.path.join(ENV_SHARE_PATH, SUB_PATH)

    except RuntimeError as e:
        # Handle the error if home directory can't be determined
        print(f"Error occurred: {e}")
        # Set a fallback path or handle the error appropriately
        # Example: using a predefined directory or terminating the program
        # Replace 'fallback_directory_path' with an actual path or another error handling strategy
        ENV_SHARE_PATH = ENV_SHARE_FALLBACK_PATH
        SUB_PATH = f"{TRACE_FILE_NAME_PREFIX}.txt"
        SUB_PATH = SUB_PATH.lstrip("/\\")
        TRACE_FILENAME = os.path.join(ENV_SHARE_PATH, SUB_PATH)
        sys.path.append(ENV_SHARE_PATH)

print(f"TRACE_FILENAME: {TRACE_FILENAME}")

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
            TRACE_FILENAME = ENV_SHARE_FALLBACK_PATH + "/c1_core_tracing.txt"

# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)

APPLICATIONINSIGHTS_INSTRUMENTATION_KEY_DEV = "8f02ef9a-cd94-48cf-895a-367f102e8a24"

APPLICATIONINSIGHTS_CONNECTION_STRING_DEV = (
    f"InstrumentationKey={APPLICATIONINSIGHTS_INSTRUMENTATION_KEY_DEV};"
    "IngestionEndpoint=https://eastus-8.in.applicationinsights.azure.com/;"
    "LiveEndpoint=https://eastus.livediagnostics.monitor.azure.com/"
)

class FileTraceExporter:
    """
    A class that exports spans to a file for environment tracing.
    """

    def __init__(self):
        self.file_path = TRACE_FILENAME
        self.file_handler = TimedRotatingFileHandler(
            self.file_path, when="midnight", interval=1, backupCount=7
        )
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    def to_readable_dict(self, span):
        return {
            "trace_id": str(span.context.trace_id),
            "span_id": str(span.context.span_id),
            "parent_id": str(span.parent.span_id) if span.parent else None,
            "name": span.name,
            "status": span.status.status_code.name,
            "kind": span.kind.name,
            "start_time": str(span.start_time),
            "end_time": str(span.end_time),
            "attributes": dict(span.attributes),
        }

    def export(self, spans):
        for span in spans:
            span_dict = self.to_readable_dict(span)
            record_dict = {
                "msg": f"Span Data: {span_dict}",
                "args": None,
                "levelname": "INFO",
            }
            log_record = logging.makeLogRecord(record_dict)
            self.file_handler.handle(log_record)
        return SpanExportResult.SUCCESS

    def shutdown(self):
        self.file_handler.close()

class TracerSingleton:
    _instance = None
    log_to_console = False

    @staticmethod
    def instance(calling_namespace_name, calling_service_name, data_product_id, environment, default_connection_string=None):
        if TracerSingleton._instance is None:
            TracerSingleton(calling_namespace_name, calling_service_name, data_product_id, environment, default_connection_string)
        return TracerSingleton._instance

    def __init__(self, calling_namespace_name, calling_service_name, data_product_id, environment="dev", default_connection_string=None):
        if TracerSingleton._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            TracerSingleton._instance = self

        service_name = f"{data_product_id}.{calling_service_name}"
        cloud_role = f"{data_product_id}-{calling_service_name}-{environment}"

        resource = Resource.create({
            ResourceAttributes.SERVICE_NAME: service_name,
            ResourceAttributes.SERVICE_NAMESPACE: calling_namespace_name,
            "ai.cloud.role": cloud_role,
            "ai.cloud.roleInstance": socket.gethostname()
        })

        trace.set_tracer_provider(TracerProvider(resource=resource))

        if not default_connection_string:
            if environment == "prod":
                default_connection_string = (
                    "InstrumentationKey=e7808e07-4242-4ed3-908e-c0a4c3b719b1;"
                    "IngestionEndpoint=https://eastus-8.in.applicationinsights.azure.com/;"
                    "LiveEndpoint=https://eastus.livediagnostics.monitor.azure.com/"
                )
            else:
                default_connection_string = APPLICATIONINSIGHTS_CONNECTION_STRING_DEV

        connection_string = default_connection_string
        os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"] = connection_string

        self.instrumentation_key = self.extract_instrumentation_key(connection_string)

        file_trace_exporter = FileTraceExporter()
        file_span_processor = BatchSpanProcessor(file_trace_exporter)
        self.file_trace_exporter = file_trace_exporter
        trace.get_tracer_provider().add_span_processor(file_span_processor)

        exporter = AzureMonitorTraceExporter(connection_string=connection_string)
        self.azure_trace_exporter = exporter
        azure_span_processor = BatchSpanProcessor(exporter)
        trace.get_tracer_provider().add_span_processor(azure_span_processor)

        if TracerSingleton.log_to_console:
            trace.get_tracer_provider().add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))

        self.tracer = trace.get_tracer(__name__)

    def extract_instrumentation_key(self, connection_string):
        parts = connection_string.split(";")
        for part in parts:
            if part.startswith("InstrumentationKey="):
                return part.split("=")[1]
        return None

    def get_trace_file_path(self):
        return self.file_trace_exporter.file_path

    def get_tracer(self):
        return self.tracer

    def shutdown(self):
        try:
            trace.get_tracer_provider().force_flush()
        except Exception as e:
            logging.error(f"Error during force flush: {e}")

        try:
            self.file_trace_exporter.shutdown()
        except Exception as e:
            logging.error(f"Error during file trace exporter shutdown: {e}")

        try:
            trace.get_tracer_provider().shutdown()
        except Exception as e:
            logging.error(f"Error during tracer provider shutdown: {e}")

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
        trace.get_tracer_provider().force_flush()
