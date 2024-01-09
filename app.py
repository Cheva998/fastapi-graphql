from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import declarative_base, sessionmaker, Session
import strawberry
from strawberry.asgi import GraphQL
from strawberry.fastapi import GraphQLRouter



print('creating app ...')
app = FastAPI()

SQLALCHEMY_DATABASE_URL = "sqlite:///.example.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autofluxh=False, bing=engine)
Base: DeclarativeMeta = declarative_base()

def get_db(request: Request):
    return request.state.db

class Item(Base):
    __tablename__= 'items'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)

@strawberry.type
class ItemType:
    name: str
    description: str

@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "GraphQL query"

@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_item(self, info, name: str, description: str) -> ItemType:
        db_item = Item(name=name, description=description)
        db = info.context['db']
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return ItemType(name=db_item.name, description=db_item.description)

schema = strawberry.Schema(query=Query, mutation=Mutation)

# graphql_app = GraphQL(schema)
graphql_app = GraphQLRouter(schema)

app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
def hello():
    return "hello"

@app.get("/test")
def test_endpoint():
    return {"message": "working"}


# @app.post("/graphql")
# async def graphql(request: Request, db: Session = Depends(get_db)):
#     return await GraphQL(schema, context={"db": db}).__call__(request)


if __name__ == "__main__":
    app.run()