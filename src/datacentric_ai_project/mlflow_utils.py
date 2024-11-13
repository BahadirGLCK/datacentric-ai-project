import mlflow
import mlflow.pytorch
import os

class MLflowHelper:
    def __init__(self, experiment_name="Default Experiment", run_name=None):
        """
        Initialize MLflowHelper with an experiment name and an optional run name.
        """
        self.experiment_name = experiment_name
        self.run_name = run_name
        mlflow.set_experiment(self.experiment_name)
        self.run = None

    def start_run(self, params=None):
        """
        Start a new MLflow run. Logs parameters if provided.
        
        Args:
            params (dict): A dictionary of parameters to log.
        """
        self.run = mlflow.start_run(run_name=self.run_name)

        if params:
            self.log_params(params)
    
    def log_params(self, params):
        """
        Log parameters to the active MLflow run.
        
        Args:
            params (dict): A dictionary of parameters to log.
        """
        if not self.run:
            raise RuntimeError("No active MLflow run. Call start_run() first.")
        
        for key, value in params.items():
            mlflow.log_param(key, value)

    def log_metric(self, key, value, step=None):
        """
        Log a single metric to the active MLflow run.
        
        Args:
            key (str): Metric name.
            value (float): Metric value.
            step (int, optional): Training step at which the metric is logged.
        """
        if not self.run:
            raise RuntimeError("No active MLflow run. Call start_run() first.")
        
        mlflow.log_metric(key, value, step=step)

    def log_metrics(self, metrics, step=None):
        """
        Log multiple metrics at once to the active MLflow run.
        
        Args:
            metrics (dict): A dictionary of metrics to log.
            step (int, optional): Training step at which the metrics are logged.
        """
        if not self.run:
            raise RuntimeError("No active MLflow run. Call start_run() first.")
        
        for key, value in metrics.items():
            mlflow.log_metric(key, value, step=step)

    def log_artifact(self, file_path, artifact_path=None):
        """
        Log an artifact (e.g., a file) to the active MLflow run.
        
        Args:
            file_path (str): Path to the file to log.
            artifact_path (str, optional): Directory within the MLflow artifacts to place the file.
        """
        if not self.run:
            raise RuntimeError("No active MLflow run. Call start_run() first.")
        
        mlflow.log_artifact(file_path, artifact_path=artifact_path)

    def log_model(self, model, path="model"):
        """
        Log a PyTorch model to the active MLflow run.
        
        Args:
            model (torch.nn.Module): PyTorch model to log.
            path (str): Directory within the MLflow artifacts to place the model.
        """
        if not self.run:
            raise RuntimeError("No active MLflow run. Call start_run() first.")
        
        mlflow.pytorch.log_model(model, path)

    def log_figure(self, fig, filename="figure.png", artifact_path="figures"):
        """
        Log a matplotlib figure as an artifact.
        
        Args:
            fig (matplotlib.figure.Figure): Figure to log.
            filename (str): Filename to save the figure as.
            artifact_path (str): Directory within the MLflow artifacts to place the figure.
        """
        fig_path = os.path.join(artifact_path, filename)
        os.makedirs(artifact_path, exist_ok=True)
        fig.savefig(fig_path)
        self.log_artifact(fig_path, artifact_path=artifact_path)

    def end_run(self):
        """
        End the current MLflow run.
        """
        if self.run:
            mlflow.end_run()
            self.run = None