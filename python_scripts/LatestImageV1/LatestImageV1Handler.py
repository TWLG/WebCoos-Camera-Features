from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from python_scripts.LatestImageV1.LatestImageV1Model import LatestImageV1Model


class LatestImageV1Handler:
    interval = 30
    running = False

    def __init__(self, app, scheduler: BackgroundScheduler, socketIO):
        self.scheduler = scheduler
        self.name = "LatestImageV1"
        self.app = app
        self.job = None

        self.socketIO = socketIO
        self.model = LatestImageV1Model(self.app, self.socketIO)

    def get_return_head(self):
        """
        Returns a formatted string containing the current time and job name.

        Returns:
            str: A formatted string in the format '[current_time] (jobName): '
        """
        return f"({self.name}): "

    def update_interval(self, new_interval=30):
        """
        Update the interval for the job and reschedule it.

        Args:
            new_interval (int): The new interval in minutes. Default is 30.

        Returns:
            str: A message indicating the result of the update.

        Raises:
            None

        """
        if new_interval < 1:
            return self.get_return_head() + f"ERROR - Interval must be at least 1 minute"

        if self.scheduler.get_job(self.job):
            self.scheduler.remove_job(self.job)
            prev_interval = self.interval
            self.interval = new_interval
            self.job = self.scheduler.add_job(
                self.run, 'interval', minutes=self.interval)
        else:
            prev_interval = self.interval
            self.interval = new_interval

        return self.get_return_head() + f"Interval updated from {prev_interval} to {self.interval} minutes."

    def start(self):
        """
        Starts the service with the specified interval.

        If a job is already running, it is removed before starting a new one.
        The service is scheduled to run at the specified interval in minutes.

        Returns:
            str: A message indicating that the service has started with the specified interval.
        """
        if self.job:
            self.scheduler.remove_job(self.job.id)
        self.job = self.scheduler.add_job(
            self.run, 'interval', minutes=self.interval)
        self.running = True
        return self.get_return_head() + f"Service started with {self.interval} minute interval."

    def run(self):
        """
        Runs the job to predict the latest image using the WebCoos API.

        This method calls the `predict_image` function with the WebCoos API key
        from the application's configuration. It sets the `running` flag to True
        if the prediction is successful.

        Raises:
            Exception: If an error occurs during the prediction process.

        Returns:
            None
        """

        try:
            self.socketIO.emit('interface_console',
                               {'message': self.get_return_head() + "Running LatestImageV1"})

            data_request_result = self.model.request_latest_image()

            self.socketIO.emit('interface_console',
                               {'message': self.get_return_head() + data_request_result})

            model_results = self.model.run_model()

            self.socketIO.emit('interface_console',
                               {'message': self.get_return_head() + str(model_results)})

            self.running = True
        except Exception as e:
            self.socketIO.emit('interface_console',
                               {'message': self.get_return_head() + str(e)})
            self.app.logger.error(
                self.get_return_head() + f"An error occurred: {str(e)}")
            self.running = False
            self.stop()

    def get_running_state(self):
        if self.running:
            return self.get_return_head() + "Service is running."
        else:
            return self.get_return_head() + "Service is not running."

    def stop(self):
        """
        Stops the service.

        If the service is running, it removes the scheduled job and sets the `job` attribute to None.
        It also sets the `running` attribute to False.

        Returns:
            str: A message indicating that the service has been stopped.
        """
        if self.job:
            self.scheduler.remove_job(self.job.id)
            self.job = None
        self.running = False
        return self.get_return_head() + f"Service stopped."
