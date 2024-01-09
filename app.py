from fastapi import FastAPI, Depends, HTTPException, Request
import strawberry
from strawberry.asgi import GraphQL
from strawberry.fastapi import GraphQLRouter
from strawberry import ID
from typing import List
from models import Item, SessionLocal
from schemas import ItemType, PaginationInput


print('creating app ...')
app = FastAPI()


def get_db(request: Request):
    return request.state.db

### Resolvers ####
class QueryResolver:
    @staticmethod
    def get_item_by_id(item_id: ID) -> (ItemType | None):
        db = SessionLocal()
        try:
            item = db.query(Item)\
              .filter(Item.id == item_id)\
              .first()
        finally:
            db.close()
        return item
    @staticmethod
    def get_items(pagination: (PaginationInput | None) = None) -> List[ItemType]:
        db = SessionLocal()
        try:
            query = db.query(Item)
            if pagination is not None:
                query = query\
                  .offset(pagination.offset)\
                  .limit(pagination.limit)
            items = query.all()
        finally:
            db.close()
        return items

class MutationResolver:
    @staticmethod
    def add_item(item_name: str, item_description: str) -> ItemType:
        db = SessionLocal()
        try:
            item = Item(name=item_name, description=item_description)
            db.add(item)
            db.commit()
            db.refresh(item)
        finally:
            db.close()
        return item


#### GraphQL types Query and Mutation ###
@strawberry.type
class Query:
    items: List[ItemType] = strawberry.field(resolver=QueryResolver.get_items)
    item_id: (ItemType | None) = strawberry.field(resolver=QueryResolver.get_item_by_id)
    @strawberry.field
    def hello(self) -> str:
        return "GraphQL query"

@strawberry.type
class Mutation:
    add_item: ItemType = strawberry.field(resolver=MutationResolver.add_item)

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