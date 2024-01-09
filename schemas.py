import strawberry

### GraphQL Schemas ###
@strawberry.type
class ItemType:
    id: int
    name: str
    description: str

@strawberry.input
class PaginationInput:
    offset: int
    limit: int