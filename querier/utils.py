class M(models.Model):
  first_name = models.CharField()
  last_name = models.CharField()
  username = models.CharField()
  age = models.IntegerField()