from django.db import models
import datetime
from django.contrib.auth.models import User
import hashlib
# Create your models here.


class VoteModel(models.Model):
    class Meta:
        # название записи в таблице
        verbose_name = 'Голосование'
        # название таблицы
        verbose_name_plural = 'Голосования'

    # параметр = тип поля()
    title = models.CharField(max_length=300, verbose_name='Название', default='')
    date = models.DateField(verbose_name='Дата', default=datetime.date.today)
    description = models.TextField(verbose_name="Описание", default="", blank=True)
    candidate = models.CharField(max_length=300, verbose_name='Название', default='', blank=True)
    complete = models.BooleanField(verbose_name="Завершить голосование", default=False)
    start = models.BooleanField(verbose_name="Начать голосование", default=False)

    public_key = models.TextField(verbose_name="Открытый ключ", default="", blank=True)
    private_key = models.TextField(verbose_name="Закрытый ключ", default="", blank=True)
    p = models.IntegerField(verbose_name="p", default=1, blank=True)
    q = models.IntegerField(verbose_name="q", default=1, blank=True)

    # отвечает за название записи в самой таблице
    def __str__(self):
        return self.title


class CandidateModel(models.Model):
    class Meta:
        verbose_name = 'Кандидат'
        verbose_name_plural = 'Кандидаты'

    name = models.CharField(max_length=300, verbose_name='ФИО', default='')
    type = models.CharField(max_length=100, verbose_name="Тип", default="", blank=True)
    description = models.TextField(verbose_name="Описание", default="", blank=True)
    group = models.CharField(max_length=100, verbose_name="Группа", default="", blank=True)
    # внешняя ссылка на голосование для кандидата
    vote = models.ForeignKey(VoteModel, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class VoiceUser(models.Model):
    class Meta:
        verbose_name = 'Голос пользователя'
        verbose_name_plural = 'Голоса Пользователей'

    # внешняя ссылка на голосование для голоса пользователя
    vote = models.ForeignKey(VoteModel, blank=True, null=True, on_delete=models.PROTECT)
    voice = models.IntegerField(verbose_name='Значение голоса')
    # внешняя ссылка на пользователя, который голосует
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.PROTECT)

    def __str__(self):
        return self.user.username

    # функция вычисления хэша
    def get_hash(self):
        res_str = str.encode(
            str(self.vote.title) + str(self.user.username) + str(self.voice)
        )
        return hashlib.sha256(res_str).hexdigest()


class HashVoiceUser(models.Model):
    class Meta:
        verbose_name = 'Хеш голоса пользователя'
        verbose_name_plural = 'Хеши Голосов Пользователей'

    voice_hash = models.TextField(verbose_name='Хеш значения голоса', default=0)
    # внешняя ссылка на голос пользователя
    voice = models.ForeignKey(VoiceUser, on_delete=models.PROTECT)

    def __str__(self):
        return str(self.voice.vote.title) + ' ' + str(self.voice.user.username)

    # функция проверки целостности
    def integrity_control(self):
        return self.voice.get_hash() == self.voice_hash
