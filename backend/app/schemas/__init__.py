"""Pydantic schemas: the shape of request bodies and responses.

FastAPI uses these to validate input (bad input gets a 422 automatically) and to
generate the /docs page. Keep them separate from the database models, so changing a
table doesn't accidentally change what the API returns.
"""
