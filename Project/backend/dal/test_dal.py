import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from testcontainers.postgres import PostgresContainer
from dal.dal import Recognition_DAL, Feature_set, Features

@pytest.fixture(scope="module")
async def db_session():
    # Start a PostgreSQL container
    postgres_container = PostgresContainer("postgres:latest")
    await postgres_container.start()

    # Create an async SQLAlchemy engine
    engine = create_async_engine(postgres_container.get_connection_url())

    # Create the database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create a sessionmaker
    async_session = sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    # Provide the session to the tests
    yield async_session()

    # Clean up - stop the container
    await async_session.close()
    await postgres_container.stop()

@pytest.mark.asyncio
async def test_upload_feature_set(db_session):
    # Initialize the DAL
    dal = Recognition_DAL()

    # Test data
    json_data = {
        "FeatureSet": "TestFeatureSet",
        "Features": ["Feature1", "Feature2", "Feature3"]
    }

    # Upload the feature set
    result = await dal.upload_feature_set(db_session, json_data)

    # Check if the upload was successful
    assert result is True

    # Verify that the feature set exists in the database
    feature_set = await db_session.execute(select(Feature_set).where(Feature_set.name == "TestFeatureSet"))
    assert feature_set is not None
    assert feature_set.name == "TestFeatureSet"
    assert len(feature_set.feature_children) == 3

@pytest.mark.asyncio
async def test_extend_feature_set(db_session):
    # Initialize the DAL
    dal = Recognition_DAL()

    # Test data
    json_data = {
        "FeatureSet": "TestFeatureSet",
        "Features": ["Feature4", "Feature5"]
    }

    # Extend the feature set
    result = await dal.extend_feature_set(db_session, json_data)

    # Check if the extension was successful
    assert result is True

    # Verify that the features were added to the feature set in the database
    feature_set = await db_session.execute(select(Feature_set).where(Feature_set.name == "TestFeatureSet"))
    assert feature_set is not None
    assert len(feature_set.feature_children) == 5

@pytest.mark.asyncio
async def test_delete_feature_set(db_session):
    # Initialize the DAL
    dal = Recognition_DAL()

    # Test data
    json_data = {
        "FeatureSet": "TestFeatureSet"
    }

    # Delete the feature set
    result = await dal.delete_feature_set(db_session, json_data)

    # Check if the deletion was successful
    assert result is True

    # Verify that the feature set no longer exists in the database
    feature_set = await db_session.execute(select(Feature_set).where(Feature_set.name == "TestFeatureSet"))
    assert feature_set is None

@pytest.mark.asyncio
async def test_get_list_of_all_feature_sets(db_session):
    # Initialize the DAL
    dal = Recognition_DAL()

    # Test data
    await db_session.execute(Feature_set.__table__.insert().values(name="FeatureSet1"))
    await db_session.execute(Feature_set.__table__.insert().values(name="FeatureSet2"))

    # Get list of all feature sets
    result = await dal.get_list_of_all_feature_sets(db_session)

    # Check if the result contains the expected feature sets
    assert result is not False
    assert len(result["FeatureSets"]) == 2
    assert "FeatureSet1" in result["FeatureSets"]
    assert "FeatureSet2" in result["FeatureSets"]

@pytest.mark.asyncio
async def test_principal_component_analysis(db_session):
    # Initialize the DAL
    dal = Recognition_DAL()

    # Test data
    json_data = {
        "FeatureSet": "TestFeatureSet",
        "NumOfComponents": 2
    }

    # Perform PCA
    result = await dal.principalComponentAnalysis(db_session, json_data)

    # Check if PCA was successful
    assert result is not False
    assert "FeatureSet" in result
    assert "X_pca" in result
    assert "ExplainedVariance" in result
    assert "1-NNScoreOriginal" in result
    assert "1-NNScorePCA" in result

@pytest.mark.asyncio
async def test_optimized_principal_component_analysis(db_session):
    # Initialize the DAL
    dal = Recognition_DAL()

    # Test data
    json_data = {
        "FeatureSet": "TestFeatureSet",
        "RequestedVariance": 0.95
    }

    # Perform optimized PCA
    result = await dal.optimizedPrincipalComponentAnalysis(db_session, json_data)

    # Check if optimized PCA was successful
    assert result is not False
    assert "FeatureSet" in result
    assert "OptimalNumOfComponents" in result
    assert "X_optimal_pca" in result
    assert "ExplainedVariance" in result
    assert "1-NNScoreOriginal" in result
    assert "1-NNScorePCA" in result

@pytest.mark.asyncio
async def test_hierarchical_clustering(db_session):
    # Initialize the DAL
    dal = Recognition_DAL()

    # Test data
    json_data = {
        "FeatureSet": "TestFeatureSet",
        "Metric": "euclidean",
        "NumOfClusters": 2
    }

    # Perform hierarchical clustering
    result = await dal.hierarhicalClustering(db_session, json_data)

    # Check if hierarchical clustering was successful
    assert result is not False
    assert "FeatureSet" in result
    assert "Metric" in result
    assert "DistanceMatrix" in result
    assert "LinkageMatrix" in result
    assert "ClusterLabels" in result
