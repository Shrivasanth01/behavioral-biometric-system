import numpy as np
import pandas as pd
from typing import Optional, List, Dict, Tuple, Any
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    roc_curve,
    precision_recall_curve,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    accuracy_score,
    matthews_corrcoef,
)
from scipy import stats
import logging

logger = logging.getLogger(__name__)


class Evaluator:
    @staticmethod
    def evaluate_binary(
        y_true: np.ndarray,
        y_scores: np.ndarray,
        threshold: Optional[float] = None,
    ) -> Dict[str, Any]:
        y_true = np.asarray(y_true, dtype=np.int64)
        y_scores = np.asarray(y_scores, dtype=np.float64)

        if threshold is None:
            threshold = np.percentile(y_scores, 95)

        y_pred = (y_scores >= threshold).astype(np.int64)

        n_pos = int(np.sum(y_true))
        n_neg = int(len(y_true) - n_pos)

        metrics = {
            "n_samples": len(y_true),
            "n_positive": n_pos,
            "n_negative": n_neg,
            "threshold": float(threshold),
        }

        if len(np.unique(y_true)) < 2:
            logger.warning("Only one class present in y_true")
            metrics.update({
                "accuracy": float(accuracy_score(y_true, y_pred)),
                "f1": 0.0,
                "precision": 0.0,
                "recall": 0.0,
                "mcc": 0.0,
                "roc_auc": 0.0,
                "avg_precision": 0.0,
            })
            return metrics

        metrics.update({
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "f1": float(f1_score(y_true, y_pred, zero_division=0)),
            "precision": float(precision_score(y_true, y_pred, zero_division=0)),
            "recall": float(recall_score(y_true, y_pred, zero_division=0)),
            "mcc": float(matthews_corrcoef(y_true, y_pred)),
            "roc_auc": float(roc_auc_score(y_true, y_scores)),
            "avg_precision": float(average_precision_score(y_true, y_scores)),
        })

        tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
        metrics["true_positive"] = int(tp)
        metrics["true_negative"] = int(tn)
        metrics["false_positive"] = int(fp)
        metrics["false_negative"] = int(fn)

        if (tp + fp) > 0:
            metrics["false_discovery_rate"] = float(fp / (tp + fp))
        else:
            metrics["false_discovery_rate"] = 0.0

        if (tn + fp) > 0:
            metrics["false_positive_rate"] = float(fp / (tn + fp))
        else:
            metrics["false_positive_rate"] = 0.0

        return metrics

    @staticmethod
    def cross_validate(
        model_fn,
        features: np.ndarray,
        labels: np.ndarray,
        n_folds: int = 5,
        random_state: int = 42,
    ) -> Dict[str, Any]:
        from sklearn.model_selection import StratifiedKFold

        features = np.asarray(features, dtype=np.float64)
        labels = np.asarray(labels, dtype=np.int64)

        if len(np.unique(labels)) < 2:
            return {"error": "Need at least 2 classes for cross-validation"}

        skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=random_state)
        fold_metrics = []

        for fold_idx, (train_idx, test_idx) in enumerate(skf.split(features, labels)):
            X_train, X_test = features[train_idx], features[test_idx]
            y_train, y_test = labels[train_idx], labels[test_idx]

            try:
                model = model_fn()
                model.train(X_train)
                scores = model.score_batch(X_test)
                metrics = Evaluator.evaluate_binary(y_test, scores)
                metrics["fold"] = fold_idx
                fold_metrics.append(metrics)
            except Exception as e:
                logger.error(f"Fold {fold_idx} failed: {e}")
                continue

        if not fold_metrics:
            return {"error": "All folds failed"}

        summary = {}
        for key in ["accuracy", "f1", "precision", "recall", "mcc", "roc_auc", "avg_precision"]:
            values = [m[key] for m in fold_metrics]
            summary[key] = {
                "mean": float(np.mean(values)),
                "std": float(np.std(values)),
                "values": [float(v) for v in values],
            }

        summary["n_folds"] = len(fold_metrics)
        summary["fold_metrics"] = fold_metrics
        return summary

    @staticmethod
    def compare_models(
        model_results: Dict[str, Dict[str, float]],
        metric: str = "roc_auc",
    ) -> Dict[str, Any]:
        if len(model_results) < 2:
            return {"error": "Need at least 2 models to compare"}

        models = list(model_results.keys())
        scores_a = np.array([model_results[m].get(metric, 0) for m in models])

        comparisons = {}
        for i in range(len(models)):
            for j in range(i + 1, len(models)):
                m1, m2 = models[i], models[j]
                s1, s2 = model_results[m1].get(metric, 0), model_results[m2].get(metric, 0)

                if hasattr(s1, "__iter__") and hasattr(s2, "__iter__"):
                    t_stat, p_value = stats.ttest_ind(s1, s2)
                else:
                    t_stat, p_value = 0.0, 1.0

                comparisons[f"{m1}_vs_{m2}"] = {
                    "model_1": m1,
                    "model_2": m2,
                    "score_1": float(np.mean(s1)) if hasattr(s1, "__iter__") else float(s1),
                    "score_2": float(np.mean(s2)) if hasattr(s2, "__iter__") else float(s2),
                    "difference": float(np.mean(s1) - np.mean(s2)) if hasattr(s1, "__iter__") else float(s1 - s2),
                    "t_statistic": float(t_stat),
                    "p_value": float(p_value),
                    "significant": bool(p_value < 0.05),
                }

        return {
            "metric": metric,
            "comparisons": comparisons,
            "best_model": max(models, key=lambda m: np.mean(model_results[m].get(metric, 0)) if hasattr(model_results[m].get(metric, 0), "__iter__") else model_results[m].get(metric, 0)),
        }

    @staticmethod
    def compute_roc_curve(
        y_true: np.ndarray,
        y_scores: np.ndarray,
    ) -> Dict[str, Any]:
        fpr, tpr, thresholds = roc_curve(y_true, y_scores)
        auc = roc_auc_score(y_true, y_scores)
        return {
            "fpr": fpr.tolist(),
            "tpr": tpr.tolist(),
            "thresholds": thresholds.tolist(),
            "auc": float(auc),
            "equal_error_rate": float(
                fpr[np.argmin(np.abs(fpr - (1 - tpr)))] if len(fpr) > 0 else 0.0
            ),
        }

    @staticmethod
    def compute_pr_curve(
        y_true: np.ndarray,
        y_scores: np.ndarray,
    ) -> Dict[str, Any]:
        precision, recall, thresholds = precision_recall_curve(y_true, y_scores)
        ap = average_precision_score(y_true, y_scores)
        return {
            "precision": precision.tolist(),
            "recall": recall.tolist(),
            "thresholds": thresholds.tolist(),
            "average_precision": float(ap),
        }

    @staticmethod
    def find_optimal_threshold(
        y_true: np.ndarray,
        y_scores: np.ndarray,
        method: str = "youden",
    ) -> Dict[str, Any]:
        fpr, tpr, thresholds = roc_curve(y_true, y_scores)

        if method == "youden":
            youden_j = tpr - fpr
            best_idx = np.argmax(youden_j)
        elif method == "closest_to_01":
            dist = np.sqrt((1 - tpr) ** 2 + fpr ** 2)
            best_idx = np.argmin(dist)
        elif method == "f1":
            precision, recall, _ = precision_recall_curve(y_true, y_scores)
            f1_scores = 2 * precision * recall / (precision + recall + 1e-10)
            best_idx = np.argmax(f1_scores)
            return {
                "threshold": float(thresholds[best_idx]) if best_idx < len(thresholds) else float(thresholds[-1]),
                "f1": float(f1_scores[best_idx]),
                "method": method,
            }
        else:
            best_idx = np.argmax(tpr - fpr)

        return {
            "threshold": float(thresholds[best_idx]) if best_idx < len(thresholds) else float(thresholds[-1]),
            "tpr": float(tpr[best_idx]),
            "fpr": float(fpr[best_idx]),
            "youden_j": float(tpr[best_idx] - fpr[best_idx]),
            "method": method,
        }

    @staticmethod
    def permutation_feature_importance(
        model,
        features: np.ndarray,
        labels: np.ndarray,
        n_repeats: int = 5,
        random_state: int = 42,
    ) -> Dict[str, Any]:
        features = np.asarray(features, dtype=np.float64)
        labels = np.asarray(labels, dtype=np.int64)
        rng = np.random.RandomState(random_state)

        baseline_scores = model.score_batch(features)
        baseline_auc = roc_auc_score(labels, baseline_scores)

        n_features = features.shape[1]
        importances = np.zeros((n_features, n_repeats))

        for feat_idx in range(n_features):
            for repeat in range(n_repeats):
                permuted = features.copy()
                permuted[:, feat_idx] = rng.permutation(permuted[:, feat_idx])
                permuted_scores = model.score_batch(permuted)
                permuted_auc = roc_auc_score(labels, permuted_scores)
                importances[feat_idx, repeat] = baseline_auc - permuted_auc

        return {
            "importances_mean": [float(np.mean(importances[i])) for i in range(n_features)],
            "importances_std": [float(np.std(importances[i])) for i in range(n_features)],
            "baseline_auc": float(baseline_auc),
        }

    @staticmethod
    def statistical_significance(
        scores_a: np.ndarray,
        scores_b: np.ndarray,
        test: str = "wilcoxon",
    ) -> Dict[str, Any]:
        scores_a = np.asarray(scores_a, dtype=np.float64)
        scores_b = np.asarray(scores_b, dtype=np.float64)

        if test == "wilcoxon":
            if len(scores_a) != len(scores_b):
                raise ValueError("Wilcoxon test requires paired samples")
            stat, p_value = stats.wilcoxon(scores_a, scores_b)
        elif test == "mannwhitney":
            stat, p_value = stats.mannwhitneyu(scores_a, scores_b)
        elif test == "ttest":
            stat, p_value = stats.ttest_ind(scores_a, scores_b)
        else:
            raise ValueError(f"Unknown test: {test}")

        return {
            "test": test,
            "statistic": float(stat),
            "p_value": float(p_value),
            "significant": bool(p_value < 0.05),
            "mean_a": float(np.mean(scores_a)),
            "mean_b": float(np.mean(scores_b)),
        }
