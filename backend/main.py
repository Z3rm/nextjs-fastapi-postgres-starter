from typing import List

from fastapi import FastAPI, HTTPException, Query

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.dialects.mysql import insert

from intent import intent_processor
from db.seed import seed_user_if_needed
from sqlalchemy.ext.asyncio import AsyncSession
from db.db_engine import engine
from db.models import User, UserQuery, Responses

seed_user_if_needed()

app = FastAPI()

class UserRead(BaseModel):
    id: int
    name: str

class QueryInput(BaseModel):
    user_id: int
    query_input: str

class QueryResponse(BaseModel):
    response: str

class QueryResponsePair(BaseModel):
    query: str
    response: str

@app.get("/users/me")
async def get_my_user():
    async with AsyncSession(engine) as session:
        async with session.begin():
            # Sample logic to simplify getting the current user. There's only one user.
            result = await session.execute(select(User).where(User.name == "Zach"))
            user = result.scalars().first()


            if user is None:
                raise HTTPException(status_code=404, detail="User not found")
            return UserRead(id=user.id, name=user.name)


@app.post("/query",  response_model=QueryResponse)
async def query(input: QueryInput):

    # Get the query inputs from the request
    query_input_str = input.query_input
    user_id = input.user_id

    async with AsyncSession(engine) as session:
        async with session.begin():

            # Insert the query in to the 'queries' table for persistence
            query_id = await session.execute(
                insert(UserQuery).values(user_id=user_id, query_input=query_input_str).returning(UserQuery.id)
            )
            response_message = intent_processor.process_query(query_input_str)

            # Insert the response in to the 'responses' table for persistence
            await session.execute(insert(Responses).values(query_id=query_id.scalar_one(), response=response_message))

    return QueryResponse(response=response_message)


@app.get("/conversation", response_model=List[QueryResponsePair])
async def get_conversation(user: int = Query(..., description="User ID")):  # Keep using FastAPI's Query unmodified
    async with AsyncSession(engine) as session:
        async with session.begin():
            result = await session.execute(
                select(UserQuery, Responses)
                .join(Responses, UserQuery.id == Responses.query_id)
                .where(UserQuery.user_id == user)
                .order_by(UserQuery.timestamp, Responses.timestamp.desc())
            )
            conversation = result.all()

            if not conversation:
                return []

            return [
                QueryResponsePair(query=query.query_input, response=response.response)
                for query, response in conversation
            ]