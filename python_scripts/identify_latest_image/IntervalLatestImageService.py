from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from python_scripts.identify_latest_image.identify_latest_image import predict_image
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR


class IntervalLatestImageService:
    interval = 30
    running = False

    def __init__(self, app, scheduler: BackgroundScheduler, socketIO):
        self.scheduler = scheduler
        self.jobName = "IntervalLatestImageJob"
        self.app = app
        self.job = None
        self.API_KEY = app.config['WEBCOOS_API_KEY']

        self.socketIO = socketIO

        def job_listener(event):
            """
            Listens for job events and emits corresponding messages through socketIO.

            Args:
                event: The job event.

            Returns:
                None
            """
            if event.exception:
                self.app.logger.info(
                    self.get_return_head() + f"Emitting error...")
                self.socketIO.emit('IntervalLatestImageJobError', {
                    'message': event.exception.message})
            else:
                self.app.logger.info(
                    self.get_return_head() + f"Emitting success...")
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.socketIO.emit('IntervalLatestImageJobExecuted',
                                   {'message': current_time})

        self.scheduler.add_listener(
            job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    def get_return_head(self):
        """
        Returns a formatted string containing the current time and job name.

        Returns:
            str: A formatted string in the format '[current_time] (jobName): '
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"[{current_time}] ({self.jobName}): "

    def refresh_key(self):
        self.API_KEY = self.app.config['WEBCOOS_API_KEY']
        return self.get_return_head() + f"API Key refreshed."

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

        prev_interval = self.interval
        self.interval = new_interval

        if self.scheduler.get_job(self.job):
            self.scheduler.remove_job(self.job)

            self.job = self.scheduler.add_job(
                self.run, 'interval', minutes=self.interval)
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
        self.app.logger.info(
            self.get_return_head() + f"Running Job...")
        try:
            results = predict_image(self.app.config['WEBCOOS_API_KEY'])
            print(results)
            self.running = True
        except Exception as e:
            self.app.logger.error(
                self.get_return_head() + f"An error occurred: {str(e)}")

    def get_running_state(self):
        """
        Returns the current running state of the service.

        Returns:
            bool: True if the service is running, False otherwise.
        """
        return self.running

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
