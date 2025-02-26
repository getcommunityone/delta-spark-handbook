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
├── .devcontainer/              # Development container configuration
│   ├── devcontainer.json       # VS Code DevContainer settings
│   ├── Dockerfile.dev          # Development environment Dockerfile
│   ├── Dockerfile.hive         # Hive server Dockerfile
│   └── Dockerfile.kyuubi       # Kyuubi server Dockerfile
├── .docker/                    # Docker-related files and configurations
├── .pytest_cache/              # Python test cache directory
├── .venv/                      # Python virtual environment
├── .vscode/                    # VS Code editor settings
├── accelerator/                # Project accelerator materials and examples
├── delta-jars/                 # Delta Lake JAR dependencies
├── delta-sharing-conf/         # Delta Sharing server configuration
├── hive-config/                # Hive server configuration
├── kyuubi-conf/                # Kyuubi server configuration
├── minio-data/                 # MinIO object storage data
├── mk/                         # Makefile includes directory
├── spark-conf/                 # Spark configuration files
├── src/                        # Source code directory
├── tests/                      # Test files directory
├── warehouse/                  # Data warehouse directory
├── .gitignore                  # Git ignore patterns
├── derby.log                   # Derby database log file
├── docker-compose.yml          # Docker Compose configuration
├── LICENSE                     # Project license file
├── Makefile                    # Project automation scripts
├── README.md                   # Project documentation
└── requirements.txt            # Python package dependencies
```

## Quick Start

1. Clone this repository:
```bash
git clone <repository-url>
cd delta-spark-handbook
```

2. Open the project in VS Code:
```bash
code .
```

3. Create warehouse directory in project root

4. Run the setup using Make:
```bash
# View available commands
sudo make spark-download-jars
make kyu-download-jars
make delta-download-jars
```

This downloads the necessary JAR files for Spark, Kyuubi, and Delta Lake.  The entire set of JAR files is included in the `delta-jars/` directory in order to prevent version conflicts and ensure compatibility across containers.

 
## Services

The environment includes the following services:
Based on the Docker Compose file provided, here's an updated services section:

## Services

The environment includes the following services:

### MinIO (S3-compatible storage)
- Ports: 9000 (API), 9001 (Console)
- Credentials: minioadmin/minioadmin
- Volume: minio-data
- Health check enabled
- Includes a 'createbucket' service that creates a public 'wba' bucket

### PostgreSQL
- Port: 5432
- Database: metastore_db
- Credentials: admin/admin
- Health check enabled

### Hive Metastore
- Port: 9083
- Connected to PostgreSQL
- Custom configuration in hive-config/
- Includes AWS connectivity JARs

### Hive Server
- Ports: 10000, 10002
- Custom configuration in hive-config/
- Includes AWS connectivity JARs

### Spark Master
- Ports: 8080 (Web UI), 7077 (Master)
- Configuration: spark-conf/
- Delta JAR files mounted from delta-jars/
- Environment variables for MinIO access

### Spark Worker
- Memory: 4G
- Cores: 2
- Connected to Spark Master
- Delta JAR files mounted from delta-jars/

### Delta Sharing Server
- Port: 7777
- Configuration: delta-sharing-conf/delta-sharing-server-config.yaml
- Health check enabled

### Kyuubi Server
- Ports: 10009 (JDBC/THRIFT interface), 10099
- Connected to Spark Master and MinIO
- Health check enabled

### Development Container
- Built from Dockerfile.dev
- Workspace mounted at /workspace
- Docker socket mounted for Docker-in-Docker
- Connected to all other services

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

### Option 1: Docker Compose

Start up

```bash
sudo docker-compose up -d
```

Shut Down

```bash
docker-compose down
```

### Option 2: VS Code DevContainer

Start up

```bash
code .
# Reopen in Container
```

Shut down

```bash
# Close VS Code
```

## Connecting to Services

### DBeaver Connection

1. Add a new connection
2. Select "Apache Hive"
3. Configure:
   - Host: localhost
   - Port: 10009
   - Username: (leave blank for no authentication)
   - URL: jdbc:hive2://localhost:10009

### Sample SQL Queries

1. View Databases

```sql
-- View databases
SHOW DATABASES;
```

2. Create table

```sql
-- Create table
CREATE TABLE employees (
    id INT,
    first_name STRING,
    last_name STRING,
    email STRING,
    department STRING,
    salary DOUBLE,
    hire_date STRING
) USING DELTA;
```

Note you can also create tables in PARQUET and ORC formats.  However, those formats do not support ACID transactions other features of Delta Lake.

3. Insert data

```sql
-- Insert 10 rows of sample data
INSERT INTO employees VALUES
    (1, 'John', 'Smith', 'john.smith@company.com', 'Engineering', 85000.00, '2020-01-15'),
    (2, 'Sarah', 'Johnson', 'sarah.j@company.com', 'Marketing', 75000.00, '2020-03-20'),
    (3, 'Michael', 'Williams', 'mike.w@company.com', 'Sales', 90000.00, '2019-11-10'),
    (4, 'Lisa', 'Brown', 'lisa.b@company.com', 'HR', 65000.00, '2021-02-28'),
    (5, 'David', 'Miller', 'david.m@company.com', 'Engineering', 95000.00, '2019-08-15'),
    (6, 'Emily', 'Davis', 'emily.d@company.com', 'Marketing', 72000.00, '2021-06-01'),
    (7, 'James', 'Wilson', 'james.w@company.com', 'Sales', 88000.00, '2020-09-12'),
    (8, 'Jennifer', 'Taylor', 'jennifer.t@company.com', 'Engineering', 82000.00, '2021-04-05'),
    (9, 'Robert', 'Anderson', 'robert.a@company.com', 'HR', 67000.00, '2020-07-22'),
    (10, 'Maria', 'Garcia', 'maria.g@company.com', 'Sales', 86000.00, '2019-12-30');
```

4. Query data

```sql
-- Query all rows
SELECT * FROM employees;
```

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

6. Security issues on spark config
   - Ensure you have correct permission on spark-conf directory.
```bash
   sudo chown -R 1001:1001 spark-conf
   sudo chmod -R 755 ./spark-conf
   sudo chmod a+rx ./spark-conf/spark-env.sh
```

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