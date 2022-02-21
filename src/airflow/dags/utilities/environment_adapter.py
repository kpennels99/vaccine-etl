"""Class to initialise all required environment variables."""
from environs import Env

class EnvironmentAdapter:
    
    def __init__(self):
        """Initialise instance attributes.
        
        All instance variables correspond to the environmet variables required by DAGs.
        """
        self.env = Env()
        self.data_url = self.env.str("DATA_URL")
        self.import_file_path = self.env.str("IMPORT_FILE_PATH")
        self.destination_db = self.env.str("DESTINATION_DATABASE_NAME")
        self.destination_db_host = self.env.str("DESTINATION_DATABASE_HOST")
        self.destination_db_user = self.env.str("DESTINATION_DATABASE_USERNAME")
        self.destination_db_password = self.env.str("DESTINATION_DATABASE_PASSWORD")
        self.destination_db_port = self.env.str("DESTINATION_DATABASE_PORT")
        self.destination_db_table = self.env.str("DESTINATION_DATABASE_TABLE")
        
    def destination_db_connection(self, driver: str) -> str:
        """Construct database connection string.

        Args:
            driver ([str]): Name of database driver to use in connection

        Returns:
            [str]: Database connection string
        """
        return (f"{driver}://{self.destination_db_user}:{self.destination_db_password}@"
            f"{self.destination_db_host}:{self.destination_db_port}/{self.destination_db}")
        
        