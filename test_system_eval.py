from system_evaluator import SystemEvaluator
from system_evaluator_dataset import SYSTEM_EVAL_DATASET

evaluator = SystemEvaluator()

results = evaluator.evaluate_dataset(
    SYSTEM_EVAL_DATASET
)