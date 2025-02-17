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
├── .devcontainer/
│   ├── devcontainer.json          # VS Code DevContainer configuration
│   ├── docker-compose.extend.yml  # DevContainer compose extension
│   └── Dockerfile.dev            # Development container definition
├── accelerator/
│   └── materials/
│       └── 1-getting-started/
│           ├── example.ipynb     # Example notebook for getting started
│           └── readme.md         # Module-specific documentation
├── kyuubi-conf/
│   └── kyuubi-defaults.conf      # Kyuubi server configuration
├── spark-conf/
│   └── spark-defaults.conf       # Spark configuration
├── delta-jars/                   # Delta Lake and AWS connector JARs
├── warehouse/                    # Hive metastore warehouse directory
├── docker-compose.yml           # Main Docker Compose configuration
├── LICENSE                      # Project license
├── Makefile                     # Project setup and management
├── README.md                    # Main project documentation
└── requirements.txt             # Python dependencies
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
make help

# Complete setup
make setup

# Verify the setup
make verify
```

Available Make commands:
- `make setup` - Complete setup (create dirs, download JARs, create configs)
- `make clean` - Remove all generated files and directories
- `make download-jars` - Download required JARs only
- `make create-dirs` - Create required directories only
- `make create-configs` - Create configuration files only
- `make verify` - Verify all components are properly set up
- `make help` - Show available commands

3. Open the project in VS Code:
```bash
code .
```

4. When prompted, click "Reopen in Container" or use the command palette (F1) and select "Dev-Containers: Reopen in Container"

## Services

The environment includes the following services:

### Kyuubi Server
- Port: 10009 (JDBC/THRIFT interface)
- Port: 19090 (Web UI)
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

1. Connection refused to Kyuubi:
   - Ensure Kyuubi service is running: `docker-compose ps`
   - Check Kyuubi logs: `docker-compose logs kyuubi`

2. MinIO connection issues:
   - Verify MinIO is healthy: `docker-compose ps`
   - Check credentials in Spark configuration

3. Delta Lake errors:
   - Verify Delta Lake JARs are present in `delta-jars/`
   - Check Spark configuration for Delta Lake extensions

4. Make setup issues:
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