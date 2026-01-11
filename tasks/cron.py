from django_cron import CronJobBase, Schedule
from data.helpers import ProcessLeagueCSV
from .models import ProcessedTasksM


class ProcessTasksCronJob(CronJobBase):
    """
        Cron Job to start asynchronously tasks
    """
    RUN_EVERY_5_MINUTES = 5
    schedule = Schedule(run_every_mins=RUN_EVERY_5_MINUTES)
    code = 'tasks.process_tasks_cron_job'

    def do(self):
        tasks_name_dict = {'process_csv_league': ProcessLeagueCSV}
        last_5_new_tasks = ProcessedTasksM.objects.filter(status='NEW').order_by('-created_at')[:5]
        for task in last_5_new_tasks:
            try:
                instance = tasks_name_dict[task.task_name](task=task)
                instance.run()
            except Exception as e:
                task.status = 'FAILED'
                task.error_name = e
                task.save()