# Delta Spark Handbook [WSL: Ubuntu]

This repository contains a complete development environment setup for working with Apache Kyuubi, Delta Lake, Apache Spark, and MinIO. The environment is containerized using Docker and includes VS Code DevContainer configuration for a seamless development experience.

## Prerequisites

- Docker and Docker Compose
- Visual Studio Code
- VS Code Remote - Containers extension
- Git
- WSL2 with Ubuntu (for Windows users)
- GNU Make

## Project Structure

```
.
├── .devcontainer/              # Development container configuration
│   ├── devcontainer.json      # VS Code DevContainer settings
│   ├── Dockerfile.dev         # Development environment Dockerfile
│   └── Dockerfile.kyuubi      # Kyuubi server Dockerfile
├── .docker/                   # Docker-related files and configurations
├── .pytest_cache/            # Python test cache directory
├── .venv/                    # Python virtual environment
├── .vscode/                  # VS Code editor settings
├── accelerator/              # Project accelerator materials and examples
├── delta-jars/              # Delta Lake JAR dependencies
├── delta-sharing-conf/      # Delta Sharing server configuration
├── kyuubi-conf/             # Kyuubi server configuration
├── metastore_db/            # Hive metastore database files
├── minio-data/              # MinIO object storage data
├── mk/                      # Makefile includes directory
├── spark-conf/              # Spark configuration files
├── src/                     # Source code directory
├── tests/                   # Test files directory
├── warehouse/               # Data warehouse directory
├── .gitignore              # Git ignore patterns
├── derby.log               # Derby database log file
├── docker-compose.yml      # Docker Compose configuration
├── LICENSE                 # Project license file
├── Makefile               # Project automation scripts
├── README.md              # Project documentation
└── requirements.txt       # Python package dependencies
```

## Quick Start

1. Clone this repository:
```bash
git clone <repository-url>
cd delta-spark-handbook
```

2. Run the setup using Make:
```bash
# View available commands
make spark-download-jars
make kyu-download-jars
make delta-download-jars
```

This downloads the necessary JAR files for Spark, Kyuubi, and Delta Lake.  The entire set of JAR files is included in the `delta-jars/` directory in order to prevent version conflicts and ensure compatibility across containers.

3. Open the project in VS Code:
```bash
code .
```

4. When prompted, click "Reopen in Container" or use the command palette (F1) and select "Dev-Containers: Reopen in Container"

## Services

The environment includes the following services:

### Kyuubi Server
- Port: 10009 (JDBC/THRIFT interface)
- Port: 19099 (Web UI)
- Configuration: `kyuubi-conf/kyuubi-defaults.conf`

### Apache Spark
- Master Port: 7077
- Master Web UI: 8080
- Worker nodes: Configurable
- Configuration: `spark-conf/spark-defaults.conf`

### MinIO (S3-compatible storage)
- API Port: 9000
- Console Port: 9001
- Credentials: minioadmin/minioadmin
- Health check enabled

### Development Container
- Python 3.10
- Jupyter notebook support
- Code formatting with Black
- Direct access to all services
- Pre-configured VS Code extensions

## Module Structure

The project is organized into learning modules under the `accelerator/materials` directory:

1. Getting Started (`1-getting-started/`)
   - Basic Delta Lake operations
   - Connecting to services
   - Simple data transformations

Each module contains:
- Jupyter notebooks with examples and exercises
- Module-specific documentation
- Sample data (if required)
- Additional resources

## Starting Spark 


## Connecting to Services

### DBeaver Connection
1. Add a new connection
2. Select "Apache Hive"
3. Configure:
   - Host: localhost
   - Port: 10009
   - Username: (leave blank for no authentication)
   - URL: jdbc:hive2://localhost:10009

### Python Connection
```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("DeltaExample") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.secret.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()
```

## Configuration

### Customizing Spark
Edit `spark-conf/spark-defaults.conf` to modify Spark settings:
```conf
spark.executor.memory=4g
spark.executor.cores=2
```

### Customizing Kyuubi
Edit `kyuubi-conf/kyuubi-defaults.conf` to modify Kyuubi settings:
```conf
kyuubi.engine.share.level=CONNECTION
kyuubi.engine.pool.size=2
```

## Troubleshooting

### Common Issues

1. DelayedCommitProtocol or serialVersionUID mismatches in the following repositories:
   - Error: SQL Error: org.apache.kyuubi.KyuubiSQLException: org.apache.kyuubi.KyuubiSQLException: Error operating ExecuteStatement: org.apache.spark.SparkException: Job aborted due to stage failure: Task 0 in stage 8.0 failed 4 times, most recent failure: Lost task 0.3 in stage 8.0 (TID 25) (172.23.0.6 executor 0): java.io.InvalidClassException: org.apache.spark.sql.delta.files.DelayedCommitProtocol; local class incompatible: stream classdesc serialVersionUID = 6189279856998302271, local class serialVersionUID = -6318904361964873150
   - Ensure you have the correct version of the Delta Lake JARs
   - Check for version conflicts in `delta-jars/`
   - Ensure that both spark-master and kyuubi containers are using the same version of the JARs in delta-jars

2. Connection refused to Kyuubi:
   - Ensure Kyuubi service is running: `docker-compose ps`
   - Check Kyuubi logs: `docker-compose logs kyuubi`

3. MinIO connection issues:
   - Verify MinIO is healthy: `docker-compose ps`
   - Check credentials in Spark configuration

4. Delta Lake errors:
   - Verify Delta Lake JARs are present in `delta-jars/`
   - Check Spark configuration for Delta Lake extensions

5. Make setup issues:
   - Ensure you have GNU Make installed: `make --version`
   - Check for error messages in the Make output
   - Run `make verify` to check the setup
   - Try `make clean` followed by `make setup` for a fresh start

### Logs
View service logs:
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs kyuubi
docker-compose logs spark-master
docker-compose logs minio
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Create a pull request

### Development Setup
1. Run `make setup` to initialize the development environment
2. Make your changes
3. Use `make verify` to ensure everything is working
4. Submit your pull request

## License

[Add your license information here]