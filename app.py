from fastapi import FastAPI
import strawberry
from strawberry.fastapi import GraphQLRouter
from strawberry import ID
from typing import List
from models import Item, SessionLocal
from schemas import ItemType, ItemInput, PaginationInput


print('creating app ...')
app = FastAPI()


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
            # db.refresh(item)
        finally:
            db.close()
        return item
    @staticmethod
    def add_items(items: List[ItemInput]) -> List[ItemType]:
        db = SessionLocal()
        items_added = [Item(name=item.name, description=item.description) for item in items]
        try:
            db.add_all(items_added)
            db.commit()
            [db.refresh(item_added) for item_added in items_added]
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
        return items_added
        
        
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
    add_items: List[ItemType] = strawberry.field(resolver=MutationResolver.add_items)


schema = strawberry.Schema(query=Query, mutation=Mutation)

graphql_app = GraphQLRouter(schema)

app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
def hello():
    return "hello"

@app.get("/test")
def test_endpoint():
    return {"message": "working"}

@app.get("/get-number-tasks")
def get_number_of_tasks():
    db = SessionLocal()
    items = db.query(Item)
    return items

if __name__ == "__main__":
    app.run()