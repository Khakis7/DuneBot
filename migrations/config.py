class Config:
    DB_USER = 'postgres'
    DB_PASSWORD = 'Dixoy9M$sm[PH8Y:$78D35k?_VIt'
    DB_HOST = 'dunespicewars.cn77zah16h10.us-east-2.rds.amazonaws.com:5432'
    DB_CONFIG = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}"