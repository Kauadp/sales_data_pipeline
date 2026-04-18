from sqlalchemy import create_engine

_engine = None

def get_engine(DATABASE_URL: str = None):
    global _engine

    if _engine is None:
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL não foi fornecido.")
        
        print("Conectando ao banco de dados...")

        _engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=300
        )
    
    print("Conexão estabelecida.")

    return _engine

