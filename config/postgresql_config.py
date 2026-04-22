"""
PostgreSQL Configuration for Carbon Trace Kenya
Optimized settings for Matatu fleet data management
"""

import os
from typing import Dict, Any

class PostgreSQLConfig:
    """PostgreSQL configuration class with optimized settings"""
    
    # Default connection settings
    DEFAULT_HOST = "localhost"
    DEFAULT_PORT = 5432
    DEFAULT_USER = "postgres"
    DEFAULT_PASSWORD = "password"
    DEFAULT_DATABASE = "carbon_trace"
    
    # Connection pool settings
    POOL_SIZE = 10
    MAX_OVERFLOW = 20
    POOL_PRE_PING = True
    POOL_RECYCLE = 3600  # 1 hour
    
    # Query optimization settings
    ECHO = False  # Set to True for SQL debugging
    FUTURE = True  # Use SQLAlchemy 2.0 style
    
    # Performance settings
    ISOLATION_LEVEL = "READ_COMMITTED"
    EXECUTION_OPTIONS = {
        "stream_results": True,
        "compiled_cache": {}
    }
    
    @classmethod
    def get_connection_url(cls, **kwargs) -> str:
        """Generate PostgreSQL connection URL"""
        host = kwargs.get('host', cls.DEFAULT_HOST)
        port = kwargs.get('port', cls.DEFAULT_PORT)
        user = kwargs.get('user', cls.DEFAULT_USER)
        password = kwargs.get('password', cls.DEFAULT_PASSWORD)
        database = kwargs.get('database', cls.DEFAULT_DATABASE)
        
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    @classmethod
    def get_engine_kwargs(cls) -> Dict[str, Any]:
        """Get PostgreSQL-specific engine arguments"""
        return {
            'echo': cls.ECHO,
            'future': cls.FUTURE,
            'pool_size': cls.POOL_SIZE,
            'max_overflow': cls.MAX_OVERFLOW,
            'pool_pre_ping': cls.POOL_PRE_PING,
            'pool_recycle': cls.POOL_RECYCLE,
            'isolation_level': cls.ISOLATION_LEVEL,
            'execution_options': cls.EXECUTION_OPTIONS
        }
    
    @classmethod
    def get_environment_config(cls) -> Dict[str, str]:
        """Get configuration from environment variables"""
        return {
            'host': os.getenv('POSTGRES_HOST', cls.DEFAULT_HOST),
            'port': int(os.getenv('POSTGRES_PORT', cls.DEFAULT_PORT)),
            'user': os.getenv('POSTGRES_USER', cls.DEFAULT_USER),
            'password': os.getenv('POSTGRES_PASSWORD', cls.DEFAULT_PASSWORD),
            'database': os.getenv('POSTGRES_DATABASE', cls.DEFAULT_DATABASE)
        }

# PostgreSQL-specific optimizations for Matatu fleet data
class MatatuPostgreSQLOptimizations:
    """PostgreSQL optimizations specific to Matatu fleet data"""
    
    # Recommended indexes for performance
    RECOMMENDED_INDEXES = [
        # SACCO indexes
        "CREATE INDEX IF NOT EXISTS idx_matatu_saccos_name ON matatu_saccos (name);",
        "CREATE INDEX IF NOT EXISTS idx_matatu_saccos_compliance ON matatu_saccos (ntsa_compliance_rating);",
        
        # Vehicle indexes
        "CREATE INDEX IF NOT EXISTS idx_matatu_vehicles_sacco_id ON matatu_vehicles (sacco_id);",
        "CREATE INDEX IF NOT EXISTS idx_matatu_vehicles_registration ON matatu_vehicles (registration_number);",
        "CREATE INDEX IF NOT EXISTS idx_matatu_vehicles_route ON matatu_vehicles (route_number);",
        "CREATE INDEX IF NOT EXISTS idx_matatu_vehicles_active ON matatu_vehicles (is_active);",
        "CREATE INDEX IF NOT EXISTS idx_matatu_vehicles_fuel_type ON matatu_vehicles (fuel_type);",
        
        # Inspection indexes
        "CREATE INDEX IF NOT EXISTS idx_ntsa_inspections_vehicle_id ON ntsa_inspections (vehicle_id);",
        "CREATE INDEX IF NOT EXISTS idx_ntsa_inspections_date ON ntsa_inspections (inspection_date);",
        "CREATE INDEX IF NOT EXISTS idx_ntsa_inspections_rating ON ntsa_inspections (overall_rating);",
        
        # Composite indexes for common queries
        "CREATE INDEX IF NOT EXISTS idx_vehicles_sacco_active ON matatu_vehicles (sacco_id, is_active);",
        "CREATE INDEX IF NOT EXISTS idx_inspections_vehicle_date ON ntsa_inspections (vehicle_id, inspection_date);"
    ]
    
    # Partitioning suggestions for large datasets
    PARTITIONING_SUGGESTIONS = [
        # Partition inspections by year for better performance
        """
        CREATE TABLE ntsa_inspections_partitioned (
            LIKE ntsa_inspections INCLUDING ALL
        ) PARTITION BY RANGE (inspection_date);
        
        CREATE TABLE ntsa_inspections_2024 PARTITION OF ntsa_inspections_partitioned
        FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
        
        CREATE TABLE ntsa_inspections_2025 PARTITION OF ntsa_inspections_partitioned
        FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
        
        CREATE TABLE ntsa_inspections_2026 PARTITION OF ntsa_inspections_partitioned
        FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');
        """,
        
        # Partition vehicles by year of manufacture for analytics
        """
        CREATE TABLE matatu_vehicles_partitioned (
            LIKE matatu_vehicles INCLUDING ALL
        ) PARTITION BY RANGE (year_of_manufacture);
        
        CREATE TABLE matatu_vehicles_pre_2010 PARTITION OF matatu_vehicles_partitioned
        FOR VALUES FROM (MINVALUE) TO (2010);
        
        CREATE TABLE matatu_vehicles_2010_2015 PARTITION OF matatu_vehicles_partitioned
        FOR VALUES FROM (2010) TO (2015);
        
        CREATE TABLE matatu_vehicles_2015_2020 PARTITION OF matatu_vehicles_partitioned
        FOR VALUES FROM (2015) TO (2020);
        
        CREATE TABLE matatu_vehicles_2020_plus PARTITION OF matatu_vehicles_partitioned
        FOR VALUES FROM (2020) TO (MAXVALUE);
        """
    ]
    
    # JSON column optimizations for PostgreSQL
    JSON_OPTIMIZATIONS = [
        # Create GIN indexes for JSON columns
        "CREATE INDEX IF NOT EXISTS idx_inspections_violations_gin ON ntsa_inspections USING GIN (violations_found);",
        "CREATE INDEX IF NOT EXISTS idx_inspections_recommendations_gin ON ntsa_inspections USING GIN (recommendations);"
    ]
    
    # Performance monitoring queries
    PERFORMANCE_QUERIES = {
        'table_sizes': """
            SELECT 
                schemaname,
                tablename,
                attname,
                n_distinct,
                correlation
            FROM pg_stats 
            WHERE schemaname = 'public' 
            AND tablename IN ('matatu_saccos', 'matatu_vehicles', 'ntsa_inspections')
            ORDER BY tablename, attname;
        """,
        
        'index_usage': """
            SELECT 
                schemaname,
                tablename,
                indexname,
                idx_scan,
                idx_tup_read,
                idx_tup_fetch
            FROM pg_stat_user_indexes 
            WHERE schemaname = 'public'
            ORDER BY idx_scan DESC;
        """,
        
        'slow_queries': """
            SELECT 
                query,
                calls,
                total_time,
                mean_time,
                rows
            FROM pg_stat_statements 
            WHERE query LIKE '%matatu%' OR query LIKE '%ntsa%'
            ORDER BY mean_time DESC
            LIMIT 10;
        """
    }

# PostgreSQL backup and maintenance commands
class PostgreSQLMaintenance:
    """Backup and maintenance operations for PostgreSQL"""
    
    @staticmethod
    def backup_command(host: str, port: int, database: str, user: str, password: str, backup_file: str) -> str:
        """Generate pg_dump backup command"""
        return f"PGPASSWORD={password} pg_dump -h {host} -p {port} -U {user} -d {database} > {backup_file}"
    
    @staticmethod
    def restore_command(host: str, port: int, database: str, user: str, password: str, backup_file: str) -> str:
        """Generate psql restore command"""
        return f"PGPASSWORD={password} psql -h {host} -p {port} -U {user} -d {database} < {backup_file}"
    
    @staticmethod
    def vacuum_analyze_command(database: str) -> str:
        """Generate VACUUM ANALYZE command"""
        return f"psql -d {database} -c 'VACUUM ANALYZE;'"
    
    @staticmethod
    def reindex_command(database: str) -> str:
        """Generate REINDEX command"""
        return f"psql -d {database} -c 'REINDEX DATABASE {database};'"
