from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    #Cloudinary Config
    CLOUDINARY_CLOUD_NAME: str = 'dmrfaxbtv'
    CLOUDINARY_API_KEY: str = '597737683316288'
    CLOUDINARY_API_SECRET: str = 'GAbCUWQC1ojhtqmfIAuH_cCZJ5E'
    
    # Database settings
    DB_SERVER: str = 'db-instance-opentalent.ccdr4urnwhez.ap-south-1.rds.amazonaws.com'
    DB_NAME: str = 'Indixpert_Api_Training_NonProd'
    DB_USER: str = 'training'
    DB_PASSWORD: str = 'Indixpert@12345'
    DB_DRIVER: str = 'ODBC+Driver+17+for+SQL+Server'
    @property
    def DATABASE_URL(self):
        return (
            f"mssql+pyodbc://{self.DB_USER}:{self.DB_PASSWORD.replace('@', '%40')}"
            f"@{self.DB_SERVER}/{self.DB_NAME}?driver={self.DB_DRIVER.replace(' ', '+')}"
        )

    class Config:
        env_file = ".env"  # load values from .env file
        
    


settings = Settings() # type: ignore