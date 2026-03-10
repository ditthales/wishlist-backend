from database import engine
import models

print("Dropando todas as tabelas...")
models.Base.metadata.drop_all(bind=engine)

print("Criando todas as tabelas...")
models.Base.metadata.create_all(bind=engine)

print("✓ Banco de dados resetado com sucesso!")
