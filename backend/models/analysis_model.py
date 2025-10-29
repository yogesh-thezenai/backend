from django.db import models


class AgentEvaluation(models.Model):
    id = models.AutoField(primary_key=True)
    file_id = models.IntegerField(default=-1)
    evaluation_type = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create_from_json(cls, evaluation, data: dict):
        model_fields = {f.name for f in cls._meta.get_fields()}
        filtered_data = {k: v for k, v in data.items() if k in model_fields}
        return cls.objects.create(evaluation=evaluation, **filtered_data)


class BusinessCriticalMetric(models.Model):
    evaluation = models.ForeignKey(AgentEvaluation, on_delete=models.CASCADE, related_name="business_metrics")
    greet_intro = models.IntegerField(default=0)
    greet_intro_pg = models.IntegerField(default=0)
    greet_intro_agent_intro = models.IntegerField(default=0)
    cust_verf = models.IntegerField(default=0)
    cust_verf_correct = models.IntegerField(default=0)
    cust_verf_acc = models.IntegerField(default=0)
    call_purp = models.IntegerField(default=0)
    call_purp_clear = models.IntegerField(default=0)
    call_purp_tone = models.IntegerField(default=0)
    total_score = models.IntegerField(default=0)
    max_score = models.IntegerField(default=0)

    @classmethod
    def create_from_json(cls, evaluation, data: dict):
        model_fields = {f.name for f in cls._meta.get_fields()}
        filtered_data = {k: v for k, v in data.items() if k in model_fields}
        return cls.objects.create(evaluation=evaluation, **filtered_data)

class CustomerCriticalErrorMetric(models.Model):
    evaluation = models.ForeignKey(AgentEvaluation, on_delete=models.CASCADE, related_name="customer_error_metrics")
    metric_name = models.CharField(max_length=100)
    score = models.IntegerField(default=0)
    max_score = models.IntegerField(default=0)
    comment = models.TextField()

    @classmethod
    def create_from_json(cls, evaluation, data: dict):
        print("cleaning before inserting")
        print(data)
        model_fields = {f.name for f in cls._meta.get_fields()}
        filtered_data = {k: v for k, v in data.items() if k in model_fields}
        return cls.objects.create(evaluation=evaluation, **filtered_data)
