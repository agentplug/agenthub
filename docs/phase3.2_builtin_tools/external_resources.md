# External Resources Access System Implementation Plan

## 🎯 Overview

A comprehensive external resources access system that provides secure, efficient access to databases, APIs, IoT sensors, cloud services, and other external data sources. Built using the existing `@tool` decorator system for seamless integration with various protocols and authentication methods.

## 📋 Core Capabilities

- **Database Connectivity**: SQL databases, NoSQL databases, data warehouses
- **API Integration**: REST APIs, GraphQL, webhooks, authentication
- **IoT Device Access**: Sensors, actuators, real-time data streams
- **Cloud Services**: AWS, Azure, GCP, storage, compute, AI services
- **File Systems**: Local, network, cloud storage access
- **Message Queues**: RabbitMQ, Apache Kafka, Redis, message processing
- **Security**: Authentication, authorization, encryption, audit logging

## 🛠️ Tool Implementations

### 1. Database Query Tool

```python
@tool(
    name="database_query",
    description="Execute queries on various database systems"
)
def database_query(
    query: str,
    database_type: str = "postgresql",
    connection_string: str = None,
    query_type: str = "select",
    timeout: int = 30,
    max_rows: int = 1000,
    parameters: dict = None,
    explain: bool = False
) -> dict:
    """
    Execute queries on various database systems.
    
    Args:
        query: SQL query to execute
        database_type: Database type ('postgresql', 'mysql', 'sqlite', 'mongodb', 'redis')
        connection_string: Database connection string
        query_type: Type of query ('select', 'insert', 'update', 'delete', 'ddl')
        timeout: Query timeout in seconds
        max_rows: Maximum number of rows to return
        parameters: Query parameters for prepared statements
        explain: Whether to include query execution plan
    
    Returns:
        dict: Query results with data, metadata, and execution info
    """
    pass
```

### 2. API Client Tool

```python
@tool(
    name="api_request",
    description="Make HTTP requests to external APIs"
)
def api_request(
    url: str,
    method: str = "GET",
    headers: dict = None,
    params: dict = None,
    data: dict = None,
    json_data: dict = None,
    auth_type: str = None,
    auth_credentials: dict = None,
    timeout: int = 30,
    retry_count: int = 3,
    rate_limit: int = None
) -> dict:
    """
    Make HTTP requests to external APIs with authentication and rate limiting.
    
    Args:
        url: API endpoint URL
        method: HTTP method ('GET', 'POST', 'PUT', 'DELETE', 'PATCH')
        headers: HTTP headers
        params: URL parameters
        data: Form data
        json_data: JSON payload
        auth_type: Authentication type ('basic', 'bearer', 'api_key', 'oauth2')
        auth_credentials: Authentication credentials
        timeout: Request timeout in seconds
        retry_count: Number of retry attempts
        rate_limit: Requests per minute limit
    
    Returns:
        dict: API response with data, status, headers, and metadata
    """
    pass
```

### 3. IoT Device Tool

```python
@tool(
    name="iot_device_access",
    description="Access and control IoT devices and sensors"
)
def iot_device_access(
    device_id: str,
    action: str = "read",
    protocol: str = "mqtt",
    data: dict = None,
    timeout: int = 10,
    retry_count: int = 3,
    qos: int = 1
) -> dict:
    """
    Access and control IoT devices and sensors.
    
    Args:
        device_id: Unique device identifier
        action: Action to perform ('read', 'write', 'subscribe', 'unsubscribe')
        protocol: Communication protocol ('mqtt', 'coap', 'http', 'modbus', 'opcua')
        data: Data to send to device
        timeout: Operation timeout in seconds
        retry_count: Number of retry attempts
        qos: Quality of Service level for MQTT
    
    Returns:
        dict: Device response with data, status, and metadata
    """
    pass
```

### 4. Cloud Storage Tool

```python
@tool(
    name="cloud_storage",
    description="Access cloud storage services"
)
def cloud_storage(
    operation: str,
    provider: str = "aws",
    bucket_name: str = None,
    object_key: str = None,
    local_path: str = None,
    credentials: dict = None,
    region: str = None,
    storage_class: str = "STANDARD"
) -> dict:
    """
    Access cloud storage services for file operations.
    
    Args:
        operation: Operation to perform ('upload', 'download', 'list', 'delete', 'copy')
        provider: Cloud provider ('aws', 'azure', 'gcp', 'minio')
        bucket_name: Storage bucket/container name
        object_key: Object key/path in storage
        local_path: Local file path
        credentials: Cloud provider credentials
        region: Cloud region
        storage_class: Storage class for uploads
    
    Returns:
        dict: Operation result with status, metadata, and data
    """
    pass
```

### 5. Message Queue Tool

```python
@tool(
    name="message_queue",
    description="Send and receive messages from message queues"
)
def message_queue(
    operation: str,
    queue_name: str,
    message: dict = None,
    broker_type: str = "rabbitmq",
    connection_string: str = None,
    routing_key: str = None,
    exchange: str = None,
    durable: bool = True,
    timeout: int = 30
) -> dict:
    """
    Send and receive messages from message queues.
    
    Args:
        operation: Operation ('publish', 'consume', 'declare', 'delete')
        queue_name: Name of the queue
        message: Message to send (for publish operations)
        broker_type: Message broker type ('rabbitmq', 'kafka', 'redis', 'sqs')
        connection_string: Broker connection string
        routing_key: Message routing key
        exchange: Exchange name (for RabbitMQ)
        durable: Whether queue should be durable
        timeout: Operation timeout in seconds
    
    Returns:
        dict: Operation result with status and message data
    """
    pass
```

### 6. File System Tool

```python
@tool(
    name="file_system",
    description="Access local and network file systems"
)
def file_system(
    operation: str,
    path: str,
    content: str = None,
    encoding: str = "utf-8",
    create_dirs: bool = True,
    recursive: bool = False,
    pattern: str = None,
    follow_symlinks: bool = True
) -> dict:
    """
    Access local and network file systems.
    
    Args:
        operation: Operation ('read', 'write', 'list', 'delete', 'copy', 'move', 'exists')
        path: File or directory path
        content: Content to write (for write operations)
        encoding: Text encoding for file operations
        create_dirs: Whether to create directories if they don't exist
        recursive: Whether to perform operation recursively
        pattern: File pattern for list operations (e.g., '*.txt')
        follow_symlinks: Whether to follow symbolic links
    
    Returns:
        dict: Operation result with data, status, and metadata
    """
    pass
```

## 🏗️ Implementation Architecture

### Core Components

```python
# agenthub/core/tools/builtin/external/
class ExternalResourceManager:
    """Central manager for external resource access."""
    
    def __init__(self):
        self.connections = {}
        self.authenticators = {
            'basic': BasicAuthenticator(),
            'bearer': BearerAuthenticator(),
            'api_key': APIKeyAuthenticator(),
            'oauth2': OAuth2Authenticator()
        }
        self.rate_limiters = {}
        self.audit_logger = AuditLogger()
    
    def get_connection(self, resource_type: str, config: dict) -> Connection:
        """Get or create connection to external resource."""
        connection_id = self._generate_connection_id(resource_type, config)
        
        if connection_id in self.connections:
            return self.connections[connection_id]
        
        # Create new connection
        connection = self._create_connection(resource_type, config)
        self.connections[connection_id] = connection
        
        return connection
    
    def _create_connection(self, resource_type: str, config: dict) -> Connection:
        """Create new connection based on resource type."""
        if resource_type == 'database':
            return DatabaseConnection(config)
        elif resource_type == 'api':
            return APIConnection(config)
        elif resource_type == 'iot':
            return IoTConnection(config)
        elif resource_type == 'cloud':
            return CloudConnection(config)
        else:
            raise ValueError(f"Unknown resource type: {resource_type}")

class DatabaseConnection:
    """Database connection with connection pooling."""
    
    def __init__(self, config: dict):
        self.config = config
        self.pool = self._create_connection_pool()
        self.query_cache = QueryCache()
    
    def execute_query(self, query: str, params: dict = None) -> dict:
        """Execute database query with caching and monitoring."""
        # Check cache
        cache_key = self._generate_cache_key(query, params)
        cached_result = self.query_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Get connection from pool
        connection = self.pool.get_connection()
        
        try:
            # Execute query
            result = connection.execute(query, params)
            
            # Cache result
            self.query_cache.set(cache_key, result)
            
            return result
        
        except Exception as e:
            self.audit_logger.log_error('database_query', str(e))
            raise
        
        finally:
            self.pool.return_connection(connection)

class APIConnection:
    """API connection with authentication and rate limiting."""
    
    def __init__(self, config: dict):
        self.config = config
        self.session = requests.Session()
        self.authenticator = self._setup_authentication()
        self.rate_limiter = RateLimiter(config.get('rate_limit', 60))
    
    def make_request(self, method: str, url: str, **kwargs) -> dict:
        """Make authenticated API request with rate limiting."""
        # Check rate limit
        if not self.rate_limiter.can_make_request():
            raise RateLimitExceeded("Rate limit exceeded")
        
        # Add authentication
        headers = kwargs.get('headers', {})
        headers.update(self.authenticator.get_headers())
        kwargs['headers'] = headers
        
        # Make request
        response = self.session.request(method, url, **kwargs)
        
        # Record rate limit usage
        self.rate_limiter.record_request()
        
        return {
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'data': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
            'url': response.url
        }
```

### Database Implementations

```python
class PostgreSQLConnection:
    """PostgreSQL database connection."""
    
    def __init__(self, config: dict):
        self.connection_string = config['connection_string']
        self.pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=self.connection_string
        )
    
    def execute_query(self, query: str, params: dict = None) -> dict:
        """Execute PostgreSQL query."""
        connection = self.pool.getconn()
        cursor = connection.cursor()
        
        try:
            cursor.execute(query, params)
            
            if query.strip().upper().startswith('SELECT'):
                data = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                return {
                    'success': True,
                    'data': [dict(zip(columns, row)) for row in data],
                    'row_count': len(data)
                }
            else:
                connection.commit()
                return {
                    'success': True,
                    'row_count': cursor.rowcount
                }
        
        except Exception as e:
            connection.rollback()
            raise DatabaseError(f"Query execution failed: {e}")
        
        finally:
            cursor.close()
            self.pool.putconn(connection)

class MongoDBConnection:
    """MongoDB database connection."""
    
    def __init__(self, config: dict):
        self.client = pymongo.MongoClient(config['connection_string'])
        self.database = self.client[config['database']]
    
    def execute_query(self, query: dict, collection: str) -> dict:
        """Execute MongoDB query."""
        try:
            collection_obj = self.database[collection]
            
            if 'find' in query:
                cursor = collection_obj.find(query['find'])
                if 'limit' in query:
                    cursor = cursor.limit(query['limit'])
                if 'sort' in query:
                    cursor = cursor.sort(query['sort'])
                
                data = list(cursor)
                return {
                    'success': True,
                    'data': data,
                    'count': len(data)
                }
            
            elif 'insert' in query:
                result = collection_obj.insert_many(query['insert'])
                return {
                    'success': True,
                    'inserted_ids': result.inserted_ids,
                    'count': len(result.inserted_ids)
                }
            
            elif 'update' in query:
                result = collection_obj.update_many(
                    query['filter'],
                    query['update']
                )
                return {
                    'success': True,
                    'modified_count': result.modified_count,
                    'matched_count': result.matched_count
                }
            
            else:
                raise ValueError("Unknown MongoDB operation")
        
        except Exception as e:
            raise DatabaseError(f"MongoDB operation failed: {e}")
```

### IoT Device Implementations

```python
class MQTTDeviceConnection:
    """MQTT-based IoT device connection."""
    
    def __init__(self, config: dict):
        self.client = mqtt.Client()
        self.broker_host = config['broker_host']
        self.broker_port = config.get('broker_port', 1883)
        self.username = config.get('username')
        self.password = config.get('password')
        
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)
        
        self.client.connect(self.broker_host, self.broker_port)
        self.client.loop_start()
    
    def read_device(self, device_id: str, topic: str = None) -> dict:
        """Read data from IoT device."""
        if not topic:
            topic = f"devices/{device_id}/data"
        
        try:
            # Subscribe to device topic
            self.client.subscribe(topic)
            
            # Wait for message
            message = self.client.wait_for_message(timeout=10)
            
            if message:
                data = json.loads(message.payload.decode())
                return {
                    'success': True,
                    'device_id': device_id,
                    'data': data,
                    'timestamp': time.time()
                }
            else:
                return {
                    'success': False,
                    'error': 'No data received from device'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': f"Device read failed: {e}"
            }
    
    def write_device(self, device_id: str, data: dict, topic: str = None) -> dict:
        """Write data to IoT device."""
        if not topic:
            topic = f"devices/{device_id}/command"
        
        try:
            message = json.dumps(data)
            self.client.publish(topic, message)
            
            return {
                'success': True,
                'device_id': device_id,
                'data_sent': data
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f"Device write failed: {e}"
            }
```

## 📊 Performance Optimizations

### 1. Connection Pooling
```python
class ConnectionPool:
    """Generic connection pool for external resources."""
    
    def __init__(self, factory, max_connections: int = 10):
        self.factory = factory
        self.max_connections = max_connections
        self.connections = []
        self.available = []
        self.lock = threading.Lock()
    
    def get_connection(self) -> Connection:
        """Get connection from pool."""
        with self.lock:
            if self.available:
                return self.available.pop()
            elif len(self.connections) < self.max_connections:
                connection = self.factory()
                self.connections.append(connection)
                return connection
            else:
                raise ConnectionPoolExhausted("No available connections")
    
    def return_connection(self, connection: Connection):
        """Return connection to pool."""
        with self.lock:
            if connection.is_valid():
                self.available.append(connection)
            else:
                self.connections.remove(connection)
```

### 2. Caching Strategy
```python
class ExternalResourceCache:
    """Intelligent caching for external resource data."""
    
    def __init__(self, max_size: int = 1000, ttl: int = 300):
        self.cache = {}
        self.max_size = max_size
        self.ttl = ttl  # Time to live in seconds
        self.access_times = {}
    
    def get(self, key: str) -> Any:
        """Get cached data."""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                self.access_times[key] = time.time()
                return data
            else:
                del self.cache[key]
                if key in self.access_times:
                    del self.access_times[key]
        return None
    
    def set(self, key: str, value: Any):
        """Cache data."""
        if len(self.cache) >= self.max_size:
            self._evict_lru()
        
        self.cache[key] = (value, time.time())
        self.access_times[key] = time.time()
```

### 3. Async Operations
```python
@tool(name="external_async_request", description="Make async requests to external resources")
async def external_async_request(
    requests: list,
    max_concurrent: int = 10
) -> dict:
    """Make multiple async requests to external resources."""
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def make_single_request(request_config):
        async with semaphore:
            if request_config['type'] == 'api':
                return await api_request_async(**request_config['params'])
            elif request_config['type'] == 'database':
                return await database_query_async(**request_config['params'])
            else:
                raise ValueError(f"Unknown request type: {request_config['type']}")
    
    tasks = [make_single_request(req) for req in requests]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return {
        'results': results,
        'total': len(requests),
        'successful': sum(1 for r in results if not isinstance(r, Exception))
    }
```

## 🔒 Security & Validation

### Authentication Management
```python
class AuthenticationManager:
    """Centralized authentication management."""
    
    def __init__(self):
        self.credentials = {}
        self.encryption = EncryptionService()
    
    def store_credentials(self, resource_id: str, credentials: dict) -> None:
        """Store encrypted credentials."""
        encrypted = self.encryption.encrypt(json.dumps(credentials))
        self.credentials[resource_id] = encrypted
    
    def get_credentials(self, resource_id: str) -> dict:
        """Get decrypted credentials."""
        if resource_id not in self.credentials:
            raise CredentialsNotFound(f"No credentials for {resource_id}")
        
        encrypted = self.credentials[resource_id]
        decrypted = self.encryption.decrypt(encrypted)
        return json.loads(decrypted)
    
    def rotate_credentials(self, resource_id: str, new_credentials: dict) -> None:
        """Rotate credentials for a resource."""
        self.store_credentials(resource_id, new_credentials)

class SecurityValidator:
    """Security validation for external resource access."""
    
    def __init__(self):
        self.allowed_domains = set()
        self.blocked_patterns = [
            r'localhost',
            r'127\.0\.0\.1',
            r'0\.0\.0\.0',
            r'file://',
            r'ftp://'
        ]
    
    def validate_url(self, url: str) -> bool:
        """Validate URL for security."""
        parsed = urlparse(url)
        
        # Check for blocked patterns
        for pattern in self.blocked_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                raise SecurityError(f"Blocked URL pattern: {pattern}")
        
        # Check domain whitelist
        if self.allowed_domains and parsed.netloc not in self.allowed_domains:
            raise SecurityError(f"Domain not in whitelist: {parsed.netloc}")
        
        return True
    
    def validate_query(self, query: str, query_type: str) -> bool:
        """Validate database query for security."""
        query_upper = query.upper()
        
        # Check for dangerous operations
        if query_type == 'select':
            dangerous_ops = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'INSERT', 'UPDATE']
            if any(op in query_upper for op in dangerous_ops):
                raise SecurityError("Dangerous operation in SELECT query")
        
        # Check for SQL injection patterns
        injection_patterns = [
            r';\s*DROP',
            r';\s*DELETE',
            r'UNION\s+SELECT',
            r'OR\s+1\s*=\s*1'
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                raise SecurityError("Potential SQL injection detected")
        
        return True
```

## 📈 Usage Examples

### Database Operations
```python
# Query PostgreSQL database
result = database_query(
    query="SELECT * FROM users WHERE age > %s",
    database_type="postgresql",
    connection_string="postgresql://user:pass@localhost/db",
    parameters={"age": 25},
    max_rows=100
)

# Query MongoDB
result = database_query(
    query={"find": {"status": "active"}, "limit": 50},
    database_type="mongodb",
    connection_string="mongodb://localhost:27017/mydb"
)
```

### API Operations
```python
# Make authenticated API request
response = api_request(
    url="https://api.example.com/data",
    method="GET",
    auth_type="bearer",
    auth_credentials={"token": "your_token"},
    headers={"Accept": "application/json"}
)

# POST data to API
response = api_request(
    url="https://api.example.com/create",
    method="POST",
    json_data={"name": "John", "email": "john@example.com"},
    auth_type="api_key",
    auth_credentials={"key": "your_api_key"}
)
```

### IoT Device Operations
```python
# Read from IoT sensor
sensor_data = iot_device_access(
    device_id="sensor_001",
    action="read",
    protocol="mqtt"
)

# Control IoT device
control_result = iot_device_access(
    device_id="actuator_001",
    action="write",
    protocol="mqtt",
    data={"command": "turn_on", "value": 1}
)
```

## 🧪 Testing Strategy

### Unit Tests
```python
def test_database_query():
    """Test database query functionality."""
    result = database_query(
        "SELECT 1 as test",
        "sqlite",
        ":memory:"
    )
    assert result["success"] == True
    assert result["data"][0]["test"] == 1

def test_api_request():
    """Test API request functionality."""
    result = api_request(
        "https://httpbin.org/get",
        "GET"
    )
    assert result["status_code"] == 200
```

### Integration Tests
```python
def test_end_to_end_workflow():
    """Test complete external resource workflow."""
    # 1. Query database
    db_result = database_query("SELECT * FROM test_table", "sqlite", ":memory:")
    
    # 2. Send data to API
    api_result = api_request(
        "https://httpbin.org/post",
        "POST",
        json_data=db_result["data"]
    )
    
    # 3. Store result in cloud storage
    storage_result = cloud_storage(
        "upload",
        "aws",
        bucket_name="test-bucket",
        object_key="result.json",
        data=api_result
    )
    
    # Verify all operations completed successfully
    assert db_result["success"] == True
    assert api_result["status_code"] == 200
    assert storage_result["success"] == True
```

## 📊 Performance Metrics

- **Database Queries**: < 1 second for simple queries
- **API Requests**: < 2 seconds for typical REST calls
- **IoT Operations**: < 5 seconds for device communication
- **Connection Pool**: Support 50+ concurrent connections
- **Cache Hit Rate**: > 80% for repeated operations

## 🔄 Future Enhancements

1. **GraphQL Support**: Native GraphQL query execution
2. **Real-time Streaming**: WebSocket and Server-Sent Events support
3. **Blockchain Integration**: Smart contract interaction
4. **Edge Computing**: IoT edge device management
5. **AI/ML Services**: Integration with cloud AI services
6. **Data Pipeline**: Automated data processing workflows
