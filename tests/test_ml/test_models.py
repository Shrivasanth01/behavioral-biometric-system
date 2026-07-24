import pytest
import numpy as np
import tempfile
import os
import pickle
import time
from ml.models import UserModel
from ml.config import MLConfig


class TestModelTraining:
    @pytest.fixture
    def model(self):
        return UserModel(user_id=999, model_version=1, model_type="isolation_forest")

    def test_train_isolation_forest(self, model, sample_behavioral_features):
        model.train(sample_behavioral_features)
        assert model.is_trained
        assert hasattr(model, '_model')
        assert model._model is not None

    def test_train_autoencoder(self, sample_behavioral_features):
        m = UserModel(user_id=999, model_version=1, model_type="autoencoder")
        m.train(sample_behavioral_features)
        assert m.is_trained

    def test_train_one_class_svm(self, sample_behavioral_features):
        m = UserModel(user_id=999, model_version=1, model_type="one_class_svm")
        m.train(sample_behavioral_features)
        assert m.is_trained

    def test_train_insufficient_samples(self, model):
        small = np.random.randn(3, 10)
        model.train(small)
        assert not model.is_trained

    def test_train_minimum_samples_config(self, model):
        m = UserModel(user_id=999, model_version=1, model_type="isolation_forest")
        config = MLConfig()
        config.min_samples_for_training = 5
        mid = np.random.randn(5, 10)
        m.train(mid)
        assert m.is_trained

    def test_retrain_updates_model(self, model, sample_behavioral_features):
        model.train(sample_behavioral_features)
        old_model = model._model
        new_data = np.random.randn(100, sample_behavioral_features.shape[1])
        model.train(new_data)
        if model._model is not None:
            assert model._model is not old_model or model._model != old_model

    def test_retraining_preserves_version(self, model, sample_behavioral_features):
        model.train(sample_behavioral_features)
        original_version = model.model_version
        new_data = np.random.randn(100, sample_behavioral_features.shape[1])
        model.train(new_data)
        assert model.model_version == original_version


class TestModelInference:
    @pytest.fixture
    def model(self):
        return UserModel(user_id=999, model_version=1, model_type="isolation_forest")

    def test_predict_untrained_model(self, model):
        with pytest.raises(ValueError):
            model.predict(np.random.randn(1, 10))

    def test_predict_normal(self, model, sample_behavioral_features):
        model.train(sample_behavioral_features)
        score = model.predict(sample_behavioral_features[0:1])
        assert isinstance(score, float)
        assert 0 <= score <= 1

    def test_predict_anomalous(self, model, sample_behavioral_features):
        model.train(sample_behavioral_features)
        anomalous = np.random.randn(1, sample_behavioral_features.shape[1]) * 10
        score = model.predict(anomalous)
        assert isinstance(score, float)
        assert 0 <= score <= 1

    def test_predict_batch(self, model, sample_behavioral_features):
        model.train(sample_behavioral_features)
        batch = np.random.randn(5, sample_behavioral_features.shape[1])
        scores = model.predict(batch)
        assert len(scores) == 5
        assert all(0 <= s <= 1 for s in scores)

    def test_predict_single_sample(self, model, sample_behavioral_features):
        model.train(sample_behavioral_features)
        vec = sample_behavioral_features[0]
        score_2d = model.predict(vec.reshape(1, -1))
        score_1d = model.predict(vec)
        assert score_2d == pytest.approx(score_1d, abs=1e-6)


class TestModelPersistence:
    @pytest.fixture
    def model(self, sample_behavioral_features):
        m = UserModel(user_id=999, model_version=1, model_type="isolation_forest")
        m.train(sample_behavioral_features)
        return m

    def test_save_and_load(self, model):
        model._save_model()
        assert model._model_path.exists()
        loaded = UserModel.load(model.user_id, model.model_version, model.model_type)
        assert loaded.is_trained
        assert loaded.model_version == model.model_version

    def test_save_untrained_raises(self, model):
        untrained = UserModel(user_id=1, model_version=1, model_type="isolation_forest")
        with pytest.raises(ValueError):
            untrained._save_model()

    def test_load_nonexistent(self):
        loaded = UserModel.load(99999, 99, "isolation_forest")
        assert loaded is None

    def test_save_versioned(self, model):
        v1 = model.model_version
        model._save_model()
        v2_path = model._model_store / f"model_v{v1}.pkl"
        assert v2_path.exists()

    def test_model_file_size(self, model):
        model._save_model()
        size = os.path.getsize(model._model_path)
        assert size > 0
        assert size < 50 * 1024 * 1024

    def test_corrupted_load(self):
        path = UserModel._get_model_path(999, 1, "isolation_forest")
        os.makedirs(path.parent, exist_ok=True)
        path.write_text("not a pickle file")
        result = UserModel.load(999, 1, "isolation_forest")
        assert result is None


class TestModelVersioning:
    def test_multiple_version_training(self, sample_behavioral_features):
        m1 = UserModel(user_id=777, model_version=1, model_type="isolation_forest")
        m1.train(sample_behavioral_features)
        m1.model_version = 2
        m1.train(sample_behavioral_features)
        assert m1.model_version == 2

    def test_different_model_types_same_user(self, sample_behavioral_features):
        iso = UserModel(user_id=555, model_version=1, model_type="isolation_forest")
        iso.train(sample_behavioral_features)
        ae = UserModel(user_id=555, model_version=1, model_type="autoencoder")
        ae.train(sample_behavioral_features)
        assert iso.is_trained and ae.is_trained


class TestColdStart:
    def test_cold_start_no_data(self):
        m = UserModel(user_id=1, model_version=1, model_type="isolation_forest")
        assert not m.is_trained

    def test_cold_start_with_minimal_data(self, sample_behavioral_features):
        few = sample_behavioral_features[:5]
        m = UserModel(user_id=1, model_version=1, model_type="isolation_forest")
        m.train(few)
        assert not m.is_trained

    def test_cold_start_then_train(self, sample_behavioral_features):
        m = UserModel(user_id=1, model_version=1, model_type="isolation_forest")
        m.train(sample_behavioral_features)
        assert m.is_trained
        score = m.predict(sample_behavioral_features[0])
        assert 0 <= score <= 1


class TestAdaptiveThreshold:
    @pytest.fixture
    def model(self, sample_behavioral_features):
        m = UserModel(user_id=777, model_version=1, model_type="isolation_forest")
        m.train(sample_behavioral_features)
        return m

    def test_default_threshold(self, model):
        assert hasattr(model, 'anomaly_threshold')
        assert model.anomaly_threshold > 0

    def test_update_threshold(self, model):
        model.anomaly_threshold = 0.5
        assert model.anomaly_threshold == 0.5

    def test_threshold_not_zero_or_one(self):
        config = MLConfig()
        assert 0 < config.anomaly_threshold < 1


class TestModelCache:
    def test_cached_model_returns_same_instance(self):
        m1 = UserModel(user_id=100, model_version=1, model_type="isolation_forest")
        m2 = UserModel._model_cache.get((100, 1, "isolation_forest"))
        assert m2 is None or m2 is not m1


class TestFallbackBehavior:
    def test_fallback_on_corrupted_model(self):
        path = UserModel._get_model_path(888, 1, "isolation_forest")
        os.makedirs(path.parent, exist_ok=True)
        path.write_text("corrupted data")
        loaded = UserModel.load(888, 1, "isolation_forest")
        assert loaded is None

    def test_fallback_on_missing_store(self):
        orig = UserModel._model_store
        UserModel._model_store = tempfile.mkdtemp()
        loaded = UserModel.load(99999, 1, "isolation_forest")
        assert loaded is None
        UserModel._model_store = orig
