import pytest
import warnings
from fastapi.testclient import TestClient

@pytest.fixture(autouse=True)
def ignore_warnings():
    warnings.simplefilter("ignore", DeprecationWarning)
    warnings.simplefilter("ignore", RuntimeWarning)
    warnings.simplefilter("ignore", UserWarning)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.session import get_db

@pytest.fixture
def test_client():

    with TestClient(app) as client:
        yield client

# Optionally, mock the db dependency if we have db-dependent tests
@pytest.fixture
def mock_db_session():
    # Simple fake session that we can patch or customize per test
    class FakeSession:
        async def execute(self, *args, **kwargs):
            return None
        async def commit(self):
            pass
        async def close(self):
            pass
    
    return FakeSession()

@pytest.fixture
def override_get_db(mock_db_session):
    async def _override_get_db():
        yield mock_db_session
        
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()
