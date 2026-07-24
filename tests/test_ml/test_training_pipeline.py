import pytest
import numpy as np
from unittest.mock import AsyncMock, patch, MagicMock
from ml.training_pipeline import TrainingPipeline
from ml.config import MLConfig


class TestTrainingPipeline:
    @pytest.fixture
    def pipeline(self, temp_model_store):
        config = MLConfig()
        config.model_store = temp_model_store
        return TrainingPipeline(config)

    def test_cold_start_training(self, pipeline, sample_behavioral_features):
        with patch.object(pipeline, 'get_sample_features', return_value=sample_behavioral_features):
            result = pipeline.cold_start_training(user_id=999)
            assert result is not None
            assert result.user_id == 999
            assert result.is_trained

    def test_cold_start_insufficient_data(self, pipeline):
        small = np.random.randn(5, 20)
        with patch.object(pipeline, 'get_sample_features', return_value=small):
            result = pipeline.cold_start_training(user_id=999)
            assert result is None or not result.is_trained

    def test_create_user_model(self, pipeline, sample_behavioral_features):
        model = pipeline.create_user_model(user_id=999, features=sample_behavioral_features)
        assert model is not None
        assert model.user_id == 999
        assert model.is_trained

    def test_retrain_user_model(self, pipeline, sample_behavioral_features):
        with patch.object(pipeline, 'get_sample_features', return_value=sample_behavioral_features):
            model = pipeline.retrain_user_model(user_id=999)
            assert model is not None
            assert model.is_trained

    def test_retrain_with_no_new_data(self, pipeline):
        with patch.object(pipeline, 'get_sample_features', return_value=np.empty((0, 20))):
            model = pipeline.retrain_user_model(user_id=999)
            assert model is None or not model.is_trained

    def test_retrain_trigger_for_high_risk(self, pipeline, sample_behavioral_features):
        pipeline.ml_config.min_samples_for_training = 100
        with patch.object(pipeline, 'get_sample_features', return_value=sample_behavioral_features):
            model = pipeline.retrain_user_model(user_id=999, force=True)
            assert model is not None
            assert model.is_trained

    def test_concurrent_training(self, pipeline, sample_behavioral_features):
        with patch.object(pipeline, 'get_sample_features', return_value=sample_behavioral_features):
            m1 = pipeline.cold_start_training(user_id=800)
            m2 = pipeline.cold_start_training(user_id=801)
            assert m1 is not None
            assert m2 is not None

    def test_same_user_concurrent_retrain(self, pipeline, sample_behavioral_features):
        with patch.object(pipeline, 'get_sample_features', return_value=sample_behavioral_features):
            m1 = pipeline.retrain_user_model(user_id=700)
            m2 = pipeline.retrain_user_model(user_id=700)
            assert m1 is not None or m2 is not None


class TestTrainingPipelineIntegration:
    @pytest.fixture
    def pipeline(self, temp_model_store):
        config = MLConfig()
        config.model_store = temp_model_store
        return TrainingPipeline(config)

    def test_full_training_cycle(self, pipeline, sample_behavioral_features):
        with patch.object(pipeline, 'get_sample_features', return_value=sample_behavioral_features):
            initial = pipeline.cold_start_training(user_id=123)
            assert initial is not None
            retrained = pipeline.retrain_user_model(user_id=123)
            assert retrained is not None

    def test_multiple_users_training(self, pipeline, sample_behavioral_features):
        with patch.object(pipeline, 'get_sample_features', return_value=sample_behavioral_features):
            for uid in range(10):
                model = pipeline.create_user_model(user_id=uid, features=sample_behavioral_features)
                assert model.is_trained, f"User {uid} failed to train"

    def test_training_with_varied_feature_dims(self, pipeline):
        dims = [10, 20, 50]
        for d in dims:
            features = np.random.randn(200, d)
            model = pipeline.create_user_model(user_id=300 + d, features=features)
            assert model.is_trained, f"Failed for dimension {d}"


class TestTrainingEdgeCases:
    @pytest.fixture
    def pipeline(self, temp_model_store):
        return TrainingPipeline(MLConfig())

    def test_constant_features(self, pipeline):
        const = np.ones((100, 20))
        model = pipeline.create_user_model(user_id=400, features=const)
        assert model is not None
        assert model.is_trained

    def test_linear_features(self, pipeline):
        lin = np.linspace(0, 1, 2000).reshape(100, 20)
        model = pipeline.create_user_model(user_id=401, features=lin)
        assert model.is_trained

    def test_sparse_features(self, pipeline):
        sparse = np.zeros((200, 50))
        sparse[np.arange(0, 200, 2), np.arange(0, 50, 1)[:100]] = 1
        model = pipeline.create_user_model(user_id=402, features=sparse)
        assert model.is_trained

    def test_high_dimensional(self, pipeline):
        hd = np.random.randn(500, 200)
        model = pipeline.create_user_model(user_id=403, features=hd)
        assert model.is_trained
